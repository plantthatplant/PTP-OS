"""The Edge Watcher — turn a folder of scheduled Synopta exports into a live Canonical Snapshot,
safely and unattended, forever.

What it guarantees (the Sprint-14 contract):

  • Watches an import folder on a fixed interval.
  • Detects new exports; ignores files it has already imported (content-hash dedup).
  • Detects partial writes: a file must be the same size, unmodified, and openable for a debounce
    window before it is read — an export still being written is left alone.
  • Recovers after reboot / power loss: the checkpoint is durable; `latest.json` is only ever
    replaced atomically; an interrupted import simply re-runs idempotently next scan.
  • Retries safely: a transient (IO) failure is retried a bounded number of times, then the file
    is quarantined to FAILED — never an infinite loop.
  • Never publishes an invalid observation (validation gate) and never overwrites newer reality
    with older (freshness guard).
  • Never crashes: every file is processed in isolation; a bad file degrades to a logged failure
    and a raised Knowledge Gap, and the watcher keeps going.
  • Processes multiple exports arriving together, oldest reading first, so `latest.json` ends on
    the freshest truth.
"""
from __future__ import annotations

import os
import shutil
import time
from typing import Dict, List, Optional, Tuple

from .. import _paths
from ..log import append_event, now_iso
from . import gaps
from .checkpoint import Checkpoint, file_hash
from .config import EdgeConfig
from .health import CollectorHealth
from .parsers import ParseError, parse_export
from .pipeline import process_export

# Files that are obviously still being written or are editor/lock artefacts — never imported.
_IGNORE_PREFIXES = ("~$", ".", "_")
_IGNORE_SUFFIXES = (".tmp", ".part", ".partial", ".crdownload", ".filepart", ".~tmp", ".lock")


def _safe_event(event):
    """Wrap the event/log callback so a logging problem (e.g. a console that can't encode a
    character) can never propagate into — and be mistaken for — a file-processing failure."""
    if event is None:
        return lambda msg: None

    def safe(msg):
        try:
            event(msg)
        except Exception:
            pass

    return safe


def _read_facility(path: str) -> dict:
    import json
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


class Watcher:
    def __init__(self, cfg: EdgeConfig, event=None):
        self.cfg = cfg
        self.event = _safe_event(event)
        cfg.ensure_dirs()
        self.checkpoint = Checkpoint(cfg.checkpoint_path)
        self.health = CollectorHealth.load_or_new(
            cfg.health_path, watching=cfg.import_path, expected_interval_s=cfg.freshness_sla_s)
        self.facility = _read_facility(cfg.facility_path)
        # path -> (size, mtime, monotonic_first_seen) for the stability/debounce window
        self._pending: Dict[str, Tuple[int, float, float]] = {}
        self.health.save()

    # ── discovery ──────────────────────────────────────────────────────────────
    def _candidates(self) -> List[str]:
        try:
            names = os.listdir(self.cfg.import_path)
        except OSError as e:
            self.event(f"import folder unreadable: {e}")
            return []
        out = []
        for n in names:
            low = n.lower()
            if n.startswith(_IGNORE_PREFIXES) or low.endswith(_IGNORE_SUFFIXES):
                continue
            if os.path.splitext(low)[1] not in self.cfg.supported_formats:
                continue
            full = os.path.join(self.cfg.import_path, n)
            if os.path.isfile(full):
                out.append(full)
        return out

    def _is_stable(self, path: str) -> bool:
        """True once a file has clearly finished being written AND can be opened for reading.

        "Finished" is satisfied either way:
          • it has been quiet on disk (mtime older than the debounce window) — covers files
            already waiting at startup / after a reboot, imported without an extra cycle's delay; or
          • we have seen the same size+mtime for the debounce window across scans — covers a file
            that arrived while we were watching.
        The final open-for-read guard rejects a file a writer still holds locked, so an export
        mid-write is never mistaken for a finished one."""
        try:
            st = os.stat(path)
        except OSError:
            self._pending.pop(path, None)
            return False
        size, mtime = st.st_size, st.st_mtime
        now_mono, now_wall = time.monotonic(), time.time()
        prev = self._pending.get(path)
        if prev is None or prev[0] != size or prev[1] != mtime:
            self._pending[path] = (size, mtime, now_mono)
            first_seen = now_mono
        else:
            first_seen = prev[2]
        quiet_on_disk = (now_wall - mtime) >= self.cfg.stability_seconds
        unchanged_window = (now_mono - first_seen) >= self.cfg.stability_seconds
        if not (quiet_on_disk or unchanged_window):
            return False
        # Final guard: a partially written / locked file may match on size but refuse to open.
        try:
            with open(path, "rb") as f:
                f.read(1)
        except OSError:
            return False
        return True

    # ── one scan ─────────────────────────────────────────────────────────────────
    def scan_once(self) -> int:
        """Process every stable, new file. Returns how many were published. Never raises."""
        published = 0
        try:
            stable = [p for p in self._candidates() if self._is_stable(p)]
        except Exception as e:                              # discovery must never crash the loop
            self.event(f"scan error (ignored): {e}")
            return 0
        # Drop tracking for files that have left the folder.
        present = set(self._candidates())
        for gone in [p for p in self._pending if p not in present]:
            self._pending.pop(gone, None)
        # Oldest reading first, so latest.json lands on the freshest export when several arrive.
        stable.sort(key=lambda p: os.path.getmtime(p) if os.path.exists(p) else 0)
        for path in stable:
            try:
                if self._process_file(path) == "published":
                    published += 1
            except Exception as e:                          # one bad file never stops the rest
                self._fail_transient_or_content(path, f"unexpected error: {e}", content=False)
        return published

    # ── per-file processing ───────────────────────────────────────────────────────
    def _process_file(self, path: str) -> str:
        name = os.path.basename(path)
        # Size guard before doing anything expensive.
        try:
            size = os.path.getsize(path)
        except OSError:
            return "skipped"
        if size > self.cfg.max_file_bytes:
            self._move(path, self.cfg.failed_path, name)
            gap = gaps.raise_gap("invalid-export",
                                 f"export '{name}' exceeds the size limit and was not imported",
                                 file=name, detail=f"{size} bytes > {self.cfg.max_file_bytes}")
            self.health.record_failure(name, "file too large", gap)
            self._log(name, "failed", note="file too large")
            return "failed"

        # Content-hash identity → dedup and reboot reconciliation.
        try:
            digest = file_hash(path)
        except OSError as e:
            return self._fail_transient_or_content(path, f"could not read file: {e}", content=False)

        if self.checkpoint.is_processed(digest):
            # Already imported in a previous cycle/run — reconcile by filing it away, don't redo.
            self._move(path, self.cfg.archive_path, name)
            self.health.record_duplicate()
            self._pending.pop(path, None)
            self._log(name, "duplicate", note="content already imported")
            return "duplicate"

        # PARSE (format → raw vendor dict). A parse failure is a content problem: no retry.
        t0 = time.monotonic()
        try:
            raw = parse_export(path, column_map=self.cfg.column_map, default_tz=self.cfg.default_tz)
        except ParseError as e:
            return self._fail_transient_or_content(path, f"unparseable export: {e}", content=True)
        except OSError as e:
            return self._fail_transient_or_content(path, f"read error: {e}", content=False)

        # TRANSLATE → VALIDATE → PUBLISH (reuses the existing pipeline unchanged).
        outcome = process_export(raw, self.facility, allow_older=self.cfg.allow_older)
        duration_ms = int((time.monotonic() - t0) * 1000)

        if outcome.status == "quarantined":
            # A well-formed file that does not produce a valid snapshot — content problem.
            self._move(path, self.cfg.failed_path, name)
            self.checkpoint.mark_processed(digest, name, "quarantined")
            gap = gaps.raise_gap("invalid-export",
                                 f"export '{name}' did not produce a valid snapshot; "
                                 "latest.json left unchanged",
                                 file=name, detail="; ".join(outcome.errors)[:400])
            self.health.record_failure(name, "validation failed", gap)
            self._pending.pop(path, None)
            self._log(name, "quarantined", errors=outcome.errors, warnings=outcome.warnings)
            return "failed"

        # Success paths: mark processed BEFORE moving (so an interrupted move never re-imports).
        self.checkpoint.mark_processed(digest, name, outcome.status, outcome.reading_time)
        self._move(path, self.cfg.archive_path, name)
        self._pending.pop(path, None)

        if outcome.status == "stale-skipped":
            self.health.record_stale_skip(name)
            self._log(name, "stale-skipped", note="older than published reading",
                      warnings=outcome.warnings)
            return "stale-skipped"

        self.health.record_success(name, duration_ms, outcome.reading_time)
        self._log(name, "published", duration_ms=duration_ms,
                  observations=len(outcome.snapshot.get("observations") or []),
                  coverage_pct=outcome.coverage_pct,
                  reality_confidence=outcome.reality_confidence,
                  changes=outcome.change_lines, warnings=outcome.warnings)
        self.event(f"imported {name} → published "
                   f"({len(outcome.snapshot.get('observations') or [])} observations, "
                   f"{duration_ms} ms)")
        return "published"

    # ── failure handling ──────────────────────────────────────────────────────────
    def _fail_transient_or_content(self, path: str, reason: str, *, content: bool) -> str:
        """A content failure goes straight to FAILED (retrying won't help). A transient failure
        is retried up to max_retries, then quarantined — never retried forever."""
        name = os.path.basename(path)
        if content:
            self._move(path, self.cfg.failed_path, name)
            gap = gaps.raise_gap("invalid-export",
                                 f"could not import '{name}'; latest.json left unchanged",
                                 file=name, detail=reason)
            self.health.record_failure(name, reason, gap)
            self._pending.pop(path, None)
            self._log(name, "failed", note=reason)
            return "failed"

        count = self.checkpoint.record_retry(name)
        if count > self.cfg.max_retries:
            self._move(path, self.cfg.failed_path, name)
            self.checkpoint.clear_retries(name)
            gap = gaps.raise_gap("import-failed",
                                 f"gave up importing '{name}' after {count - 1} retries",
                                 file=name, detail=reason)
            self.health.record_failure(name, f"{reason} (after {count - 1} retries)", gap)
            self._pending.pop(path, None)
            self._log(name, "failed", note=f"{reason} (retries exhausted)")
            return "failed"
        self.event(f"transient failure on {name} (attempt {count}/{self.cfg.max_retries}): {reason}")
        self._log(name, "retry", note=reason, attempt=count)
        return "retry"

    # ── helpers ──────────────────────────────────────────────────────────────────
    def _move(self, path: str, dest_dir: str, name: str) -> Optional[str]:
        """Move a processed file out of the import folder, never colliding and never destroying
        the import folder's contents. Best-effort: a move failure is logged, not fatal."""
        try:
            os.makedirs(dest_dir, exist_ok=True)
            stamp = now_iso().replace(":", "").replace("-", "")
            dest = os.path.join(dest_dir, f"{stamp}-{name}")
            n = 1
            while os.path.exists(dest):
                base, ext = os.path.splitext(name)
                dest = os.path.join(dest_dir, f"{stamp}-{base}({n}){ext}")
                n += 1
            shutil.move(path, dest)
            return dest
        except OSError as e:
            self.event(f"could not move {name} to {dest_dir}: {e}")
            return None

    def _log(self, file: str, status: str, **extra) -> None:
        rec = {"at": now_iso(), "component": "edge-watcher", "file": file, "status": status}
        rec.update({k: v for k, v in extra.items() if v is not None})
        append_event(rec)

    # ── the loop ───────────────────────────────────────────────────────────────────
    def run_forever(self, stop=None) -> None:
        """Scan on the configured interval until stopped. The loop body is fully guarded; nothing
        a single scan can do will end the watch."""
        self.event(f"Edge Collector watching {self.cfg.import_path} "
                   f"(every {self.cfg.poll_interval_s}s, formats {','.join(self.cfg.supported_formats)})")
        # Recover any files already waiting from before this process started.
        try:
            self.scan_once()
        except Exception as e:
            self.event(f"initial scan error (ignored): {e}")
        while True:
            if stop is not None and stop.wait(self.cfg.poll_interval_s):
                break
            if stop is None:
                time.sleep(self.cfg.poll_interval_s)
            try:
                self.scan_once()
            except Exception as e:                          # the ultimate backstop
                self.event(f"scan cycle error (ignored, still watching): {e}")
        self.event("Edge Collector stopped.")

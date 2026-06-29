"""Collector Health — a durable, honest record of how the bridge is doing.

Persisted to a JSON file (configurable) so it survives a restart and can be read by anyone: an
operator at a terminal (`python -m collector.edge.health`), the Control Center, or the Gaia API.
It is written after every cycle and reports exactly what the Sprint-14 brief asks for:

    last_successful_import   · when reality was last imported successfully
    last_file_processed      · the filename of that import
    last_import_duration_ms  · how long the last import took
    failed_imports           · how many imports have failed (since the counter was created)
    current_freshness        · how old the currently-published reading is, computed at read time

plus a derived `status` (ok / stale / degraded / starting) and the most recent failure and gap,
so a single glance answers "is Gaia seeing the greenhouse right now?".
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Optional

from ..log import now_iso


def _age_seconds(iso: Optional[str]) -> Optional[int]:
    if not iso:
        return None
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int((datetime.now(timezone.utc) - dt).total_seconds())


@dataclass
class CollectorHealth:
    path: str
    watching: str = ""
    expected_interval_s: int = 0          # used only to judge "stale" (≈ export cadence)
    last_successful_import: Optional[str] = None
    last_file_processed: Optional[str] = None
    last_import_duration_ms: Optional[int] = None
    last_reading_time: Optional[str] = None       # captured_at of the published reading
    imports_total: int = 0
    failed_imports: int = 0
    skipped_duplicates: int = 0
    stale_skipped: int = 0
    last_outcome: Optional[str] = None      # "success" | "failure" — the last import's result
    last_failure: Optional[dict] = None
    last_gap: Optional[dict] = None
    started_at: str = field(default_factory=now_iso)
    updated_at: Optional[str] = None

    # ── lifecycle ──────────────────────────────────────────────────────────────
    @classmethod
    def load_or_new(cls, path: str, watching: str = "", expected_interval_s: int = 0) -> "CollectorHealth":
        """Resume counters from disk if a prior run left them; otherwise start fresh. The
        failure/import counters intentionally persist across restarts so they reflect the
        deployment, not just the current process."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            data = {}
        h = cls(path=path, watching=watching or data.get("watching", ""),
                expected_interval_s=expected_interval_s or data.get("expected_interval_s", 0))
        for k in ("last_successful_import", "last_file_processed", "last_import_duration_ms",
                  "last_reading_time", "imports_total", "failed_imports", "skipped_duplicates",
                  "stale_skipped", "last_outcome", "last_failure", "last_gap", "started_at"):
            if data.get(k) is not None:
                setattr(h, k, data[k])
        return h

    # ── recording ──────────────────────────────────────────────────────────────
    def record_success(self, filename: str, duration_ms: int, reading_time: Optional[str]) -> None:
        self.last_successful_import = now_iso()
        self.last_file_processed = filename
        self.last_import_duration_ms = duration_ms
        self.last_reading_time = reading_time or self.last_reading_time
        self.imports_total += 1
        self.last_outcome = "success"
        self.save()

    def record_failure(self, filename: Optional[str], reason: str, gap: Optional[dict] = None) -> None:
        self.failed_imports += 1
        self.last_outcome = "failure"
        self.last_failure = {"at": now_iso(), "file": filename, "reason": reason[:300]}
        if gap:
            self.last_gap = gap
        self.save()

    def record_duplicate(self) -> None:
        self.skipped_duplicates += 1
        self.save()

    def record_stale_skip(self, filename: str) -> None:
        self.stale_skipped += 1
        self.last_file_processed = filename
        self.save()

    # ── reporting ────────────────────────────────────────────────────────────────
    def status(self) -> str:
        if self.last_successful_import is None:
            return "starting"
        # A failed most-recent attempt is the most actionable signal — surface it first.
        # Uses an explicit last-outcome flag, not timestamp ordering (which is only second-grained).
        if self.last_outcome == "failure":
            return "degraded"
        # Otherwise "stale" if the published reading is older than the freshness SLA (≈ a few
        # export cycles). expected_interval_s here holds that SLA, not the poll interval.
        fresh = _age_seconds(self.last_reading_time)
        if self.expected_interval_s and fresh is not None and fresh > self.expected_interval_s:
            return "stale"
        return "ok"

    def render(self) -> dict:
        """The full health view, with freshness computed at read time."""
        d = asdict(self)
        d.pop("path", None)
        d["status"] = self.status()
        d["current_freshness_seconds"] = _age_seconds(self.last_reading_time)
        d["seconds_since_last_success"] = _age_seconds(self.last_successful_import)
        return d

    def save(self) -> None:
        self.updated_at = now_iso()
        try:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
            tmp = f"{self.path}.{os.getpid()}.tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.render(), f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, self.path)
        except OSError:
            pass      # health is best-effort; never let writing it crash a good import


def read_health(path: str) -> Optional[dict]:
    """Read the durable health file (for the API / Control Center / a CLI). Recomputes freshness
    so 'current_freshness_seconds' is accurate at the moment it is read, not when it was written."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    data["current_freshness_seconds"] = _age_seconds(data.get("last_reading_time"))
    data["seconds_since_last_success"] = _age_seconds(data.get("last_successful_import"))
    return data


def _main(argv=None) -> int:
    """`python -m collector.edge.health [path]` — print current health as JSON for ops."""
    import sys
    from .config import EdgeConfig
    path = (argv or sys.argv[1:])
    health_path = path[0] if path else EdgeConfig.from_env().health_path
    data = read_health(health_path)
    if data is None:
        print(json.dumps({"status": "unknown",
                          "note": f"no health file at {health_path}"}, indent=2))
        return 1
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())

#!/usr/bin/env python3
"""Gaia Collector — collect one greenhouse reading and publish it as a Canonical Snapshot.

    python collector/collect.py                                  # fixture source (default)
    python collector/collect.py --source drop-folder --path D:\\Synopta\\Export

Pipeline:  Synopta  ->  Source.fetch()  ->  translate  ->  validate  ->  diff  ->
           data/inbox/latest.json  (the file Gaia consumes, unchanged)

Resilience (specs/gaia-collector.md §5):
  - source failure        -> previous latest.json is left untouched; exit 3
  - invalid snapshot      -> quarantined, NOT published; exit 2
  - one unreadable value  -> one honest gap + a warning; collection continues

It reads and translates. It does not reason, recommend, or use AI.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# Runnable both as a module (`python -m collector.collect`) and as a script
# (`python collector/collect.py`): ensure the repo root is importable either way.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collector import _paths
from collector.log import append_event, now_iso
from collector.sources import make_source, SourceError
from collector.translate import to_snapshot
from collector.validate import validate
from collector.changes import detect_changes

_FACILITY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "facility.json")


def _read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _write_json(path, data):
    """Write JSON atomically: serialise to a temp file in the same directory, flush to
    disk, then os.replace() into place. A reader (Gaia) therefore only ever sees the old
    file or the complete new one — never a half-written snapshot — and two collectors racing
    end with one clean winner rather than interleaved bytes. UTF-8, never ASCII-escaped."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)  # atomic on the same filesystem (Windows & POSIX)


def _archive_previous(prev: dict) -> str:
    """Keep the snapshot we are about to replace — snapshots are immutable records of a
    moment (snapshot Principle 9), and the diff needs the past to stay honest."""
    os.makedirs(_paths.HISTORY_DIR, exist_ok=True)
    stamp = (prev.get("assembled_at") or now_iso()).replace(":", "").replace("-", "")
    dest = os.path.join(_paths.HISTORY_DIR, f"snapshot-{stamp}.json")
    try:
        _write_json(dest, prev)
    except OSError:
        return ""
    return dest


def _print_summary(source_label, snap, result, change, warnings, status, out_path):
    print("Gaia Collector")
    print(f"  source:      {source_label}")
    print(f"  greenhouse:  {snap.get('greenhouse_name')} ({snap.get('greenhouse_id')})")
    print(f"  assembled:   {snap.get('assembled_at')}")
    print(f"  observations:{len(snap.get('observations') or [])}  "
          f"(coverage {result.coverage['coverage_pct']}%, "
          f"reality confidence {result.reality_confidence['label']} "
          f"{result.reality_confidence['score_pct']}%)")
    if warnings:
        print(f"  warnings ({len(warnings)}) — values not invented:")
        for w in warnings:
            print(f"    - {w}")
    print("  changes since previous:")
    for line in change["lines"]:
        print(f"    - {line}")
    print(f"  status:      {status.upper()}")
    print(f"  written:     {out_path}")


def run(source_name: str = "fixture", path: str = None, facility_path: str = _FACILITY) -> int:
    facility = _read_json(facility_path) or {}
    assembled_at = now_iso()
    base = {"at": assembled_at, "source": None, "status": None}

    # 1) READ — the only vendor seam. A total failure must not erase yesterday's snapshot.
    source = make_source(source_name, path)
    base["source"] = source.label
    try:
        raw = source.fetch()
    except SourceError as e:
        append_event({**base, "status": "source-failed", "error": str(e),
                      "note": "previous latest.json left untouched"})
        print(f"Gaia Collector\n  source:  {source.label}\n  status:  SOURCE-FAILED — {e}")
        print(f"  note:    previous {os.path.basename(_paths.LATEST)} left untouched "
              "(the Brain keeps the last good snapshot rather than seeing nothing).")
        return 3

    # 2) TRANSLATE — field-mapping only; gaps become honest absence, not numbers.
    warnings: list = []
    snap = to_snapshot(raw, facility, assembled_at, warnings)

    # 3) VALIDATE — using Gaia's own importer; an invalid snapshot is never published.
    result = validate(snap)
    if not result.ok:
        os.makedirs(_paths.QUARANTINE_DIR, exist_ok=True)
        q = os.path.join(_paths.QUARANTINE_DIR, f"snapshot-{assembled_at.replace(':', '')}.json")
        _write_json(q, snap)
        append_event({**base, "status": "quarantined", "errors": result.errors,
                      "warnings": warnings, "quarantine": q})
        print(f"Gaia Collector\n  source:  {source.label}\n  status:  QUARANTINED — "
              f"snapshot failed validation, latest.json NOT changed")
        for err in result.errors:
            print(f"    - {err}")
        print(f"  written: {q}")
        return 2

    # 4) DIFF — against the previous snapshot, before we replace it.
    previous = _read_json(_paths.LATEST)
    change = detect_changes(previous, snap)

    # 5) PUBLISH — archive the old, write the new latest.json.
    archived = _archive_previous(previous) if previous else ""
    _write_json(_paths.LATEST, snap)

    log_path = append_event({
        **base, "status": "published",
        "source_file": raw.get("_source_file") if isinstance(raw, dict) else None,
        "observations": len(snap.get("observations") or []),
        "coverage_pct": result.coverage["coverage_pct"],
        "reality_confidence": result.reality_confidence,
        "warnings": warnings,
        "changes": change["lines"],
        "change_counts": change["counts"],
        "archived_previous": archived or None,
        "output": _paths.LATEST,
    })

    _print_summary(source.label, snap, result, change, warnings, "published", _paths.LATEST)
    print(f"  log:         {log_path}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Collect Synopta data into a Canonical Snapshot.")
    ap.add_argument("--source", default="fixture",
                    help="fixture (default) | drop-folder")
    ap.add_argument("--path", default=None,
                    help="for drop-folder: the export folder; for fixture: an alternate file")
    ap.add_argument("--facility", default=_FACILITY, help="facility config JSON")
    args = ap.parse_args(argv)
    return run(args.source, args.path, args.facility)


if __name__ == "__main__":
    raise SystemExit(main())

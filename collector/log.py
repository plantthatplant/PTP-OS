"""Collection logging — an append-only, debuggable record of every run.

One JSON line per collection into data/logs/collector-YYYYMMDD.jsonl, capturing what was
read, what couldn't be, coverage, confidence, changes, and the outcome. Captured for
debugging and audit; not analysed here. A calm human-readable summary is printed by the
caller (collect.py).
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from . import _paths


def now_iso() -> str:
    """UTC, to the second — the Collector's single clock for assembled_at and log times."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def append_event(record: dict) -> str:
    """Append one collection event; returns the log file path. Never raises on logging
    problems — failing to log must not stop a collection that otherwise succeeded."""
    os.makedirs(_paths.LOGS_DIR, exist_ok=True)
    day = (record.get("at") or now_iso())[:10].replace("-", "")
    path = os.path.join(_paths.LOGS_DIR, f"collector-{day}.jsonl")
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass
    return path

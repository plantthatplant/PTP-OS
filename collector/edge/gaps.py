"""Raise a Knowledge Gap when reality could not be observed this cycle.

The Edge Collector does not reason and does not own the Knowledge Gap Engine
(specs/knowledge-gap-engine.md) — that lives in the Brain and decides what is worth asking a
grower. The Collector's honest job at the boundary is narrower: when an export fails to import,
**declare the gap plainly** so the rest of the system (and a human) can see that the greenhouse
was not observed, and why.

It does this two safe, additive ways:
  1. the previous `latest.json` is left untouched (handled in the pipeline) — the Brain keeps
     reasoning from the last good snapshot rather than from nothing or from a fabricated value;
  2. a structured gap record is appended to `data/logs/knowledge-gaps.jsonl` and surfaced in
     Collector Health.

It never writes into the Brain's question store, never invents a value, and never decides what
the gap *means* — it only states "I could not see reality, here is why."
"""
from __future__ import annotations

import json
import os
from typing import Optional

from .. import _paths
from ..log import now_iso


def _gaps_path() -> str:
    return os.path.join(_paths.LOGS_DIR, "knowledge-gaps.jsonl")


def raise_gap(kind: str, summary: str, *, file: Optional[str] = None,
              detail: Optional[str] = None) -> dict:
    """Record a knowledge gap and return the record. Never raises — failing to log a gap must
    not crash the watcher (the gap is also visible via Health and the untouched last snapshot)."""
    record = {
        "at": now_iso(),
        "type": "knowledge-gap",
        "kind": kind,                       # e.g. "import-failed" | "no-export" | "invalid-export"
        "summary": summary,                 # plain-language statement of what was not observed
        "file": file,
        "detail": (detail or "")[:500] or None,
        "source": "edge-collector",
    }
    try:
        os.makedirs(_paths.LOGS_DIR, exist_ok=True)
        with open(_gaps_path(), "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass
    return record

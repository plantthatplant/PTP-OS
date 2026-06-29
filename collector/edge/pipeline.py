"""The thin reuse layer: a raw vendor reading → Canonical Snapshot on disk.

Everything here is the EXISTING acquisition pipeline, called as a library so the watcher and the
one-shot `collect.py` produce byte-identical results:

    translate.to_snapshot  →  validate (Gaia's own importer)  →  changes.detect_changes
                           →  atomic write of data/inbox/latest.json

It adds exactly one production guard the one-shot CLI doesn't need: **never overwrite newer
reality with older.** If a late export arrives carrying a reading older than the one already
published, the file is accepted and archived (it is not an error) but `latest.json` is left
pointing at the fresher truth — unless `allow_older` is set.

No biology, no inference. Validation failure still quarantines and never publishes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .. import _paths  # noqa: F401  (puts app/ on the import path)
from ..collect import _archive_previous, _read_json, _write_json  # reuse the proven atomic IO
from ..changes import detect_changes
from ..log import now_iso
from ..translate import to_snapshot
from ..validate import validate


@dataclass
class PublishOutcome:
    status: str                       # "published" | "stale-skipped" | "quarantined"
    snapshot: Optional[dict]
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    change_lines: List[str] = field(default_factory=list)
    coverage_pct: Optional[float] = None
    reality_confidence: Optional[dict] = None
    reading_time: Optional[str] = None
    quarantine_path: Optional[str] = None

    @property
    def published(self) -> bool:
        return self.status == "published"


def reading_time(snap: Optional[dict]) -> Optional[str]:
    """The freshest moment the snapshot actually observed — the max `captured_at` across its
    observations, falling back to `assembled_at`. Used to compare which reading is newer."""
    if not snap:
        return None
    times = [o.get("captured_at") for o in (snap.get("observations") or [])
             if isinstance(o, dict) and o.get("captured_at")]
    if times:
        return max(times)
    return snap.get("assembled_at")


def process_export(raw: dict, facility: dict, *, allow_older: bool = False) -> PublishOutcome:
    """Translate, validate, and (if valid and not stale) publish one reading. Pure with respect
    to the watcher: it returns an outcome and never raises for a *content* problem — a malformed
    snapshot becomes a quarantined outcome, not an exception."""
    assembled_at = now_iso()
    warnings: List[str] = []
    snap = to_snapshot(raw, facility, assembled_at, warnings)

    result = validate(snap)
    if not result.ok:
        import os
        os.makedirs(_paths.QUARANTINE_DIR, exist_ok=True)
        q = os.path.join(_paths.QUARANTINE_DIR, f"snapshot-{assembled_at.replace(':', '')}.json")
        try:
            _write_json(q, snap)
        except OSError:
            q = None
        return PublishOutcome(status="quarantined", snapshot=snap, warnings=warnings,
                              errors=list(result.errors), quarantine_path=q)

    previous = _read_json(_paths.LATEST)
    new_t, prev_t = reading_time(snap), reading_time(previous)
    if previous and prev_t and new_t and new_t < prev_t and not allow_older:
        # Older reality arrived late — accept the file but keep the fresher published truth.
        return PublishOutcome(status="stale-skipped", snapshot=snap, warnings=warnings,
                              reading_time=new_t,
                              coverage_pct=result.coverage["coverage_pct"],
                              reality_confidence=result.reality_confidence)

    change = detect_changes(previous, snap)
    if previous:
        _archive_previous(previous)
    _write_json(_paths.LATEST, snap)

    return PublishOutcome(
        status="published", snapshot=snap, warnings=warnings,
        change_lines=list(change["lines"]),
        coverage_pct=result.coverage["coverage_pct"],
        reality_confidence=result.reality_confidence,
        reading_time=new_t,
    )

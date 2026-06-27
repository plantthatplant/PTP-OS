"""Snapshot Importer — raw JSON (canonical format) -> Greenhouse Snapshot.

Deliberately forgiving: a malformed entry is skipped, a missing section becomes empty,
a null value becomes an honest gap. It NEVER raises on missing or messy data — that is
the whole point. What it cannot read, it simply does not invent.
"""
from __future__ import annotations

from .snapshot import Snapshot, SnapshotObservation, SnapshotZone


def _observation(d) -> SnapshotObservation:
    if not isinstance(d, dict) or not d.get("subject") or not d.get("kind"):
        return None
    return SnapshotObservation(
        subject=str(d.get("subject")),
        kind=str(d.get("kind")),
        value=d.get("value"),
        unit=d.get("unit"),
        captured_at=d.get("captured_at"),
        source=d.get("source"),
        method=d.get("method"),
        confidence=d.get("confidence"),
        absence=d.get("absence"),
        verbatim=d.get("verbatim"),
    )


def import_snapshot(raw) -> Snapshot:
    raw = raw if isinstance(raw, dict) else {}
    structure = raw.get("structure") or {}
    zones = []
    for z in (structure.get("zones") or []):
        if isinstance(z, dict) and z.get("id"):
            zones.append(SnapshotZone(
                id=str(z["id"]), name=str(z.get("name", z["id"])),
                stage=str(z.get("stage", "unknown")), crop=str(z.get("crop", "")),
            ))
    observations = [o for o in (_observation(x) for x in (raw.get("observations") or [])) if o]
    coverage = raw.get("coverage") or {}
    return Snapshot(
        greenhouse_id=str(raw.get("greenhouse_id", "unknown")),
        greenhouse_name=str(raw.get("greenhouse_name") or raw.get("site") or "Greenhouse"),
        assembled_at=raw.get("assembled_at"),
        provenance=raw.get("provenance") or [],
        not_observed=coverage.get("not_observed") or [],
        zones=zones,
        observations=observations,
    )

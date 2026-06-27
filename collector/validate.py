"""Validate a snapshot dict against the canonical contract — using Gaia's own importer.

'Valid' here means 'exactly what Gaia can consume'. So validation round-trips the dict
through the Brain's import_snapshot() and then checks the contract from
specs/greenhouse-snapshot.md §6: the Snapshot-level required fields, and that every present
observation is well-formed (value+unit, or an explicit absence). A snapshot that fails is
never published (collect.py quarantines it instead).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from . import _paths  # noqa: F401  (puts app/ on the path)
from greenhouse_brain.snapshot_importer import import_snapshot


@dataclass
class ValidationResult:
    ok: bool
    errors: List[str]
    snapshot: object          # the parsed greenhouse_brain.snapshot.Snapshot
    coverage: dict
    reality_confidence: dict


def validate(snap_dict: dict) -> ValidationResult:
    errors: List[str] = []

    # Snapshot-level required fields (snapshot §6).
    for required in ("greenhouse_id", "assembled_at", "provenance", "coverage"):
        if not snap_dict.get(required):
            errors.append(f"missing required snapshot field: {required}")

    # Round-trip through Gaia's own importer — the real test of consumability.
    snapshot = import_snapshot(snap_dict)

    # Per-observation wellformedness (the importer keeps only subject+kind; we enforce the
    # rest of the envelope here so nothing half-formed slips through).
    for i, o in enumerate(snapshot.observations):
        if o.has_value():
            for fld in ("captured_at", "source", "method", "confidence"):
                if not getattr(o, fld):
                    errors.append(f"observation #{i} ({o.subject}/{o.kind}): missing {fld}")
        elif not o.absence:
            errors.append(f"observation #{i} ({o.subject}/{o.kind}): no value and no absence marker")

    return ValidationResult(
        ok=not errors,
        errors=errors,
        snapshot=snapshot,
        coverage=snapshot.coverage(),
        reality_confidence=snapshot.reality_confidence(),
    )

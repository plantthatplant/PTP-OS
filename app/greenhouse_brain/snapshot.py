"""The canonical Greenhouse Snapshot, in code (see specs/greenhouse-snapshot.md).

A point-in-time, provenance- and confidence-bearing collection of observations about
one greenhouse. It records what was OBSERVED — never what it means (no Plant State,
no Disease Risk; those are inferred downstream). Missing data is represented honestly
and reduces confidence; it never becomes a fabricated value and never an error.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

# How much a single observation is trusted, by its stated confidence.
_CONF_WEIGHT = {"high": 1.0, "medium": 0.65, "low": 0.35}


@dataclass
class SnapshotObservation:
    """The universal envelope: every datum about reality wears this."""
    subject: str                       # which zone / site / equipment it is about
    kind: str                          # what is observed (air-temperature, leaf-wetness, ...)
    value: Any = None                  # the observed value (number / text / category) — or None
    unit: Optional[str] = None
    captured_at: Optional[str] = None
    source: Optional[str] = None
    method: Optional[str] = None        # measured | observed-by-human | derived | forecast | imported
    confidence: Optional[str] = None    # high | medium | low
    absence: Optional[str] = None       # set when the value is knowingly missing (and why)
    verbatim: Optional[str] = None      # a human's exact words, preserved

    def has_value(self) -> bool:
        return self.value is not None and self.absence is None


@dataclass
class SnapshotZone:
    id: str
    name: str
    stage: str = "unknown"
    crop: str = ""


@dataclass
class Snapshot:
    greenhouse_id: str
    greenhouse_name: str
    assembled_at: Optional[str] = None
    provenance: List[dict] = field(default_factory=list)
    not_observed: List[str] = field(default_factory=list)   # declared coverage gaps
    zones: List[SnapshotZone] = field(default_factory=list)
    observations: List[SnapshotObservation] = field(default_factory=list)

    def present(self) -> List[SnapshotObservation]:
        return [o for o in self.observations if o.has_value()]

    def missing(self) -> List[SnapshotObservation]:
        return [o for o in self.observations if not o.has_value()]

    def coverage(self) -> dict:
        """How much of reality this Snapshot actually saw. Each null/absent observation
        and each declared 'not observed' slot is a gap."""
        present = len(self.present())
        gaps = len(self.missing()) + len(self.not_observed)
        total = present + gaps
        pct = (100.0 * present / total) if total else 0.0
        return {"present": present, "gaps": gaps, "total": total, "coverage_pct": round(pct, 1)}

    def reality_confidence(self) -> dict:
        """How much to trust this Snapshot overall: the quality of the observations we DO
        have, scaled by how much of reality we saw. Missing data lowers it; never errors."""
        present = self.present()
        weights = [_CONF_WEIGHT.get((o.confidence or "").lower(), 0.5) for o in present]
        data_quality = (sum(weights) / len(weights)) if weights else 0.0
        cov = self.coverage()["coverage_pct"] / 100.0
        score = data_quality * cov
        label = "High" if score >= 0.7 else ("Medium" if score >= 0.4 else "Low")
        return {"label": label, "score_pct": round(100 * score, 1),
                "data_quality_pct": round(100 * data_quality, 1)}

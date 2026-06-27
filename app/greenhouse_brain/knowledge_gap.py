"""The Knowledge Gap Engine — ask only when the answer would change a decision.

A transparent Value-of-Information score (no ML) decides which of the day's possible
questions are worth the grower's attention. Most are not. See
specs/knowledge-gap-engine.md.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple

# --- VoI weights (legible; a grower could audit them) ------------------------
_STAKES = {"Critical": 1.0, "High": 0.8, "Medium": 0.5, "Low": 0.3}
_UNCERT = {"Low": 1.0, "Medium": 0.6, "Medium-high": 0.3, "High": 0.1}
_DECISIVE = {"prevent": 1.0, "inspect": 1.0, "close": 0.7,
             "progress": 0.4, "opportunity": 0.3, "protect": 0.2, "follow": 0.3}
_INTERRUPT = 0.15
_THRESHOLD = 0.15
_BUDGET = 3


@dataclass
class Question:
    id: str
    timestamp: str
    text: str
    kind: str                       # confirm | scout | follow | close (delivery role)
    decision_kind: str              # the decision it serves (prevent/protect/inspect/…)
    subject: str
    suggested_location: str
    suggested_timing: str
    snapshot_ref: Optional[str]
    decision_id: Optional[str]
    experiment_id: Optional[str]    # set for 'close' questions
    biological_reason: str
    uncertainty: str
    expected_impact: str
    voi: float
    voi_components: dict
    relevant_if_late: bool


def _voi(stakes: str, confidence: str, decision_kind: str, prior: float) -> Tuple[float, dict]:
    s = _STAKES.get(stakes, 0.5)
    u = _UNCERT.get(confidence, 0.6)
    d = _DECISIVE.get(decision_kind, 0.3)
    score = round(s * u * d * prior - _INTERRUPT, 3)
    return score, {"stakes": s, "uncertainty": u, "decisiveness": d, "prior": prior,
                   "interruption_cost": _INTERRUPT}


# The single most-diagnostic question for each decision kind (specific, located, timed).
def _diagnostic(decision_kind: str, zone: str, rec: str = ""):
    z = zone
    if decision_kind == "prevent":
        return ("confirm",
                f"Do you see condensation or a wet canopy on the leaves in {z}?",
                "disease risk is inferred from climate; only the wet canopy confirms it",
                "whether the leaves are actually wet (the disease trigger)",
                "confirms or denies the disease setup — raises the priority, or drops it",
                z, "on the walk", True)
    if decision_kind == "inspect":
        return ("scout",
                f"In {z}, do the plants actually look off — any thrips on the benches, or real cold?",
                "a reading disagrees with how the crop looks; the plant is ground truth",
                "whether the odd reading reflects a real problem or a faulty sensor",
                "decides whether to act on the reading or ignore it",
                z, "on the walk", True)
    if decision_kind == "protect":
        return ("confirm",
                f"Will the {z} cuttings want their shade before midday?",
                "protecting rootless cuttings ahead of heat",
                "exactly when the peak hits",
                "barely changes the action — Gaia will shade them regardless",
                z, "before midday", True)
    if decision_kind == "progress":
        return ("scout",
                f"Has the {z} batch firmed up at all since yesterday?",
                "toning is judged over days",
                "how far toning has progressed",
                "tunes the toning regime, but not today's core decision",
                z, "on the walk", True)
    if decision_kind == "opportunity":
        return ("follow",
                f"Is the {z} mother stock still in prime condition for cuttings?",
                "propagation potential is best taken at peak vigour",
                "whether the window is still open",
                "informs a value opportunity, not an urgent decision",
                z, "on the walk", True)
    if decision_kind == "close":
        return ("close",
                f"{z}: yesterday we suggested — {rec}. Did it help? (better / same / worse / not sure)",
                "an open experiment's outcome is due",
                "what actually happened after the action",
                "closes the loop and calibrates confidence",
                z, "on the walk", True)
    return ("follow", f"Anything notable in {z}?", "general", "unknown", "low", z, "on the walk", True)


def generate(analysis, carried, snapshot_ref, date, prior=None) -> Tuple[List[Question], List[Question]]:
    """Return (asked, held_back). Only questions whose VoI clears the bar are asked."""
    prior = prior or {}
    ts = datetime.now().isoformat(timespec="seconds")
    scored: List[Question] = []

    def make(decision_kind, zone, conf, stakes, did=None, eid=None, rec=""):
        role, text, bio, unc, impact, loc, timing, late = _diagnostic(decision_kind, zone, rec)
        voi, comp = _voi(stakes, conf, decision_kind, prior.get(decision_kind, 1.0))
        return Question(
            id=f"kq-{date}-{decision_kind}-{len(scored)}", timestamp=ts, text=text, kind=role,
            decision_kind=decision_kind, subject=zone, suggested_location=loc, suggested_timing=timing,
            snapshot_ref=snapshot_ref, decision_id=did, experiment_id=eid,
            biological_reason=bio, uncertainty=unc, expected_impact=impact,
            voi=voi, voi_components=comp, relevant_if_late=late)

    # Carried experiments due to close (high learning value).
    for e in carried:
        scored.append(make("close", e.zone, e.confidence_before or "Medium", "High",
                            eid=e.id, rec=e.recommendation))
    # Today's decisions (priorities + opportunities).
    for c in list(analysis.priorities) + list(analysis.opportunities):
        scored.append(make(c.kind, c.zone_name, c.confidence, c.value, did=c.zone_id))
    # Curiosities — low-decisiveness candidates (rarely clear the bar today).
    for cu in analysis.curiosities[:2]:
        scored.append(make("follow", cu.subject, "Low", "Low"))

    asked = sorted([q for q in scored if q.voi > _THRESHOLD], key=lambda q: -q.voi)[:_BUDGET]
    held = [q for q in scored if q not in asked]
    return asked, held

"""The recommendation lifecycle — an Experiment that travels the whole loop.

    Observation -> Reasoning -> Recommendation -> Action -> Outcome -> Memory
                                                                        -> better future recommendation

A recommendation, the moment it is made, becomes an Experiment carrying a testable
expectation. Through the day it gains an action and an outcome; in the evening it gains a
lesson and an updated confidence, and is preserved forever as a memory. This is
docs/gaia-learning-loop.md, made concrete — no machine learning, just a grower's record of
what was tried and what happened.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

# Biological confidence, as a small ladder we step up or down.
_LADDER = ["Low", "Medium", "Medium-high", "High"]


def _idx(c: str) -> int:
    return _LADDER.index(c) if c in _LADDER else 1


def step(confidence: str, delta: int) -> str:
    return _LADDER[max(0, min(len(_LADDER) - 1, _idx(confidence) + delta))]


@dataclass
class Experiment:
    id: str
    opened_on: str
    zone: str
    kind: str                       # prevent | protect | inspect | progress | opportunity
    # the chain — set at the morning (the hypothesis)
    observation: List[str]          # the supporting evidence
    reasoning: str                  # why
    recommendation: str             # the action proposed
    expected_outcome: str           # the testable prediction (+ window)
    window: str                     # Now | Hours | Today | Days
    confidence_before: str
    biological_principles: str
    # set later — action & outcome
    action: Optional[str] = None        # done | modified | skipped (+ note)
    outcome: Optional[str] = None       # improved | unchanged | worse | unknown
    outcome_note: str = ""
    # set in the evening — the learning
    lesson: Optional[str] = None
    confidence_after: Optional[str] = None
    status: str = "open"                # open | closed
    closed_on: Optional[str] = None


def experiment_from_candidate(c, date: str) -> Experiment:
    """Open an experiment from a recommendation (a Decision Engine Candidate)."""
    return Experiment(
        id=f"exp-{date}-{c.zone_id}-{c.kind}",
        opened_on=date, zone=c.zone_name, kind=c.kind,
        observation=list(c.evidence),
        reasoning=c.why,
        recommendation=c.action,
        expected_outcome=f"{c.expected_benefit} (within: {c.window})",
        window=c.window,
        confidence_before=c.confidence,
        biological_principles=c.objective,
    )


def reinforce(exp: Experiment, agrees: bool, note: str):
    """A field observation arrives mid-day and updates the live recommendation's confidence —
    up if it confirms the inference, down if it contradicts it. Returns (old, new)."""
    old = exp.confidence_before
    exp.confidence_before = step(old, +1 if agrees else -1)
    exp.observation = list(exp.observation) + [
        f"field {'confirmed' if agrees else 'contradicted'} (grower): {note}"]
    return old, exp.confidence_before


def apply_outcome(exp: Experiment, action: str, outcome: str, note: str, date: str) -> Experiment:
    """Close the experiment: compare expectation with reality, form a lesson, move confidence."""
    exp.action, exp.outcome, exp.outcome_note = action, outcome, note
    b = exp.confidence_before
    if outcome == "improved":
        exp.confidence_after = step(b, +1)
        exp.lesson = (f"Prediction held — {exp.expected_outcome}. The principle "
                      f"({exp.biological_principles}) is reinforced.")
    elif outcome == "worse":
        exp.confidence_after = step(b, -1)
        exp.lesson = "Surprise — the action did not help. Belief weakened; this needs re-examination."
    elif outcome == "unchanged":
        exp.confidence_after = b
        exp.lesson = "No clear effect — hold the belief; a cleaner test would settle it."
    else:  # unknown
        exp.confidence_after = b
        exp.lesson = "Could not judge the outcome — re-observe next time."
    if action == "skipped":
        exp.lesson += " (Recommendation was not carried out; outcome reflects no action.)"
    exp.status, exp.closed_on = "closed", date
    return exp

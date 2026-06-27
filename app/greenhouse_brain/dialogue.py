"""The Daily Grower Dialogue — ask only the few questions that matter today.

See specs/daily-grower-dialogue.md. This is composition, not a new engine: it reads the
Morning Analysis and the open experiments and chooses a small handful of questions worth
asking on the walk — to confirm what Gaia can't see, to scout a real risk, to follow a
curiosity, and to close yesterday's experiments.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Question:
    id: str
    text: str
    kind: str                       # confirm | scout | follow | close
    subject: str = ""
    experiment_id: Optional[str] = None


def questions_for_today(analysis, carried_experiments, budget: int = 4) -> List[Question]:
    """Ask the few questions whose answers would change a decision or close a loop."""
    qs: List[Question] = []

    # Highest value: close yesterday's still-open experiments (their window has come due).
    for e in carried_experiments:
        qs.append(Question(
            id=f"q-close-{e.id}", kind="close", subject=e.zone, experiment_id=e.id,
            text=(f"{e.zone}: yesterday we suggested — {e.recommendation}. "
                  f"Did it help? (better / same / worse / not sure)")))

    # Confirm an inference Gaia made from climate but cannot see.
    for c in analysis.concerns:
        if c.kind == "prevent":
            qs.append(Question(f"q-confirm-{c.zone_id}", kind="confirm", subject=c.zone_name,
                               text=f"{c.zone_name}: did you see condensation or a wet canopy this morning?"))
        elif c.kind == "inspect":
            qs.append(Question(f"q-scout-{c.zone_id}", kind="scout", subject=c.zone_name,
                               text=f"{c.zone_name}: do the plants actually look off — any pests, or real cold?"))

    # Follow a curiosity (one is plenty).
    for cu in analysis.curiosities[:1]:
        qs.append(Question(f"q-follow-{cu.subject}", kind="follow", subject=cu.subject,
                           text=f"{cu.subject}: {cu.worth_a_look}"))

    return qs[:budget]

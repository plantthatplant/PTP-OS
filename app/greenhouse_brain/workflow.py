"""Adaptive Workflow — ask the right question at the right moment.

Not more questions: better timing. Given the day's VoI-scored questions, decide for each
one whether to raise it now, hold it for a natural moment, ask it opportunistically when the
grower is already at that location, or drop it because it's resolved or no longer worth it.

Pure orchestration over the existing engines — no new reasoning, no new architecture.
"""
from __future__ import annotations

_THRESHOLD = 0.15


def schedule(questions):
    """Decide when each question should be raised — so the grower never gets a form dump."""
    plan = []
    for q in questions:
        if q.decision_kind == "prevent" and q.voi >= 0.40:
            when, why = "now, at the morning conversation", "decision-changing and time-sensitive"
        elif q.voi >= 0.30:
            when, why = "at the morning conversation", "worth a shared moment"
        elif "midday" in (q.suggested_timing or ""):
            when, why = "by midday", "time-bound — when you pass, else a quiet nudge"
        else:
            when, why = f"when you're in {q.subject}", "opportunistic — no need to interrupt"
        plan.append({"q": q, "when": when, "why": why})
    return plan


def matches_location(subject: str, location: str) -> bool:
    return bool(location) and location.lower().strip() in (subject or "").lower()


def surface(questions, location, resolved_ids):
    """The questions worth raising right here, right now — grouped by where the grower is."""
    return [q for q in questions
            if q.id not in resolved_ids and q.voi > _THRESHOLD and matches_location(q.subject, location)]


def interrupt_now(q, resolved_ids) -> bool:
    """Only the most valuable, decision-changing, time-sensitive question earns an interruption."""
    return q.id not in resolved_ids and q.voi >= 0.40 and q.decision_kind == "prevent"

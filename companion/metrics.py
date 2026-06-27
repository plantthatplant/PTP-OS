"""Day metrics — instrument the trial so we can answer "is this worth using?".

Computed from what actually happened during a day (the phone messages shown, the glasses
interruptions, the interaction records), plus a few counters the runner passes in. Honest
estimates are labelled as estimates. No biology here; this only measures the experience.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List

_LADDER = ["Low", "Medium", "Medium-high", "High"]
_WPM = 200.0          # adult reading speed, for a reading-time estimate
_MANUAL_BRIEF_MIN = 12.0   # a grower's manual "scan the dashboards + decide where to look" each morning


def _idx(c):
    return _LADDER.index(c) if c in _LADDER else 1


@dataclass
class DayMetrics:
    questions_asked: int
    questions_silenced: int          # considered worth-while by VoI but spaced/cost-gated → not asked
    questions_unanswered: int        # asked but the grower gave no usable info
    interruptions: int               # glasses moments that broke attention (questions + alerts)
    alerts: int
    notes_captured: int
    phone_messages: int
    reading_words: int
    reading_seconds_est: float
    walking_phases: int
    confidence_steps_gained: int     # net up-steps on the confidence ladder, from field answers
    recommendations_surfaced: int
    recommendations_followed: int
    recommendations_ignored: int
    interactions_remembered: int
    time_saved_min_est: float        # manual morning scan avoided − time spent reading Gaia

    def render(self) -> str:
        L = ["DAY METRICS  (the trial, measured)",
             "─" * 52,
             f"  Questions asked            {self.questions_asked}",
             f"  Questions held (silenced)  {self.questions_silenced}",
             f"  Questions unanswered       {self.questions_unanswered}",
             f"  Interruptions (total)      {self.interruptions}   (alerts {self.alerts})",
             f"  Notes captured             {self.notes_captured}",
             f"  Phone cards shown          {self.phone_messages}  (~{self.reading_words} words,"
             f" ~{self.reading_seconds_est:.0f}s reading)",
             f"  Walking phases             {self.walking_phases}",
             f"  Confidence gained          +{self.confidence_steps_gained} ladder step(s)",
             f"  Recommendations            {self.recommendations_followed} followed /"
             f" {self.recommendations_ignored} ignored of {self.recommendations_surfaced}",
             f"  Interactions remembered    {self.interactions_remembered}",
             f"  Time saved (est.)          ~{self.time_saved_min_est:.0f} min"
             "   [estimate: manual morning scan avoided − Gaia reading time]"]
        return "\n".join(L)


def compute(phone_shown, engine_records, *, questions_asked, questions_silenced,
            alerts, notes, walk_phases, recs_surfaced, recs_followed, recs_ignored) -> DayMetrics:
    words = sum(len((m.headline + " " + (m.detail or "")).split()) for m in phone_shown)
    reading_seconds = words / _WPM * 60.0
    unanswered = sum(1 for r in engine_records if r.decision == "asked" and not r.answer.strip())
    conf_gain = sum(max(0, _idx(r.confidence_after) - _idx(r.confidence_before))
                    for r in engine_records
                    if r.answered and r.confidence_before and r.confidence_after)
    time_saved = _MANUAL_BRIEF_MIN - reading_seconds / 60.0
    return DayMetrics(
        questions_asked=questions_asked, questions_silenced=questions_silenced,
        questions_unanswered=unanswered, interruptions=questions_asked + alerts, alerts=alerts,
        notes_captured=notes, phone_messages=len(phone_shown), reading_words=words,
        reading_seconds_est=reading_seconds, walking_phases=walk_phases,
        confidence_steps_gained=conf_gain, recommendations_surfaced=recs_surfaced,
        recommendations_followed=recs_followed, recommendations_ignored=recs_ignored,
        interactions_remembered=len(engine_records), time_saved_min_est=time_saved)


def as_record(m: DayMetrics, date: str) -> dict:
    d = asdict(m)
    d["date"] = date
    return d

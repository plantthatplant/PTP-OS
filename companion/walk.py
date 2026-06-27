"""WalkSession — run one greenhouse walk through a device, in Gaia's voice.

Composes the Interaction Engine, the Morning Analysis, and a CompanionDisplay into the
interaction modes. It chooses *wording* and *which primitive* to use (interaction concerns);
all biological meaning comes from the engines. It never reasons about plants.
"""
from __future__ import annotations

import re
from typing import List, Optional

from .messages import CompanionMessage, Primitive, Urgency, Mode
from .display import CompanionDisplay
from .interaction_engine import InteractionEngine


def _short_subject(subject: str) -> str:
    return re.sub(r"\s*\(.*?\)\s*", "", subject or "").strip() or (subject or "")


# Faithful short forms of the engine's own question, for a glanceable screen.
_SHORT_Q = {
    "prevent": ("{z}: canopy wet?", ["yes", "no", "not sure"]),
    "inspect": ("{z}: plants look off?", ["yes", "no", "not sure"]),
    "protect": ("{z}: shade before noon?", ["yes", "no", "not sure"]),
    "progress": ("{z}: firmed up?", ["yes", "no", "not sure"]),
    "opportunity": ("{z}: stock still prime?", ["yes", "no", "not sure"]),
    "close": ("{z}: did it help?", ["better", "same", "worse", "not sure"]),
}


def _short_question(q):
    z = _short_subject(q.subject)
    tmpl, options = _SHORT_Q.get(q.decision_kind, ("{z}: anything notable?", ["yes", "no", "not sure"]))
    return tmpl.format(z=z), options


class WalkSession:
    def __init__(self, analysis, questions, open_experiments, snapshot, display: CompanionDisplay):
        self.analysis = analysis
        self.display = display
        self.snapshot = snapshot
        self.engine = InteractionEngine(questions, open_experiments,
                                        snapshot_ref=snapshot.assembled_at,
                                        date=(snapshot.assembled_at or "today")[:10])
        self._alerted: set = set()
        self._tick = 0

    # --- MORNING_WALK --------------------------------------------------------
    def start(self):
        a = self.analysis
        self.display.show_summary(f"{_short_subject(a.greenhouse_name)}: {self._summary_headline()}",
                                  detail=f"confidence {a.confidence_level.lower()}")
        if a.priorities:
            p = a.priorities[0]
            self.display.show_priority(f"Today: {_short_subject(p.zone_name)} — {p.title}",
                                       detail=p.action)

    def _summary_headline(self) -> str:
        a = self.analysis
        crit = [c for c in a.concerns if c.value == "Critical"]
        if crit:
            return f"watch {_short_subject(crit[0].zone_name)}"
        return "settled this morning" if not a.concerns else "a few things to watch"

    # --- one step of the walk (the grower has moved to `location`) -----------
    def tick(self, location: str):
        self._tick += 1
        # KNOWLEDGE_GAP takes precedence: a question is the *actionable* interaction (it updates
        # confidence), so if there's one worth asking here, ask it rather than merely warning.
        decision, q = self.engine.consider(location, self._tick)
        if decision == "ask":
            return self._ask(q, location)
        if decision == "silent":
            return Mode.SILENT_MONITORING        # considered, judged not worth interrupting

        # ALERT only for a critical concern here that NO question already covers (avoid
        # double-speaking about the same thing).
        covered = {self._short_subject_of(qq.subject) for qq in self.engine.questions}
        for c in self.analysis.concerns:
            if c.value == "Critical" and c.zone_id not in self._alerted \
                    and _short_subject(location).lower() in c.zone_name.lower() \
                    and _short_subject(c.zone_name) not in covered:
                self._alerted.add(c.zone_id)
                self.display.show_warning(f"{_short_subject(c.zone_name)}: {c.title}",
                                          detail=c.action)
                return Mode.ALERT
        return Mode.SILENT_MONITORING

    @staticmethod
    def _short_subject_of(subject: str) -> str:
        return _short_subject(subject)

    # --- KNOWLEDGE_GAP + OBSERVATION_CONFIRMATION ---------------------------
    def _ask(self, q, location) -> Mode:
        headline, options = _short_question(q)
        self.engine.record_ask(q, location, headline)
        msg = CompanionMessage(Primitive.QUESTION, headline, detail=q.text,
                               urgency=Urgency.ASK, needs_response=True, options=options, id=q.id)
        answer = self.display.show_question(msg)
        result = self.engine.answer(q, answer, location, self._tick, headline)
        self.display.show_confirmation(self._confirmation(result))
        return Mode.OBSERVATION_CONFIRMATION

    @staticmethod
    def _confirmation(result: dict) -> str:
        z = _short_subject(result["subject"])
        if not result["informative"]:
            return f"OK — I'll keep watching {z}."
        if result["negated"]:
            return f"Good — I no longer need to ask about {z}."
        return "Thank you — that raised my confidence."

    # --- NAVIGATION (optional, grower-initiated suggestion) ------------------
    def suggest_next(self) -> Optional[str]:
        for p in self.analysis.priorities:
            z = _short_subject(p.zone_name)
            if p.zone_id not in self.engine.resolved_ids:
                self.display.show_navigation(f"Next: look at {z}", detail=p.title)
                return z
        return None

    # --- EVENING_REVIEW ------------------------------------------------------
    def finish(self):
        s = self.engine.stats()
        moves = [r for r in self.engine.records
                 if r.answered and r.confidence_after and r.confidence_after != r.confidence_before]
        self.display.show_summary(
            f"Walk done — asked {s['asked']}, stayed silent {s['silenced']}",
            detail=f"{len(moves)} confidence update(s)")
        for r in moves:
            self.display.show_status(
                f"{_short_subject(r.location)}: {r.confidence_before}→{r.confidence_after}",
                detail="updated from your answer")
        return s

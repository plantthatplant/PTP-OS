"""The Interaction Engine — choose the next interruption, or choose silence.

It does NOT reason about biology. It takes Gaia's already-VoI-scored questions and decides,
moment to moment on the walk, whether the expected biological value of asking *here, now*
exceeds the (context-aware) cost of interrupting — reusing workflow timing/location, the
knowledge-gap VoI components, and the lifecycle confidence ladder. Silence is the default.

Every decision (asked, or considered-and-silenced) is recorded permanently as evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from . import _paths  # noqa: F401  (puts app/ on the path)
from greenhouse_brain import store, workflow
from greenhouse_brain.lifecycle import reinforce, apply_outcome

# Don't interrupt again within this many ticks unless it's critical (spacing makes silence the
# texture of the walk, not the exception).
_SPACING_TICKS = 2
_RECENT_PENALTY = 4.0   # how much a recent interruption inflates the next one's cost


@dataclass
class InteractionRecord:
    """The permanent memory of one interaction (or one considered silence)."""
    question_id: str
    timestamp: str
    snapshot_ref: Optional[str]
    decision_id: Optional[str]
    experiment_id: Optional[str]
    reason: str
    uncertainty: str
    evi: float                       # expected value of information (pre-interruption)
    interruption_cost: float         # context-aware cost at the moment of the decision
    confidence_before: Optional[str]
    confidence_after: Optional[str]
    worthwhile: Optional[bool]
    # interaction context
    mode: str
    primitive: str
    urgency: str
    location: str
    decision: str                    # asked | silenced
    wording_shown: str = ""
    answered: bool = False
    answer: str = ""


def _negated(ans: str) -> bool:
    al = f" {ans.lower()} "
    return any(w in al for w in (" no ", " not ", "n't", " clear ", " dry ", " none ", " fine ",
                                 " worse "))


def _informative(ans: str) -> bool:
    return bool(ans) and not any(w in ans.lower() for w in ("not sure", "dunno",
                                                            "don't know", "no idea"))


class InteractionEngine:
    def __init__(self, questions, open_experiments, snapshot_ref, date):
        self.questions = list(questions)
        self.experiments: Dict[str, object] = {e.id: e for e in open_experiments}
        self.snapshot_ref = snapshot_ref
        self.date = date
        self.resolved_ids: set = set()
        self.records: List[InteractionRecord] = []
        self._last_interrupt_tick: int = -10
        self._considered = 0
        self._asked = 0

    # --- interaction economics (NOT biology) ---------------------------------
    @staticmethod
    def _evi(q) -> float:
        c = q.voi_components or {}
        return round(c.get("stakes", 0.5) * c.get("uncertainty", 0.6)
                     * c.get("decisiveness", 0.3) * c.get("prior", 1.0), 3)

    def _effective_cost(self, q, tick: int) -> float:
        base = (q.voi_components or {}).get("interruption_cost", 0.15)
        recent = (tick - self._last_interrupt_tick) < _SPACING_TICKS
        return round(base * (_RECENT_PENALTY if recent else 1.0), 3)

    def _experiment_for(self, q):
        if q.experiment_id and q.experiment_id in self.experiments:
            return self.experiments[q.experiment_id]
        guess = f"exp-{self.date}-{q.decision_id}-{q.decision_kind}"
        return self.experiments.get(guess)

    # --- the decision: ask here/now, or stay silent --------------------------
    def consider(self, location: str, tick: int) -> Tuple[str, Optional[object]]:
        """Returns ("ask", q) | ("silent", q) | ("none", None).
        'none'  = nothing relevant here (pure silence, not recorded).
        'silent'= something could be asked but the value didn't beat the cost (recorded)."""
        here = workflow.surface(self.questions, location, self.resolved_ids)
        if not here:
            return ("none", None)
        self._considered += 1
        best = max(here, key=self._evi)
        evi, cost = self._evi(best), self._effective_cost(best, tick)
        critical = workflow.interrupt_now(best, self.resolved_ids)
        if critical or evi > cost:
            return ("ask", best)
        self._record(best, evi, cost, location, decision="silenced")
        return ("silent", best)

    # --- recording -----------------------------------------------------------
    def _record(self, q, evi, cost, location, decision, mode="knowledge-gap",
                primitive="question", urgency="silent", wording="", answered=False,
                answer="", conf_before=None, conf_after=None, worthwhile=None) -> InteractionRecord:
        exp = self._experiment_for(q)
        rec = InteractionRecord(
            question_id=q.id, timestamp=datetime.now().isoformat(timespec="seconds"),
            snapshot_ref=self.snapshot_ref, decision_id=q.decision_id,
            experiment_id=getattr(exp, "id", q.experiment_id),
            reason=q.biological_reason, uncertainty=q.uncertainty, evi=evi,
            interruption_cost=cost, confidence_before=conf_before, confidence_after=conf_after,
            worthwhile=worthwhile, mode=mode, primitive=primitive, urgency=urgency,
            location=location, decision=decision, wording_shown=wording,
            answered=answered, answer=answer)
        self.records.append(rec)
        store.append_interaction(asdict(rec))   # permanent memory
        return rec

    def record_ask(self, q, location, wording) -> Tuple[Optional[str], object]:
        """Mark that we asked q. Returns (confidence_before, experiment)."""
        self._asked += 1
        exp = self._experiment_for(q)
        return (getattr(exp, "confidence_before", None), exp)

    def answer(self, q, answer_text: str, location: str, tick: int, wording: str) -> dict:
        """Process the grower's answer: update the decision's confidence, learn whether the
        interruption was worthwhile, and store the full interaction record. Returns a small
        result the WalkSession turns into a confirmation message."""
        exp = self._experiment_for(q)
        evi, cost = self._evi(q), self._effective_cost(q, tick)  # cost reflects state BEFORE this ask
        self._last_interrupt_tick = tick
        self.resolved_ids.add(q.id)
        informative = _informative(answer_text)
        negated = _negated(answer_text)
        conf_before = getattr(exp, "confidence_before", None)
        conf_after = conf_before

        if q.kind == "close" and exp is not None:
            outcome = ("improved" if any(w in answer_text.lower() for w in ("better", "help", "improv"))
                       else "worse" if "worse" in answer_text.lower()
                       else "unchanged" if any(w in answer_text.lower() for w in ("same", "unchanged"))
                       else "unknown")
            action = "skipped" if any(w in answer_text.lower() for w in ("didn't", "did not", "skip", "no")) else "done"
            apply_outcome(exp, action, outcome, answer_text, self.date)
            store.append_memory(exp)
            conf_after = exp.confidence_after
            worthwhile = outcome != "unknown"
            store.append_question_eval({"question_id": q.id, "decision_kind": "close",
                                        "voi": q.voi, "answer": answer_text,
                                        "changed_decision": outcome != "unknown",
                                        "confidence_increase": True, "worthwhile": worthwhile,
                                        "captured_on": self.date})
        else:
            if exp is not None and informative:
                conf_before, conf_after = reinforce(exp, agrees=not negated, note=answer_text)
            worthwhile = informative and (q.voi >= 0.30 or negated)
            store.append_answer({"question": q.text, "answer": answer_text, "kind": q.kind,
                                 "subject": q.subject, "captured_on": self.date})
            store.append_question_eval({"question_id": q.id, "decision_kind": q.decision_kind,
                                        "voi": q.voi, "answer": answer_text, "changed_decision": negated,
                                        "confidence_increase": informative, "worthwhile": worthwhile,
                                        "captured_on": self.date})

        self._record(q, evi, cost, location, decision="asked", primitive="question",
                     urgency="ask", wording=wording, answered=True, answer=answer_text,
                     conf_before=conf_before, conf_after=conf_after, worthwhile=worthwhile)
        return {"worthwhile": worthwhile, "informative": informative, "negated": negated,
                "confidence_before": conf_before, "confidence_after": conf_after,
                "subject": q.subject}

    def stats(self) -> dict:
        return {"considered": self._considered, "asked": self._asked,
                "silenced": self._considered - self._asked,
                "interactions_recorded": len(self.records)}

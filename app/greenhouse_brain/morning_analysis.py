"""Morning Analysis — the Brain's proactive start to the day.

Before anyone arrives, the Brain collects everything available, builds context,
and works out the day: its concerns, its opportunities, its priorities, and its
curiosities. The result is stored, so when the grower later asks 'How is the
greenhouse today?' the answer is already waiting — the Brain has been working since
before the lights came on.

This composes the existing engines; it adds no new reasoning of its own — it is the
daily *rhythm* around the one intelligence (docs/daily-operating-cycle.md).
"""
from __future__ import annotations

from datetime import datetime

from .context_engine import ContextEngine
from .decision_engine import DecisionEngine, CAVEATS
from .curiosity_engine import CuriosityEngine
from .domain import MorningAnalysis


class MorningAnalysisEngine:
    def __init__(self, context=None, decision=None, curiosity=None):
        self.context = context or ContextEngine()
        self.decision = decision or DecisionEngine()
        self.curiosity = curiosity or CuriosityEngine()

    def run(self, provider) -> MorningAnalysis:
        # 1. collect + 2. build context
        ctx = self.context.assemble(provider)

        # 3-5. concerns, opportunities, priorities
        candidates = self.decision.generate_candidates(ctx)
        ranked = self.decision.rank(candidates)
        concerns = [c for c in ranked if c.kind in ("prevent", "protect", "inspect")]
        opportunities = [c for c in candidates if c.kind == "opportunity"]
        priorities = [c for c in ranked if c.kind != "opportunity"][:3]

        # 6. curiosities
        curiosities = self.curiosity.generate(ctx, provider)

        concern = concerns[0] if concerns else None
        recommendation = priorities[0] if priorities else None
        conf_level, conf_rationale = self.decision.overall_confidence(recommendation, ctx)
        summary = self.decision.morning_summary(ctx, concern, opportunities, curiosities)

        return MorningAnalysis(
            prepared_at=datetime.now().strftime("%H:%M"),
            greenhouse_name=ctx.greenhouse.name,
            summary=summary,
            concerns=concerns,
            opportunities=opportunities,
            priorities=priorities,
            curiosities=curiosities,
            confidence_level=conf_level,
            confidence_rationale=conf_rationale,
            data_source=getattr(provider, "data_source", "mock"),
            caveats=list(CAVEATS),
        )

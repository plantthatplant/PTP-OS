"""GreenhouseBrain — proactive by default.

The Brain starts the day on its own: run_morning_analysis() collects everything,
builds context, and works out the day, then stores it. When the grower later asks
"How is the greenhouse today?", the Brain answers from that stored Morning Analysis
instead of analysing afresh — like a head grower who was already at work before
everyone arrived.

    Reality -> Provider -> Context -> Decision (+ Curiosity) -> Morning Analysis -> stored
    "how is the greenhouse today?" -> served from the stored Morning Analysis -> Language
"""
from __future__ import annotations

from . import store
from .providers.base import GreenhouseProvider
from .providers import make_provider
from .morning_analysis import MorningAnalysisEngine
from .language_engine import LanguageRenderer, TemplateLanguageRenderer
from .domain import MorningAnalysis


_STATUS_HINTS = ("how is", "how's", "status", "today", "greenhouse", "houses", "going", "morning")


class GreenhouseBrain:
    def __init__(self, provider: GreenhouseProvider = None,
                 morning: MorningAnalysisEngine = None,
                 language: LanguageRenderer = None):
        self.provider = provider or make_provider()
        self.morning = morning or MorningAnalysisEngine()
        self.language = language or TemplateLanguageRenderer()

    # The proactive start of the day: analyse and remember.
    def run_morning_analysis(self) -> MorningAnalysis:
        analysis = self.morning.run(self.provider)
        store.save(analysis)
        return analysis

    def morning_briefing(self) -> str:
        return self.language.render_morning(self.run_morning_analysis())

    # The reactive question, answered from the morning's work.
    def answer(self, question: str) -> str:
        prefix = ""
        if not any(h in question.lower() for h in _STATUS_HINTS):
            prefix = "(v1 understands one question — the daily status — so here is that.)\n\n"

        analysis = store.load()
        if analysis is None:
            # Nobody ran the morning analysis yet; do it now and say so.
            analysis = self.run_morning_analysis()
            prefix += ("(No morning analysis was waiting, so I looked things over just now.)\n\n")

        return prefix + self.language.render_status(analysis)

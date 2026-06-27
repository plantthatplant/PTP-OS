"""Language Engine — explain calmly. It phrases; it never decides (ADR-001).

Two views of the same stored Morning Analysis:
  * render_morning()  — the full proactive briefing (the head grower's start of day).
  * render_status()   — the answer to "How is the greenhouse today?", drawn from the
                        already-prepared analysis (summary, three priorities, one
                        concern, one recommendation, confidence).

Deterministic templates, no AI model (ADR-001 permits this for simple cases). An
AI-backed renderer can replace this behind the same interface later (ADR-003).
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from .domain import MorningAnalysis


class LanguageRenderer(ABC):
    @abstractmethod
    def render_morning(self, analysis: MorningAnalysis) -> str: ...

    @abstractmethod
    def render_status(self, analysis: MorningAnalysis) -> str: ...


_KIND = {"protect": "Protect", "prevent": "Prevent", "inspect": "Inspect",
         "progress": "Progress", "maintain": "Maintain", "opportunity": "Opportunity",
         "hold": "Hold"}


def _rule(width: int = 64) -> str:
    return "-" * width


class TemplateLanguageRenderer(LanguageRenderer):

    # --- the full morning briefing ------------------------------------------

    def render_morning(self, a: MorningAnalysis) -> str:
        L = []
        L.append(f"MORNING ANALYSIS  —  {a.greenhouse_name}")
        L.append(f"Prepared at {a.prepared_at}, before the day began.")
        L.append("=" * 64)
        L.append("")
        L.append("SUMMARY")
        L.append(f"  {a.summary}")
        L.append("")

        L.append("CONCERNS")
        if a.concerns:
            for c in a.concerns:
                L.append(f"  - [{_KIND[c.kind]} - {c.value}] {c.zone_name}: {c.title}")
                L.append(f"      {c.why}.")
        else:
            L.append("  None this morning.")
        L.append("")

        L.append("OPPORTUNITIES")
        if a.opportunities:
            for c in a.opportunities:
                L.append(f"  - {c.zone_name}: {c.title}")
                L.append(f"      {c.action} — {c.expected_benefit}.")
        else:
            L.append("  None standing out this morning.")
        L.append("")

        L.append("TODAY'S PRIORITIES")
        for i, c in enumerate(a.priorities, 1):
            L.append(f"  {i}. [{_KIND[c.kind]} - {c.value}] {c.zone_name}: {c.action}")
            L.append(f"      (why: {c.why}; if ignored: {c.if_ignored}; "
                     f"effort {c.effort}, urgency {c.window}, confidence {c.confidence})")
        L.append("")

        L.append("CURIOSITIES  (not alarms — things I'd like to understand)")
        if a.curiosities:
            for cu in a.curiosities:
                L.append(f"  - I'm curious: {cu.observation}.")
                L.append(f"      Why it matters: {cu.why_it_matters}.")
                L.append(f"      Worth a look: {cu.worth_a_look}.")
        else:
            L.append("  Nothing pulling at my attention today.")
        L.append("")

        L.append("OVERALL CONFIDENCE")
        L.append(f"  {a.confidence_level}. {a.confidence_rationale}")
        L.append("")
        L.append(_rule())
        L.append(f"Sprint-1 prototype on {a.data_source} data. Known shortcuts:")
        for cav in a.caveats:
            L.append(f"  * {cav}")
        return "\n".join(L)

    # --- the answer to "how is the greenhouse today?" -----------------------

    def render_status(self, a: MorningAnalysis) -> str:
        L = []
        L.append(f"How is the greenhouse today?  —  {a.greenhouse_name}")
        L.append(f"(from this morning's analysis, prepared at {a.prepared_at} before you arrived)")
        L.append("=" * 64)
        L.append("")
        L.append("SUMMARY")
        L.append(f"  {a.summary}")
        L.append("")

        L.append("TOP THREE PRIORITIES")
        for i, c in enumerate(a.priorities, 1):
            L.append(f"  {i}. [{_KIND[c.kind]} - {c.value}] {c.zone_name}: {c.action}")
        L.append("")

        if a.concerns:
            c = a.concerns[0]
            L.append("ONE CONCERN")
            L.append(f"  {c.title} - {c.zone_name}.")
            L.append(f"  {c.why}.")
            if c.evidence:
                L.append(f"  Evidence: {'; '.join(c.evidence)}.")
            L.append("")

        if a.priorities:
            r = a.priorities[0]
            L.append("ONE RECOMMENDATION")
            L.append(f"  {r.action}.")
            L.append(f"    - Why: {r.why}.")
            L.append(f"    - Objective: {r.objective}.")
            L.append(f"    - Expected benefit: {r.expected_benefit}.")
            L.append(f"    - If ignored: {r.if_ignored}.")
            L.append(f"    - Effort: {r.effort}.  Urgency: {r.window}.  Confidence: {r.confidence}.")
            L.append("")

        L.append("OVERALL CONFIDENCE")
        L.append(f"  {a.confidence_level}. {a.confidence_rationale}")
        L.append("")
        if a.opportunities or a.curiosities:
            bits = []
            if a.opportunities:
                bits.append(f"{len(a.opportunities)} opportunity(ies)")
            if a.curiosities:
                bits.append(f"{len(a.curiosities)} curiosity(ies)")
            L.append(f"(I'm also holding {' and '.join(bits)} from this morning — "
                     f"ask for the morning analysis to see them.)")
        L.append("")
        L.append(_rule())
        L.append(f"Sprint-1 prototype on {a.data_source} data — see docs/sprint-1-shortcuts.md.")
        return "\n".join(L)

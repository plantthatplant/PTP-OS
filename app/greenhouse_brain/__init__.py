"""PTP OS — Greenhouse Brain (Sprint 1 reasoning prototype).

Proactive by default: it runs a Morning Analysis (concerns, opportunities,
priorities, curiosities) before anyone arrives, and answers 'How is the greenhouse
today?' from that stored analysis. Production data sources and AI rendering arrive
later behind the same seams.
"""
from .brain import GreenhouseBrain

__all__ = ["GreenhouseBrain"]

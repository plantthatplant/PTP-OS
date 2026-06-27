"""The Provider Layer boundary (see specs/greenhouse-provider.md, ADR-002).

The single seam through which the brain learns about reality. Everything above it
depends only on this interface and the Domain Model — never on a vendor. Swapping
the mock for Claude Dispatch, then Synopta, must change nothing above this line.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List

from ..domain import Greenhouse, ClimateReading, Observation, Outlook, Change


class GreenhouseProvider(ABC):
    """Answers 'what is happening in the greenhouse?' as Domain Model types only."""

    name: str = "abstract"

    @abstractmethod
    def get_greenhouse(self) -> Greenhouse: ...

    @abstractmethod
    def get_latest_climate(self) -> Dict[str, ClimateReading]:
        """Latest reading per zone id."""

    @abstractmethod
    def get_humidity_history(self, zone_id: str) -> List[float]:
        """Recent same-time-of-day humidity values, oldest first (for trend)."""

    @abstractmethod
    def get_observations(self) -> List[Observation]: ...

    @abstractmethod
    def get_outlook(self) -> Outlook:
        """Day-ahead outlook. NOTE: a Sprint-1 stand-in for a real Weather provider."""

    def get_recent_changes(self) -> List[Change]:
        """Deliberate recent changes worth following up. Default: none."""
        return []

    def health_check(self) -> bool:
        return True

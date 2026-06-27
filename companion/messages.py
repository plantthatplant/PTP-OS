"""Device-independent message and mode vocabulary.

A CompanionMessage is what Gaia wants to convey, in a form ANY device can render — a tiny
heads-up display, a phone, AR glasses, a voice assistant, a robot. It is deliberately small:
one headline, optionally one short detail, and (for a question) a tiny fixed answer set. The
device adapter decides how to show it; this layer decides only what to say.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

# How small the headline must be to read at a glance, in sunlight, while walking.
HEADLINE_MAX = 40
DETAIL_MAX = 48


class Mode(str, Enum):
    MORNING_WALK = "morning-walk"
    INSPECTION = "inspection"
    KNOWLEDGE_GAP = "knowledge-gap"
    OBSERVATION_CONFIRMATION = "observation-confirmation"
    ALERT = "alert"
    NAVIGATION = "navigation"
    SILENT_MONITORING = "silent-monitoring"
    EVENING_REVIEW = "evening-review"


class Urgency(str, Enum):
    SILENT = "silent"     # nothing to show
    INFO = "info"         # a calm, glanceable note
    ASK = "ask"           # needs a short answer
    WARN = "warn"         # a warning worth a beat of attention


class Primitive(str, Enum):
    MESSAGE = "message"
    PRIORITY = "priority"
    QUESTION = "question"
    STATUS = "status"
    NAVIGATION = "navigation"
    CONFIRMATION = "confirmation"
    WARNING = "warning"
    SUMMARY = "summary"


@dataclass
class CompanionMessage:
    """One thing to convey. Headline is the glance; detail is optional and short."""
    primitive: Primitive
    headline: str
    detail: str = ""
    urgency: Urgency = Urgency.INFO
    needs_response: bool = False
    options: List[str] = field(default_factory=list)   # tiny fixed answer set, no typing
    id: Optional[str] = None                            # question/interaction id when relevant

    def fits_one_screen(self) -> bool:
        return len(self.headline) <= HEADLINE_MAX and len(self.detail) <= DETAIL_MAX

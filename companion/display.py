"""CompanionDisplay — the device-independent interface every client implements.

Gaia speaks through these eight primitives and nothing else. A device adapter (Even G2 today;
Android, AR, voice, robot tomorrow) translates each call into its own display capabilities.
Nothing above this line knows which device is connected; nothing in Gaia imports a device.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from .messages import CompanionMessage, Primitive, Urgency


class CompanionDisplay(ABC):
    """Render device-independent messages on a specific device.

    The default implementations route every primitive through one `render()` the adapter must
    provide — so a new device only implements `render()` (and may override individual
    primitives for richer treatment). The grower's answer to a question is returned by
    `ask()`."""

    name: str = "abstract-display"

    @abstractmethod
    def render(self, message: CompanionMessage) -> None:
        """Show a single message. Must respect the small-display rules (one screen)."""

    def ask(self, message: CompanionMessage) -> str:
        """Show a question and return the grower's chosen answer (device-specific input).
        Default: render and return empty (a silent/no-input device). Override per device."""
        self.render(message)
        return ""

    # --- the eight primitives (device-independent) ---------------------------
    def show_message(self, headline, detail="", urgency=Urgency.INFO):
        self.render(CompanionMessage(Primitive.MESSAGE, headline, detail, urgency))

    def show_priority(self, headline, detail=""):
        self.render(CompanionMessage(Primitive.PRIORITY, headline, detail, Urgency.INFO))

    def show_question(self, message: CompanionMessage) -> str:
        return self.ask(message)

    def show_status(self, headline, detail=""):
        self.render(CompanionMessage(Primitive.STATUS, headline, detail, Urgency.INFO))

    def show_navigation(self, headline, detail=""):
        self.render(CompanionMessage(Primitive.NAVIGATION, headline, detail, Urgency.INFO))

    def show_confirmation(self, headline, detail=""):
        self.render(CompanionMessage(Primitive.CONFIRMATION, headline, detail, Urgency.INFO))

    def show_warning(self, headline, detail=""):
        self.render(CompanionMessage(Primitive.WARNING, headline, detail, Urgency.WARN))

    def show_summary(self, headline, detail=""):
        self.render(CompanionMessage(Primitive.SUMMARY, headline, detail, Urgency.INFO))

"""PhoneDisplay — the iPhone 'information' surface.

Where Oskar reads and captures. Unlike the Even G2 (one glanceable line), the phone may show a
short calm block — a headline plus a few wrapped lines of the *why*. It is still device-
independent: it renders the same eight CompanionMessage primitives, only with more room. It
holds no biology and makes no decisions.
"""
from __future__ import annotations

import textwrap
from typing import Callable, List, Optional

from ..display import CompanionDisplay
from ..messages import CompanionMessage


class PhoneDisplay(CompanionDisplay):
    name = "phone"
    WIDTH = 56

    _LABEL = {"summary": "", "priority": "TODAY", "status": "STATUS", "question": "GAIA ASKS",
              "confirmation": "", "warning": "ALERT", "navigation": "GO", "message": ""}

    def __init__(self, answer_source: Optional[Callable[[CompanionMessage], str]] = None):
        self.answer_source = answer_source
        self.shown: List[CompanionMessage] = []

    def render(self, message: CompanionMessage) -> None:
        self.shown.append(message)
        label = self._LABEL.get(message.primitive.value, "")
        bar = f"  {label}" if label else ""
        print(f"  ┌{'─' * self.WIDTH}┐{bar}")
        for line in textwrap.wrap(message.headline, self.WIDTH - 2) or [""]:
            print(f"  │ {line.ljust(self.WIDTH - 2)} │")
        if message.detail:
            print(f"  │ {' ' * (self.WIDTH - 2)} │")
            for line in textwrap.wrap(message.detail, self.WIDTH - 2):
                print(f"  │ {line.ljust(self.WIDTH - 2)} │")
        print(f"  └{'─' * self.WIDTH}┘")

    def ask(self, message: CompanionMessage) -> str:
        self.render(message)
        if message.options:
            print(f"      [ {' / '.join(message.options)} ]")
        if self.answer_source:
            return self.answer_source(message)
        try:
            return input("      > ").strip()
        except (EOFError, KeyboardInterrupt):
            return ""

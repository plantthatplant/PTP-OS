"""ConsoleDisplay — render Gaia's primitives to a terminal, for development.

A plain-text device adapter: it proves the device-independent interface works on a second,
totally different "device" (a terminal) with no change to the Companion or the Brain. Answers
come from an injectable source (a scripted list for demos/tests, or stdin).
"""
from __future__ import annotations

from typing import Callable, List, Optional

from ..display import CompanionDisplay
from ..messages import CompanionMessage


class ConsoleDisplay(CompanionDisplay):
    name = "console"

    def __init__(self, answer_source: Optional[Callable[[CompanionMessage], str]] = None):
        self.answer_source = answer_source
        self.shown: List[CompanionMessage] = []

    def render(self, message: CompanionMessage) -> None:
        self.shown.append(message)
        tag = message.primitive.value.upper()
        line = f"[{tag}] {message.headline}"
        if message.detail:
            line += f" — {message.detail}"
        print(line)

    def ask(self, message: CompanionMessage) -> str:
        self.render(message)
        if message.options:
            print(f"        options: {' / '.join(message.options)}")
        if self.answer_source:
            return self.answer_source(message)
        try:
            return input("        > ").strip()
        except (EOFError, KeyboardInterrupt):
            return ""

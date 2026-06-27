"""EvenG2Display — render Gaia's primitives on the Even G2 heads-up display.

The G2 is a tiny monochrome HUD seen at a glance in sunlight while walking: one short line,
no scrolling, no menus, no typing. This adapter's whole job is to fit a CompanionMessage into
that contract and hand it to the device. It contains NO Gaia logic — only formatting + the
one transport seam (`_send_to_device`) where the real Even G2 SDK call will go.

For development there is no glasses hardware reachable, so `_send_to_device` records the exact
line that would be shown (and prints a framed mock of the lens). Going live = implementing that
one method against the SDK; nothing above it changes.
"""
from __future__ import annotations

from typing import Callable, List, Optional

from ..display import CompanionDisplay
from ..messages import CompanionMessage, HEADLINE_MAX

# Glanceable glyphs per primitive (a monochrome HUD has no colour to lean on).
_GLYPH = {"warning": "!", "question": "?", "confirmation": "✓", "priority": "›",
          "navigation": "→", "status": "·", "summary": "=", "message": " "}


def _truncate(text: str, limit: int) -> str:
    text = " ".join((text or "").split())          # collapse whitespace for a single line
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


class EvenG2Display(CompanionDisplay):
    name = "even-g2"
    LINE_WIDTH = HEADLINE_MAX

    def __init__(self, answer_source: Optional[Callable[[CompanionMessage], str]] = None,
                 echo: bool = True):
        # answer_source simulates the device's input (gesture/voice selection of an option).
        self.answer_source = answer_source
        self.echo = echo
        self.sent: List[str] = []        # every line sent to the lens (for audit/tests)

    # --- the one transport seam (replace with the real SDK to go live) -------
    def _send_to_device(self, line: str) -> None:
        self.sent.append(line)
        if self.echo:
            print(f"   ┌{'─' * (self.LINE_WIDTH + 2)}┐")
            print(f"   │ {line.ljust(self.LINE_WIDTH)} │   ◉ Even G2")
            print(f"   └{'─' * (self.LINE_WIDTH + 2)}┘")

    def _format(self, m: CompanionMessage) -> str:
        glyph = _GLYPH.get(m.primitive.value, " ")
        line = _truncate(m.headline, self.LINE_WIDTH - 2)
        return f"{glyph} {line}".rstrip()

    def render(self, message: CompanionMessage) -> None:
        # One screen: the headline line. (A second tiny detail line is shown only if present
        # and short — the G2 can hold a brief sub-line; longer detail is dropped, not scrolled.)
        self._send_to_device(self._format(message))
        if message.detail:
            self._send_to_device(f"  {_truncate(message.detail, self.LINE_WIDTH - 2)}")

    def ask(self, message: CompanionMessage) -> str:
        self.render(message)
        if message.options:
            self._send_to_device(_truncate("[ " + " / ".join(message.options) + " ]",
                                           self.LINE_WIDTH))
        answer = self.answer_source(message) if self.answer_source else ""
        if self.echo and answer:
            print(f"        grower ▸ {answer}")
        return answer

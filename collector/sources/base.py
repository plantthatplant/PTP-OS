"""The Source boundary — `fetch() -> raw vendor reading dict`.

The single seam through which Synopta data enters the Collector. A source contains ALL
the vendor-specific messiness (where the data lives, how it is shaped, how it can fail) and
hands up a plain dict. It never translates to the Snapshot — that is translate.py's job —
so the same translation runs over every source.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class SourceError(Exception):
    """A source could not deliver a reading at all (missing file, unreachable, unparseable).

    Distinct from a *partial* reading: a missing single value is not an error — it is an
    honest gap handled in translation. SourceError means there was nothing to translate."""


class SynoptaSource(ABC):
    """Answers 'what did Synopta report?' as a raw, vendor-shaped dict."""

    label: str = "source"

    @abstractmethod
    def fetch(self) -> dict:
        """Return the raw greenhouse reading as a dict, or raise SourceError."""

"""FixtureSource — a bundled, captured Synopta reading.

Offline and deterministic: it lets the whole pipeline (translate → validate → write →
Gaia) be proven today, with no greenhouse reachable. The real sources return the same
shape, so swapping this out changes nothing downstream.
"""
from __future__ import annotations

import json
import os

from .base import SynoptaSource, SourceError

_SAMPLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_synopta_export.json")


class FixtureSource(SynoptaSource):
    label = "fixture"

    def __init__(self, path: str = _SAMPLE):
        self.path = path

    def fetch(self) -> dict:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError as e:
            raise SourceError(f"fixture not found: {self.path}") from e
        except json.JSONDecodeError as e:
            raise SourceError(f"fixture is not valid JSON: {e}") from e

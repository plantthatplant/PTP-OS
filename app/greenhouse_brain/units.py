"""Small, vendor-neutral primitives for reading messy real-world values.

These are not biology and not vendor logic — just the low-level cleaning that every
acquisition path needs (a Provider, the Collector). Keeping them in one place means there is
a single, tested definition of "what is this number?" rather than a copy per layer.
"""
from __future__ import annotations

from typing import Optional


def to_number(raw) -> Optional[float]:
    """Reduce a real-world value to a float, or None if there genuinely isn't one.

    Handles the mess live data arrives in — European comma decimals, unit suffixes, stray
    spaces ('24,2 °C' -> 24.2, '20%' -> 20.0) — and refuses to guess: a non-numeric value
    ('closed', '') becomes None, never a fabricated 0. None/booleans are not numbers.
    """
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    s = str(raw).strip().replace(",", ".")
    num = ""
    for ch in s:
        if ch.isdigit() or ch in ".-":
            num += ch
        elif num:
            break
    try:
        return float(num)
    except ValueError:
        return None


def airflow_from_vent(raw) -> str:
    """Translate a vent position into the airflow the plants actually feel:
    low / normal / good. Accepts a number, a percent string, or the words
    'closed'/'open'. Unknown -> 'normal' (a neutral assumption, not a fabricated reading)."""
    if raw is None:
        return "normal"
    s = str(raw).lower()
    if "closed" in s:
        return "low"
    if "open" in s:
        return "good"
    n = to_number(raw)
    if n is None:
        return "normal"
    if n <= 0:
        return "low"
    return "normal" if n <= 40 else "good"

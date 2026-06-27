"""Lightweight feedback — a 30-second morning gut-check.

After the Morning Analysis, the grower rates each recommendation with one of three
words and, optionally, one line of "why". That's all. We **capture** it; we do not
analyse it and we do not learn from it yet (that is a later sprint). The point is to
start collecting real-world validation from day one.

This module only collects and stores. It is UI-agnostic: it takes an `ask` (prompt ->
text) and a `say` (text -> None) so it can be driven by a terminal, tests, or — later
— voice.
"""
from __future__ import annotations

from datetime import datetime

from . import store
from .domain import MorningAnalysis


RATINGS = {
    "c": "Correct", "1": "Correct",
    "p": "Partially Correct", "2": "Partially Correct",
    "i": "Incorrect", "3": "Incorrect",
}


def review(analysis: MorningAnalysis, ask, say) -> int:
    """Walk the morning's recommendations; store one rating (+ optional why) each.
    Returns how many responses were saved."""
    recs = analysis.priorities
    if not recs:
        say("No recommendations to review this morning.")
        return 0

    say(f"Quick check on this morning's {len(recs)} recommendations (~20 seconds).")
    say("For each:  [c]orrect   [p]artially   [i]ncorrect    (Enter to skip, q to quit)")
    say("")

    saved = 0
    for idx, r in enumerate(recs, 1):
        say(f"{idx}/{len(recs)}  {r.zone_name}: {r.action}")
        choice = ask("   your call (c/p/i): ").strip().lower()
        if choice == "q":
            break
        if choice not in RATINGS:
            say("   (skipped)\n")
            continue

        why = ask("   why? (optional, Enter to skip): ").strip()
        store.append_feedback({
            "captured_at": datetime.now().isoformat(timespec="seconds"),
            "analysis_prepared_at": analysis.prepared_at,
            "greenhouse": analysis.greenhouse_name,
            "recommendation": {
                "zone": r.zone_name,
                "kind": r.kind,
                "title": r.title,
                "action": r.action,
            },
            "rating": RATINGS[choice],
            "why": why,
        })
        saved += 1
        say("")

    return saved

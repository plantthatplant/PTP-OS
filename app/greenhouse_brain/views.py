"""The grower-facing experience — a calm, beautiful Morning Brief and Evening Review.

Presentation only. It reads the existing Morning Analysis, the day's questions, the
snapshot's data quality, and the day's experiments, and lays them out for a head grower
to read in under a minute. No reasoning happens here.
"""
from __future__ import annotations

from typing import Dict, List

_W = 66
_TAG = {"prevent": "PREVENT", "protect": "PROTECT", "inspect": "INSPECT",
        "progress": "PROGRESS", "opportunity": "OPPORTUNITY", "maintain": "MAINTAIN"}


def _box_top(title):
    return "┌─ " + title + " " + "─" * max(0, _W - len(title) - 4) + "┐"


def _rule(ch="─"):
    return ch * _W


def recall_notes(analysis, memories: List[dict]) -> Dict[str, str]:
    """For each of today's priorities, the most recent matching memory — the loop closing."""
    notes = {}
    for c in analysis.priorities:
        matches = [m for m in memories if m.get("zone") == c.zone_name and m.get("kind") == c.kind]
        if matches:
            m = matches[-1]
            notes[c.zone_name + "|" + c.kind] = (
                f"last time ({m.get('closed_on')}): {m.get('outcome')} — "
                f"confidence {m.get('confidence_before')} → {m.get('confidence_after')}")
    return notes


def render_brief(analysis, coverage: dict, reality: dict, questions, recalls, changes=None, held_back=0) -> str:
    a = analysis
    L = []
    L.append("╔" + "═" * _W + "╗")
    L.append("║" + f"  GOOD MORNING — {a.greenhouse_name}".ljust(_W) + "║")
    L.append("║" + f"  Prepared at {a.prepared_at}, before the day began.".ljust(_W) + "║")
    L.append("╚" + "═" * _W + "╝")
    L.append("")
    L.append("  " + a.summary)
    L.append("")

    if changes is not None:
        L.append(_box_top("SINCE YESTERDAY"))
        if changes:
            for ch in changes:
                L.append(f"  •  {ch}")
        else:
            L.append("  No notable change overnight.")
        L.append("")

    L.append(_box_top("TODAY'S THREE PRIORITIES"))
    if a.priorities:
        for i, c in enumerate(a.priorities, 1):
            L.append(f"  {i}.  [{_TAG.get(c.kind, c.kind)} · {c.value}]  {c.zone_name}")
            L.append(f"      {c.action}")
            key = c.zone_name + "|" + c.kind
            if key in recalls:
                L.append(f"      ↻ {recalls[key]}")
    else:
        L.append("  Nothing pressing — the houses look settled.")
    L.append("")

    L.append(_box_top("OPPORTUNITIES"))
    if a.opportunities:
        for c in a.opportunities:
            L.append(f"  •  {c.zone_name}: {c.action}")
    else:
        L.append("  None standing out this morning.")
    L.append("")

    L.append(_box_top("CURIOSITIES  (things I'd like to understand — not alarms)"))
    if a.curiosities:
        for cu in a.curiosities:
            L.append(f"  ?  {cu.observation}")
    else:
        L.append("  Nothing pulling at my attention today.")
    L.append("")

    L.append(_box_top("ON YOUR WALK, COULD YOU CHECK"))
    if questions:
        for q in questions:
            L.append(f"  →  {q.text}")
    else:
        L.append("  Nothing worth asking today — enjoy the walk.")
    if held_back:
        L.append(f"  (held back {held_back} lower-value question(s) — not worth interrupting you)")
    L.append("")

    L.append(_rule())
    L.append(f"  Source: {a.data_source}  ·  reality confidence {reality['label']} "
             f"({reality['score_pct']}%)  ·  coverage {coverage['coverage_pct']}%")
    L.append(f"  When you're back from the walk:  gaia walk    ·    End of day:  gaia evening")
    return "\n".join(L)


_ARROW = {"up": "↑", "down": "↓", "flat": "→"}


def _move(before, after):
    order = ["Low", "Medium", "Medium-high", "High"]
    try:
        d = order.index(after) - order.index(before)
    except ValueError:
        d = 0
    return _ARROW["up"] if d > 0 else (_ARROW["down"] if d < 0 else _ARROW["flat"])


def render_evening(closed, greenhouse_name: str, date: str) -> str:
    L = []
    L.append("╔" + "═" * _W + "╗")
    L.append("║" + f"  EVENING REVIEW — {greenhouse_name}".ljust(_W) + "║")
    L.append("║" + f"  {date}".ljust(_W) + "║")
    L.append("╚" + "═" * _W + "╝")
    L.append("")
    if not closed:
        L.append("  Nothing came due to review today.")
        return "\n".join(L)

    counts = {"improved": 0, "unchanged": 0, "worse": 0, "unknown": 0}
    for e in closed:
        counts[e.outcome] = counts.get(e.outcome, 0) + 1
        L.append(_box_top(f"{e.zone}  ·  {_TAG.get(e.kind, e.kind)}"))
        L.append(f"  Morning expectation : {e.expected_outcome}")
        L.append(f"                        (confidence {e.confidence_before})")
        L.append(f"  Action taken        : {e.action}")
        L.append(f"  Observed outcome    : {e.outcome.upper()}" + (f" — {e.outcome_note}" if e.outcome_note else ""))
        L.append(f"  Lesson              : {e.lesson}")
        L.append(f"  Confidence          : {e.confidence_before} {_move(e.confidence_before, e.confidence_after)} {e.confidence_after}")
        L.append("")

    held = counts["improved"]
    L.append(_rule())
    L.append(f"  Reviewed {len(closed)}: {counts['improved']} improved · {counts['unchanged']} unchanged · "
             f"{counts['worse']} worse · {counts['unknown']} unknown")
    L.append(f"  Predictions that held: {held}/{len(closed)}.  Each is now a memory; "
             f"tomorrow's advice is a little wiser for it.")
    return "\n".join(L)

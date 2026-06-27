"""Gaia Memory v1 — the first real Memory Engine.

Gaia must remember yesterday. Each day becomes ONE permanent Day Memory holding the whole
day: the morning snapshot, the brief, the recommendations, the actions, the walk
observations, the evening review, the outcomes, and the lessons.

It is **append-only**. A committed day is never overwritten — the journal only grows. Every
recommendation stays linked to its outcome forever by its experiment id. Optimised for
truth, not performance: it is a plain JSON-lines journal that is read in full and never
mutated.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict, field
from datetime import datetime, date as _date
from typing import List, Optional

from . import store

_MEM_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "memory")
_JOURNAL = os.path.join(_MEM_DIR, "journal.jsonl")


@dataclass
class DayMemory:
    date: str
    greenhouse: str
    committed_at: str
    snapshot: dict                  # the morning snapshot (meta + key signals + coverage)
    brief: dict                     # the morning brief (summary + priorities)
    recommendations: List[dict]     # every recommendation, with its outcome link (experiment id)
    walk_observations: List[dict]   # what the grower reported on the walk
    evening_review: List[dict]      # the recommendations closed today, with outcomes
    lessons: List[str]              # what was learned today
    outcomes: dict                  # counts: improved / unchanged / worse / unknown / open


# --- writing (append-only) ---------------------------------------------------

def _all() -> List[dict]:
    if not os.path.exists(_JOURNAL):
        return []
    out = []
    with open(_JOURNAL, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def _exp_dict(e) -> dict:
    return asdict(e)


def commit_day(date: str, greenhouse: str) -> Optional[DayMemory]:
    """Assemble today's permanent memory from the day's records and append it. Never
    overwrites: if this date is already remembered, it is left exactly as it was."""
    if any(d["date"] == date for d in _all()):
        return None  # already committed — memory is immutable

    analysis = store.load()
    snap = store.load_today_snapshot() or {}

    closed = [m for m in store.load_memories() if m.get("opened_on") == date]
    still_open = [_exp_dict(e) for e in store.load_open_experiments() if e.opened_on == date]
    recommendations = closed + still_open
    walk = [a for a in store.load_answers() if a.get("captured_on") == date]
    closed_today = [m for m in closed if m.get("closed_on") == date]
    lessons = [m["lesson"] for m in closed if m.get("lesson")]

    outcomes = {"improved": 0, "unchanged": 0, "worse": 0, "unknown": 0, "open": 0}
    for r in recommendations:
        outcomes[r.get("outcome") or "open"] = outcomes.get(r.get("outcome") or "open", 0) + 1

    brief = {
        "summary": getattr(analysis, "summary", ""),
        "priorities": [{"zone": c.zone_name, "kind": c.kind, "action": c.action}
                       for c in getattr(analysis, "priorities", [])],
    }

    day = DayMemory(
        date=date, greenhouse=greenhouse,
        committed_at=datetime.now().isoformat(timespec="seconds"),
        snapshot=snap, brief=brief, recommendations=recommendations,
        walk_observations=walk, evening_review=closed_today,
        lessons=lessons, outcomes=outcomes,
    )
    os.makedirs(_MEM_DIR, exist_ok=True)
    with open(_JOURNAL, "a", encoding="utf-8") as f:   # append-only
        f.write(json.dumps(asdict(day), ensure_ascii=False) + "\n")
    return day


# --- reading / questions -----------------------------------------------------

def all_days() -> List[dict]:
    return sorted(_all(), key=lambda d: d["date"])


def latest() -> Optional[dict]:
    days = all_days()
    return days[-1] if days else None


def on_date(d: str) -> Optional[dict]:
    for day in all_days():
        if day["date"] == d:
            return day
    return None


def _weekday(d: str) -> str:
    try:
        return _date.fromisoformat(d).strftime("%A").lower()
    except ValueError:
        return ""


def last_weekday(name: str) -> Optional[dict]:
    name = name.lower()
    for day in reversed(all_days()):
        if _weekday(day["date"]) == name:
            return day
    return None


def humidity_exceeded(threshold: float) -> List[dict]:
    hits = []
    for day in all_days():
        zones = (day.get("snapshot", {}).get("signals", {}) or {}).get("zones", {})
        worst = max((z.get("hum", 0) for z in zones.values()), default=0)
        if worst > threshold:
            hits.append((day, worst))
    return [{"date": d["date"], "worst_humidity": w, "day": d} for d, w in hits]


def decisions_of_kind(kind: str, since: Optional[str] = None) -> List[dict]:
    out = []
    for day in all_days():
        if since and day["date"] < since:
            continue
        for r in day.get("recommendations", []):
            if r.get("kind") == kind:
                out.append({"date": day["date"], **r})
    return out


def learnings() -> List[dict]:
    """What Gaia has learned — aggregated from memory, per situation + decision type."""
    cells = {}
    for day in all_days():
        for r in day.get("recommendations", []):
            key = (r.get("zone", "?"), r.get("kind", "?"))
            c = cells.setdefault(key, {"zone": r.get("zone"), "kind": r.get("kind"),
                                       "tried": 0, "improved": 0, "unchanged": 0, "worse": 0,
                                       "unknown": 0, "open": 0, "first_conf": None,
                                       "last_conf": None, "lessons": []})
            c["tried"] += 1
            c[r.get("outcome") or "open"] = c.get(r.get("outcome") or "open", 0) + 1
            if c["first_conf"] is None:
                c["first_conf"] = r.get("confidence_before")
            if r.get("confidence_after"):
                c["last_conf"] = r.get("confidence_after")
            if r.get("lesson") and r["lesson"] not in c["lessons"]:
                c["lessons"].append(r["lesson"])
    return list(cells.values())

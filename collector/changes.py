"""Detect what changed since the previous snapshot — in the data, never in meaning.

A transparent observation-level diff of the new snapshot against the previous latest.json:
values that appeared, disappeared, or changed (per subject+kind), plus alarms raised/cleared
and coverage shifts. It states *what* changed; it never says what a change *implies* — that
leap is the Brain's, downstream. On the first ever run there is nothing to compare to, and
that is said plainly, not treated as an error.
"""
from __future__ import annotations

from typing import Dict, List, Optional


def _present_values(snap: dict) -> Dict[str, object]:
    """{ 'subject|kind': value } for every observation that actually has a value."""
    out: Dict[str, object] = {}
    for o in snap.get("observations") or []:
        if not isinstance(o, dict):
            continue
        subject, kind = o.get("subject"), o.get("kind")
        if not subject or not kind:
            continue
        if o.get("value") is not None and not o.get("absence"):
            out[f"{subject}|{kind}"] = o.get("value")
    return out


def _fmt(v) -> str:
    return f"{v:g}" if isinstance(v, (int, float)) else str(v)


def detect_changes(prev: Optional[dict], curr: dict) -> dict:
    """Return {first_run, lines, counts}. `lines` are human-readable; `counts` are for logs."""
    if not prev:
        return {"first_run": True,
                "lines": ["first collection — nothing to compare against yet"],
                "counts": {"appeared": 0, "disappeared": 0, "changed": 0}}

    pv, cv = _present_values(prev), _present_values(curr)
    lines: List[str] = []
    appeared = sorted(set(cv) - set(pv))
    disappeared = sorted(set(pv) - set(cv))
    changed = sorted(k for k in (set(pv) & set(cv)) if pv[k] != cv[k])

    for k in changed:
        subject, kind = k.split("|", 1)
        if kind == "alarm":
            lines.append(f"{subject}: alarm changed — {_fmt(pv[k])} → {_fmt(cv[k])}")
        else:
            lines.append(f"{subject}: {kind} {_fmt(pv[k])} → {_fmt(cv[k])}")
    for k in appeared:
        subject, kind = k.split("|", 1)
        lines.append(f"{subject}: {kind} now observed ({_fmt(cv[k])})"
                     + (" — ALARM raised" if kind == "alarm" else ""))
    for k in disappeared:
        subject, kind = k.split("|", 1)
        lines.append(f"{subject}: {kind} no longer observed"
                     + (" — alarm cleared" if kind == "alarm" else ""))

    # Coverage shifts (what we stopped/started being able to see).
    prev_na = set(prev.get("coverage", {}).get("not_observed") or [])
    curr_na = set(curr.get("coverage", {}).get("not_observed") or [])
    for slot in sorted(curr_na - prev_na):
        lines.append(f"coverage: newly un-observed — {slot}")
    for slot in sorted(prev_na - curr_na):
        lines.append(f"coverage: now observed — {slot}")

    if not lines:
        lines.append("no notable changes since the previous snapshot")

    return {"first_run": False, "lines": lines,
            "counts": {"appeared": len(appeared), "disappeared": len(disappeared),
                       "changed": len(changed)}}

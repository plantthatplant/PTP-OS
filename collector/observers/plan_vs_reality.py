"""Plan vs reality — turn a plan/observation conflict into a Knowledge Gap.

When the Business Knowledge Observer's *intention* (expected-/planned-) disagrees with what is
*observed* (Synopta, the grower, cameras), this raises a question — it NEVER overwrites reality.
Reality always wins; the deviation is valuable precisely because it is a question worth asking.

This is a mechanical comparison (numbers, dates, categories) — NOT biological reasoning. It
decides nothing about plants; it only notices that a plan and an observation diverge and asks.
"""
from __future__ import annotations

from typing import List, Optional

_PLAN_PREFIXES = ("expected-", "planned-")
_REALITY_PREFIXES = ("observed-", "measured-")
_REL_TOL = 0.10   # numbers within 10% are "as planned"; beyond that, ask


def _base(kind: str) -> str:
    k = kind or ""
    for p in _PLAN_PREFIXES + _REALITY_PREFIXES:
        if k.startswith(p):
            return k[len(p):]
    return k


def _num(v):
    try:
        return float(str(v).replace("%", "").replace(",", ".").strip())
    except (TypeError, ValueError):
        return None


def _has_value(o) -> bool:
    return o.get("value") is not None and not o.get("absence")


def _gap(subject, base, planned, observed, plan_src, reality_src, reason) -> dict:
    return {
        "kind": "knowledge-gap", "subject": subject, "topic": base,
        "text": (f"{subject}: planned {base.replace('-', ' ')} ({planned}) differs from "
                 f"observed ({observed}) — which is right?"),
        "planned": planned, "observed": observed, "reason": reason,
        "plan_source": plan_src, "reality_source": reality_src,
    }


def compare(plan_obs: List[dict], reality_obs: List[dict], now_iso: Optional[str] = None) -> List[dict]:
    """Return Knowledge-Gap questions where plan and reality diverge. Inputs are never mutated;
    reality is never overwritten."""
    gaps: List[dict] = []

    # Index reality by (subject, base-kind) — the last observed value wins.
    reality = {}
    for o in reality_obs:
        if _has_value(o):
            reality[(o.get("subject"), _base(o.get("kind", "")))] = o

    for p in plan_obs:
        kind = p.get("kind", "")
        if not kind.startswith(_PLAN_PREFIXES) or not _has_value(p):
            continue
        base = _base(kind)
        subject = p.get("subject")

        # 1) overlapping fact: plan vs observed of the same (subject, base)
        r = reality.get((subject, base))
        if r is not None:
            pv, rv = p["value"], r["value"]
            pn, rn = _num(pv), _num(rv)
            deviates = (abs(pn - rn) > _REL_TOL * max(abs(rn), 1e-9)) if (pn is not None and rn is not None) \
                else (str(pv).strip().lower() != str(rv).strip().lower())
            if deviates:
                gaps.append(_gap(subject, base, pv, rv, p.get("source"), r.get("source"),
                                 "plan and observation diverge"))

        # 2) expected harvest/shipment date that has already passed → ask if it happened
        if base in ("harvest-date", "shipment-date") and now_iso:
            if str(p["value"]) < now_iso[:10]:
                gaps.append({
                    "kind": "knowledge-gap", "subject": subject, "topic": base,
                    "text": (f"{subject}: the planned {base.replace('-', ' ')} ({p['value']}) has "
                             f"passed — did it happen, or is the schedule slipping?"),
                    "planned": p["value"], "observed": f"today is {now_iso[:10]}",
                    "reason": "expected date appears unrealistic", "plan_source": p.get("source"),
                    "reality_source": "clock",
                })
    return gaps

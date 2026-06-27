"""Knowledge Fusion — make Gaia speak with one voice.

NOT a new AI and NOT new reasoning. A synthesis layer: it takes what the engines and observers
already produced — the Morning Analysis (reality reasoning), plan/intention observations, plan-
vs-reality gaps, memory, overnight changes, and the day's worth-asking questions — and merges
them into ONE coherent understanding. It resolves which thing matters most, weaves reality +
intention + memory into single thoughts, and prepares one priority, one explanation, one
question. It never invents, and it keeps provenance internally (so the grower hears one mind,
not 'Synopta says… the spreadsheet says…').

It answers, naturally: what is happening · what was supposed to happen · what changed · what
worries me · what can wait · what to do first · what to observe · what to ask · what I learned
yesterday that matters today.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


def _short(name: str) -> str:
    return re.sub(r"\s*\(.*?\)\s*", "", name or "").strip() or (name or "")


def _zone_label(subject: str) -> str:
    """Speak in one voice: 'h2' -> 'House 2', 'site' -> 'the site', 'crop:Dahlia' -> 'Dahlia'."""
    s = str(subject or "").strip()
    m = re.fullmatch(r"[hH](\d+)", s)
    if m:
        return f"House {m.group(1)}"
    if s == "site":
        return "the site"
    if s.startswith("crop:"):
        return s[5:]
    return _short(s)


@dataclass
class UnifiedBrief:
    headline: str                       # one glanceable line
    narrative: str                      # the "one thought" — merged, not source-by-source
    whats_happening: str
    what_was_planned: str
    what_changed: str
    what_worries: str
    what_can_wait: str
    do_first: str
    observe_today: str
    ask_today: str
    learned_yesterday: str
    one_priority: str
    one_explanation: str
    one_recommendation: str
    confidence: str
    provenance: Dict[str, List[str]] = field(default_factory=dict)   # INTERNAL only


def _plan_for(plan_obs, subject_id, kinds):
    return [o for o in (plan_obs or [])
            if o.get("subject") == subject_id and o.get("kind") in kinds and o.get("value") is not None]


def _gap_for(plan_gaps, subject_id):
    return next((g for g in (plan_gaps or []) if g.get("subject") == subject_id), None)


def _memory_for(memories, zone_name):
    z = _short(zone_name).lower()
    for m in reversed(memories or []):
        if z and z in str(m.get("zone", "")).lower() and m.get("lesson"):
            return m
    return None


def _planned_phrase(plan_obs, zone_id):
    harvest = _plan_for(plan_obs, zone_id, {"expected-harvest"})
    date = _plan_for(plan_obs, zone_id, {"expected-harvest-date"})
    occ = _plan_for(plan_obs, zone_id, {"expected-occupancy"})
    if harvest and date:
        return f"the plan expected {harvest[0]['value']} around {date[0]['value']}"
    if harvest:
        return f"the plan expected {harvest[0]['value']}"
    if occ:
        return f"the plan expected this house about {occ[0]['value']}% full"
    return ""


def synthesize(analysis, *, coverage=None, reality=None, plan_obs=None, plan_gaps=None,
               memories=None, changes=None, questions=None) -> UnifiedBrief:
    prov: Dict[str, List[str]] = {}

    def note(src, what):
        prov.setdefault(src, []).append(what)

    concerns = list(analysis.concerns or [])
    priorities = list(analysis.priorities or [])
    gh = _short(analysis.greenhouse_name)

    # Lead with the single most important thing: a *critical* reality concern; else a plan
    # deviation (schedule/occupancy slip); else the top concern/priority; else settled.
    critical = next((c for c in concerns if getattr(c, "value", "") == "Critical"), None)
    lead = critical or (concerns[0] if concerns else (priorities[0] if priorities else None))
    planned_lead = ""

    if lead is None and plan_gaps:                       # ---- plan-led morning ----
        g = plan_gaps[0]
        subj = _zone_label(g.get("subject", "the greenhouse"))
        note("business knowledge (Google Drive)", f"{subj}: {g.get('reason')}")
        note("reality (Synopta + reasoning)", f"{subj}: observed differs from plan")
        clause = g["text"].split("—")[0].strip()
        clause = re.sub(r"^" + re.escape(str(g.get("subject", ""))) + r":\s*", "", clause).strip()
        s = [f"{subj} is behind plan — {clause.lower()}."]
        mem = _memory_for(memories, subj)
        if mem:
            s.append(f"Yesterday's record supports this — {mem['lesson'].split('.')[0].lower()}.")
            note("memory", f"{subj}: prior lesson")
        elif changes:
            s.append(f"Overnight, {changes[0].lower()}.")
        s.append("The schedule looks at risk; reality has not met the plan.")
        narrative = " ".join(s)
        whats = f"{subj}: observed differs from the plan ({g.get('reason')})"
        planned_lead = f"{subj}: {g.get('planned')}"
        worries = f"{subj}: schedule slip"
        do_first = f"{subj} — confirm the real state, then re-plan if needed"
        one_expl, one_rec = g["text"], "reconcile plan with reality (never change the crop on the plan's word)"
        headline = f"{gh}: {subj} behind plan"

    elif lead is not None:                               # ---- concern/priority-led morning ----
        zone_id, zone = lead.zone_id, _short(lead.zone_name)
        note("reality (Synopta + reasoning)", f"{zone}: {lead.title}")
        planned_lead = _planned_phrase(plan_obs, zone_id)
        gap = _gap_for(plan_gaps, zone_id)
        mem = _memory_for(memories, zone)
        s = [f"{zone} {lead.title[0].lower()}{lead.title[1:]}."]
        if planned_lead:
            s.append(f"Meanwhile {planned_lead}.")
            note("business knowledge (Google Drive)", f"{zone}: plan context")
        elif gap:
            s.append(gap["text"].split("—")[0].strip() + ".")
            note("business knowledge (Google Drive)", f"{zone}: plan deviation")
        if mem:
            s.append(f"Yesterday's record supports this — {mem['lesson'].split('.')[0].lower()}.")
            note("memory", f"{zone}: prior lesson")
        elif changes:
            s.append(f"Overnight, {changes[0].lower()}.")
            note("overnight change", changes[0])
        s.append(lead.why.split(";")[0].strip().capitalize() + ".")
        narrative = " ".join(s)
        whats = f"{zone}: {lead.title} — {lead.why.split(';')[0].strip()}"
        worries = f"{zone}: {lead.title} (confidence {getattr(lead, 'confidence', '—').lower()})"
        do_first = f"{zone} — {getattr(lead, 'action', lead.title)}"
        one_expl, one_rec = lead.why, getattr(lead, "action", lead.title)
        headline = f"{gh}: {('watch ' + zone) if concerns else zone}"

    else:                                                # ---- settled morning ----
        narrative = f"{gh} is on plan and settled this morning — nothing needs you first."
        whats, worries = analysis.summary, "nothing pressing"
        do_first = "no single action stands out — walk and observe"
        one_expl, one_rec = analysis.confidence_rationale, "stay the course; re-observe"
        headline = f"{gh}: settled"
        note("reality (Synopta + reasoning)", "no critical concern")

    # --- shared tail (the rest of the one understanding) --------------------
    revenue = next((o for o in (plan_obs or []) if o.get("kind") == "expected-revenue"), None)
    what_was_planned = planned_lead or (
        f"annual revenue ~{int(revenue['value']):,} kr".replace(",", " ") if revenue
        else "no specific plan on file for today")
    if revenue and not planned_lead:
        note("business knowledge (Google Drive)", "expected revenue")

    what_changed = changes[0] if changes else "nothing notable overnight"
    if changes:
        note("overnight change", changes[0])

    rest = concerns[1:] + [p for p in priorities if p not in concerns]
    what_can_wait = ("; ".join(f"{_short(c.zone_name)}: {c.title}" for c in rest[:2])
                     if rest else "everything else is steady")

    qs = sorted(list(questions or []), key=lambda q: -getattr(q, "voi", 0))
    if qs:
        ask_today = qs[0].text
        observe_today = f"{_short(qs[0].subject)}: {qs[0].biological_reason}"
        note("knowledge gap", f"ask about {_short(qs[0].subject)}")
    elif plan_gaps:
        ask_today, observe_today = plan_gaps[0]["text"], "reconcile plan with reality"
    else:
        ask_today, observe_today = "nothing worth interrupting you for", "nothing beyond the normal walk"

    last_mem = next((m for m in reversed(memories or []) if m.get("lesson")), None)
    learned_yesterday = (last_mem["lesson"].split(".")[0] + "." if last_mem
                         else "no closed experiments yet — learning starts as the loop runs")
    if last_mem:
        note("memory", "yesterday's lesson")

    return UnifiedBrief(
        headline=headline, narrative=narrative, whats_happening=whats,
        what_was_planned=what_was_planned, what_changed=what_changed, what_worries=worries,
        what_can_wait=what_can_wait, do_first=do_first, observe_today=observe_today,
        ask_today=ask_today, learned_yesterday=learned_yesterday,
        one_priority=do_first, one_explanation=one_expl, one_recommendation=one_rec,
        confidence=analysis.confidence_level, provenance=prov)

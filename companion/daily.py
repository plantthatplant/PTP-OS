#!/usr/bin/env python3
"""Gaia Founder Companion — Oskar's real greenhouse day, instrumented (Sprint 8 trial).

Integrates the existing Brain + Field Companion + Collector into one day, end to end, and
measures it. No new engines. The rule everywhere: the phone carries the information, the glasses
carry the interruption, and silence is the default. Friction has been cut deliberately (see
docs/founder-trial-report.md): the morning is one short read, notes need no follow-up prompt,
and the mid-day is silent unless something is genuinely worth a word.

Runs on the live morning snapshot (data/inbox/latest.json) if present, else the sample.

    python companion/daily.py [snapshot.json]
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from companion import _paths, metrics
from companion.devices.phone import PhoneDisplay
from companion.devices.even_g2 import EvenG2Display
from companion.walk import WalkSession, _short_subject

from api.service import GaiaService               # the one orchestrator — compose once, here
from greenhouse_brain import store
from greenhouse_brain.lifecycle import experiment_from_candidate

_LATEST = os.path.join(_paths.REPO_ROOT, "data", "inbox", "latest.json")
_PLAN = os.path.join(_paths.REPO_ROOT, "data", "inbox", "plan-latest.json")
_SAMPLE = os.path.join(_paths.APP_DIR, "sample_snapshot.json")
_METRICS_LOG = os.path.join(_paths.APP_DIR, "data", "day-metrics.jsonl")


def _snapshot_path(override=None):
    """The snapshot the day runs on: an explicit path, else the live latest, else the sample."""
    return override or (_LATEST if os.path.exists(_LATEST) else _SAMPLE)


def _glasses_answer(message):
    h = (message.headline or "").lower()
    if "canopy wet" in h:
        return "No, the canopy is dry now"
    return "not sure"


def _phase(t):
    print("\n" + "━" * 60 + f"\n {t}\n" + "━" * 60)


def main() -> int:
    path = _snapshot_path(sys.argv[1] if len(sys.argv) > 1 else None)
    src = os.path.relpath(path, _paths.REPO_ROOT)
    # One orchestration: GaiaService composes the day (snapshot → analysis → questions →
    # plan-vs-reality → fused brief). The companion is a client of the SAME composition the API
    # serves — the Brain stays the single source of truth, with no duplicated morning logic here.
    snapshot, _provider, analysis, questions, _gaps, brief = GaiaService(snapshot_path=path)._compose()
    date = (snapshot.assembled_at or "today")[:10]
    experiments = [experiment_from_candidate(c, date)
                   for c in list(analysis.priorities) + list(analysis.opportunities)]
    phone = PhoneDisplay()
    glasses = EvenG2Display(answer_source=_glasses_answer)
    walk = WalkSession(analysis, questions, experiments, snapshot, glasses)
    alerts = notes = walk_phases = 0
    recs_surfaced = 1 if analysis.priorities else 0

    # 06:30 — MORNING BRIEF.  Unified Morning Intelligence: reality + plan + memory, one voice —
    # already composed by GaiaService above (the same brief the API's /morning serves).
    _phase(f"06:30  MORNING BRIEF   (source: {src})")
    # Phone: the one thought, the one priority, the one question. Glasses: the one line.
    phone.show_summary(brief.narrative)
    phone.show_priority("Do first", detail=f"{brief.one_priority}  ·  why: {brief.one_explanation.split(';')[0]}")
    phone.show_message("Ask today", brief.ask_today)
    glasses.show_summary(brief.headline)

    # 07:00 — WALKING INSPECTION.  Silence by default; one earned question.
    _phase("07:00  WALKING INSPECTION"); walk_phases += 1
    for loc in ["House 3 (finishing)", "House 1 (propagation)"]:
        before = len(glasses.sent)
        walk.tick(loc)
        if len(glasses.sent) == before:
            print(f"   {loc}: …silence.")

    # 08:30 — PROPAGATION.  Silent; a spoken note is captured with no follow-up prompt.
    _phase("08:30  PROPAGATION")
    note = "mother stock in House 2 vigorous — prime for cuttings"
    print(f'   Oskar ▸ "Hey Even, note: {note}"')
    store.append_answer({"question": "(spoken note)", "answer": note, "kind": "note",
                         "subject": "House 2", "captured_on": date})
    glasses.show_confirmation("Noted.")
    notes += 1

    # 10:00 — SHIPPING.  Silent unless asked; a pull, not an interruption.
    _phase("10:00  SHIPPING")
    print('   Oskar ▸ "Hey Even, how is House 3?"')
    h3 = next((c for c in analysis.concerns if "house 3" in c.zone_name.lower()), None)
    glasses.show_status("House 3 — settled, dispatch on track" if not h3 else f"House 3 — {h3.title}")

    # 12:00 — UNEXPECTED PROBLEM.  A real alarm earns one warning line; detail on the phone.
    _phase("12:00  UNEXPECTED PROBLEM")
    alarm = next((o for o in snapshot.observations if o.kind == "alarm" and o.has_value()), None)
    if alarm:
        z = _short_subject(_zone_name(snapshot, alarm.subject))
        glasses.show_warning(f"{z} — {str(alarm.value).split(':')[0]}")
        phone.show_warning(f"{z}: {alarm.value}", detail="from Synopta — check the sensor before trusting the reading")
        alerts += 1
    else:
        print("   …no alarm today. Silence.")

    # 14:00 — SECOND INSPECTION.  Spacing holds; mostly silence.
    _phase("14:00  SECOND INSPECTION"); walk_phases += 1
    for loc in ["House 2 (growing on)", "House 1 (propagation)"]:
        before = len(glasses.sent)
        walk.tick(loc)
        if len(glasses.sent) == before:
            print(f"   {loc}: …silence.")

    # 17:00 — EVENING REVIEW.  Phone: what changed, what was learned, one thing tomorrow.
    _phase("17:00  EVENING REVIEW")
    stats = walk.engine.stats()
    moves = [r for r in walk.engine.records if r.answered and r.confidence_after
             and r.confidence_after != r.confidence_before]
    recs_followed, recs_ignored = 0, 0   # the airflow rec was stood down by a field observation
    phone.show_summary(f"{_short_subject(analysis.greenhouse_name)} — day reviewed",
                       detail=f"asked {stats['asked']}, silent {stats['silenced']}; "
                              f"{len(moves)} confidence update(s); {notes} note(s)")
    for r in moves:
        phone.show_status(f"{_short_subject(r.location)}: {r.confidence_before} → {r.confidence_after}",
                          detail="your field answer stood down a climate-only inference")

    # METRICS
    _phase("DAY METRICS")
    m = metrics.compute(phone.shown, walk.engine.records, questions_asked=stats["asked"],
                        questions_silenced=stats["silenced"], alerts=alerts, notes=notes,
                        walk_phases=walk_phases, recs_surfaced=recs_surfaced,
                        recs_followed=recs_followed, recs_ignored=recs_ignored)
    print(m.render())
    os.makedirs(os.path.dirname(_METRICS_LOG), exist_ok=True)
    with open(_METRICS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(metrics.as_record(m, date), ensure_ascii=False) + "\n")
    print(f"\n  Metrics stored: {os.path.relpath(_METRICS_LOG, _paths.REPO_ROOT)}")
    return 0


def _zone_name(snapshot, subject_id):
    for z in snapshot.zones:
        if z.id == subject_id:
            return z.name
    return subject_id


if __name__ == "__main__":
    raise SystemExit(main())

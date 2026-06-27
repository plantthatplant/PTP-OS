#!/usr/bin/env python3
"""Gaia Founder Companion — Oskar's day, end to end (Sprint 7 MVP).

Composes the existing Brain + Field Companion into the five things that earn daily use:
morning brief, a silent walk with one earned question, a spoken note, an alarm if real, and an
evening review. Two surfaces, routed by the simple rule from the MVP doc:
**the phone carries the information; the glasses carry the interruption.**

Runs on the real morning snapshot if present (data/inbox/latest.json from the Collector /
screen-read), else the bundled sample. No new architecture, no biology here — it only relays,
times, and records what the Brain produced.

    python companion/daily.py
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from companion import _paths
from companion.devices.phone import PhoneDisplay
from companion.devices.even_g2 import EvenG2Display
from companion.walk import WalkSession, _short_subject

from greenhouse_brain.snapshot_importer import import_snapshot
from greenhouse_brain.providers.snapshot_provider import SnapshotProvider
from greenhouse_brain.morning_analysis import MorningAnalysisEngine
from greenhouse_brain import knowledge_gap, store
from greenhouse_brain.lifecycle import experiment_from_candidate

_LATEST = os.path.join(_paths.REPO_ROOT, "data", "inbox", "latest.json")
_SAMPLE = os.path.join(_paths.APP_DIR, "sample_snapshot.json")


def _load_snapshot(override: str = None):
    # Default: the live morning snapshot (Collector / screen-read), else the bundled sample.
    # An explicit path may be passed (e.g. to demo the full experience on richer data).
    path = override or (_LATEST if os.path.exists(_LATEST) else _SAMPLE)
    with open(path, "r", encoding="utf-8") as f:
        return import_snapshot(json.load(f)), os.path.relpath(path, _paths.REPO_ROOT)


def _glasses_answer(message):
    h = (message.headline or "").lower()
    if "canopy wet" in h:
        return "No, the canopy is dry now"
    if "did it help" in h:
        return "better"
    return "not sure"


def _hdr(t):
    print("\n" + "━" * 62 + f"\n {t}\n" + "━" * 62)


def main() -> int:
    override = sys.argv[1] if len(sys.argv) > 1 else None
    snapshot, src = _load_snapshot(override)
    date = (snapshot.assembled_at or "today")[:10]
    provider = SnapshotProvider(snapshot)
    analysis = MorningAnalysisEngine().run(provider)
    experiments = [experiment_from_candidate(c, date)
                   for c in list(analysis.priorities) + list(analysis.opportunities)]
    questions, held = knowledge_gap.generate(analysis, [], snapshot.assembled_at, date,
                                             store.prior_worth_by_kind())
    cov, real = snapshot.coverage(), snapshot.reality_confidence()

    phone = PhoneDisplay()
    glasses = EvenG2Display(answer_source=_glasses_answer)
    walk = WalkSession(analysis, questions, experiments, snapshot, glasses)

    # ── MORNING ── the information goes to the phone; one headline to the glasses ──
    _hdr(f"MORNING · phone  (source: {src}, reality confidence {real['label']})")
    phone.show_summary(f"{analysis.greenhouse_name} — {analysis.summary}")
    if analysis.priorities:
        p = analysis.priorities[0]
        phone.show_priority(f"{_short_subject(p.zone_name)} — {p.title}",
                            detail=(f"{p.action}  ·  why: {p.why}  ·  if ignored: {p.if_ignored}  "
                                    f"·  confidence {p.confidence}, effort {p.effort}, {p.window}"))
    phone.show_status(f"Overall confidence: {analysis.confidence_level}",
                      detail=f"{analysis.confidence_rationale}  ·  coverage {cov['coverage_pct']}%")
    for q in questions:
        phone.show_message("On the walk I may ask", q.text)

    _hdr("MORNING · glasses  (one headline)")
    walk.start()

    # ── WALK ── glasses only; silence by default, one earned question, a spoken note ──
    for loc in ["House 3 (finishing)", "House 1 (propagation)"]:
        _hdr(f"WALK · {loc}")
        before = len(glasses.sent)
        walk.tick(loc)
        if len(glasses.sent) == before:
            print("   …silence.")

    _hdr("WALK · Oskar speaks a note")
    note = "brown spots, lower leaves, bench 3"
    print(f'   Oskar ▸ "Hey Even, note: {note}"')
    store.append_answer({"question": "(spoken note)", "answer": note, "kind": "note",
                         "subject": "House 1", "captured_on": date})
    glasses.show_confirmation("Noted. Photo? (phone)")

    for loc in ["House 2 (growing on)", "House 3 (finishing)"]:
        _hdr(f"WALK · {loc}")
        before = len(glasses.sent)
        walk.tick(loc)
        if len(glasses.sent) == before:
            print("   …silence.")

    # ── EVENING ── back to the phone: what changed, what was learned, one thing tomorrow ──
    stats = walk.engine.stats()
    moves = [r for r in walk.engine.records if r.answered and r.confidence_after
             and r.confidence_after != r.confidence_before]
    _hdr("EVENING · phone")
    phone.show_summary(f"{analysis.greenhouse_name} — day reviewed",
                       detail=f"asked {stats['asked']}, stayed silent {stats['silenced']}; "
                              f"{len(moves)} confidence update(s); 1 note captured")
    for r in moves:
        phone.show_status(f"{_short_subject(r.location)}: {r.confidence_before} → {r.confidence_after}",
                          detail="updated from your answer on the walk")
    tomorrow = held[0].text if held else "nothing outstanding"
    phone.show_message("One thing to confirm tomorrow", tomorrow)

    _hdr("EVENING · glasses  (closing line)")
    glasses.show_summary(f"Day reviewed — {len(moves)} update, 1 to confirm")

    print("\n" + "─" * 62)
    print("  The phone carried the information; the glasses carried the interruption.")
    print("  Interactions stored to memory:", os.path.relpath(store._INTERACTIONS_FILE, _paths.REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

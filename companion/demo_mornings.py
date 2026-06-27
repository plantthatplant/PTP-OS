#!/usr/bin/env python3
"""Three greenhouse mornings — before (source-by-source) vs after (one mind).

Shows how Knowledge Fusion turns several systems' outputs into one understanding, on three
realistic mornings: a normal day, a delayed-production day, and a disease-risk day.

    python companion/demo_mornings.py
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from companion import _paths  # noqa: F401
from greenhouse_brain.snapshot_importer import import_snapshot
from greenhouse_brain.providers.snapshot_provider import SnapshotProvider
from greenhouse_brain.morning_analysis import MorningAnalysisEngine
from greenhouse_brain import knowledge_gap, fusion

_SAMPLE = os.path.join(_paths.APP_DIR, "sample_snapshot.json")


def _calm_snapshot(assembled="2026-06-27T05:50:00Z"):
    return import_snapshot({
        "greenhouse_id": "gh-kalaberga", "greenhouse_name": "Kålaberga",
        "assembled_at": assembled,
        "provenance": [{"source": "synopta", "method": "measured"}],
        "coverage": {"not_observed": []},
        "structure": {"zones": [
            {"id": "h1", "name": "House 1 (propagation)", "stage": "propagation"},
            {"id": "h2", "name": "House 2 (growing on)", "stage": "vegetative"},
            {"id": "h3", "name": "House 3 (finishing)", "stage": "finishing"}]},
        "observations": [
            {"subject": "h1", "kind": "air-temperature", "value": 24, "unit": "°C",
             "captured_at": assembled, "source": "synopta", "method": "measured", "confidence": "high"},
            {"subject": "h1", "kind": "relative-humidity", "value": 78, "unit": "%RH",
             "captured_at": assembled, "source": "synopta", "method": "measured", "confidence": "high"},
            {"subject": "h1", "kind": "vent-position", "value": "open", "captured_at": assembled,
             "source": "synopta", "method": "measured", "confidence": "high"},
            {"subject": "h2", "kind": "air-temperature", "value": 22, "unit": "°C",
             "captured_at": assembled, "source": "synopta", "method": "measured", "confidence": "high"},
            {"subject": "h2", "kind": "relative-humidity", "value": 68, "unit": "%RH",
             "captured_at": assembled, "source": "synopta", "method": "measured", "confidence": "high"},
            {"subject": "h2", "kind": "vent-position", "value": "20%", "captured_at": assembled,
             "source": "synopta", "method": "measured", "confidence": "high"},
            {"subject": "h3", "kind": "air-temperature", "value": 20, "unit": "°C",
             "captured_at": assembled, "source": "synopta", "method": "measured", "confidence": "high"},
            {"subject": "h3", "kind": "relative-humidity", "value": 62, "unit": "%RH",
             "captured_at": assembled, "source": "synopta", "method": "measured", "confidence": "high"},
            {"subject": "h3", "kind": "vent-position", "value": "30%", "captured_at": assembled,
             "source": "synopta", "method": "measured", "confidence": "high"}]})


def _analyse(snapshot):
    provider = SnapshotProvider(snapshot)
    analysis = MorningAnalysisEngine().run(provider)
    date = (snapshot.assembled_at or "today")[:10]
    questions, _ = knowledge_gap.generate(analysis, [], snapshot.assembled_at, date, {})
    return analysis, questions


def _before(title, analysis, plan_obs, plan_gaps, memories, questions):
    print(f"\n  BEFORE — source by source (the disconnected feeling):")
    c = analysis.concerns[0] if analysis.concerns else None
    print(f"    Synopta says:        {c.title + ' in ' + c.zone_name if c else 'climate within range'}")
    if plan_obs:
        po = plan_obs[0]
        print(f"    Spreadsheet says:    {po['subject']}: {po['kind']} = {po['value']}")
    if plan_gaps:
        print(f"    Plan check says:     {plan_gaps[0]['text']}")
    if memories:
        print(f"    Memory says:         {memories[0]['lesson']}")
    if questions:
        print(f"    Knowledge Gap says:  {questions[0].text}")


def _after(brief):
    print(f"\n  AFTER — one mind (Knowledge Fusion):")
    print(f"    “{brief.narrative}”")
    print(f"    · do first:   {brief.do_first}")
    print(f"    · ask today:  {brief.ask_today}")
    print(f"    · learned:    {brief.learned_yesterday}")
    print(f"    · (internal provenance: {', '.join(brief.provenance)})")


def morning(title, analysis, questions, *, plan_obs=None, plan_gaps=None, memories=None, changes=None):
    print("\n" + "═" * 70 + f"\n {title}\n" + "═" * 70)
    _before(title, analysis, plan_obs or [], plan_gaps or [], memories or [], questions)
    brief = fusion.synthesize(analysis, plan_obs=plan_obs, plan_gaps=plan_gaps,
                              memories=memories, changes=changes, questions=questions)
    _after(brief)


def main() -> int:
    # 1) NORMAL DAY — everything roughly on plan.
    a, q = _analyse(_calm_snapshot())
    morning("MORNING 1 · a normal day", a, q,
            plan_obs=[{"subject": "h2", "kind": "expected-occupancy", "value": 53, "source": "google-drive"}])

    # 2) DELAYED PRODUCTION — no climate alarm, but the schedule has slipped.
    a, q = _analyse(_calm_snapshot())
    morning("MORNING 2 · a delayed-production day", a, q,
            plan_obs=[{"subject": "h2", "kind": "expected-harvest", "value": "500 × Anthurium",
                       "source": "google-drive"},
                      {"subject": "h2", "kind": "expected-harvest-date", "value": "2026-06-22",
                       "source": "google-drive"}],
            plan_gaps=[{"kind": "knowledge-gap", "subject": "h2", "topic": "harvest-date",
                        "text": "h2: the planned harvest date (2026-06-22) has passed — did it happen, "
                                "or is the schedule slipping?",
                        "planned": "500 × Anthurium by 2026-06-22", "observed": "today is 2026-06-27",
                        "reason": "expected date appears unrealistic"}],
            memories=[{"zone": "House 2", "lesson": "House 2 ran about two weeks behind under the same climate last cycle."}])

    # 3) DISEASE-RISK DAY — the real sample (House 1 propagation).
    with open(_SAMPLE, "r", encoding="utf-8") as f:
        snap = import_snapshot(json.load(f))
    a, q = _analyse(snap)
    morning("MORNING 3 · a disease-risk day", a, q,
            plan_obs=[{"subject": "h1", "kind": "expected-occupancy", "value": 7, "source": "google-drive"}],
            memories=[{"zone": "House 1", "lesson": "A wet canopy on bench B preceded Botrytis two cycles ago."}],
            changes=["House 1 humidity 88% → 92%"])

    print("\n" + "─" * 70)
    print("  Before: the grower assembles four systems in their head.")
    print("  After:  Gaia hands them one understanding — one thought, one priority, one question.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

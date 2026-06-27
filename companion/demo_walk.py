#!/usr/bin/env python3
"""Demonstrate one complete greenhouse walk through the Even G2 Field Companion.

    Morning Brief → walk starts → silence → ONE biologically valuable question →
    grower answers → recommendation confidence updates → memory updates → silence →
    walk finishes → Evening Review → learning.

Everything biological comes from Gaia's existing engines; the Companion only decides when to
speak, in what words, and records what happened. Runs on a simulated Even G2 display (the only
missing piece for real glasses is the SDK transport in EvenG2Display._send_to_device).

    python companion/demo_walk.py
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from companion import _paths
from companion.devices.even_g2 import EvenG2Display
from companion.walk import WalkSession

from greenhouse_brain.snapshot_importer import import_snapshot
from greenhouse_brain.providers.snapshot_provider import SnapshotProvider
from greenhouse_brain.morning_analysis import MorningAnalysisEngine
from greenhouse_brain import knowledge_gap, store
from greenhouse_brain.lifecycle import experiment_from_candidate

_SNAPSHOT = os.path.join(_paths.APP_DIR, "sample_snapshot.json")


def _scripted_answer(message):
    """Stand in for the grower's on-device input (a glance/gesture/voice pick of one option)."""
    h = (message.headline or "").lower()
    if "did it help" in h:
        return "better"
    if "canopy wet" in h:           # the House 1 disease-risk confirm
        return "No, the canopy is dry now"
    return "not sure"


def _hr(title):
    print("\n" + "═" * 60 + f"\n{title}\n" + "═" * 60)


def main() -> int:
    with open(_SNAPSHOT, "r", encoding="utf-8") as f:
        snapshot = import_snapshot(json.load(f))
    date = (snapshot.assembled_at or "today")[:10]

    # Gaia's morning work (existing engines, untouched).
    provider = SnapshotProvider(snapshot)
    analysis = MorningAnalysisEngine().run(provider)
    experiments = [experiment_from_candidate(c, date)
                   for c in list(analysis.priorities) + list(analysis.opportunities)]
    prior = store.prior_worth_by_kind()
    questions, held = knowledge_gap.generate(analysis, [], snapshot.assembled_at, date, prior)

    display = EvenG2Display(answer_source=_scripted_answer)
    walk = WalkSession(analysis, questions, experiments, snapshot, display)

    _hr("MORNING BRIEF  (Gaia → Even G2)")
    print(f"  Gaia prepared {len(questions)} question(s) worth the walk; "
          f"{len(held)} held back as not worth interrupting for.\n")
    walk.start()

    # The walk: the grower moves between houses. Gaia is silent unless it's worth speaking.
    path = ["House 3 (finishing)", "House 1 (propagation)",
            "House 2 (growing on)", "House 3 (finishing)"]
    for loc in path:
        _hr(f"WALK · now in {loc}")
        before = len(display.sent)
        mode = walk.tick(loc)
        if len(display.sent) == before:
            print(f"   …silence. (Gaia considered, judged it not worth interrupting — {mode.value})")

    _hr("EVENING REVIEW  (Gaia → Even G2)")
    stats = walk.finish()

    _hr("WHAT GAIA REMEMBERS  (permanent interaction records)")
    for r in walk.engine.records:
        print(f"  • {r.question_id}  [{r.decision}]  EVI={r.evi}  cost={r.interruption_cost}  "
              f"conf {r.confidence_before}→{r.confidence_after}  worthwhile={r.worthwhile}")
        print(f"      reason: {r.reason}")
    print(f"\n  Walk economics — considered {stats['considered']}, asked {stats['asked']}, "
          f"stayed silent {stats['silenced']}; {stats['interactions_recorded']} records stored.")
    print(f"  Stored in: {os.path.relpath(store._INTERACTIONS_FILE, _paths.REPO_ROOT)}")
    print("\n  Learning: the worthwhile signal feeds prior_worth_by_kind(), so low-value "
          "question kinds clear the bar less often tomorrow — Gaia learns to ask less.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

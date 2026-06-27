#!/usr/bin/env python3
"""Demonstrate the whole bridge, end to end:

    Synopta (fixture) -> Collector -> Canonical Snapshot -> data/inbox/latest.json -> Gaia

Step 1 runs the Collector, which publishes data/inbox/latest.json.
Step 2 has GAIA consume exactly that file through its EXISTING path (import_snapshot ->
SnapshotProvider -> Morning Analysis -> Language) with no modification — proving the
Collector's output is consumable as-is.

    python collector/demo_pipeline.py
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collector import _paths
from collector.collect import run

# Gaia's own, unchanged consumption path.
from greenhouse_brain.snapshot_importer import import_snapshot
from greenhouse_brain.providers.snapshot_provider import SnapshotProvider
from greenhouse_brain.morning_analysis import MorningAnalysisEngine
from greenhouse_brain.language_engine import TemplateLanguageRenderer


def main() -> int:
    print("=" * 70)
    print("STEP 1 — COLLECTOR:  Synopta (fixture) -> Canonical Snapshot -> latest.json")
    print("=" * 70)
    code = run(source_name="fixture")
    if code != 0:
        print(f"\nCollector did not publish (exit {code}); stopping demo.")
        return code

    print("\n" + "=" * 70)
    print("STEP 2 — GAIA:  consume data/inbox/latest.json through the UNCHANGED path")
    print("=" * 70)
    with open(_paths.LATEST, "r", encoding="utf-8") as f:
        raw = json.load(f)

    snapshot = import_snapshot(raw)                       # Gaia's importer — untouched
    provider = SnapshotProvider(snapshot)                 # Gaia's provider — untouched
    analysis = MorningAnalysisEngine().run(provider)      # Gaia's engine   — untouched
    print(TemplateLanguageRenderer().render_morning(analysis))

    print("\n" + "=" * 70)
    print("PROOF — Gaia consumed the Collector's snapshot WITHOUT modification")
    print("=" * 70)
    climate = provider.get_latest_climate()
    print(f"  File Gaia read:        {_paths.LATEST}")
    print(f"  Greenhouse:            {snapshot.greenhouse_name} ({snapshot.greenhouse_id})")
    print(f"  Zones with climate:    {', '.join(sorted(climate)) or '(none)'}")
    h1 = climate.get("h1")
    if h1:
        print(f"  House 1 air temp:      {h1.temp_c} °C  "
              f"(Collector cleaned '24,2 °C' -> {h1.temp_c}; Gaia never saw the mess)")
    print(f"  Reality confidence:    {snapshot.reality_confidence()['label']} "
          f"({snapshot.reality_confidence()['score_pct']}%)")
    top = analysis.concerns[0] if analysis.concerns else None
    print(f"  Top concern:           {top.title} @ {top.zone_name}" if top else "  Top concern: none")
    print("\n  The Collector produced the file; Gaia read it with no code change.")
    print("  Acquisition and reasoning are cleanly separated — the architecture held.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

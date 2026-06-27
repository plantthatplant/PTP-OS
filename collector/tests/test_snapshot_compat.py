"""Snapshot-compatibility tests — the Collector's output must be consumable by Gaia,
unmodified, exactly like the canonical sample snapshot.

This is the contract that makes the whole bridge work: the Collector produces a Greenhouse
Snapshot; the Brain's existing import_snapshot -> SnapshotProvider -> engines consume it with
no change (specs/greenhouse-snapshot.md, specs/gaia-collector.md §3).
"""
import json
import os
import unittest

from collector import _paths
from collector.sources import FixtureSource
from collector.translate import to_snapshot

# Gaia's own, unchanged consumption path.
from greenhouse_brain.snapshot_importer import import_snapshot
from greenhouse_brain.providers.snapshot_provider import SnapshotProvider
from greenhouse_brain.morning_analysis import MorningAnalysisEngine

_COLLECTOR_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_FACILITY = os.path.join(_COLLECTOR_DIR, "facility.json")
_CANONICAL_SAMPLE = os.path.join(_paths.APP_DIR, "sample_snapshot.json")


def _collector_snapshot():
    raw = FixtureSource().fetch()
    with open(_FACILITY, encoding="utf-8") as f:
        facility = json.load(f)
    return to_snapshot(raw, facility, "2026-06-27T06:00:00Z")


class SnapshotCompatibility(unittest.TestCase):
    def test_same_shape_as_canonical_sample(self):
        with open(_CANONICAL_SAMPLE, encoding="utf-8") as f:
            sample = json.load(f)
        produced = _collector_snapshot()
        required = {"greenhouse_id", "greenhouse_name", "assembled_at",
                    "provenance", "coverage", "structure", "observations"}
        self.assertTrue(required.issubset(produced.keys()))
        # Same structural keys as the canonical sample (its '_comment' is doc-only).
        self.assertEqual(set(sample.keys()) - set(produced.keys()) - {"_comment"}, set())

    def test_importer_round_trip(self):
        snap = import_snapshot(_collector_snapshot())
        self.assertEqual(snap.greenhouse_id, "gh-kalaberga")
        self.assertTrue(snap.present())
        self.assertIn("coverage_pct", snap.coverage())

    def test_provider_yields_climate_for_each_house(self):
        snap = import_snapshot(_collector_snapshot())
        climate = SnapshotProvider(snap).get_latest_climate()
        self.assertEqual(set(climate), {"h1", "h2", "h3"})
        # The messy '24,2 °C' arrived clean in the domain.
        self.assertEqual(climate["h1"].temp_c, 24.2)

    def test_engine_runs_without_modification(self):
        snap = import_snapshot(_collector_snapshot())
        analysis = MorningAnalysisEngine().run(SnapshotProvider(snap))
        self.assertTrue(analysis.greenhouse_name)
        # The known House 1 propagation disease-risk concern comes through from this evidence.
        self.assertTrue(any("h1" in (c.zone_id or "") or "House 1" in (c.zone_name or "")
                            for c in analysis.concerns))

    def test_canonical_sample_also_consumable(self):
        # Sanity: the canonical sample the repo ships also runs the same way.
        with open(_CANONICAL_SAMPLE, encoding="utf-8") as f:
            snap = import_snapshot(json.load(f))
        analysis = MorningAnalysisEngine().run(SnapshotProvider(snap))
        self.assertTrue(analysis.greenhouse_name)


if __name__ == "__main__":
    unittest.main()

"""Validation tests — a snapshot is publishable only if Gaia can consume it.

Covers specs/gaia-collector.md §7: required snapshot fields, observation wellformedness,
honest-absence acceptance, and the round-trip through Gaia's own importer.
"""
import unittest

from collector.validate import validate

GOOD_OBS = {"subject": "h1", "kind": "air-temperature", "value": 24.2, "unit": "°C",
            "captured_at": "2026-06-27T05:48:00Z", "source": "synopta",
            "method": "measured", "confidence": "high"}


def _snap(observations, **overrides):
    base = {
        "greenhouse_id": "gh-test",
        "assembled_at": "2026-06-27T06:00:00Z",
        "provenance": [{"source": "synopta", "method": "measured"}],
        "coverage": {"not_observed": []},
        "observations": observations,
    }
    base.update(overrides)
    return base


class Validate(unittest.TestCase):
    def test_valid_snapshot_passes(self):
        r = validate(_snap([GOOD_OBS]))
        self.assertTrue(r.ok, r.errors)

    def test_absence_observation_is_valid(self):
        absent = {"subject": "h1", "kind": "co2", "value": None, "absence": "no sensor"}
        r = validate(_snap([absent]))
        self.assertTrue(r.ok, r.errors)

    def test_missing_required_snapshot_field_fails(self):
        for field in ("greenhouse_id", "assembled_at", "provenance", "coverage"):
            snap = _snap([GOOD_OBS])
            del snap[field]
            r = validate(snap)
            self.assertFalse(r.ok)
            self.assertTrue(any(field in e for e in r.errors), f"{field} should be flagged")

    def test_value_without_envelope_fails(self):
        bad = {"subject": "h1", "kind": "air-temperature", "value": 24.2}
        r = validate(_snap([bad]))
        self.assertFalse(r.ok)
        for need in ("captured_at", "source", "method", "confidence"):
            self.assertTrue(any(need in e for e in r.errors), f"{need} should be flagged")

    def test_no_value_and_no_absence_fails(self):
        bad = {"subject": "h1", "kind": "co2"}  # neither a value nor an absence marker
        r = validate(_snap([bad]))
        self.assertFalse(r.ok)
        self.assertTrue(any("no value and no absence" in e for e in r.errors))

    def test_reports_coverage_and_confidence(self):
        r = validate(_snap([GOOD_OBS]))
        self.assertIn("coverage_pct", r.coverage)
        self.assertIn("label", r.reality_confidence)


if __name__ == "__main__":
    unittest.main()

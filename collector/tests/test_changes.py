"""Change-detection tests — what changed in the data, never what it means.

Covers specs/gaia-collector.md §9: first run, no-change, value change, appeared/disappeared,
alarm raised/cleared, and coverage shifts.
"""
import unittest

from collector.changes import detect_changes


def _snap(observations, not_observed=None):
    return {"observations": observations, "coverage": {"not_observed": not_observed or []}}


def _o(subject, kind, value):
    return {"subject": subject, "kind": kind, "value": value}


class Changes(unittest.TestCase):
    def test_first_run(self):
        r = detect_changes(None, _snap([_o("h1", "air-temperature", 24.2)]))
        self.assertTrue(r["first_run"])
        self.assertIn("first collection", r["lines"][0])

    def test_no_changes(self):
        snap = _snap([_o("h1", "air-temperature", 24.2)])
        r = detect_changes(snap, _snap([_o("h1", "air-temperature", 24.2)]))
        self.assertFalse(r["first_run"])
        self.assertEqual(r["counts"], {"appeared": 0, "disappeared": 0, "changed": 0})
        self.assertIn("no notable changes", r["lines"][0])

    def test_value_changed(self):
        prev = _snap([_o("h1", "air-temperature", 24.2)])
        curr = _snap([_o("h1", "air-temperature", 25.1)])
        r = detect_changes(prev, curr)
        self.assertEqual(r["counts"]["changed"], 1)
        self.assertTrue(any("24.2 → 25.1" in s for s in r["lines"]))

    def test_appeared_and_disappeared(self):
        prev = _snap([_o("h1", "air-temperature", 24.2)])
        curr = _snap([_o("h1", "relative-humidity", 90)])
        r = detect_changes(prev, curr)
        self.assertEqual(r["counts"]["appeared"], 1)
        self.assertEqual(r["counts"]["disappeared"], 1)
        self.assertTrue(any("relative-humidity now observed" in s for s in r["lines"]))
        self.assertTrue(any("air-temperature no longer observed" in s for s in r["lines"]))

    def test_alarm_raised_and_cleared(self):
        no_alarm = _snap([_o("h2", "air-temperature", 16)])
        with_alarm = _snap([_o("h2", "air-temperature", 16), _o("h2", "alarm", "Sensor fault")])
        raised = detect_changes(no_alarm, with_alarm)
        self.assertTrue(any("ALARM raised" in s for s in raised["lines"]))
        cleared = detect_changes(with_alarm, no_alarm)
        self.assertTrue(any("alarm cleared" in s for s in cleared["lines"]))

    def test_absence_does_not_count_as_a_value(self):
        # An observation present only as absence must not look like an appeared value.
        prev = _snap([_o("h1", "air-temperature", 24.2)])
        curr = {"observations": [_o("h1", "air-temperature", 24.2),
                                 {"subject": "h1", "kind": "co2", "value": None, "absence": "no sensor"}],
                "coverage": {"not_observed": []}}
        r = detect_changes(prev, curr)
        self.assertEqual(r["counts"]["appeared"], 0)

    def test_coverage_shift(self):
        prev = _snap([_o("h1", "air-temperature", 24.2)], not_observed=[])
        curr = _snap([_o("h1", "air-temperature", 24.2)], not_observed=["House 2 — no reading"])
        r = detect_changes(prev, curr)
        self.assertTrue(any("newly un-observed" in s for s in r["lines"]))


if __name__ == "__main__":
    unittest.main()

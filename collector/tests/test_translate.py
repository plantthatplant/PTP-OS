"""Translation tests — raw Synopta reading -> Canonical Snapshot.

Covers the rules in specs/gaia-collector.md §6: unit/number cleaning, vent text, provenance-
based confidence, honest absence (never a fabricated value), site outside-temperature,
coverage gaps, and the assembled_at/captured_at distinction.
"""
import unittest

from collector.translate import to_snapshot

FACILITY = {
    "greenhouse_id": "gh-test",
    "greenhouse_name": "Test House",
    "zones": [
        {"house_id": "1", "id": "h1", "name": "House 1", "stage": "propagation", "crop": "x"},
        {"house_id": "2", "id": "h2", "name": "House 2", "stage": "vegetative", "crop": "y"},
    ],
    "known_absent": ["co2 — no CO₂ sensor"],
}


def _raw(houses):
    return {"captured_at": "2026-06-27T05:48:00Z", "site": "Test", "houses": houses}


def _obs(snap, subject, kind):
    for o in snap["observations"]:
        if o["subject"] == subject and o["kind"] == kind:
            return o
    return None


class Translate(unittest.TestCase):
    def test_cleans_messy_number(self):
        snap = to_snapshot(_raw([
            {"house_id": "1", "signals": {"air_temp": {"value": "24,2 °C"},
                                          "rel_humidity": {"value": 92},
                                          "vent_position": {"value": 0}}}]), FACILITY,
            "2026-06-27T06:00:00Z")
        self.assertEqual(_obs(snap, "h1", "air-temperature")["value"], 24.2)
        self.assertEqual(_obs(snap, "h1", "air-temperature")["unit"], "°C")

    def test_vent_text(self):
        snap = to_snapshot(_raw([
            {"house_id": "1", "signals": {"air_temp": {"value": 20}, "rel_humidity": {"value": 60},
                                          "vent_position": {"value": 0}}},
            {"house_id": "2", "signals": {"air_temp": {"value": 20}, "rel_humidity": {"value": 60},
                                          "vent_position": {"value": 30}}}]), FACILITY,
            "2026-06-27T06:00:00Z")
        self.assertEqual(_obs(snap, "h1", "vent-position")["value"], "closed")
        self.assertEqual(_obs(snap, "h2", "vent-position")["value"], "30%")

    def test_sensor_fault_lowers_confidence_and_carries_alarm(self):
        snap = to_snapshot(_raw([
            {"house_id": "1", "signals": {"air_temp": {"value": 16}, "rel_humidity": {"value": 66},
                                          "vent_position": {"value": 20},
                                          "alarm": {"active": True, "text": "Sensor fault: out of range"}}}]),
            FACILITY, "2026-06-27T06:00:00Z")
        self.assertEqual(_obs(snap, "h1", "air-temperature")["confidence"], "low")
        self.assertEqual(_obs(snap, "h1", "relative-humidity")["confidence"], "low")
        alarm = _obs(snap, "h1", "alarm")
        self.assertIsNotNone(alarm)
        self.assertIn("Sensor fault", alarm["value"])
        # The alarm is carried, never interpreted into a conclusion.
        self.assertEqual(alarm["method"], "measured")

    def test_healthy_reading_is_high_confidence(self):
        snap = to_snapshot(_raw([
            {"house_id": "1", "signals": {"air_temp": {"value": 21}, "rel_humidity": {"value": 64},
                                          "vent_position": {"value": 30}, "alarm": {"active": False}}}]),
            FACILITY, "2026-06-27T06:00:00Z")
        self.assertEqual(_obs(snap, "h1", "air-temperature")["confidence"], "high")
        self.assertIsNone(_obs(snap, "h1", "alarm"))  # inactive alarm is not recorded

    def test_missing_value_becomes_absence_not_zero(self):
        warnings = []
        snap = to_snapshot(_raw([
            {"house_id": "1", "signals": {"air_temp": {"value": None}, "rel_humidity": {"value": 64},
                                          "vent_position": {"value": 30}}}]),
            FACILITY, "2026-06-27T06:00:00Z", warnings)
        at = _obs(snap, "h1", "air-temperature")
        self.assertIsNone(at["value"])
        self.assertIn("absence", at)
        self.assertNotIn("unit", at)            # not a quantitative observation
        self.assertTrue(any("air-temperature" in w for w in warnings))

    def test_known_absent_sensors_declared_in_coverage(self):
        snap = to_snapshot(_raw([
            {"house_id": "1", "signals": {"air_temp": {"value": 21}, "rel_humidity": {"value": 64},
                                          "vent_position": {"value": 30}}}]),
            FACILITY, "2026-06-27T06:00:00Z")
        self.assertIn("co2 — no CO₂ sensor", snap["coverage"]["not_observed"])
        # And no fabricated co2 observation exists.
        self.assertIsNone(_obs(snap, "h1", "co2"))

    def test_configured_house_absent_from_export_is_coverage_gap(self):
        warnings = []
        snap = to_snapshot(_raw([
            {"house_id": "1", "signals": {"air_temp": {"value": 21}, "rel_humidity": {"value": 64},
                                          "vent_position": {"value": 30}}}]),
            FACILITY, "2026-06-27T06:00:00Z", warnings)
        self.assertTrue(any("House 2" in s for s in snap["coverage"]["not_observed"]))
        self.assertTrue(any("House 2" in w for w in warnings))

    def test_unknown_house_skipped_with_warning(self):
        warnings = []
        to_snapshot(_raw([
            {"house_id": "1", "signals": {"air_temp": {"value": 21}, "rel_humidity": {"value": 64},
                                          "vent_position": {"value": 30}}},
            {"house_id": "9", "signals": {"air_temp": {"value": 21}}}]),
            FACILITY, "2026-06-27T06:00:00Z", warnings)
        self.assertTrue(any("9" in w and "skipped" in w for w in warnings))

    def test_outside_temperature_recorded_once_at_site(self):
        snap = to_snapshot(_raw([
            {"house_id": "1", "signals": {"air_temp": {"value": 21}, "rel_humidity": {"value": 64},
                                          "vent_position": {"value": 30}, "outside_temp": {"value": 11}}},
            {"house_id": "2", "signals": {"air_temp": {"value": 20}, "rel_humidity": {"value": 60},
                                          "vent_position": {"value": 20}, "outside_temp": {"value": 11}}}]),
            FACILITY, "2026-06-27T06:00:00Z")
        site = [o for o in snap["observations"] if o["subject"] == "site"
                and o["kind"] == "outside-temperature"]
        self.assertEqual(len(site), 1)
        self.assertEqual(site[0]["value"], 11.0)

    def test_assembled_and_captured_times_distinct(self):
        snap = to_snapshot(_raw([
            {"house_id": "1", "signals": {"air_temp": {"value": 21}, "rel_humidity": {"value": 64},
                                          "vent_position": {"value": 30}}}]),
            FACILITY, "2026-06-27T06:00:00Z")
        self.assertEqual(snap["assembled_at"], "2026-06-27T06:00:00Z")
        self.assertEqual(_obs(snap, "h1", "air-temperature")["captured_at"], "2026-06-27T05:48:00Z")

    def test_structure_and_required_fields_present(self):
        snap = to_snapshot(_raw([]), FACILITY, "2026-06-27T06:00:00Z")
        self.assertEqual(snap["greenhouse_id"], "gh-test")
        self.assertTrue(snap["provenance"])
        self.assertIn("coverage", snap)
        self.assertEqual(len(snap["structure"]["zones"]), 2)


if __name__ == "__main__":
    unittest.main()

"""UTF-8 handling tests.

The greenhouse's reality is full of non-ASCII: 'Kålaberga', '°C', '%RH', 'CO₂', em dashes.
These must survive translation, atomic write, and read-back without corruption or escaping,
and a non-UTF-8 source must fail cleanly rather than publish mojibake.
"""
import json
import os
import shutil
import tempfile
import unittest

from collector import collect
from collector.sources import FixtureSource, SourceError
from collector.translate import to_snapshot

FACILITY = {
    "greenhouse_id": "gh-kalaberga",
    "greenhouse_name": "Kålaberga",
    "zones": [{"house_id": "1", "id": "h1", "name": "Hus 1 — förökning", "stage": "propagation",
               "crop": "blandade aroider"}],
    "known_absent": ["co2 — ingen CO₂-givare"],
}


class Utf8(unittest.TestCase):
    def test_non_ascii_survives_translation(self):
        snap = to_snapshot(
            {"captured_at": "2026-06-27T05:48:00Z",
             "houses": [{"house_id": "1", "signals": {"air_temp": {"value": "24,2 °C"},
                                                      "rel_humidity": {"value": 92},
                                                      "vent_position": {"value": 0}}}]},
            FACILITY, "2026-06-27T06:00:00Z")
        self.assertEqual(snap["greenhouse_name"], "Kålaberga")
        temp = next(o for o in snap["observations"] if o["kind"] == "air-temperature")
        self.assertEqual(temp["unit"], "°C")
        self.assertTrue(any("CO₂" in s for s in snap["coverage"]["not_observed"]))

    def test_atomic_write_round_trip_preserves_unicode_and_leaves_no_tmp(self):
        d = tempfile.mkdtemp()
        try:
            path = os.path.join(d, "latest.json")
            payload = {"greenhouse_name": "Kålaberga", "unit": "°C", "note": "CO₂ — soft"}
            collect._write_json(path, payload)
            # Bytes on disk are real UTF-8, not \uXXXX escapes.
            with open(path, "rb") as f:
                raw_bytes = f.read()
            self.assertIn("Kålaberga".encode("utf-8"), raw_bytes)
            self.assertNotIn(b"\\u", raw_bytes)
            # Reads back identically, and the temp file was renamed away.
            with open(path, "r", encoding="utf-8") as f:
                self.assertEqual(json.load(f), payload)
            self.assertEqual([n for n in os.listdir(d) if n.endswith(".tmp")], [])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_bundled_fixture_is_utf8(self):
        # The shipped sample must itself be valid UTF-8 (guards against a bad commit).
        raw = FixtureSource().fetch()
        self.assertIn("houses", raw)

    def test_non_utf8_source_fails_cleanly(self):
        d = tempfile.mkdtemp()
        try:
            bad = os.path.join(d, "latin1.json")
            with open(bad, "wb") as f:
                f.write('{"site": "Kåla"}'.encode("latin-1"))  # invalid UTF-8 bytes
            with self.assertRaises(SourceError):
                FixtureSource(path=bad).fetch()
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

"""Parser tests — every export format collapses to the one canonical raw shape, and the messy
realities of real exports are handled without ever inventing a value.

Covers Sprint-14 Phase 3 & 8: CSV/TSV/Excel/JSON, missing values, unexpected columns, column-order
changes, encoding problems, comma decimals, alarm flags, daylight-saving transitions, corruption.
"""
import os
import shutil
import tempfile
import unittest

from collector.edge import parsers
from collector.edge.parsers import ParseError, parse_export, parse_timestamp
from collector.tests._xlsx_write import write_xlsx

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def _signals(raw, house_id):
    for h in raw["houses"]:
        if str(h["house_id"]) == str(house_id):
            return h["signals"]
    raise AssertionError(f"house {house_id} not in {[h['house_id'] for h in raw['houses']]}")


class FormatParity(unittest.TestCase):
    """The same reading in CSV, TSV and JSON must yield the same canonical houses/signals."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_realistic_csv(self):
        raw = parse_export(os.path.join(FIX, "synopta_export_realistic.csv"))
        self.assertEqual(len(raw["houses"]), 3)
        s1 = _signals(raw, "1")
        self.assertEqual(s1["air_temp"]["value"], "24,2")        # left messy; translate cleans it
        self.assertEqual(s1["rel_humidity"]["value"], "92")
        self.assertFalse(_signals(raw, "1")["alarm"]["active"])
        self.assertTrue(_signals(raw, "2")["alarm"]["active"])
        self.assertIn("Sensorfel", _signals(raw, "2")["alarm"]["text"])

    def test_realistic_csv_uses_its_own_timestamp(self):
        # The Swedish 'Tidpunkt' column is the reading's time — used, not the file's mtime.
        raw = parse_export(os.path.join(FIX, "synopta_export_realistic.csv"))
        self.assertEqual(raw["captured_at"], "2026-06-29T05:48:00+00:00")

    def test_realistic_tsv(self):
        raw = parse_export(os.path.join(FIX, "synopta_export_realistic.tsv"))
        self.assertEqual(len(raw["houses"]), 3)
        self.assertEqual(_signals(raw, "1")["air_temp"]["value"], "24.2")

    def test_records_json_with_missing_value(self):
        raw = parse_export(os.path.join(FIX, "synopta_export_records.json"))
        self.assertEqual(len(raw["houses"]), 3)
        # House 3 has no humidity in the source — it must simply be absent, never zero-filled.
        self.assertNotIn("rel_humidity", _signals(raw, "3"))
        self.assertEqual(_signals(raw, "3")["air_temp"]["value"], 21.0)

    def test_vendor_json_passthrough(self):
        # The established vendor 'houses' shape is passed straight through.
        raw = parse_export(os.path.join(os.path.dirname(FIX), "..", "sources",
                                        "sample_synopta_export.json"))
        self.assertIn("houses", raw)
        self.assertEqual(raw["site"], "Kalaberga")

    def test_excel(self):
        path = os.path.join(self.tmp, "export.xlsx")
        write_xlsx(path, [
            ["timestamp", "house", "air_temp", "rel_humidity", "vent_position", "outside_temp", "alarm"],
            ["2026-06-29T05:48:00Z", 1, 24.2, 92, 0, 11.0, 0],
            ["2026-06-29T05:48:00Z", 2, 16.0, 66, 20, 11.0, 1],
        ])
        raw = parse_export(path)
        self.assertEqual(len(raw["houses"]), 2)
        self.assertEqual(_signals(raw, "1")["air_temp"]["value"], 24.2)
        self.assertTrue(_signals(raw, "2")["alarm"]["active"])


class MessyInputs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _csv(self, text, name="x.csv", encoding="utf-8"):
        p = os.path.join(self.tmp, name)
        with open(p, "w", encoding=encoding, newline="") as f:
            f.write(text)
        return p

    def test_unexpected_columns_ignored(self):
        p = self._csv("house;air_temp;operator;mood;rel_humidity\n1;22,0;Erik;sunny;70\n")
        raw = parse_export(p)
        s = _signals(raw, "1")
        self.assertEqual(s["air_temp"]["value"], "22,0")
        self.assertEqual(s["rel_humidity"]["value"], "70")
        self.assertNotIn("operator", s)

    def test_column_order_change(self):
        a = parse_export(self._csv("house;air_temp;rel_humidity\n1;22,0;70\n", "a.csv"))
        b = parse_export(self._csv("rel_humidity;house;air_temp\n70;1;22,0\n", "b.csv"))
        self.assertEqual(_signals(a, "1")["air_temp"]["value"], _signals(b, "1")["air_temp"]["value"])
        self.assertEqual(_signals(a, "1")["rel_humidity"]["value"], _signals(b, "1")["rel_humidity"]["value"])

    def test_missing_values_become_absent_not_zero(self):
        p = self._csv("house;air_temp;rel_humidity\n1;;70\n")     # air_temp empty
        s = _signals(parse_export(p), "1")
        self.assertNotIn("air_temp", s)                          # absent — NOT {"value": 0}
        self.assertEqual(s["rel_humidity"]["value"], "70")

    def test_utf8_bom(self):
        p = self._csv("house;air_temp\n1;22,0\n", "bom.csv", encoding="utf-8-sig")
        raw = parse_export(p)
        self.assertEqual(_signals(raw, "1")["air_temp"]["value"], "22,0")

    def test_cp1252_encoding(self):
        # 'Sensorfel: temperatur utanför' written in Windows-1252 (ö = 0xF6) must still decode.
        p = os.path.join(self.tmp, "latin.csv")
        with open(p, "w", encoding="cp1252", newline="") as f:
            f.write("house;air_temp;alarm;alarm_text\n2;16,0;1;Sensorfel utanför\n")
        raw = parse_export(p)
        self.assertIn("utanf", _signals(raw, "2")["alarm"]["text"])

    def test_header_units_in_parentheses(self):
        p = self._csv("Hus;Lufttemperatur (°C);Luftfuktighet (%)\n1;24,2;92\n")
        s = _signals(parse_export(p), "1")
        self.assertEqual(s["air_temp"]["value"], "24,2")
        self.assertEqual(s["rel_humidity"]["value"], "92")

    def test_no_house_column_raises(self):
        with self.assertRaises(ParseError):
            parse_export(self._csv("when;air_temp\n2026;22\n"))

    def test_empty_file_raises(self):
        with self.assertRaises(ParseError):
            parse_export(self._csv("", "empty.csv"))

    def test_corrupt_json_raises(self):
        p = os.path.join(self.tmp, "bad.json")
        with open(p, "w", encoding="utf-8") as f:
            f.write("{not valid json")
        with self.assertRaises(ParseError):
            parse_export(p)

    def test_corrupt_xlsx_raises(self):
        p = os.path.join(self.tmp, "bad.xlsx")
        with open(p, "wb") as f:
            f.write(b"this is not a zip file")
        with self.assertRaises(ParseError):
            parse_export(p)

    def test_unsupported_extension_raises(self):
        with self.assertRaises(ParseError):
            parse_export(self._csv("house;air_temp\n1;22\n", "x.pdf"))


def _tzdata_available() -> bool:
    """True only if the IANA tz database resolves (zoneinfo + tzdata). On a dependency-free
    Windows box it often is not — the parser then falls back to UTC, which these tests respect."""
    return type(parsers._zone("Europe/Stockholm")).__name__ == "ZoneInfo"


class Timestamps(unittest.TestCase):
    """Daylight-saving and timezone handling. The recommended (and always-correct) path is an
    offset-aware export timestamp; naive-time interpretation depends on tzdata being present."""

    def test_offset_aware_to_utc(self):
        # 05:48 at +02:00 (Stockholm summer / CEST) is 03:48 UTC — correct WITHOUT any tzdata.
        self.assertEqual(parse_timestamp("2026-06-29T05:48:00+02:00"), "2026-06-29T03:48:00+00:00")

    def test_zulu(self):
        self.assertEqual(parse_timestamp("2026-06-29T05:48:00Z"), "2026-06-29T05:48:00+00:00")

    @unittest.skipUnless(_tzdata_available(), "IANA tzdata not installed on this host")
    def test_naive_interpreted_in_default_tz_summer(self):
        # Naive local Stockholm time in summer is CEST (+02:00).
        out = parse_timestamp("2026-06-29 05:48:00", default_tz="Europe/Stockholm")
        self.assertEqual(out, "2026-06-29T03:48:00+00:00")

    @unittest.skipUnless(_tzdata_available(), "IANA tzdata not installed on this host")
    def test_naive_interpreted_in_default_tz_winter(self):
        # The SAME wall-clock string in winter is CET (+01:00) — the DST offset differs and must
        # be applied correctly rather than assumed fixed.
        out = parse_timestamp("2026-01-15 05:48:00", default_tz="Europe/Stockholm")
        self.assertEqual(out, "2026-01-15T04:48:00+00:00")

    def test_naive_without_tzdata_falls_back_to_utc_not_crash(self):
        # Whatever the host, a naive timestamp must resolve to a valid UTC instant, never crash.
        out = parse_timestamp("2026-06-29 05:48:00", default_tz="Europe/Stockholm")
        self.assertTrue(out.endswith("+00:00"))

    def test_dst_spring_forward_gap_does_not_crash(self):
        # 02:30 on 2026-03-29 does not exist in Europe/Stockholm (clocks jump 02:00→03:00).
        out = parse_timestamp("2026-03-29 02:30:00", default_tz="Europe/Stockholm")
        self.assertIsNotNone(out)                # resolved (not crashed), to a real UTC instant

    def test_unparseable_timestamp_is_none(self):
        self.assertIsNone(parse_timestamp("not a date"))
        self.assertIsNone(parse_timestamp(""))

    def test_export_without_timestamp_column_uses_file_time(self):
        # A CSV with no time column still gets a captured_at (the file's own production time),
        # so every observation is well-formed — honest provenance, not a fabricated reading.
        d = tempfile.mkdtemp()
        try:
            p = os.path.join(d, "no_ts.csv")
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write("house;air_temp\n1;22,0\n")
            raw = parse_export(p)
            self.assertIn("captured_at", raw)
            self.assertTrue(raw["captured_at"].endswith("+00:00"))
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

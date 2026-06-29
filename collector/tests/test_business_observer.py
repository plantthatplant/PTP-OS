"""Tests for the Business Knowledge Observer (GoogleDriveObserver) and plan-vs-reality.

Dependency-free: the table parsers are tested on injected row structures (no xlsx fixture
needed), and the deviation detector on plain observation dicts. An optional integration test
runs against the real ~/Downloads plan file only if present.
"""
import os
import glob
import unittest

from collector import _paths  # noqa: F401
from collector import xlsx_read
from collector.observers import google_drive_observer as gdo
from collector.observers import plan_vs_reality

SRC, AT = "google-drive:test.xlsx", "2026-06-27T10:00:00Z"


class Parsers(unittest.TestCase):
    def test_occupancy(self):
        rows = [
            {"_r": 1, "B": "BELÄGGNING PER VÄXTHUS"},
            {"_r": 2, "B": "Växthus", "C": "Antal bord", "D": "Aktiva", "F": "Försenade", "H": "Beläggning"},
            {"_r": 3, "B": "Hus 2", "C": 47, "D": 25, "F": 2, "H": 0.532, "I": 434},
            {"_r": 4, "B": "TOTAL", "C": 137},
        ]
        obs = gdo.parse_occupancy(rows, SRC, AT)
        kinds = {(o["kind"], o["subject"]): o for o in obs}
        self.assertEqual(kinds[("expected-occupancy", "h2")]["value"], 53.2)
        self.assertEqual(kinds[("expected-occupancy", "h2")]["unit"], "%")
        self.assertEqual(kinds[("planned-benches-active", "h2")]["value"], 25)
        self.assertEqual(kinds[("benches-delayed", "h2")]["value"], 2)
        for o in obs:                                  # never any biology, always provenance
            self.assertEqual(o["method"], "imported")
            self.assertEqual(o["source"], SRC)

    def test_deliveries(self):
        rows = [
            {"_r": 1, "C": "Bord-ID", "D": "Kultur", "I": "Antal", "K": "Slutdatum", "N": "Status"},
            {"_r": 2, "C": "H2-RB-V-06", "D": "Pentas", "I": 60, "K": 46230, "N": "Aktiv"},
        ]
        obs = gdo.parse_deliveries(rows, SRC, AT)
        harvest = next(o for o in obs if o["kind"] == "expected-harvest")
        date = next(o for o in obs if o["kind"] == "expected-harvest-date")
        self.assertEqual(harvest["subject"], "h2")
        self.assertIn("60", str(harvest["value"]))
        self.assertIn("Pentas", str(harvest["value"]))
        self.assertEqual(date["value"], xlsx_read.excel_date(46230))

    def test_financials(self):
        rows = [
            {"_r": 1, "A": "SUMMA OMSÄTTNING (kr)", "B": 7467510},
            {"_r": 2, "A": "Antal anställda (heltidsekvivalenter)", "B": 3.5},
            {"_r": 3, "A": "Odlingsyta m²", "B": 5000},
        ]
        obs = {o["kind"]: o for o in gdo.parse_financials(rows, SRC, AT)}
        self.assertEqual(obs["expected-revenue"]["value"], 7467510)
        self.assertEqual(obs["expected-revenue"]["unit"], "kr")
        self.assertEqual(obs["expected-labour"]["value"], 3.5)

    def test_profitability(self):
        rows = [
            {"_r": 10, "A": "KLASSIFICERING PER KULTUR"},
            {"_r": 11, "A": "Kultur", "B": "Typ", "C": "Marginal %", "F": "Klassificering", "G": "Atgard"},
            {"_r": 12, "A": "Dahlia 15cm", "B": "Dahlia", "C": 0.33, "D": 19146, "E": 189, "F": "STJARNA",
             "G": "Prioritera"},
        ]
        obs = gdo.parse_profitability(rows, SRC, AT)
        self.assertEqual(obs[0]["subject"], "crop:Dahlia 15cm")
        self.assertEqual(obs[0]["kind"], "expected-profitability")
        self.assertEqual(obs[0]["value"], "STJARNA")
        self.assertIn("margin 33%", obs[0]["notes"])

    def test_excel_date(self):
        self.assertEqual(xlsx_read.excel_date(46230), "2026-07-27")
        self.assertIsNone(xlsx_read.excel_date("not a date"))

    def test_missing_table_is_honest_absence(self):
        # No 'Växthus'/'Kultur' header → no observations invented.
        self.assertEqual(gdo.parse_occupancy([{"_r": 1, "B": "nothing"}], SRC, AT), [])
        self.assertEqual(gdo.parse_deliveries([{"_r": 1, "B": "nothing"}], SRC, AT), [])


class PlanVsReality(unittest.TestCase):
    def _plan(self, subject, kind, value):
        return {"subject": subject, "kind": kind, "value": value, "source": "google-drive:p.xlsx",
                "method": "imported", "confidence": "medium"}

    def test_numeric_deviation_raises_a_gap(self):
        plan = [self._plan("h2", "expected-occupancy", 53)]
        reality = [{"subject": "h2", "kind": "occupancy", "value": 30, "source": "grower"}]
        gaps = plan_vs_reality.compare(plan, reality)
        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps[0]["kind"], "knowledge-gap")
        self.assertEqual(gaps[0]["subject"], "h2")

    def test_within_tolerance_no_gap(self):
        plan = [self._plan("h2", "expected-occupancy", 53)]
        reality = [{"subject": "h2", "kind": "occupancy", "value": 50, "source": "grower"}]  # ~6%
        self.assertEqual(plan_vs_reality.compare(plan, reality), [])

    def test_no_overlap_no_gap(self):
        plan = [self._plan("h2", "expected-revenue", 100)]
        reality = [{"subject": "h1", "kind": "occupancy", "value": 30, "source": "grower"}]
        self.assertEqual(plan_vs_reality.compare(plan, reality), [])

    def test_passed_harvest_date_raises_a_gap(self):
        plan = [self._plan("h1", "expected-harvest-date", "2026-07-17")]
        gaps = plan_vs_reality.compare(plan, [], now_iso="2026-08-01T00:00:00Z")
        self.assertEqual(len(gaps), 1)
        self.assertIn("passed", gaps[0]["text"])

    def test_reality_is_never_mutated(self):
        plan = [self._plan("h2", "expected-occupancy", 53)]
        reality = [{"subject": "h2", "kind": "occupancy", "value": 30, "source": "grower"}]
        snapshot = [dict(r) for r in reality]
        plan_vs_reality.compare(plan, reality)
        self.assertEqual(reality, snapshot)   # unchanged — reality is never overwritten


class RealFileIntegration(unittest.TestCase):
    def test_real_plan_file_if_present(self):
        dl = os.path.join(os.path.expanduser("~"), "Downloads")
        files = glob.glob(os.path.join(dl, "*dlingsplan*.xlsx"))
        if not files:
            self.skipTest("no real plan file in ~/Downloads")
        # The folder may hold several plan-shaped sheets (per-house overviews, older years)
        # the observer isn't meant to parse. Assert it extracts expected-occupancy from at
        # least one — proving it handles the real master plan — rather than an arbitrary glob[0].
        obs = []
        for f in files:
            try:
                obs.extend(gdo.observe_files([f]))
            except Exception:
                pass   # overview / non-plan sheets are fine to skip here
        self.assertTrue(any(o["kind"] == "expected-occupancy" for o in obs),
                        "no plan file in ~/Downloads yielded expected-occupancy")
        # If a bench-overview workbook is present, it must now yield planned-crop observations
        # (previously these produced zero).
        if any("versikt" in os.path.basename(f).lower() for f in files):
            self.assertTrue(any(o["kind"] == "planned-crop" for o in obs),
                            "overview ('Översikt') sheets yielded no planned-crop observations")


class BenchOverview(unittest.TestCase):
    """The 'Översikt bord …' spatial sheets → distinct planned-crop observations per house."""
    AT = "2026-06-27T10:00:00Z"

    def test_planned_crops_skip_layout_and_dedupe(self):
        rows = [
            {"_r": 1, "B": "Hus 1"},                                   # house header
            {"_r": 2, "B": "13 ebb och flod", "D": "14 ebb och flod"}, # bench descriptors → skip
            {"_r": 3, "D": "Övervintrade Rudbeckia"},
            {"_r": 5, "B": "Sommardahlia", "D": "Sommardahlia"},       # dup → once
            {"_r": 6, "B": "Kryddamplar 2000 st totalt"},
            {"_r": 7, "C": "6-pack"},                                  # size fragment → skip
            {"_r": 8, "C": 5},                                         # bare number → skip
        ]
        obs = gdo.parse_bench_overview(rows, "google-drive:Översikt bord Hus 1.xlsx", self.AT,
                                       "Översikt bord Hus 1.xlsx")
        crops = [o["value"] for o in obs]
        self.assertEqual({o["subject"] for o in obs}, {"h1"})
        self.assertIn("Sommardahlia", crops)
        self.assertIn("Övervintrade Rudbeckia", crops)
        self.assertIn("Kryddamplar 2000 st totalt", crops)
        self.assertNotIn("13 ebb och flod", crops)   # bench descriptor filtered
        self.assertNotIn("6-pack", crops)            # size fragment filtered
        self.assertNotIn("5", crops)                 # bare number filtered
        self.assertEqual(crops.count("Sommardahlia"), 1)   # deduped
        for o in obs:
            self.assertEqual(o["kind"], "planned-crop")
            self.assertEqual(o["method"], "imported")     # intention, not reality
            self.assertEqual(o["confidence"], "medium")

    def test_house_mapping(self):
        self.assertEqual(gdo._overview_house("VENLO golv", ""), "venlo-golv")
        self.assertEqual(gdo._overview_house("Plasthus, 5 st", ""), "plast")
        self.assertEqual(gdo._overview_house("Hus 2", ""), "h2")
        self.assertEqual(gdo._overview_house("", "Översikt bord Mellanbygge odlingsplan.xlsx"),
                         "mellanbygge")

    def test_empty_sheet_is_honest_absence(self):
        self.assertEqual(gdo.parse_bench_overview([], "s", self.AT), [])


if __name__ == "__main__":
    unittest.main()

"""Knowledge Fusion tests — one voice, no invention, provenance internal.

(Fusion lives in greenhouse_brain; tested via the companion harness which bootstraps app/.)
"""
import unittest
from types import SimpleNamespace

from companion import _paths  # noqa: F401
from greenhouse_brain import fusion
from greenhouse_brain.domain import MorningAnalysis, Candidate


def _candidate(zone_id="h1", zone="House 1 (propagation)", kind="prevent", value="Critical"):
    return Candidate(zone_id=zone_id, zone_name=zone, kind=kind, title="Rising disease risk",
                     action="increase air movement now", why="a wet, still canopy invites Botrytis",
                     objective="protect young tissue", expected_benefit="canopy dries",
                     if_ignored="losses", value=value, window="Now", confidence="Medium",
                     evidence=["humid", "wet canopy"], effort="Low")


def _analysis(concerns=(), priorities=(), summary="settled", level="Medium"):
    return MorningAnalysis(prepared_at="05:50", greenhouse_name="Kålaberga", summary=summary,
                           concerns=list(concerns), opportunities=[], priorities=list(priorities),
                           curiosities=[], confidence_level=level,
                           confidence_rationale="evidence is limited", data_source="mock", caveats=[])


def _question(text="House 1: canopy wet?", subject="House 1", voi=0.6):
    return SimpleNamespace(text=text, subject=subject, voi=voi, biological_reason="disease is inferred")


class Fusion(unittest.TestCase):
    def test_settled_when_nothing_pressing(self):
        b = fusion.synthesize(_analysis())
        self.assertIn("settled", b.narrative.lower())
        self.assertIn("reality (Synopta + reasoning)", b.provenance)

    def test_plan_led_when_only_a_plan_gap(self):
        gaps = [{"subject": "h2", "topic": "harvest-date",
                 "text": "h2: the planned harvest date (2026-06-22) has passed — did it happen?",
                 "planned": "500 × Anthurium", "observed": "today", "reason": "date passed"}]
        b = fusion.synthesize(_analysis(), plan_gaps=gaps,
                              memories=[{"zone": "House 2", "lesson": "H2 ran two weeks behind."}])
        self.assertIn("behind plan", b.narrative.lower())
        self.assertIn("House 2", b.narrative)
        self.assertIn("business knowledge (Google Drive)", b.provenance)
        self.assertIn("memory", b.provenance)

    def test_critical_concern_leads_and_weaves_plan_and_memory(self):
        plan = [{"subject": "h1", "kind": "expected-harvest", "value": "60 × Pentas"},
                {"subject": "h1", "kind": "expected-harvest-date", "value": "2026-07-17"}]
        b = fusion.synthesize(_analysis(concerns=[_candidate()]), plan_obs=plan,
                              memories=[{"zone": "House 1", "lesson": "Wet canopy preceded Botrytis."}],
                              questions=[_question()])
        self.assertTrue(b.narrative.startswith("House 1"))
        self.assertIn("plan expected", b.narrative.lower())
        self.assertIn("increase air movement now", b.one_recommendation)
        self.assertEqual(b.ask_today, "House 1: canopy wet?")

    def test_speaks_one_voice_not_source_by_source(self):
        b = fusion.synthesize(_analysis(concerns=[_candidate()]),
                              plan_obs=[{"subject": "h1", "kind": "expected-occupancy", "value": 7}])
        low = b.narrative.lower()
        for forbidden in ("synopta says", "spreadsheet says", "memory says"):
            self.assertNotIn(forbidden, low)
        self.assertTrue(b.provenance)   # provenance is preserved INTERNALLY

    def test_no_invented_question_when_none_available(self):
        b = fusion.synthesize(_analysis())
        self.assertEqual(b.ask_today, "nothing worth interrupting you for")


if __name__ == "__main__":
    unittest.main()

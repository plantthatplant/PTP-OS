"""GaiaService tests — the gateway returns understanding only, and the Brain stays the source.

State (store) is redirected to a temp dir so tests never touch real data.
"""
import json
import os
import shutil
import tempfile
import unittest

from api import _paths  # noqa: F401
from api import service
from api.service import GaiaService
from greenhouse_brain import store

_SAMPLE = os.path.join(_paths.APP_DIR, "sample_snapshot.json")


class ServiceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._orig = {k: getattr(store, k) for k in
                      ("_DATA_DIR", "_QUESTIONS_FILE", "_EXPERIMENTS_FILE", "_ANSWERS_FILE",
                       "_QEVAL_FILE", "_MEMORIES_FILE", "_INTERACTIONS_FILE")}
        store._DATA_DIR = self.tmp
        store._QUESTIONS_FILE = os.path.join(self.tmp, "q.json")
        store._EXPERIMENTS_FILE = os.path.join(self.tmp, "exp.json")
        store._ANSWERS_FILE = os.path.join(self.tmp, "ans.jsonl")
        store._QEVAL_FILE = os.path.join(self.tmp, "qeval.jsonl")
        store._MEMORIES_FILE = os.path.join(self.tmp, "mem.jsonl")
        store._INTERACTIONS_FILE = os.path.join(self.tmp, "int.jsonl")
        self._orig_obs_log = service._OBS_LOG          # the posted-observation log lives in api.service
        service._OBS_LOG = os.path.join(self.tmp, "obs.jsonl")
        self.svc = GaiaService(snapshot_path=_SAMPLE)

    def tearDown(self):
        for k, v in self._orig.items():
            setattr(store, k, v)
        service._OBS_LOG = self._orig_obs_log
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_morning_is_understanding_with_no_implementation_leak(self):
        m = self.svc.morning()
        for k in ("greenhouse", "brief", "priority", "first_recommendation", "confidence",
                  "ask_today", "knowledge_gaps"):
            self.assertIn(k, m)
        blob = json.dumps(m).lower()
        for leak in ("synopta", "latest.json", "/data/", "google-drive", ".py", "method"):
            self.assertNotIn(leak, blob)   # clients see understanding, not internals/vendors

    def test_houses_expose_domain_not_observer_identity(self):
        houses = self.svc.houses()
        self.assertTrue(houses and all("id" in h and "climate" in h for h in houses))
        self.assertNotIn("suspect", json.dumps(houses).lower())  # trust shown as 'reliable', not vendor terms

    def test_companion_is_exactly_one_message(self):
        c = self.svc.companion()
        self.assertEqual(set(c), {"message", "urgency", "confidence", "acknowledged", "question_id"})
        self.assertIn(c["urgency"], ("info", "ask", "warn", "silent"))

    def test_voice_note_becomes_canonical_observation(self):
        r = self.svc.voice_note("brown spots, bench 3", subject="h1")
        o = r["observation"]
        self.assertEqual(o["method"], "observed-by-human")
        self.assertEqual(o["subject"], "h1")
        self.assertEqual(o["kind"], "note")

    def test_post_observation_accepts_canonical_rejects_malformed(self):
        good = {"subject": "h2", "kind": "leaf-wetness", "value": "wet", "source": "dji",
                "method": "vision-inferred", "confidence": "medium"}
        bad = {"source": "dji"}  # no subject/kind/value
        r = self.svc.post_observation([good, bad])
        self.assertEqual(r, {"accepted": 1, "rejected": 1})

    def test_answer_routes_and_moves_confidence(self):
        self.svc.morning()                       # populates the day's questions in the store
        q = self.svc.questions()
        prevent = next((x for x in q if x["id"].endswith("prevent-0")), q[0])
        r = self.svc.answer_question(prevent["id"], "No, the canopy is dry")
        self.assertIn("confidence_before", r)
        self.assertIn("confidence_after", r)
        self.assertTrue(r.get("worthwhile"))

    def test_unknown_question_is_handled(self):
        self.assertIn("error", self.svc.answer_question("nope", "x"))

    def test_observation_history_includes_posted_and_voice(self):
        self.svc.post_observation({"subject": "h2", "kind": "leaf-wetness", "value": "wet",
                                   "source": "dji", "method": "vision-inferred", "confidence": "medium"})
        self.svc.voice_note("brown spots, bench 3", subject="h1")
        hist = self.svc.observations()
        kinds = {o["kind"] for o in hist}
        self.assertIn("leaf-wetness", kinds)
        self.assertIn("note", kinds)
        self.assertTrue(all({"subject", "kind", "value", "captured_at"} <= set(o) for o in hist))

    def test_voice_note_carries_a_full_timestamp(self):
        # Regression: voice notes used a date-only stamp ("2026-06-29"), which always sorts BELOW
        # timestamped observations ("2026-06-29T…") — so they silently dropped out of the
        # newest-first, limit-capped history. They now carry a full ISO timestamp and sort by time.
        self.svc.voice_note("brown spots, bench 3", subject="h1")
        note = next(o for o in self.svc.observations() if o["kind"] == "note")
        self.assertIn("T", str(note["captured_at"]))   # full timestamp, not a bare date

    def test_learning_reports_calibration(self):
        learn = self.svc.learning()
        self.assertIn("calibration", learn)
        self.assertIn("hold_rate", learn["calibration"])


if __name__ == "__main__":
    unittest.main()

"""Interaction Engine tests — the economics of when to speak.

Silence is the default; ask only when EVI beats the (context-aware) cost; record everything;
update confidence from answers; and never reason about biology.
"""
import os
import tempfile
import unittest

from companion import _paths  # noqa: F401  (path bootstrap)
from greenhouse_brain import store, knowledge_gap
from greenhouse_brain.lifecycle import Experiment
from companion.interaction_engine import InteractionEngine, InteractionRecord


def _question(qid, decision_kind, subject, decision_id, evi_product, kind="confirm",
              interruption_cost=0.15):
    # Build a real knowledge_gap.Question with VoI components that yield a chosen EVI.
    comps = {"stakes": evi_product, "uncertainty": 1.0, "decisiveness": 1.0, "prior": 1.0,
             "interruption_cost": interruption_cost}
    voi = round(evi_product - interruption_cost, 3)
    return knowledge_gap.Question(
        id=qid, timestamp="t", text=f"{subject}: question?", kind=kind,
        decision_kind=decision_kind, subject=subject, suggested_location=subject,
        suggested_timing="on the walk", snapshot_ref="snap-1", decision_id=decision_id,
        experiment_id=None, biological_reason="reason", uncertainty="Medium",
        expected_impact="impact", voi=voi, voi_components=comps, relevant_if_late=True)


def _experiment(date, zone_id, kind, conf="Medium"):
    return Experiment(
        id=f"exp-{date}-{zone_id}-{kind}", opened_on=date, zone="House 1", kind=kind,
        observation=["e"], reasoning="r", recommendation="do x", expected_outcome="y",
        window="Today", confidence_before=conf, biological_principles="p")


class _IsolatedStore(unittest.TestCase):
    """Redirect the interaction/eval/answer logs to a temp dir so tests never touch real data."""
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._orig = (store._INTERACTIONS_FILE, store._ANSWERS_FILE, store._QEVAL_FILE,
                      store._MEMORIES_FILE)
        store._INTERACTIONS_FILE = os.path.join(self.tmp, "interactions.jsonl")
        store._ANSWERS_FILE = os.path.join(self.tmp, "answers.jsonl")
        store._QEVAL_FILE = os.path.join(self.tmp, "qeval.jsonl")
        store._MEMORIES_FILE = os.path.join(self.tmp, "memories.jsonl")
        store._DATA_DIR = self.tmp

    def tearDown(self):
        (store._INTERACTIONS_FILE, store._ANSWERS_FILE, store._QEVAL_FILE,
         store._MEMORIES_FILE) = self._orig


class Economics(_IsolatedStore):
    def test_silence_when_nothing_matches_location(self):
        eng = InteractionEngine([_question("q1", "prevent", "House 1", "h1", 0.6)], [], "snap", "2026-06-27")
        decision, q = eng.consider("House 9", tick=1)
        self.assertEqual(decision, "none")
        self.assertEqual(eng.records, [])   # pure silence is not an interaction

    def test_ask_when_evi_beats_cost(self):
        eng = InteractionEngine([_question("q1", "prevent", "House 1", "h1", 0.6)], [], "snap", "2026-06-27")
        decision, q = eng.consider("House 1", tick=1)
        self.assertEqual(decision, "ask")
        self.assertGreater(eng._evi(q), eng._effective_cost(q, 1))

    def test_spacing_silences_a_lower_value_question_right_after_an_ask(self):
        date = "2026-06-27"
        q_hi = _question("q-hi", "prevent", "House 1", "h1", 0.6)
        q_lo = _question("q-lo", "inspect", "House 2", "h2", 0.5)
        exps = [_experiment(date, "h1", "prevent"), _experiment(date, "h2", "inspect")]
        eng = InteractionEngine([q_hi, q_lo], exps, "snap", date)
        # Ask the high-value one, then immediately consider the lower one nearby.
        self.assertEqual(eng.consider("House 1", tick=1)[0], "ask")
        eng.answer(q_hi, "no, dry", "House 1", tick=1, wording="House 1: canopy wet?")
        decision, _ = eng.consider("House 2", tick=2)   # within spacing window
        self.assertEqual(decision, "silent")            # recorded, not asked

    def test_answer_records_full_provenance_and_updates_confidence(self):
        date = "2026-06-27"
        q = _question("q1", "prevent", "House 1", "h1", 0.6)
        exp = _experiment(date, "h1", "prevent", conf="Medium")
        eng = InteractionEngine([q], [exp], "snap-ref", date)
        eng.consider("House 1", tick=1)
        eng.answer(q, "yes, wet canopy", "House 1", tick=1, wording="House 1: canopy wet?")
        rec = [r for r in eng.records if r.answered][0]
        # Every required field present.
        for fld in ("question_id", "timestamp", "snapshot_ref", "decision_id", "reason",
                    "uncertainty", "evi", "interruption_cost", "confidence_before",
                    "confidence_after", "worthwhile"):
            self.assertIsNotNone(getattr(rec, fld), fld)
        # 'yes, wet' agrees with the disease inference → confidence steps up.
        self.assertEqual(rec.confidence_before, "Medium")
        self.assertEqual(rec.confidence_after, "Medium-high")
        self.assertTrue(rec.worthwhile)
        # Persisted to (temp) memory.
        self.assertTrue(os.path.exists(store._INTERACTIONS_FILE))
        self.assertEqual(len(store.load_interactions()), 1)

    def test_contradicting_answer_lowers_confidence(self):
        date = "2026-06-27"
        q = _question("q1", "prevent", "House 1", "h1", 0.6)
        exp = _experiment(date, "h1", "prevent", conf="Medium")
        eng = InteractionEngine([q], [exp], "snap", date)
        eng.consider("House 1", tick=1)
        res = eng.answer(q, "no, the canopy is dry now", "House 1", tick=1, wording="x")
        self.assertEqual(res["confidence_after"], "Low")   # stood down — a false alarm avoided
        self.assertTrue(res["worthwhile"])

    def test_engine_imports_no_device(self):
        # Device-independence: the interaction engine must not import any device adapter.
        import companion.interaction_engine as ie
        with open(ie.__file__, encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("even_g2", src)
        self.assertNotIn("devices", src)


if __name__ == "__main__":
    unittest.main()

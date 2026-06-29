"""End-to-end integration test — the whole production chain over HTTP.

Spins up the real `serve()` server over a real `GaiaService` (composing the Brain from the
bundled sample snapshot) and exercises EVERY public endpoint the way a real client day does:
Even Hub / Lovable / mobile all speak the same `/api/v1`. State (store) is redirected to a temp
dir so the test never touches real data. This is the chain verification:

    HTTP transport → GaiaService → Brain (Morning Analysis · Knowledge Fusion · Lifecycle/Memory)

If any link breaks, the matching endpoint assertion fails with a clear message.
"""
import json
import os
import shutil
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

from api import _paths  # noqa: F401  (path bootstrap)
from api.server import serve
from api.service import GaiaService
from greenhouse_brain import store

_SAMPLE = os.path.join(_paths.APP_DIR, "sample_snapshot.json")
_KEY = "itest-key"


class EndToEndTest(unittest.TestCase):
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
        # No third-party keys in CI → /ask answers honestly rather than calling out.
        for k in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
            os.environ.pop(k, None)
        self.httpd = serve(host="127.0.0.1", port=0,
                           service=GaiaService(snapshot_path=_SAMPLE), api_key=_KEY)
        self.port = self.httpd.server_address[1]
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        for k, v in self._orig.items():
            setattr(store, k, v)
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --- helpers ---
    def _req(self, method, path, body=None, ctype="application/json"):
        data = None
        if body is not None:
            data = body if isinstance(body, bytes) else json.dumps(body).encode()
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/api/v1{path}",
                                     data=data, method=method)
        req.add_header("Authorization", f"Bearer {_KEY}")
        if data is not None:
            req.add_header("Content-Type", ctype)
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.status, json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode() or "null")

    def get(self, path):
        return self._req("GET", path)

    def post(self, path, body, ctype="application/json"):
        return self._req("POST", path, body, ctype)

    # --- the whole chain, one client day ---
    def test_every_endpoint(self):
        # health (public)
        s, o = self.get("/health")
        self.assertEqual(s, 200, "health")
        self.assertIn(o.get("status"), ("ok", "degraded", "down"), "health.status")

        # morning brief (Brain + Knowledge Fusion)
        s, o = self.get("/morning")
        self.assertEqual(s, 200, "morning")
        for k in ("greenhouse", "brief", "priority", "confidence", "knowledge_gaps"):
            self.assertIn(k, o, f"morning.{k}")

        # houses + house detail
        s, houses = self.get("/houses")
        self.assertEqual(s, 200, "houses")
        self.assertTrue(houses and all("id" in h for h in houses), "houses non-empty with ids")
        s, one = self.get(f"/houses/{houses[0]['id']}")
        self.assertEqual(s, 200, "house detail")
        self.assertEqual(one["id"], houses[0]["id"], "house id roundtrip")

        # memory + search
        self.assertEqual(self.get("/memory")[0], 200, "memory")
        self.assertEqual(self.get("/memory/search?q=disease")[0], 200, "memory search")

        # knowledge gaps, learning, questions, companion, evening
        for path in ("/knowledge-gaps", "/learning", "/questions", "/companion", "/evening"):
            s, o = self.get(path)
            self.assertEqual(s, 200, path)
            self.assertIsNotNone(o, path)

        # observations history
        self.assertEqual(self.get("/observations")[0], 200, "observations GET")

        # POST a canonical observation
        s, o = self.post("/observations", {"subject": "h2", "kind": "leaf-wetness",
                                            "value": "wet", "source": "dji",
                                            "method": "vision-inferred", "confidence": "medium"})
        self.assertEqual(s, 201, "observations POST")

        # POST a voice note → Canonical Observation
        s, o = self.post("/voice-notes", {"text": "brown spots, bench 3", "subject": "h1"})
        self.assertEqual(s, 201, "voice-notes")
        self.assertEqual(o["observation"]["method"], "observed-by-human", "voice note canonical")

        # answer the day's question (if any), exercising the learning loop
        s, qs = self.get("/questions")
        if isinstance(qs, list) and qs:
            qid = qs[0]["id"]
            s, o = self.post(f"/questions/{qid}/answer", {"answer": "No, the canopy is dry"})
            self.assertEqual(s, 200, "answer question")
            self.assertIn("confidence_after", o, "answer → confidence")

        # talk to Gaia — no keys in CI → honest, never a crash
        s, o = self.post("/ask", {"question": "Is House 1 at risk this morning?"})
        self.assertEqual(s, 200, "ask")
        self.assertIn("answer", o, "ask.answer")

        # raw PCM audio path also routes (octet-stream) and answers honestly
        s, o = self.post("/ask", b"\x00\x01rawpcm", ctype="application/octet-stream")
        self.assertEqual(s, 200, "ask audio")
        self.assertIn("answer", o, "ask audio.answer")

        # auth enforced
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/api/v1/morning")
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req, timeout=5)
        self.assertEqual(cm.exception.code, 401, "unauthorized")


if __name__ == "__main__":
    unittest.main()

"""Tests for api/ask.py — talk to Gaia (speech in, answer out).

All offline: the network hops (Whisper, Claude) are never reached because the missing-key and
empty-input guards fire first. We test the WAV framing and that every failure path is honest
(returns a message, never a crash, never an invented answer).
"""
import json
import os
import struct
import threading
import unittest
import urllib.error
import urllib.request

from api import ask
from api.server import serve


class _StubService:
    """answer()/transcribe() bail at the key/input guards before touching the service."""
    def morning(self): return {}
    def houses(self): return []
    def memory(self, limit=20): return []


class PcmToWavTest(unittest.TestCase):
    def test_header_is_valid_wav(self):
        pcm = b"\x01\x02\x03\x04\x05\x06"
        wav = ask._pcm_to_wav(pcm)
        self.assertEqual(wav[:4], b"RIFF")
        self.assertEqual(wav[8:12], b"WAVE")
        self.assertIn(b"fmt ", wav)
        self.assertIn(b"data", wav)
        # 44-byte canonical header + payload
        self.assertEqual(len(wav), 44 + len(pcm))
        # the data chunk size field equals the PCM length
        data_size = struct.unpack("<I", wav[40:44])[0]
        self.assertEqual(data_size, len(pcm))
        # 16 kHz, mono, 16-bit as the glasses emit
        self.assertEqual(struct.unpack("<I", wav[24:28])[0], 16000)   # sample rate
        self.assertEqual(struct.unpack("<H", wav[22:24])[0], 1)       # channels


class GuardsTest(unittest.TestCase):
    def setUp(self):
        # Ensure both keys are absent so no network call is attempted.
        self._saved = {k: os.environ.pop(k, None) for k in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")}

    def tearDown(self):
        for k, v in self._saved.items():
            if v is not None:
                os.environ[k] = v

    def test_transcribe_requires_key(self):
        with self.assertRaises(ask.AskError) as cm:
            ask.transcribe(b"somepcm")
        self.assertIn("not configured", str(cm.exception))

    def test_transcribe_empty_audio(self):
        os.environ["OPENAI_API_KEY"] = "test-key"  # pass the key guard; empty audio still rejected
        try:
            with self.assertRaises(ask.AskError) as cm:
                ask.transcribe(b"")
            self.assertIn("no audio", str(cm.exception))
        finally:
            os.environ.pop("OPENAI_API_KEY", None)

    def test_transcribe_rejects_oversized_audio(self):
        os.environ["OPENAI_API_KEY"] = "test-key"  # pass the key + non-empty guards
        orig = ask._MAX_AUDIO_BYTES
        ask._MAX_AUDIO_BYTES = 8
        try:
            with self.assertRaises(ask.AskError) as cm:
                ask.transcribe(b"x" * 16)            # over the (lowered) cap → rejected before STT
            self.assertIn("too long", str(cm.exception))
        finally:
            ask._MAX_AUDIO_BYTES = orig
            os.environ.pop("OPENAI_API_KEY", None)

    def test_answer_empty_question(self):
        with self.assertRaises(ask.AskError):
            ask.answer("", _StubService())

    def test_answer_requires_key(self):
        with self.assertRaises(ask.AskError) as cm:
            ask.answer("Is House 1 at risk?", _StubService())
        self.assertIn("not configured", str(cm.exception))


class HandleAskTest(unittest.TestCase):
    """The endpoint always returns a usable dict (HTTP 200), honest about failure."""
    def setUp(self):
        self._saved = {k: os.environ.pop(k, None) for k in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")}

    def tearDown(self):
        for k, v in self._saved.items():
            if v is not None:
                os.environ[k] = v

    def test_json_question_without_anthropic_key(self):
        out = ask.handle_ask({"question": "Is House 1 at risk?"}, _StubService())
        self.assertIn("answer", out)
        self.assertIn("error", out)
        self.assertIn("not configured", out["answer"])

    def test_audio_without_openai_key(self):
        out = ask.handle_ask(b"rawpcmbytes", _StubService())
        self.assertIn("speech-to-text", out["answer"])

    def test_unparseable_body_is_handled(self):
        out = ask.handle_ask(None, _StubService())
        self.assertIn("answer", out)  # empty question → honest message, no crash


class LoggingTest(unittest.TestCase):
    """One structured log line per call — outcome + timings, but NEVER content."""
    def setUp(self):
        self._saved = {k: os.environ.pop(k, None) for k in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")}

    def tearDown(self):
        for k, v in self._saved.items():
            if v is not None:
                os.environ[k] = v

    def test_structured_outcome_without_content(self):
        secret = "the canopy looks wet on bench three"
        with self.assertLogs("gaia.ask", level="INFO") as cm:
            ask.handle_ask({"question": secret}, _StubService())
        line = cm.output[0]
        event = json.loads(line.split("gaia.ask:")[-1] if "gaia.ask:" in line else line[line.index("{"):])
        self.assertFalse(event["ok"])
        self.assertEqual(event["failed_at"], "answer")    # no anthropic key
        self.assertIn("total_ms", event)
        self.assertEqual(event["chars_in"], len(secret))  # length only
        # privacy: the grower's words never appear in the log line
        self.assertNotIn(secret, line)


class EndpointTest(unittest.TestCase):
    """The /ask route end-to-end through the real server — covers the binary-body dispatch."""
    def setUp(self):
        self._saved = {k: os.environ.pop(k, None) for k in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")}
        self.httpd = serve(host="127.0.0.1", port=0, service=_StubService(), api_key="k")
        self.port = self.httpd.server_address[1]
        self.t = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.t.start()

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        for k, v in self._saved.items():
            if v is not None:
                os.environ[k] = v

    def _post(self, data: bytes, ctype: str):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/api/v1/ask", data=data, method="POST")
        req.add_header("Authorization", "Bearer k")
        req.add_header("Content-Type", ctype)
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read().decode("utf-8"))

    def test_json_body_routes_and_answers_honestly(self):
        status, out = self._post(b'{"question":"hi"}', "application/json")
        self.assertEqual(status, 200)
        self.assertIn("not configured", out["answer"])

    def test_audio_body_passes_through_as_raw_bytes(self):
        # octet-stream must NOT be JSON-parsed (it would 400); it reaches /ask as raw audio.
        status, out = self._post(b"\x00\x01rawpcm", "application/octet-stream")
        self.assertEqual(status, 200)
        self.assertIn("speech-to-text", out["answer"])

    def test_unauthorized_without_key(self):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/api/v1/ask",
                                     data=b'{"question":"hi"}', method="POST")
        req.add_header("Content-Type", "application/json")
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req, timeout=5)
        self.assertEqual(cm.exception.code, 401)


class _FakeResp:
    def __init__(self, body): self._b = body
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def read(self): return self._b


class RetryTest(unittest.TestCase):
    """_http_post retries only fast transient failures, and never timeouts."""
    def _patch(self, fn):
        self._orig = ask.urllib.request.urlopen
        ask.urllib.request.urlopen = fn
        self.addCleanup(lambda: setattr(ask.urllib.request, "urlopen", self._orig))

    def test_retries_connection_reset_then_succeeds(self):
        calls = {"n": 0}
        def fake(req, timeout=None):
            calls["n"] += 1
            if calls["n"] == 1:
                raise ConnectionResetError("reset")
            return _FakeResp(b'{"ok": 1}')
        self._patch(fake)
        out = json.loads(ask._http_post("http://x", b"d", {}, timeout=1, retries=1))
        self.assertEqual(out, {"ok": 1})
        self.assertEqual(calls["n"], 2)            # retried once

    def test_retries_503_then_succeeds(self):
        calls = {"n": 0}
        def fake(req, timeout=None):
            calls["n"] += 1
            if calls["n"] == 1:
                raise urllib.error.HTTPError("http://x", 503, "overloaded", {}, None)
            return _FakeResp(b'{"ok": 2}')
        self._patch(fake)
        out = json.loads(ask._http_post("http://x", b"d", {}, timeout=1, retries=1))
        self.assertEqual(out, {"ok": 2})
        self.assertEqual(calls["n"], 2)

    def test_does_not_retry_4xx(self):
        calls = {"n": 0}
        def fake(req, timeout=None):
            calls["n"] += 1
            raise urllib.error.HTTPError("http://x", 400, "bad request", {}, None)
        self._patch(fake)
        with self.assertRaises(urllib.error.HTTPError):
            ask._http_post("http://x", b"d", {}, timeout=1, retries=1)
        self.assertEqual(calls["n"], 1)            # permanent → no retry

    def test_does_not_retry_timeout(self):
        calls = {"n": 0}
        def fake(req, timeout=None):
            calls["n"] += 1
            raise TimeoutError("slow")
        self._patch(fake)
        with self.assertRaises(TimeoutError):
            ask._http_post("http://x", b"d", {}, timeout=1, retries=1)
        self.assertEqual(calls["n"], 1)            # fail fast — the grower doesn't wait twice


class SttProviderTest(unittest.TestCase):
    """STT is a swappable, server-side provider (GAIA_STT_PROVIDER) — clients never transcribe."""
    def setUp(self):
        self._saved = {k: os.environ.pop(k, None) for k in
                       ("GAIA_STT_PROVIDER", "OPENAI_API_KEY", "WHISPERFLOW_URL", "WHISPERFLOW_API_KEY")}

    def tearDown(self):
        for k, v in self._saved.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v

    def test_default_provider_is_openai(self):
        with self.assertRaises(ask.AskError) as cm:
            ask.transcribe(b"pcm")
        self.assertIn("OPENAI_API_KEY", str(cm.exception))

    def test_unknown_provider_is_honest(self):
        os.environ["GAIA_STT_PROVIDER"] = "bogus"
        with self.assertRaises(ask.AskError) as cm:
            ask.transcribe(b"pcm")
        self.assertIn("unknown speech-to-text provider", str(cm.exception))

    def test_whisperflow_requires_url(self):
        os.environ["GAIA_STT_PROVIDER"] = "whisperflow"
        with self.assertRaises(ask.AskError) as cm:
            ask.transcribe(b"pcm")
        self.assertIn("WHISPERFLOW_URL", str(cm.exception))

    def test_whisperflow_posts_wav_and_parses_text(self):
        os.environ["GAIA_STT_PROVIDER"] = "whisperflow"
        os.environ["WHISPERFLOW_URL"] = "http://whisperflow.local/v1/audio/transcriptions"
        captured = {}
        orig = ask._http_post
        def fake(url, data, headers, timeout, retries=1):
            captured["url"] = url
            captured["has_wav_file"] = b'filename="speech.wav"' in data
            return b'{"text": "is the canopy wet"}'
        ask._http_post = fake
        try:
            out = ask.transcribe(b"\x00\x01\x02\x03")
        finally:
            ask._http_post = orig
        self.assertEqual(out, "is the canopy wet")
        self.assertEqual(captured["url"], "http://whisperflow.local/v1/audio/transcriptions")
        self.assertTrue(captured["has_wav_file"])


if __name__ == "__main__":
    unittest.main()

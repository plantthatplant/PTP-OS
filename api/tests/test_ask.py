"""Tests for api/ask.py — talk to Gaia (speech in, answer out).

All offline: the network hops (Whisper, Claude) are never reached because the missing-key and
empty-input guards fire first. We test the WAV framing and that every failure path is honest
(returns a message, never a crash, never an invented answer).
"""
import os
import struct
import unittest

from api import ask


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
        with self.assertRaises(ask.AskError) as cm:
            ask.transcribe(b"")
        self.assertIn("no audio", str(cm.exception))

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


if __name__ == "__main__":
    unittest.main()

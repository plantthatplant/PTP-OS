"""Talking to Gaia — speech in, Gaia's judgement out.

The glasses (or any client) POST a spoken question; Gaia transcribes it and answers it,
grounded in the current greenhouse picture. Two hops, both over plain HTTPS with urllib so
the API stays install-free (no SDKs):

    1. Speech-to-text  — OpenAI Whisper (`/v1/audio/transcriptions`)
    2. The answer      — Claude (`/v1/messages`), grounded in Gaia's morning/houses/memory

Honest by construction: if a key is missing or a hop fails, it says so plainly and never
invents an answer. The glasses are a window — all the reasoning is Claude's, over Gaia's data.

Keys (server-side env only — never sent to the glasses):
    OPENAI_API_KEY       Whisper STT
    ANTHROPIC_API_KEY    Claude
    GAIA_ANSWER_MODEL    Claude model (default claude-opus-4-8)
"""
from __future__ import annotations

import io
import json
import os
import struct
import urllib.error
import urllib.request

_OPENAI_URL = "https://api.openai.com/v1/audio/transcriptions"
_ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
_ANTHROPIC_VERSION = "2023-06-01"
_DEFAULT_MODEL = "claude-opus-4-8"

# The glasses mic emits PCM s16le @ 16 kHz mono (see the Even SDK / hardware reference).
_PCM_RATE = 16000
_PCM_CHANNELS = 1
_PCM_SAMPLE_BYTES = 2


class AskError(Exception):
    """A hop failed in a way worth telling the grower about (kept short, honest)."""


# --------------------------------------------------------------------------- speech → text

def _pcm_to_wav(pcm: bytes) -> bytes:
    """Wrap raw little-endian 16-bit PCM in a minimal WAV container so Whisper accepts it."""
    byte_rate = _PCM_RATE * _PCM_CHANNELS * _PCM_SAMPLE_BYTES
    block_align = _PCM_CHANNELS * _PCM_SAMPLE_BYTES
    header = b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVE"
    header += b"fmt " + struct.pack("<IHHIIHH", 16, 1, _PCM_CHANNELS, _PCM_RATE,
                                    byte_rate, block_align, _PCM_SAMPLE_BYTES * 8)
    header += b"data" + struct.pack("<I", len(pcm))
    return header + pcm


def transcribe(pcm: bytes) -> str:
    """PCM bytes from the glasses -> the words the grower spoke (OpenAI Whisper)."""
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise AskError("speech-to-text is not configured (OPENAI_API_KEY not set)")
    if not pcm:
        raise AskError("no audio received")

    wav = _pcm_to_wav(pcm)
    boundary = "----gaia-voice-boundary"
    parts = io.BytesIO()
    parts.write(f"--{boundary}\r\n".encode())
    parts.write(b'Content-Disposition: form-data; name="model"\r\n\r\nwhisper-1\r\n')
    parts.write(f"--{boundary}\r\n".encode())
    parts.write(b'Content-Disposition: form-data; name="file"; filename="speech.wav"\r\n')
    parts.write(b"Content-Type: audio/wav\r\n\r\n")
    parts.write(wav)
    parts.write(f"\r\n--{boundary}--\r\n".encode())
    body = parts.getvalue()

    req = urllib.request.Request(_OPENAI_URL, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise AskError(f"speech-to-text failed ({e.code})")
    except Exception:
        raise AskError("could not reach the speech-to-text service")
    return (data.get("text") or "").strip()


# --------------------------------------------------------------------------- grounding + answer

_SYSTEM = (
    "You are Gaia, the head grower's apprentice at the Kålaberga greenhouse. You answer the "
    "grower's spoken question out loud, shown as text on smart-glasses — so keep it to 1–3 short, "
    "plain sentences, no preamble, no lists, no markdown. Ground every answer ONLY in the "
    "greenhouse data provided below; if the data does not contain the answer, say so honestly "
    "(unknown is better than wrong) and, if useful, say what you'd need to observe to know. "
    "Biology comes before convenience: speak about plant health, not just numbers. Respond with "
    "the final answer only — no reasoning, no 'based on the data'."
)


def _gaia_context(service) -> str:
    """A compact snapshot of what Gaia currently knows, for grounding the answer."""
    ctx = {}
    for name, fn in (("morning", service.morning), ("houses", service.houses),
                     ("memory", lambda: service.memory(limit=8))):
        try:
            ctx[name] = fn()
        except Exception:
            ctx[name] = None
    return json.dumps(ctx, ensure_ascii=False)


def answer(question: str, service) -> str:
    """Claude answers the grower's question, grounded in Gaia's current picture."""
    question = (question or "").strip()
    if not question:
        raise AskError("I didn't catch a question")
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        raise AskError("Gaia's reasoning is not configured (ANTHROPIC_API_KEY not set)")

    model = os.environ.get("GAIA_ANSWER_MODEL", _DEFAULT_MODEL).strip() or _DEFAULT_MODEL
    payload = {
        "model": model,
        "max_tokens": 600,
        # effort low + no thinking keeps the glasses round-trip snappy; the answer is short.
        "output_config": {"effort": "low"},
        "system": f"{_SYSTEM}\n\nGREENHOUSE DATA (JSON):\n{_gaia_context(service)}",
        "messages": [{"role": "user", "content": question}],
    }
    req = urllib.request.Request(_ANTHROPIC_URL, data=json.dumps(payload).encode("utf-8"),
                                 method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("x-api-key", key)
    req.add_header("anthropic-version", _ANTHROPIC_VERSION)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = json.loads(e.read().decode("utf-8")).get("error", {}).get("message", "")
        except Exception:
            pass
        raise AskError(f"Gaia could not answer ({e.code}){': ' + detail if detail else ''}")
    except Exception:
        raise AskError("could not reach Gaia's reasoning service")

    if data.get("stop_reason") == "refusal":
        raise AskError("Gaia declined to answer that one")
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    text = text.strip()
    if not text:
        raise AskError("Gaia had no answer")
    return text


# --------------------------------------------------------------------------- endpoint

def handle_ask(body, service) -> dict:
    """POST /api/v1/ask — body is either JSON {"question": "..."} or raw PCM audio bytes.

    Returns {"question", "answer"}. On any failure returns {"answer": <honest message>, "error": ...}
    with HTTP 200 so the glasses always have a line to show (never a stack trace, never silence
    pretending to be an answer)."""
    try:
        if isinstance(body, (bytes, bytearray)):
            question = transcribe(bytes(body))
        elif isinstance(body, dict):
            question = (body.get("question") or body.get("text") or "").strip()
        else:
            question = ""
        reply = answer(question, service)
        return {"question": question, "answer": reply}
    except AskError as e:
        return {"answer": str(e), "error": str(e)}

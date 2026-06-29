"""Talking to Gaia — speech in, Gaia's judgement out.

The glasses (or any client) POST a spoken question; Gaia transcribes it and answers it,
grounded in the current greenhouse picture. Two hops, both over plain HTTPS with urllib so
the API stays install-free (no SDKs):

    1. Speech-to-text  — OpenAI Whisper (`/v1/audio/transcriptions`)
    2. The answer      — Claude (`/v1/messages`), grounded in Gaia's morning/houses/memory

Honest by construction: if a key is missing or a hop fails, it says so plainly and never
invents an answer. The glasses are a window — all the reasoning is Claude's, over Gaia's data.

Keys & config (server-side env only — never sent to the glasses):
    GAIA_STT_PROVIDER    speech-to-text engine: openai (default) | whisperflow
    OPENAI_API_KEY       Whisper STT  (openai provider)
    WHISPERFLOW_URL      WhisperFlow endpoint  (whisperflow provider; + optional WHISPERFLOW_API_KEY/MODEL)
    ANTHROPIC_API_KEY    Claude
    GAIA_ANSWER_MODEL    Claude model (default claude-opus-4-8)
"""
from __future__ import annotations

import io
import json
import logging
import os
import struct
import time
import urllib.error
import urllib.request

# Observability for the voice round-trip. We log timings and outcomes, NEVER content —
# no audio, no transcript, no answer text (the grower's words are private).
_log = logging.getLogger("gaia.ask")
if not _log.handlers:                       # be visible in dev too, without touching run.py
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("%(asctime)s gaia.ask %(message)s"))
    _log.addHandler(_h)
    _log.setLevel(logging.INFO)

_OPENAI_URL = "https://api.openai.com/v1/audio/transcriptions"
_ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
_ANTHROPIC_VERSION = "2023-06-01"
_DEFAULT_MODEL = "claude-opus-4-8"

# The glasses mic emits PCM s16le @ 16 kHz mono (see the Even SDK / hardware reference).
_PCM_RATE = 16000
_PCM_CHANNELS = 1
_PCM_SAMPLE_BYTES = 2
# A spoken question is seconds of audio (~32 KB/s). Cap the body to bound STT cost / abuse —
# ~5 minutes of 16 kHz mono PCM, well under OpenAI's 25 MB upload limit.
_MAX_AUDIO_BYTES = 10 * 1024 * 1024


class AskError(Exception):
    """A hop failed in a way worth telling the grower about (kept short, honest)."""


# Fast, transient cloud hiccups worth one retry. NOT timeouts — a hung service already made
# the grower wait once; retrying would double it, so timeouts fail fast.
_TRANSIENT_HTTP = {429, 500, 502, 503, 504}


def _http_post(url, data, headers, timeout, retries=1):
    """POST and return the raw response bytes, retrying only fast transient failures (429/5xx,
    connection resets) with a short backoff. Re-raises the underlying error — including
    `HTTPError`, so callers can read its body for a detail message."""
    attempt = 0
    while True:
        req = urllib.request.Request(url, data=data, method="POST")
        for k, v in headers.items():
            req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if attempt < retries and e.code in _TRANSIENT_HTTP:
                attempt += 1
                time.sleep(0.4 * attempt)
                continue
            raise
        except ConnectionError:                 # reset / refused / aborted — quick, safe to retry
            if attempt < retries:
                attempt += 1
                time.sleep(0.4 * attempt)
                continue
            raise
        # TimeoutError / URLError(DNS, etc.) → fail fast (no retry), surfaced as "could not reach …"


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


def _multipart_wav(wav: bytes, fields: dict):
    """Build a multipart/form-data body with text `fields` + a WAV `file`. Returns (body, boundary)."""
    boundary = "----gaia-voice-boundary"
    parts = io.BytesIO()
    for name, value in fields.items():
        parts.write(f"--{boundary}\r\n".encode())
        parts.write(f'Content-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    parts.write(f"--{boundary}\r\n".encode())
    parts.write(b'Content-Disposition: form-data; name="file"; filename="speech.wav"\r\n')
    parts.write(b"Content-Type: audio/wav\r\n\r\n")
    parts.write(wav)
    parts.write(f"\r\n--{boundary}--\r\n".encode())
    return parts.getvalue(), boundary


def _read_transcript(raw: bytes) -> str:
    data = json.loads(raw.decode("utf-8"))
    return (data.get("text") or data.get("transcript") or "").strip()   # OpenAI-compatible {text}


def _stt_openai(wav: bytes) -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise AskError("speech-to-text is not configured (OPENAI_API_KEY not set)")
    body, boundary = _multipart_wav(wav, {"model": "whisper-1"})
    headers = {"Authorization": f"Bearer {key}",
               "Content-Type": f"multipart/form-data; boundary={boundary}"}
    try:
        return _read_transcript(_http_post(_OPENAI_URL, body, headers, timeout=30))
    except urllib.error.HTTPError as e:
        raise AskError(f"speech-to-text failed ({e.code})")
    except AskError:
        raise
    except Exception:
        raise AskError("could not reach the speech-to-text service")


def _stt_whisperflow(wav: bytes) -> str:
    """WhisperFlow STT — an alternate/self-hosted Whisper service (GAIA_STT_PROVIDER=whisperflow).
    Expects an OpenAI-compatible transcription endpoint (multipart `file` → JSON `{text}`); if
    WhisperFlow's request/response shape differs, THIS is the one place to adapt it. Config:
    WHISPERFLOW_URL (required), WHISPERFLOW_API_KEY (optional), WHISPERFLOW_MODEL (optional)."""
    url = os.environ.get("WHISPERFLOW_URL", "").strip()
    if not url:
        raise AskError("speech-to-text is not configured (WHISPERFLOW_URL not set)")
    fields = {}
    model = os.environ.get("WHISPERFLOW_MODEL", "").strip()
    if model:
        fields["model"] = model
    body, boundary = _multipart_wav(wav, fields)
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    key = os.environ.get("WHISPERFLOW_API_KEY", "").strip()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    try:
        return _read_transcript(_http_post(url, body, headers, timeout=30))
    except urllib.error.HTTPError as e:
        raise AskError(f"speech-to-text failed ({e.code})")
    except AskError:
        raise
    except Exception:
        raise AskError("could not reach the speech-to-text service")


_STT_PROVIDERS = {"openai": _stt_openai, "whisperflow": _stt_whisperflow}


def transcribe(pcm: bytes) -> str:
    """PCM bytes from the glasses → the words the grower spoke. The STT engine is a SERVER-SIDE,
    swappable choice (GAIA_STT_PROVIDER=openai|whisperflow) — clients never transcribe; they only
    stream audio. The grounding/answer hop is unchanged regardless of provider."""
    if not pcm:
        raise AskError("no audio received")
    if len(pcm) > _MAX_AUDIO_BYTES:
        raise AskError("that was too long to transcribe — ask a shorter question")
    provider = os.environ.get("GAIA_STT_PROVIDER", "openai").strip().lower() or "openai"
    fn = _STT_PROVIDERS.get(provider)
    if fn is None:
        raise AskError(f"unknown speech-to-text provider '{provider}'")
    return fn(_pcm_to_wav(pcm))


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
    headers = {"Content-Type": "application/json", "x-api-key": key,
               "anthropic-version": _ANTHROPIC_VERSION}
    try:
        data = json.loads(_http_post(_ANTHROPIC_URL, json.dumps(payload).encode("utf-8"),
                                     headers, timeout=60).decode("utf-8"))
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

def _ms(t0: float) -> int:
    return round((time.monotonic() - t0) * 1000)


def handle_ask(body, service) -> dict:
    """POST /api/v1/ask — body is either JSON {"question": "..."} or raw PCM audio bytes.

    Returns {"question", "answer"}. On any failure returns {"answer": <honest message>, "error": ...}
    with HTTP 200 so the glasses always have a line to show (never a stack trace, never silence
    pretending to be an answer). Emits one structured, content-free log line per call."""
    t_start = time.monotonic()
    event = {"source": "audio" if isinstance(body, (bytes, bytearray)) else "text",
             "model": os.environ.get("GAIA_ANSWER_MODEL", _DEFAULT_MODEL)}
    phase = "input"
    try:
        if isinstance(body, (bytes, bytearray)):
            event["audio_bytes"] = len(body)
            event["stt_provider"] = os.environ.get("GAIA_STT_PROVIDER", "openai").strip().lower() or "openai"
            phase = "stt"
            t = time.monotonic()
            question = transcribe(bytes(body))
            event["stt_ms"] = _ms(t)
        elif isinstance(body, dict):
            question = (body.get("question") or body.get("text") or "").strip()
        else:
            question = ""
        event["chars_in"] = len(question)        # length only — never the words themselves
        phase = "answer"
        t = time.monotonic()
        reply = answer(question, service)
        event["answer_ms"] = _ms(t)
        event["chars_out"] = len(reply)
        event["ok"] = True
        event["total_ms"] = _ms(t_start)
        _log.info(json.dumps(event, ensure_ascii=False))
        return {"question": question, "answer": reply}
    except AskError as e:
        event.update(ok=False, failed_at=phase, error=str(e), total_ms=_ms(t_start))
        _log.info(json.dumps(event, ensure_ascii=False))
        return {"answer": str(e), "error": str(e)}

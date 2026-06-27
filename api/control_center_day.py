#!/usr/bin/env python3
"""Gaia Control Center — a complete founder day using ONLY the Gaia API.

This is the reference Lovable must mirror: `GaiaClient` below imports NOTHING from the Brain —
it is pure HTTP. Every screen's data comes from an endpoint; every action is a POST. If this
client ever "decided" anything, that would be a bug (it can't — it has no engines).

It runs a full day: Morning Brief → Walk (companion) → Voice Note → Question → Memory →
Observation history → Learning → Evening Review.

    python api/control_center_day.py
"""
from __future__ import annotations

import json
import os
import sys
import threading
import urllib.request
import urllib.error

# --- the client half: PURE HTTP (this is all Lovable is) -----------------------
class GaiaClient:
    def __init__(self, base, api_key):
        self.base, self.key = base.rstrip("/"), api_key

    def _req(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, method=method,
                                     headers={"Authorization": f"Bearer {self.key}",
                                              "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read().decode())

    # one method per screen/action — thin pass-throughs, no logic
    def morning(self):                return self._req("GET", "/api/v1/morning")
    def companion(self):              return self._req("GET", "/api/v1/companion")
    def houses(self):                 return self._req("GET", "/api/v1/houses")
    def memory(self):                 return self._req("GET", "/api/v1/memory")
    def knowledge_gaps(self):         return self._req("GET", "/api/v1/knowledge-gaps")
    def learning(self):               return self._req("GET", "/api/v1/learning")
    def observations(self):           return self._req("GET", "/api/v1/observations")
    def questions(self):              return self._req("GET", "/api/v1/questions")
    def evening(self):                return self._req("GET", "/api/v1/evening")
    def voice_note(self, text, subject="site"): return self._req("POST", "/api/v1/voice-notes", {"text": text, "subject": subject})
    def capture(self, obs):           return self._req("POST", "/api/v1/observations", obs)
    def answer(self, qid, text):      return self._req("POST", f"/api/v1/questions/{qid}/answer", {"answer": text})


def _screen(title, endpoint, render):
    print("\n" + "─" * 66)
    print(f"  SCREEN: {title}    ← {endpoint}")
    print("─" * 66)
    render()


def run_day(client: GaiaClient):
    m = client.morning()
    _screen("Morning Brief", "GET /api/v1/morning", lambda: (
        print(f"   {m['greenhouse']} — {m['brief']}"),
        print(f"   Do first: {m['priority']}"),
        print(f"   Confidence: {m['confidence']}   Ask today: {m['ask_today']}")))

    c = client.companion()
    _screen("Companion (Even G2)", "GET /api/v1/companion", lambda: (
        print(f"   ▸ {c['message']}   [{c['urgency']}, confidence {c['confidence']}]")))

    _screen("Greenhouses", "GET /api/v1/houses", lambda: [
        print(f"   {h['id']} {h['name']}: {h['status']}"
              + (f"  ({h['climate']['air_temperature_c']}°C / {h['climate']['humidity_pct']}%RH)"
                 if h.get('climate') else "")) for h in client.houses()])

    vn = client.voice_note("brown spots on lower leaves, bench 3", subject="h1")
    _screen("Voice Note → Observation", "POST /api/v1/voice-notes", lambda: (
        print(f"   captured: {vn['observation']['value']}  [{vn['observation']['method']}]")))

    cap = client.capture({"subject": "h1", "kind": "leaf-wetness", "value": "canopy dry now",
                          "source": "grower", "method": "observed-by-human", "confidence": "high"})
    _screen("Observation Capture", "POST /api/v1/observations", lambda: (
        print(f"   accepted: {cap['accepted']}, rejected: {cap['rejected']}")))

    qs = client.questions()
    _screen("Question → Answer", "GET /questions + POST /questions/{id}/answer", lambda: None)
    if qs:
        ans = client.answer(qs[0]["id"], "No, the canopy is dry")
        print(f"   Q: {qs[0]['text']}")
        print(f"   A: 'No, the canopy is dry'  → confidence {ans.get('confidence_before')} → "
              f"{ans.get('confidence_after')} (worthwhile: {ans.get('worthwhile')})")
    else:
        print("   (no question worth asking today)")

    _screen("Observation History", "GET /api/v1/observations", lambda: [
        print(f"   {o['captured_at']}  {o['subject']} {o['kind']}: {o['value']}") for o in client.observations()[:5]])

    _screen("Memory", "GET /api/v1/memory", lambda: ([
        print(f"   {mm['zone']}: {mm['lesson']}") for mm in client.memory()[:5]] or [print("   (no lessons yet)")]))

    lr = client.learning()
    _screen("Learning", "GET /api/v1/learning", lambda: (
        print(f"   experiments: {lr['experiments_open']} open / {lr['experiments_closed']} closed"),
        print(f"   calibration (predictions held): {lr['calibration']['hold_rate']}")))

    ev = client.evening()
    _screen("Evening Review", "GET /api/v1/evening", lambda: (
        print(f"   reviewed: {ev['reviewed']}   open experiments: {ev['open_experiments']}"),
        print(f"   calibration: {ev['calibration']['hold_rate']}")))


def main() -> int:
    # Host the API for the demo (in production the API runs as its own service; Lovable only
    # ever sees HTTP). The client below shares no code with the Brain.
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.service import GaiaService
    from api import server
    key = "gaia-dev-key"
    sample = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "app", "sample_snapshot.json")
    httpd = server.serve(port=0, service=GaiaService(snapshot_path=sample), api_key=key)
    base = f"http://127.0.0.1:{httpd.server_address[1]}"
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    print("=" * 66)
    print("  GAIA CONTROL CENTER — one founder day, using ONLY the Gaia API")
    print("  (this client imports nothing from the Brain — it is pure HTTP)")
    print("=" * 66)
    try:
        run_day(GaiaClient(base, key))
        print("\n" + "─" * 66)
        print("  Every screen above came from an endpoint. The client decided nothing.")
        print("  The Brain remained the only source of truth.")
    finally:
        httpd.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

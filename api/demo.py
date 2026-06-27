#!/usr/bin/env python3
"""Demonstrate the Gaia API: one gateway, many clients, over real HTTP.

Starts the stdlib server and calls it with urllib (no dependencies), the way Lovable, Even G2,
mobile, desktop, DJI, or a robot would — each receives only Gaia's understanding.

    python api/demo.py
"""
from __future__ import annotations

import json
import os
import sys
import threading
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.service import GaiaService
from api import server


def _call(base, key, method, path, body=None):
    url = base + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Authorization": f"Bearer {key}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as r:
        return r.status, json.loads(r.read().decode())


def _show(title, status, obj, keys=None):
    print(f"\n  {title}   → {status}")
    if isinstance(obj, list):
        for x in obj[:3]:
            print("    ·", json.dumps(x, ensure_ascii=False)[:96])
    else:
        for k in (keys or obj.keys()):
            if k in obj:
                print(f"    {k}: {json.dumps(obj[k], ensure_ascii=False)[:92]}")


def main() -> int:
    key = "gaia-dev-key"
    sample = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "app", "sample_snapshot.json")
    httpd = server.serve(port=0, service=GaiaService(snapshot_path=sample), api_key=key)
    base = f"http://127.0.0.1:{httpd.server_address[1]}/api/v1"
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        print("=" * 64 + "\nONE API, MANY CLIENTS — every client below uses the SAME endpoints\n" + "=" * 64)

        print("\n[ Lovable / Mobile / Desktop ] read the morning understanding:")
        s, o = _call(base, key, "GET", "/morning")
        _show("GET /api/v1/morning", s, o, keys=["greenhouse", "brief", "priority", "confidence", "ask_today"])

        print("\n[ Even G2 ] reads only the companion surface:")
        s, o = _call(base, key, "GET", "/companion")
        _show("GET /api/v1/companion", s, o)

        print("\n[ Even G2 / mobile ] sends a voice note — the API makes it a Canonical Observation:")
        s, o = _call(base, key, "POST", "/voice-notes", {"text": "brown spots on lower leaves, bench 3", "subject": "h1"})
        _show("POST /api/v1/voice-notes", s, o, keys=["accepted", "observation"])

        print("\n[ DJI / camera ] posts a Canonical Observation (no client-specific payload):")
        s, o = _call(base, key, "POST", "/observations",
                     {"subject": "h2", "kind": "leaf-wetness", "value": "canopy wet, bench 3",
                      "source": "dji", "method": "vision-inferred", "confidence": "medium"})
        _show("POST /api/v1/observations", s, o)

        print("\n[ any client ] answers the day's question:")
        s, qs = _call(base, key, "GET", "/questions")
        if qs:
            qid = qs[0]["id"]
            s, o = _call(base, key, "POST", f"/questions/{qid}/answer", {"answer": "No, the canopy is dry"})
            _show(f"POST /api/v1/questions/{qid}/answer", s, o)

        print("\n[ unauthenticated client ] is refused:")
        try:
            _call(base, "wrong-key", "GET", "/morning")
        except urllib.error.HTTPError as e:
            print(f"    GET /morning (bad key) → {e.code}  {e.read().decode()[:80]}")

        print("\n" + "-" * 64)
        print("  The Brain never knew which client called. Each got only understanding.")
    finally:
        httpd.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

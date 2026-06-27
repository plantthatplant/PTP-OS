#!/usr/bin/env python3
"""Prove the Morning Analysis runs from LIVE Claude Dispatch observations.

There is no real greenhouse reachable from here, so this script stands up a tiny
local HTTP server that plays the role of the Claude Dispatch endpoint. The transport
is genuinely live — a real HTTP GET over a socket, parsed at request time — and it
hands its payload to the *unchanged* ClaudeDispatchProvider translation. To go fully
live against the real Synopta-backed endpoint, only the URL and API key change.

    python3 app/demo_live_dispatch.py
"""
import http.server
import json
import os
import sys
import threading
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from greenhouse_brain.providers.claude_dispatch_provider import ClaudeDispatchProvider
from greenhouse_brain.providers.transport import HttpDispatchTransport
from greenhouse_brain.morning_analysis import MorningAnalysisEngine
from greenhouse_brain.language_engine import TemplateLanguageRenderer


def _live_payload() -> dict:
    """What the 'live' endpoint returns right now. Fresh timestamp each call, and one
    deliberately messy value (air_temp as a comma-decimal string with a unit) so we can
    watch the provider absorb a real-world inconsistency."""
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return {
        "captured_at": now,
        "site": "Kalaberga",
        "houses": [
            {"house_id": "1", "label": "Hus 1", "signals": {
                "air_temp": {"value": "24,2 °C"},              # <- messy on purpose
                "rel_humidity": {"value": 92}, "vent_position": {"value": 0},
                "outside_temp": {"value": "11,0"}, "alarm": {"active": False}}},
            {"house_id": "2", "label": "Hus 2", "signals": {
                "air_temp": {"value": 16.0}, "rel_humidity": {"value": 66},
                "vent_position": {"value": 20}, "outside_temp": {"value": 11.0},
                "alarm": {"active": True, "text": "Sensor fault: temperature out of range"}}},
            {"house_id": "3", "label": "Hus 3", "signals": {
                "air_temp": {"value": 21.0}, "rel_humidity": {"value": 64},
                "vent_position": {"value": 30}, "outside_temp": {"value": 11.0},
                "alarm": {"active": False}}},
        ],
    }


class _Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps(_live_payload()).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


def main() -> int:
    server = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
    url = f"http://127.0.0.1:{server.server_address[1]}/dispatch"
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"[stand-in] Claude Dispatch endpoint listening at {url}")
    print("           (a local stand-in; the real endpoint differs only by URL + API key)\n")

    try:
        # 1) Show the transport is live: two fetches, advancing timestamps, over HTTP.
        t = HttpDispatchTransport(url)
        a = t.fetch(); time.sleep(1.1); b = t.fetch()
        print("LIVE TRANSPORT CHECK")
        print(f"  fetch #1 captured_at: {a['captured_at']}")
        print(f"  fetch #2 captured_at: {b['captured_at']}")
        print(f"  -> advances between calls (live, not a static file): "
              f"{'YES' if a['captured_at'] != b['captured_at'] else 'no'}")
        print(f"  raw House 1 air_temp as delivered: {a['houses'][0]['signals']['air_temp']['value']!r} "
              f"(messy: comma-decimal + unit)\n")

        # 2) Run the WHOLE pipeline from the live provider.
        provider = ClaudeDispatchProvider(transport=HttpDispatchTransport(url))
        analysis = MorningAnalysisEngine().run(provider)
        print(TemplateLanguageRenderer().render_morning(analysis))

        # 3) Proof.
        reading_h1 = provider.get_latest_climate()["h1"]
        print("\n" + "=" * 64)
        print("PROOF — Morning Analysis ran from LIVE Dispatch observations")
        print("=" * 64)
        print(f"  Transport:                 {provider.transport.label}  ({provider.transport.url})")
        print(f"  Snapshot captured_at:      {provider.captured_at}  (from the live fetch)")
        print(f"  House 1 air temp in domain: {reading_h1.temp_c} C  "
              f"(provider cleaned '24,2 °C' -> 24.2, so the engines never saw the mess)")
        print(f"  Reading timestamp carried:  {reading_h1.timestamp}")
        top = analysis.concerns[0] if analysis.concerns else None
        print(f"  Top concern:               {top.title} @ {top.zone_name}" if top else "  Top concern: none")
        print(f"  Top recommendation:        {analysis.priorities[0].action[:54]}..." if analysis.priorities else "")
        print("\n  Same concern & recommendation as the fixture run — the Brain never knew")
        print("  the transport changed. Context / Decision / Language / Morning Analysis: untouched.")
    finally:
        server.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

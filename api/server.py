"""Gaia API HTTP layer — stdlib only (no web framework, keeps the project install-free).

Maps versioned routes to GaiaService methods and returns JSON. It is a thin transport: it does
no reasoning and holds no session (stateless). Auth, versioning, and a uniform error envelope
live here; understanding comes from the service.

    python api/server.py            # serve on 127.0.0.1:8000 (GAIA_API_KEY from env, else dev key)
"""
from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from .service import GaiaService
from .web import home_page

API_VERSION = "v1"
_DEV_KEY = "gaia-dev-key"
_PUBLIC = ("/api/v1/health", "/", "/index.html")   # reachable without an API key


def _auth_key():
    return os.environ.get("GAIA_API_KEY", _DEV_KEY)


# (method, compiled-path-regex) -> handler(service, match, query, body) -> (status, obj)
def _routes():
    p = lambda s: re.compile(r"^/api/v1" + s + r"$")
    return [
        ("GET", p(r"/morning"), lambda s, m, q, b: (200, s.morning())),
        ("GET", p(r"/houses"), lambda s, m, q, b: (200, s.houses())),
        ("GET", p(r"/houses/(?P<id>[^/]+)"),
         lambda s, m, q, b: ((200, s.house(m["id"])) if s.house(m["id"]) else (404, _err("not_found", "no such house")))),
        ("GET", p(r"/memory"), lambda s, m, q, b: (200, s.memory())),
        ("GET", p(r"/memory/search"), lambda s, m, q, b: (200, s.memory_search(q.get("q", [""])[0]))),
        ("GET", p(r"/knowledge-gaps"), lambda s, m, q, b: (200, s.knowledge_gaps())),
        ("GET", p(r"/learning"), lambda s, m, q, b: (200, s.learning())),
        ("GET", p(r"/questions"), lambda s, m, q, b: (200, s.questions())),
        ("GET", p(r"/companion"), lambda s, m, q, b: (200, s.companion())),
        ("GET", p(r"/evening"), lambda s, m, q, b: (200, s.evening())),
        ("GET", p(r"/health"), lambda s, m, q, b: (200, s.health())),
        ("GET", p(r"/observations"), lambda s, m, q, b: (200, s.observations())),
        ("POST", p(r"/observations"), lambda s, m, q, b: (201, s.post_observation(b))),
        ("POST", p(r"/questions/(?P<id>[^/]+)/answer"),
         lambda s, m, q, b: (200, s.answer_question(m["id"], (b or {}).get("answer", "")))),
        ("POST", p(r"/voice-notes"),
         lambda s, m, q, b: (201, s.voice_note((b or {}).get("text", ""), (b or {}).get("subject", "site")))),
    ]


def _err(code, message):
    return {"error": {"code": code, "message": message}}


def make_handler(service: GaiaService, api_key: str, logger=None):
    routes = _routes()
    log = logger or (lambda rec: None)
    home = home_page(api_key)

    class Handler(BaseHTTPRequestHandler):
        server_version = "GaiaAPI/v1"

        # Browser clients (Lovable, the Even Hub web plugin) call cross-origin, so every
        # response carries CORS headers and OPTIONS preflight is answered. The API stays the
        # single source of truth; this only permits the window to reach it (Sprint 12 blocker #4).
        def _cors(self):
            origin = self.headers.get("Origin", "*")
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, X-API-Key")
            self.send_header("Access-Control-Max-Age", "86400")

        def _send(self, status, obj):
            body = json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Gaia-API-Version", API_VERSION)
            self.send_header("Content-Length", str(len(body)))
            self._cors()
            self.end_headers()
            self.wfile.write(body)

        def _send_html(self, status, html):
            body = html.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self._cors()
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self):
            # CORS preflight — never needs auth; answer it before the key check.
            self.send_response(204)
            self._cors()
            self.end_headers()

        def _authed(self) -> bool:
            auth = self.headers.get("Authorization", "")
            key = auth[7:] if auth.startswith("Bearer ") else self.headers.get("X-API-Key", "")
            return key == api_key

        def _log(self, method, path, status, t0, error=None):
            log({"timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 "client": self.client_address[0], "method": method, "endpoint": path,
                 "status": status, "response_ms": round((time.monotonic() - t0) * 1000, 1),
                 "error": error})

        def _dispatch(self, method):
            t0 = time.monotonic()
            parsed = urlparse(self.path)
            # Built-in Control Center page (public, HTML).
            if method == "GET" and parsed.path in ("/", "/index.html"):
                self._send_html(200, home)
                return self._log(method, parsed.path, 200, t0)
            if parsed.path not in _PUBLIC and not self._authed():
                self._send(401, _err("unauthorized", "missing or invalid API key"))
                return self._log(method, parsed.path, 401, t0, "unauthorized")
            body = None
            if method == "POST":
                length = int(self.headers.get("Content-Length", 0) or 0)
                raw = self.rfile.read(length) if length else b""
                try:
                    body = json.loads(raw or b"null")
                except json.JSONDecodeError:
                    self._send(400, _err("bad_request", "body must be valid JSON"))
                    return self._log(method, parsed.path, 400, t0, "bad_json")
            status, obj, error, path_matched = None, None, None, False
            for rm, rx, fn in routes:
                mobj = rx.match(parsed.path)
                if not mobj:
                    continue
                path_matched = True
                if rm != method:
                    continue
                try:
                    status, obj = fn(service, mobj.groupdict(), parse_qs(parsed.query), body)
                except Exception as e:                       # never leak a stack trace to a client
                    status, obj, error = 500, _err("internal_error", str(e)[:200]), str(e)[:200]
                break
            if status is None:
                status = 405 if path_matched else 404
                obj = _err("method_not_allowed" if path_matched else "not_found", f"{method} {parsed.path}")
                error = obj["error"]["code"]
            self._send(status, obj)
            self._log(method, parsed.path, status, t0, error)

        def do_GET(self):
            self._dispatch("GET")

        def do_POST(self):
            self._dispatch("POST")

        def log_message(self, *a):
            pass

    return Handler


def serve(host="127.0.0.1", port=8000, service=None, api_key=None, logger=None):
    service = service or GaiaService()
    api_key = api_key or _auth_key()
    httpd = ThreadingHTTPServer((host, port), make_handler(service, api_key, logger))
    print(f"Gaia API {API_VERSION} on http://{host}:{httpd.server_address[1]}/api/v1  "
          f"(auth: {'set' if api_key != _DEV_KEY else 'dev key'})")
    return httpd


if __name__ == "__main__":
    serve().serve_forever()

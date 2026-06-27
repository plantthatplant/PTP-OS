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
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from .service import GaiaService

API_VERSION = "v1"
_DEV_KEY = "gaia-dev-key"


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
        ("POST", p(r"/observations"), lambda s, m, q, b: (201, s.post_observation(b))),
        ("POST", p(r"/questions/(?P<id>[^/]+)/answer"),
         lambda s, m, q, b: (200, s.answer_question(m["id"], (b or {}).get("answer", "")))),
        ("POST", p(r"/voice-notes"),
         lambda s, m, q, b: (201, s.voice_note((b or {}).get("text", ""), (b or {}).get("subject", "site")))),
    ]


def _err(code, message):
    return {"error": {"code": code, "message": message}}


def make_handler(service: GaiaService, api_key: str):
    routes = _routes()

    class Handler(BaseHTTPRequestHandler):
        server_version = "GaiaAPI/v1"

        def _send(self, status, obj):
            body = json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Gaia-API-Version", API_VERSION)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _authed(self) -> bool:
            auth = self.headers.get("Authorization", "")
            key = auth[7:] if auth.startswith("Bearer ") else self.headers.get("X-API-Key", "")
            return key == api_key

        def _dispatch(self, method):
            parsed = urlparse(self.path)
            if not self._authed():
                return self._send(401, _err("unauthorized", "missing or invalid API key"))
            body = None
            if method == "POST":
                length = int(self.headers.get("Content-Length", 0) or 0)
                raw = self.rfile.read(length) if length else b""
                try:
                    body = json.loads(raw or b"null")
                except json.JSONDecodeError:
                    return self._send(400, _err("bad_request", "body must be valid JSON"))
            path_matched = False
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
                    status, obj = 500, _err("internal_error", str(e)[:200])
                return self._send(status, obj)
            return self._send(405 if path_matched else 404,
                              _err("method_not_allowed" if path_matched else "not_found",
                                   f"{method} {parsed.path}"))

        def do_GET(self):
            self._dispatch("GET")

        def do_POST(self):
            self._dispatch("POST")

        def log_message(self, *a):
            pass

    return Handler


def serve(host="127.0.0.1", port=8000, service=None, api_key=None):
    service = service or GaiaService()
    api_key = api_key or _auth_key()
    httpd = ThreadingHTTPServer((host, port), make_handler(service, api_key))
    print(f"Gaia API {API_VERSION} on http://{host}:{httpd.server_address[1]}/api/v1  "
          f"(auth: {'set' if api_key != _DEV_KEY else 'dev key'})")
    return httpd


if __name__ == "__main__":
    serve().serve_forever()

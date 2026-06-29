"""CORS tests — the API permits browser windows to reach it, with an env-configurable allowlist.

Default ("*") reflects any Origin (fine for a token-authed API in dev). A configured allowlist
(GAIA_CORS_ORIGINS) permits only listed origins and sends no CORS headers for the rest, so a
disallowed browser origin is blocked by the browser.
"""
import threading
import unittest
import urllib.request

from api.server import serve


class _StubService:
    def companion(self): return {"message": "", "urgency": "info"}


class CorsTest(unittest.TestCase):
    def _serve(self):
        httpd = serve(host="127.0.0.1", port=0, service=_StubService(), api_key="k")
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        return httpd, httpd.server_address[1]

    def _preflight_origin(self, port, origin):
        req = urllib.request.Request(f"http://127.0.0.1:{port}/api/v1/companion", method="OPTIONS")
        req.add_header("Origin", origin)
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, r.headers.get("Access-Control-Allow-Origin")

    def test_default_reflects_any_origin(self):
        import os
        os.environ.pop("GAIA_CORS_ORIGINS", None)
        httpd, port = self._serve()
        try:
            status, acao = self._preflight_origin(port, "https://anything.example")
            self.assertEqual(status, 204)
            self.assertEqual(acao, "https://anything.example")
        finally:
            httpd.shutdown()

    def test_allowlist_permits_listed_and_blocks_others(self):
        import os
        os.environ["GAIA_CORS_ORIGINS"] = "https://good.example, https://lovable.app"
        httpd, port = self._serve()
        try:
            _, allowed = self._preflight_origin(port, "https://good.example")
            self.assertEqual(allowed, "https://good.example")
            _, blocked = self._preflight_origin(port, "https://evil.example")
            self.assertIsNone(blocked)   # no CORS header → the browser blocks it
        finally:
            httpd.shutdown()
            os.environ.pop("GAIA_CORS_ORIGINS", None)


if __name__ == "__main__":
    unittest.main()

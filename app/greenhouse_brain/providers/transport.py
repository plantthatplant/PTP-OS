"""Dispatch transport — *only* how the raw payload is fetched.

This is the single thing that changes between "captured fixture" and "live Claude
Dispatch". The translation in ClaudeDispatchProvider does not know or care which one
it got — it always receives a raw payload dict.

  FixtureTransport     -> reads the bundled sample file (offline, deterministic)
  HttpDispatchTransport -> GETs live JSON from a Claude Dispatch endpoint over HTTP

Swapping fixture -> live is choosing a different transport at composition time. No
code above the Provider Layer is touched.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from abc import ABC, abstractmethod

_SAMPLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_claude_dispatch.json")


class DispatchError(Exception):
    """A transport failure (unreachable, bad status, unparseable body)."""


class DispatchTransport(ABC):
    label = "transport"

    @abstractmethod
    def fetch(self) -> dict:
        """Return the raw Claude Dispatch payload as a dict."""


class FixtureTransport(DispatchTransport):
    label = "fixture"

    def __init__(self, path: str = _SAMPLE):
        self.path = path

    def fetch(self) -> dict:
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)


class HttpDispatchTransport(DispatchTransport):
    label = "live-http"

    def __init__(self, url: str, api_key: str = None, timeout: float = 5.0):
        self.url = url
        self.api_key = api_key
        self.timeout = timeout

    def fetch(self) -> dict:
        req = urllib.request.Request(self.url, headers={"Accept": "application/json"})
        if self.api_key:
            req.add_header("Authorization", f"Bearer {self.api_key}")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.URLError as e:               # unreachable, timeout, non-2xx
            raise DispatchError(f"Claude Dispatch unreachable: {e}") from e
        try:
            return json.loads(body)
        except json.JSONDecodeError as e:
            raise DispatchError(f"Claude Dispatch returned an unparseable body: {e}") from e

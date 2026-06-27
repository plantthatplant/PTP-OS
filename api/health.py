"""Shared health/uptime state — the supervisor updates it; /health reads it.

A tiny module singleton so the request handler and the service can report liveness without the
supervisor and the server sharing object references everywhere.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class HealthState:
    def __init__(self, version="1.0.0"):
        self._t0 = time.monotonic()
        self.version = version
        self.last_collection = None        # {"at":iso,"status":str,"snapshot_at":iso}
        self.last_analysis_at = None        # iso of the last successful morning composition

    def record_collection(self, status: str, snapshot_at=None):
        self.last_collection = {"at": _now(), "status": status, "snapshot_at": snapshot_at}

    def record_analysis(self):
        self.last_analysis_at = _now()

    def uptime_seconds(self) -> int:
        return int(time.monotonic() - self._t0)


STATE = HealthState()

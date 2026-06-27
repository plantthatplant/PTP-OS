"""Shared paths, and the one bit of wiring that lets the Collector reuse the Brain's
canonical snapshot model for validation.

The Collector is a separate component, but it validates its output by round-tripping it
through Gaia's *own* importer — so 'valid' means 'exactly what Gaia can read', not a second
opinion. That requires app/ on the import path; this module is the single place that happens.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
APP_DIR = os.path.join(REPO_ROOT, "app")

# The Collector writes here; Gaia reads data/inbox/latest.json (specs/gaia-collector.md).
DATA_DIR = os.path.join(REPO_ROOT, "data")
INBOX_DIR = os.path.join(DATA_DIR, "inbox")
LATEST = os.path.join(INBOX_DIR, "latest.json")
HISTORY_DIR = os.path.join(INBOX_DIR, "history")        # immutable past snapshots
QUARANTINE_DIR = os.path.join(INBOX_DIR, "quarantine")  # snapshots that failed validation
LOGS_DIR = os.path.join(DATA_DIR, "logs")

if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

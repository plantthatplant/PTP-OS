"""Put the Brain (app/) and repo root on the import path so the API can compose the engines.

This is the ONLY component permitted to import the Brain's internals (store, knowledge_gap,
lifecycle, fusion, providers, observers). Clients go through the API, never around it.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
APP_DIR = os.path.join(REPO_ROOT, "app")
for _p in (REPO_ROOT, APP_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

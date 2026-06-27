"""Put the Brain (app/) on the import path so the Companion can consume its engines.

The Companion is a separate component, but it reads Gaia's own engines and persistence rather
than reimplementing them. This is the single place that wiring happens.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
APP_DIR = os.path.join(REPO_ROOT, "app")

if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

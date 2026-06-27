"""Field Companion tests — standard-library unittest, no dependencies.

    python -m unittest discover -s companion/tests
"""
import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for p in (_REPO_ROOT, os.path.join(_REPO_ROOT, "app")):
    if p not in sys.path:
        sys.path.insert(0, p)

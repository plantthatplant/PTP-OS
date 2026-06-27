"""Gaia API tests — standard-library unittest. Run: python -m unittest discover -s api/tests"""
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for p in (_REPO, os.path.join(_REPO, "app")):
    if p not in sys.path:
        sys.path.insert(0, p)

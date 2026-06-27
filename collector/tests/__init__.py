"""Collector test suite. Dependency-free — standard library `unittest` only, in keeping
with the repo's 'no install, no dependencies' ethos.

Run from the repo root:
    python -m unittest discover -s collector/tests
"""
import os
import sys

# Make `import collector...` and `import greenhouse_brain...` work no matter the cwd.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for p in (_REPO_ROOT, os.path.join(_REPO_ROOT, "app")):
    if p not in sys.path:
        sys.path.insert(0, p)

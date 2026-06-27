#!/usr/bin/env python3
"""Give quick feedback on this morning's recommendations (~30 seconds).

Rate each as Correct / Partially / Incorrect, with an optional one-line why.
It is captured for future learning — not analysed or acted on yet.

Usage:
    python3 app/morning.py      # first, prepare the morning analysis
    python3 app/feedback.py     # then, the 30-second review
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from greenhouse_brain import store
from greenhouse_brain.feedback import review


def _ask(prompt: str) -> str:
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        return "q"


def main() -> int:
    analysis = store.load()
    if analysis is None:
        print("No morning analysis yet. Run:  python3 app/morning.py")
        return 1

    print(f"Reviewing the analysis prepared at {analysis.prepared_at}.\n")
    saved = review(analysis, _ask, print)
    print(f"Saved {saved} response(s). Thank you — captured for future learning, "
          f"not acted on yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

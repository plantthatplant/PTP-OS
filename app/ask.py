#!/usr/bin/env python3
"""Ask the Greenhouse Brain a question.

Usage:
    python3 app/ask.py
    python3 app/ask.py "How is the greenhouse today?"

No dependencies, no install, no API keys — just Python 3.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from greenhouse_brain import GreenhouseBrain


def main() -> int:
    question = " ".join(sys.argv[1:]).strip() or "How is the greenhouse today?"
    print(GreenhouseBrain().answer(question))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

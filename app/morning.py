#!/usr/bin/env python3
"""Run the morning analysis — the Brain's proactive start to the day.

This is what runs 'before everyone arrives': it collects everything, works out the
day, prints the full briefing, and stores it so that asking 'How is the greenhouse
today?' later returns this same, already-prepared picture.

Usage:
    python3 app/morning.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from greenhouse_brain import GreenhouseBrain


def main() -> int:
    print(GreenhouseBrain().morning_briefing())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

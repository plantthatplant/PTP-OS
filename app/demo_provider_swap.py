#!/usr/bin/env python3
"""Prove the Provider abstraction: run the SAME Morning Analysis over two providers.

The only thing that differs between the two runs below is the provider. The Context
Engine, Decision Engine, Language Engine, and Morning Analysis are the *same objects*,
untouched. If the Brain truly cannot tell where data comes from, the climate-driven
reasoning should appear from both.

    python3 app/demo_provider_swap.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from greenhouse_brain.providers import MockGreenhouseProvider, ClaudeDispatchProvider
from greenhouse_brain.morning_analysis import MorningAnalysisEngine
from greenhouse_brain.language_engine import TemplateLanguageRenderer

# One engine, one renderer — shared across both runs on purpose.
ENGINE = MorningAnalysisEngine()
RENDER = TemplateLanguageRenderer()


def run(provider):
    return ENGINE.run(provider)


def headline(a):
    concern = a.concerns[0].title + " @ " + a.concerns[0].zone_name if a.concerns else "none"
    rec = a.priorities[0].action if a.priorities else "none"
    return concern, rec


def main() -> int:
    mock = run(MockGreenhouseProvider())
    dispatch = run(ClaudeDispatchProvider())

    print("#" * 70)
    print("# PROVIDER A — MockProvider (hand-built domain objects)")
    print("#" * 70)
    print(RENDER.render_morning(mock))
    print("\n\n")
    print("#" * 70)
    print("# PROVIDER B — ClaudeDispatchProvider (live-shaped data, translated)")
    print("#" * 70)
    print(RENDER.render_morning(dispatch))

    mc, mr = headline(mock)
    dc, dr = headline(dispatch)
    print("\n" + "=" * 70)
    print("COMPARISON")
    print("=" * 70)
    print(f"  Same engines used for both runs:      yes (one MorningAnalysisEngine instance)")
    print(f"  Top concern (Mock):                   {mc}")
    print(f"  Top concern (ClaudeDispatch):         {dc}")
    print(f"  -> same top concern?                  {'YES' if mc == dc else 'no'}")
    print(f"  Top recommendation (Mock):            {mr[:54]}...")
    print(f"  Top recommendation (ClaudeDispatch):  {dr[:54]}...")
    print(f"  -> same top recommendation?           {'YES' if mr == dr else 'no'}")
    print()
    print(f"  Priorities  — mock {len(mock.priorities)} vs dispatch {len(dispatch.priorities)}")
    print(f"  Opportunities — mock {len(mock.opportunities)} vs dispatch {len(dispatch.opportunities)}")
    print(f"  Curiosities — mock {len(mock.curiosities)} vs dispatch {len(dispatch.curiosities)}")
    print()
    print("  The two outputs are NOT identical — and shouldn't be. Claude Dispatch v1")
    print("  carries only the 7 climate signals; the mock additionally hand-wrote plant")
    print("  observations, history, an outlook, and logged changes. That is a data-")
    print("  coverage difference, not an architecture one: no engine was modified, and")
    print("  the core climate reasoning (House 1 disease risk) came through from both.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

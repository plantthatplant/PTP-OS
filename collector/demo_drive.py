#!/usr/bin/env python3
"""Demonstrate the Business Knowledge Observer on the real planning spreadsheets.

    Google Drive spreadsheets  →  GoogleDriveObserver  →  Canonical Observations (intention)
                                                          │
                              reality (Synopta / grower)  ▼
                                            plan_vs_reality  →  Knowledge Gaps  (never overwrite)

Reads the plan files (passed as args, else found in ~/Downloads), prints the observations of
intention, saves them to data/inbox/plan-latest.json (kept separate from reality), then shows
how a plan-vs-reality divergence becomes a question.

    python collector/demo_drive.py [plan.xlsx ...]
"""
from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collector import _paths
from collector.observers import observe_files
from collector.observers import plan_vs_reality

_PLAN_OUT = os.path.join(_paths.REPO_ROOT, "data", "inbox", "plan-latest.json")


def _find_default_files():
    dl = os.path.join(os.path.expanduser("~"), "Downloads")
    pats = ["*dlingsplan*.xlsx", "*nsamhets*.xlsx", "*Odlarmall*.xlsx"]
    found = []
    for p in pats:
        found += glob.glob(os.path.join(dl, p))
    return sorted(set(found))


def main() -> int:
    files = sys.argv[1:] or _find_default_files()
    if not files:
        print("No plan spreadsheets found. Pass paths, or place them in ~/Downloads.")
        return 1

    print("Business Knowledge Observer — reading intention from:")
    for f in files:
        print(f"  • {os.path.basename(f)}")

    observations = observe_files(files)
    print(f"\nProduced {len(observations)} Canonical Observations of intention:\n")
    by_kind = {}
    for o in observations:
        by_kind.setdefault(o["kind"], []).append(o)
    for kind in sorted(by_kind):
        print(f"  {kind}  ({len(by_kind[kind])})")
        for o in by_kind[kind][:6]:
            val = o.get("value")
            unit = f" {o['unit']}" if o.get("unit") else ""
            note = f"   — {o['notes']}" if o.get("notes") else ""
            print(f"    · {o['subject']}: {val}{unit}  [{o['confidence']}, {o['method']}]{note}")
        if len(by_kind[kind]) > 6:
            print(f"      …(+{len(by_kind[kind]) - 6} more)")

    os.makedirs(os.path.dirname(_PLAN_OUT), exist_ok=True)
    with open(_PLAN_OUT, "w", encoding="utf-8") as f:
        json.dump({"_comment": "Plan/intention observations from Google Drive. NOT reality.",
                   "source": "google-drive", "observations": observations}, f,
                  indent=2, ensure_ascii=False)
    print(f"\nSaved intention to: {os.path.relpath(_PLAN_OUT, _paths.REPO_ROOT)}  (kept separate from reality)")

    # --- Plan vs reality: a divergence becomes a question (reality never overwritten) ---
    print("\n" + "═" * 64)
    print("PLAN vs REALITY  →  Knowledge Gaps")
    print("═" * 64)
    # Illustrative reality observations (as a grower count / a clock would supply):
    reality = [
        {"subject": "h2", "kind": "occupancy", "value": 30, "unit": "%",
         "source": "grower:oskar", "method": "observed-by-human", "confidence": "high"},
    ]
    print("  reality (e.g. grower's own count):")
    for r in reality:
        print(f"    · {r['subject']}: {r['kind']} {r['value']}{r.get('unit','')}  [{r['source']}]")
    gaps = plan_vs_reality.compare(observations, reality, now_iso="2026-08-01T00:00:00Z")
    print(f"\n  {len(gaps)} knowledge gap(s) raised (reality kept; plan questioned):")
    for g in gaps[:10]:
        print(f"    ? {g['text']}")
        print(f"        reason: {g['reason']}  ·  plan: {g.get('plan_source')}")
    if not gaps:
        print("    (none — plan and reality agree on the facts they share)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

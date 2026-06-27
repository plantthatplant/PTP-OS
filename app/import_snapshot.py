#!/usr/bin/env python3
"""Import a canonical Greenhouse Snapshot and run the Brain on it.

    python3 app/import_snapshot.py                 # uses app/sample_snapshot.json
    python3 app/import_snapshot.py path/to/snap.json

Reads the JSON, converts it to a Greenhouse Snapshot, runs the EXISTING Morning
Analysis (no engine touched), prints the standard Morning Brief, and then reports
which values were missing, the observation coverage %, and the overall reality
confidence. The Brain never fails because data is missing — gaps lower confidence
instead.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from greenhouse_brain.snapshot_importer import import_snapshot
from greenhouse_brain.providers.snapshot_provider import SnapshotProvider
from greenhouse_brain.morning_analysis import MorningAnalysisEngine
from greenhouse_brain.language_engine import TemplateLanguageRenderer

_DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_snapshot.json")


def run_and_report(snapshot, label):
    provider = SnapshotProvider(snapshot)
    analysis = MorningAnalysisEngine().run(provider)   # existing engine, unchanged
    print(TemplateLanguageRenderer().render_morning(analysis))

    cov = snapshot.coverage()
    rc = snapshot.reality_confidence()
    print("\n" + "=" * 64)
    print(f"DATA QUALITY — {label}")
    print("=" * 64)

    missing = snapshot.missing()
    print(f"MISSING VALUES ({len(missing) + len(snapshot.not_observed)}) — not invented:")
    for o in missing:
        print(f"  - {o.subject} / {o.kind}: {o.absence or 'value was null'}")
    for slot in snapshot.not_observed:
        print(f"  - (coverage) {slot}")
    if not missing and not snapshot.not_observed:
        print("  - none; full coverage of what this snapshot set out to observe")

    print(f"\nOBSERVATION COVERAGE:  {cov['coverage_pct']}%  "
          f"({cov['present']} observed / {cov['total']} attempted)")
    print(f"REALITY CONFIDENCE:    {rc['label']}  ({rc['score_pct']}%)")
    print(f"  = data quality {rc['data_quality_pct']}% (how good what we saw is)"
          f"  x  coverage {cov['coverage_pct']}% (how much we saw)")


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else _DEFAULT
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except FileNotFoundError:
        print(f"No snapshot file at: {path}")
        return 1
    except json.JSONDecodeError as e:
        print(f"That file isn't valid JSON: {e}")
        return 1

    snapshot = import_snapshot(raw)
    print(f"Imported snapshot of '{snapshot.greenhouse_name}' assembled at "
          f"{snapshot.assembled_at} — {len(snapshot.observations)} observations from "
          f"{len(snapshot.provenance)} source(s).\n")
    run_and_report(snapshot, "this morning's snapshot")

    # Robustness proof: an almost-empty snapshot still produces a brief, never an error.
    print("\n\n" + "#" * 64)
    print("# ROBUSTNESS CHECK — a snapshot with almost nothing in it")
    print("#" * 64)
    from greenhouse_brain.snapshot import Snapshot, SnapshotZone
    bare = Snapshot(greenhouse_id="gh-x", greenhouse_name="Kalaberga",
                    assembled_at=snapshot.assembled_at,
                    not_observed=["everything — nobody has looked yet"],
                    zones=[SnapshotZone("h1", "House 1 (propagation)", "propagation")])
    run_and_report(bare, "near-empty snapshot")
    print("\n  -> produced a brief and a confidence, with no error. Missing data lowered "
          "confidence; it did not break the Brain.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

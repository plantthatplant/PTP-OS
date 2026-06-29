"""Gaia Edge Collector — the production folder-watch bridge from a scheduled Synopta Export
to the Canonical Greenhouse Snapshot Gaia already consumes.

This package is **purely additive**. It reuses the existing acquisition pipeline unchanged —
`translate.to_snapshot` → `validate` → `changes.detect_changes` → atomic `latest.json` — and
adds only what a long-running, unattended bridge needs around it:

    parsers   — turn a real export FILE (CSV/TSV/Excel/JSON) into the same raw vendor dict
                the existing translator already understands (format translation only)
    watcher   — a robust, debounced, checkpointed folder watcher (dedup, partial-write and
                reboot/power-loss safety, safe retries, archive/quarantine of files)
    pipeline  — the thin reuse layer: raw dict → translate → validate → publish latest.json
    health    — durable Collector Health (last success, last file, duration, failures, freshness)
    config    — everything from environment variables (no hardcoded paths or keys)
    run       — the daemon entry point: `python -m collector.edge.run`

By the same hard constraints as the rest of the Collector, the Edge layer contains **no
biological reasoning, no recommendations, and no AI**. It never invents a missing value, never
publishes an invalid snapshot, never overwrites newer reality with older, and never touches the
live control bus, the controller, or the Synopta GUI. It only reads files and writes one file.
"""
from __future__ import annotations

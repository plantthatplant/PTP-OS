"""Gaia Collector — the first real bridge between Synopta and PTP-OS.

Runs locally beside Synopta. Reads greenhouse data through a single vendor seam
(`collector.sources`), translates it into a Canonical Greenhouse Snapshot, validates it,
and writes it to data/inbox/latest.json — the file Gaia already consumes.

It collects and translates. It does NOT reason, recommend, or contain AI. See
specs/gaia-collector.md.
"""

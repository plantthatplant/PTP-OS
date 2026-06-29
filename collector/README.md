# Gaia Collector

The first real bridge between **Synopta** and **PTP-OS**. It runs locally on the Windows
machine beside Synopta, reads greenhouse data, and writes it as a **Canonical Greenhouse
Snapshot** to `data/inbox/latest.json` — the file Gaia already consumes.

Spec: [`specs/gaia-collector.md`](../specs/gaia-collector.md).

```
Synopta ──▶ Source.fetch() ──▶ translate ──▶ validate ──▶ diff ──▶ data/inbox/latest.json ──▶ Gaia
            (the only vendor seam)   (field-map only)  (Gaia's own importer)        (unchanged)
```

## What it does — and never does

It **collects and translates**: read → translate → validate → save → log → diff.

It is **not** the Brain. By hard constraint it contains **no biological reasoning, no
recommendations, and no AI**. It never invents a missing value (absence is recorded
honestly) and never touches the live control bus, the controller, or the Synopta GUI.

## Run it

```
python collector/collect.py                                   # fixture source (default), one shot
python collector/collect.py --source drop-folder --path <export-folder>
python collector/demo_pipeline.py                             # Synopta → Collector → Gaia, end to end
python -m collector.edge.run                                  # the production Edge Collector (daemon)
```

### Edge Collector (Sprint 14) — the all-day scheduled-export bridge

For production, [`collector/edge/`](edge/) runs as an unattended daemon that **watches a folder** for
scheduled Synopta exports (CSV/TSV/Excel/JSON) and keeps `latest.json` current automatically:
content-hash dedup, partial-write/debounce protection, reboot & power-loss recovery, bounded safe
retries, a never-overwrite-newer freshness guard, durable Collector Health, and a Knowledge Gap on
failure. It reuses everything below (translate → validate → diff → write) unchanged — see
[`collector/edge/README.md`](edge/README.md). The single remaining dependency is Ridder enabling the
export: [`docs/ridder-synopta-export-specification.md`](../docs/ridder-synopta-export-specification.md).

No dependencies for the v1 fixture / drop-folder sources. (On this machine, Python lives at
`%LOCALAPPDATA%\Programs\Python\Python312\python.exe` until it's on PATH.)

Exit codes: `0` published · `2` quarantined (invalid, not published) · `3` source failed
(previous `latest.json` left untouched).

## The Source seam (how Synopta is read)

All vendor messiness is contained in one place — `collector/sources/` — mirroring the
Brain's transport seam. The live-source decision (a sanctioned API vs a scheduled Export
drop) is deferred; choosing it changes **one class**, nothing above it.

| Source | Role | Status |
| --- | --- | --- |
| `FixtureSource` | Bundled captured reading — proves the pipeline offline | v1 (default) |
| `DropFolderSource` | Reads the newest export file Synopta drops into a folder | v1 (ready; needs a real export path) |
| `ApiSource` | Sanctioned Synopta/Hortimax data API | Future — when access is confirmed |

To add the real source later, implement `SynoptaSource.fetch() -> dict`, register it in
`sources/__init__.py:make_source`, and finalise the field mapping in `translate.py` against a
real export sample. Nothing else moves.

## Files

| File | Role |
| --- | --- |
| `collect.py` | Orchestrator + CLI (read → translate → validate → diff → write → log) |
| `demo_pipeline.py` | End-to-end demonstration into Gaia |
| `sources/` | The vendor seam: `base`, `fixture_source`, `drop_folder_source`, `make_source` |
| `translate.py` | Raw reading → Canonical Snapshot (field-map + unit-clean only) |
| `validate.py` | Validates the snapshot using Gaia's **own** importer |
| `changes.py` | Observation-level diff vs the previous snapshot |
| `log.py` | Append-only JSONL collection log |
| `facility.json` | Known configuration: zone identity, stage, crop, known-absent sensors |

## Outputs (under the repo's `data/`)

- `data/inbox/latest.json` — the current Canonical Snapshot Gaia reads.
- `data/inbox/history/` — previous snapshots, archived (immutable records of a moment).
- `data/inbox/quarantine/` — snapshots that failed validation (never published).
- `data/logs/collector-YYYYMMDD.jsonl` — one structured line per collection.

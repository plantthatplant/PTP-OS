# Gaia Edge Collector

The production bridge from a **scheduled Synopta export** to the Canonical Greenhouse Snapshot
Gaia already consumes. It runs all day beside Synopta, watches one folder, and keeps
`data/inbox/latest.json` current — automatically, unattended, with no terminal and no Claude.

```
Synopta server ──▶ scheduled Export (CSV/TSV/Excel/JSON) ──▶ import folder
                                                                  │
                                   ┌──────────────────────────────▼──────────────────────────┐
                                   │  Edge Collector (this package)                            │
                                   │   watcher → parse(format) → translate → validate → publish│
                                   │   dedup · debounce · archive · checkpoint · health · gaps │
                                   └──────────────────────────────┬──────────────────────────┘
                                                                  ▼
                                              data/inbox/latest.json  ──▶  Gaia API ──▶ Lovable ──▶ Even G2
```

It is **purely additive**: parsing turns a real export file into the same raw vendor dict the
existing `collector/translate.py` already understands, so `translate → validate → diff → write`
are reused **unchanged**. Nothing in the Brain, the API, or the Snapshot model was modified.

## What it guarantees

| Requirement | How |
| --- | --- |
| Watches an import folder | `watcher.py`, every `IMPORT_INTERVAL` seconds |
| Detects new exports | content-hash identity, not filename |
| Ignores duplicates | checkpoint of imported hashes (`checkpoint.py`) |
| Detects partial writes | size+mtime debounce window + open-for-read guard |
| Recovers after reboot / power loss | durable checkpoint; atomic `latest.json`; idempotent re-runs |
| Retries safely | bounded transient retries → then quarantine to FAILED |
| Never publishes invalid observations | validation gate (Gaia's own importer); invalid → FAILED |
| Never overwrites newer reality | freshness guard (older reading is filed, not published) |
| Never crashes | every file processed in isolation; loop fully guarded |
| Raises a Knowledge Gap on failure | `gaps.py` + untouched last snapshot + Health |

## Run it

```
python -m collector.edge.run          # the daemon (boot task runs exactly this)
python -m collector.edge.health       # print current Collector Health as JSON
run\start-edge.cmd                     # supervised production launcher (Windows)
run\install-edge-startup.ps1           # auto-start at logon, no admin
```

## Multi-format parser

`parsers.py` accepts **CSV, TSV, Excel (.xlsx), and JSON** (vendor `houses` shape *or* a flat
array of records). All four collapse to the one canonical raw dict, so the format Ridder ships is
not load-bearing. Columns are matched by a **case/space/unit-insensitive, multilingual alias map**
(`DEFAULT_COLUMN_ALIASES`) — order-independent, tolerant of unexpected columns, English/Swedish/
Dutch headers. Add a real column name there (or via `SYNOPTA_COLUMN_MAP`) when Ridder's export is
confirmed; nothing else moves. It is translation only — it never cleans numbers (the tested
`to_number` does, downstream), never decides confidence, and **never invents a value**.

## Configuration (environment only)

| Variable | Default | Meaning |
| --- | --- | --- |
| `SYNOPTA_IMPORT_PATH` | `data/inbox/drop` | folder watched for exports |
| `SYNOPTA_ARCHIVE_PATH` | `data/inbox/archive` | where imported files are moved |
| `SYNOPTA_FAILED_PATH` | `data/inbox/failed` | where unparseable/invalid files are moved |
| `IMPORT_INTERVAL` | `30` | poll interval, seconds |
| `MAX_FILE_SIZE` | `16777216` | largest export accepted, bytes |
| `SUPPORTED_FORMATS` | `csv,tsv,xlsx,json` | extensions to import |
| `SYNOPTA_STABILITY_SECONDS` | `5` | debounce window before a file is read |
| `SYNOPTA_MAX_RETRIES` | `3` | transient retries before FAILED |
| `SYNOPTA_FRESHNESS_SLA_S` | `900` | reading older than this → Health "stale" |
| `SYNOPTA_ALLOW_OLDER` | `0` | allow an older reading to replace a newer one |
| `SYNOPTA_FACILITY` | `collector/facility.json` | zone identity / known-absent sensors |
| `SYNOPTA_DEFAULT_TZ` | `UTC` | assumed zone for export timestamps that carry none |
| `SYNOPTA_COLUMN_MAP` | – | JSON overriding the column→signal alias map |

It publishes to the **same** snapshot path the Gaia API reads (derived from the shared `GAIA_*`
settings), so the two processes never disagree about where reality lives.

## Files

| File | Role |
| --- | --- |
| `run.py` | daemon entry point (`python -m collector.edge.run`) |
| `watcher.py` | the robust folder watcher (debounce, dedup, archive, retry, recovery) |
| `parsers.py` | CSV/TSV/Excel/JSON → raw vendor dict (the format seam) |
| `pipeline.py` | raw → translate → validate → publish (reuses the existing pipeline) |
| `checkpoint.py` | durable imported-hash + retry store (reboot/dedup safety) |
| `health.py` | durable Collector Health (`python -m collector.edge.health`) |
| `gaps.py` | raise a Knowledge Gap when reality could not be observed |
| `config.py` | environment-only configuration |

## The one remaining dependency

Everything here is built and tested. The **only** thing left for live greenhouse data is **Ridder
enabling the scheduled export** into the import folder — see
[`docs/ridder-synopta-export-specification.md`](../../docs/ridder-synopta-export-specification.md)
and [`docs/sprint-14-go-live-checklist.md`](../../docs/sprint-14-go-live-checklist.md).

# Gaia Collector — How It Works

**Status:** Production documentation · the first real Synopta ↔ PTP-OS integration.
**Code:** [`collector/`](../collector/) · **Spec:** [`specs/gaia-collector.md`](../specs/gaia-collector.md)
· **Output contract:** [`specs/greenhouse-snapshot.md`](../specs/greenhouse-snapshot.md)

This document explains what the Collector is, how it works stage by stage, how it fits the
architecture, what every file does, and — most importantly — **how a future developer connects
a new Synopta source by adding a single module.**

---

## 1. What it is, in one paragraph

The Gaia Collector runs locally on the Windows machine beside Synopta. It reads greenhouse
data from Synopta, translates it into the **Canonical Greenhouse Snapshot** that Gaia already
understands, validates it, and writes it to `data/inbox/latest.json`. Gaia consumes that file
through its existing pipeline with **no code change**. The Collector *collects and translates*;
it does not reason, recommend, or contain any AI. Acquiring reality and reasoning about it are
two different jobs, and this is the first.

---

## 2. The big picture

```
   Synopta (Hortimax SynDesk / server / export)
        │
        ▼
 ┌──────────────────────────────────────────────────────────┐
 │  GAIA COLLECTOR                                            │
 │                                                           │
 │   Source.fetch()  ──▶  translate  ──▶  validate  ──▶  diff │
 │   (the only vendor      (field-map     (Gaia's own    (vs  │
 │    seam; raw dict)       + clean)       importer)    prev) │
 │                                   │                        │
 │                                   ▼                        │
 │            archive previous  +  write latest.json  +  log  │
 └───────────────────────────────────┬──────────────────────┘
                                      ▼
                        data/inbox/latest.json
                   (a Canonical Greenhouse Snapshot)
                                      │
                                      ▼
   import_snapshot() ─▶ SnapshotProvider ─▶ Context ─▶ Decision ─▶ Language ─▶ Morning
                                   ( Gaia — entirely unchanged )
```

The boundary in the middle is the whole point: **everything to the left is acquisition
(messy, vendor-specific, occasionally failing); everything to the right is reasoning.** The
Snapshot file is the contract between them, and it is the same structure no matter how the data
was acquired (Synopta today, a CSV, a camera, a manual note tomorrow).

---

## 3. How it works, stage by stage

A single run is `collector/collect.py:run()`. Each stage maps to one of the responsibilities
in the spec.

1. **Read** — `Source.fetch()` returns a raw, vendor-shaped dict. This is the *only* place
   that knows where Synopta data comes from. If it cannot deliver anything, it raises
   `SourceError`; the run stops **without touching the previous `latest.json`**, so Gaia keeps
   the last good snapshot rather than seeing nothing.
2. **Translate** — `translate.py:to_snapshot()` maps each vendor signal to a canonical
   observation: cleans numbers (`'24,2 °C' → 24.2`), normalises units, derives a
   provenance-based confidence, and turns the structure into the Snapshot envelope. It records
   *what was observed*; it never interprets it. A value it cannot read becomes an **honest
   absence and a warning — never a fabricated number.**
3. **Validate** — `validate.py:validate()` checks the snapshot against the canonical contract
   **by round-tripping it through Gaia's own importer.** "Valid" therefore means "exactly what
   Gaia can consume," not a second opinion. An invalid snapshot is **quarantined and never
   published.**
4. **Diff** — `changes.py:detect_changes()` compares the new snapshot against the previous
   `latest.json` (read before it is replaced) at the observation level: values appeared,
   disappeared, or changed; alarms raised or cleared; coverage shifts. It reports *what*
   changed, never what it *means*.
5. **Publish** — the previous snapshot is archived to `data/inbox/history/` (snapshots are
   immutable records of a moment), then the new one is written to `data/inbox/latest.json`.
6. **Log** — `log.py:append_event()` appends one structured JSON line to
   `data/logs/collector-YYYYMMDD.jsonl`, and the run prints a calm human summary.

**Exit codes:** `0` published · `2` quarantined (invalid, not published) · `3` source failed
(previous snapshot left untouched).

---

## 4. Architecture and boundaries

The Collector exists to honour the constraint in [`VISION.md`](../VISION.md): *"Greenhouse
data enters only through the Provider Layer; the value we build must outlive any source of
data."* It is a deliberate, hard-edged separation:

**What the Collector may do:** read a source, map fields, clean units, represent absence and
confidence, diff against the past, write a file, log.

**What the Collector must never do** (enforced by review and by tests):
- no biological reasoning — no Plant State, Stress, Disease Risk, Growth Potential (those are
  *latent* and inferred **downstream**; see [`BIOLOGY.md`](../BIOLOGY.md) and snapshot
  Principle 2);
- no recommendations;
- no AI / model calls;
- no inventing a value to fill a gap;
- no touching the live control bus (AMQP/RabbitMQ), the process controller, or the Synopta GUI
  (no OCR). Reading is file- or API-based and read-only.

It reuses Gaia rather than duplicating it: the canonical snapshot model
([`greenhouse_brain/snapshot.py`](../app/greenhouse_brain/snapshot.py)), the importer, and the
number/airflow primitives ([`greenhouse_brain/units.py`](../app/greenhouse_brain/units.py)) are
all the Brain's own — the Collector imports them, so there is one definition of each.

---

## 5. The Source seam

All of Synopta's vendor reality enters through one tiny interface, mirroring the Brain's own
transport seam:

```python
class SynoptaSource:
    label: str
    def fetch(self) -> dict:   # raw, vendor-shaped reading — or raise SourceError
        ...
```

v1 ships two implementations and is built so a third (the live one) is **a single new
module**:

| Source | Role | Status |
| --- | --- | --- |
| `FixtureSource` | Bundled captured reading — proves the pipeline offline | shipped |
| `DropFolderSource` | Reads the newest export file Synopta drops into a folder | shipped (needs a real export path) |
| `ApiSource` | A sanctioned Synopta/Hortimax data API | **future — one new module** |

The live-source decision (a sanctioned **API** vs a scheduled **Export** drop) is deliberately
deferred. Because of the seam, making it changes one class and the field mapping — nothing
above it. See [`docs/dispatch-runtime-investigation.md`](dispatch-runtime-investigation.md) for
why a file-drop bridge is the safest first option.

---

## 6. Every folder and file

### `collector/` — the component
| Path | What it does |
| --- | --- |
| `collect.py` | Orchestrator + CLI. The `run()` pipeline: read → translate → validate → diff → publish → log. |
| `demo_pipeline.py` | Runnable end-to-end demonstration: Synopta(fixture) → Collector → Snapshot → Gaia. |
| `translate.py` | Raw reading → Canonical Snapshot. Field-mapping and unit-cleaning only. |
| `validate.py` | Validates a snapshot using Gaia's **own** importer; computes coverage & reality confidence. |
| `changes.py` | Observation-level diff against the previous snapshot. |
| `log.py` | Append-only JSONL collection log + the single UTC clock. |
| `facility.json` | Known configuration: zone identity, stage, crop, and known-absent sensors. |
| `_paths.py` | Shared paths; the one place `app/` is put on the import path so the Brain can be reused. |
| `README.md` | Quick-start and file map. |

### `collector/sources/` — the vendor seam
| Path | What it does |
| --- | --- |
| `base.py` | `SynoptaSource` interface and `SourceError`. |
| `fixture_source.py` | Reads the bundled sample reading (offline, deterministic). |
| `drop_folder_source.py` | Reads the newest export file from a folder (read-only). |
| `sample_synopta_export.json` | A captured raw export, vendor-shaped, with deliberate messiness. |
| `__init__.py` | `make_source(name, path)` — composition-time selection. |

### `collector/tests/` — the test suite (standard-library `unittest`, no dependencies)
| Path | Covers |
| --- | --- |
| `test_units.py` | The shared number/airflow primitives. |
| `test_translate.py` | Translation: cleaning, vent text, confidence, honest absence, coverage. |
| `test_validate.py` | Required fields, observation wellformedness, importer round-trip. |
| `test_changes.py` | First run, no-change, value/appear/disappear, alarm, coverage shifts. |
| `test_failures.py` | Source errors, source-failure safety, quarantine, archiving. |
| `test_snapshot_compat.py` | The Collector's output runs through Gaia's unchanged pipeline. |

### `data/` — runtime output (generated; git-ignored)
| Path | What it holds |
| --- | --- |
| `data/inbox/latest.json` | The current Canonical Snapshot Gaia reads. |
| `data/inbox/history/` | Previous snapshots, archived (immutable records). |
| `data/inbox/quarantine/` | Snapshots that failed validation (never published). |
| `data/logs/collector-YYYYMMDD.jsonl` | One structured line per collection. |

---

## 7. How to connect a new Synopta source (the single-module path)

When the live access method is confirmed, adding it is **one new module + one line + a mapping
check**. Worked example for an API source:

1. **Create `collector/sources/api_source.py`** implementing the seam:
   ```python
   from .base import SynoptaSource, SourceError

   class ApiSource(SynoptaSource):
       label = "synopta-api"
       def __init__(self, base_url, api_key, timeout=5.0):
           self.base_url, self.api_key, self.timeout = base_url, api_key, timeout
       def fetch(self) -> dict:
           # GET the data; on any failure raise SourceError(...). Return a raw dict.
           # Contain ALL vendor specifics (endpoints, auth, paging) here.
           ...
   ```
   The whole job of this file is to return a raw dict (or raise `SourceError`). It does **not**
   build a Snapshot — that stays in `translate.py`.

2. **Register it** in `collector/sources/__init__.py:make_source()`:
   ```python
   if name in ("api", "synopta-api"):
       return ApiSource(os.environ["SYNOPTA_URL"], os.environ.get("SYNOPTA_KEY"))
   ```

3. **Confirm the field mapping.** If the real payload's shape differs from the vendor shape in
   `sample_synopta_export.json`, adjust the mapping in `translate.py` (and/or normalise inside
   the source). Capture a real sample as a new fixture and add a translation test for it.

4. **Run the tests.** `python -m unittest discover -s collector/tests`. The translation,
   validation, change-detection, and snapshot-compatibility tests already protect everything
   downstream; you are only proving the new source and its mapping.

That is the entire surface area. Nothing in `validate.py`, `changes.py`, `collect.py`, the
Snapshot model, the providers, or the engines changes. **Adding the live provider is one new
module.**

---

## 8. Running and operating it

```
python collector/collect.py                                   # fixture source (default)
python collector/collect.py --source drop-folder --path <export-folder>
python collector/demo_pipeline.py                             # end-to-end demonstration
python -m unittest discover -s collector/tests                # the test suite
```

No dependencies for the v1 sources. On this machine Python is at
`%LOCALAPPDATA%\Programs\Python\Python312\python.exe` until it is on PATH; set
`$env:PYTHONUTF8 = "1"` for correct UTF-8 console output.

**Cadence** is an operations choice (open question in the spec): run it each morning before the
grower arrives via Windows Task Scheduler, or on a fixed interval. The Brain always reads the
most recent `latest.json`; a failed collection leaves the last good one in place.

---

## 9. The honesty rules (why this is trustworthy)

These come straight from [`CLAUDE.md`](../CLAUDE.md) and the snapshot spec, and each is tested:

- **Unknown is not zero.** A missing value is recorded as absence, never coerced to a number.
- **Observation, not interpretation.** An alarm is carried as a fact; it never becomes "disease
  risk."
- **Provenance and confidence travel with every datum.** A sensor-fault alarm lowers that
  house's reading confidence — an observation-quality judgement, never a plant judgement.
- **Coverage is explicit.** "Looked, saw nothing" (a coverage gap) is distinct from "didn't
  look."
- **Fail safe.** One bad value is one gap; a dead source keeps yesterday's snapshot; an invalid
  snapshot is quarantined, never shown to Gaia.

---

## 10. Lifecycle of a snapshot

What happens to one snapshot, from birth to consumption:

1. **Acquired.** A `SynoptaSource` returns a raw reading. Its values were captured at various
   `captured_at` times by the greenhouse.
2. **Assembled.** `to_snapshot()` stamps it with a single `assembled_at` (the moment this
   coherent view was composed) and turns the readings into observations. `captured_at` and
   `assembled_at` are deliberately distinct (snapshot spec §7).
3. **Validated.** It must round-trip through Gaia's importer and carry the required fields. If
   not, it is written to `data/inbox/quarantine/` and its life ends there — it is never
   published.
4. **Compared.** It is diffed against the current `latest.json` (the previous snapshot).
5. **Published — immutably.** The previous `latest.json` is copied to
   `data/inbox/history/snapshot-<assembled_at>.json` (a permanent record of that moment), then
   the new snapshot is written to `latest.json` **atomically** (temp file + `os.replace`), so a
   reader never sees a half-written file.
6. **Recorded.** One line is appended to `data/logs/collector-YYYYMMDD.jsonl`.
7. **Consumed.** Gaia reads `latest.json` via `import_snapshot()` → `SnapshotProvider` → the
   engines. The snapshot itself is never mutated; a correction is always a *new* snapshot.

A snapshot is thus an **immutable record of a moment**. History accumulates; `latest.json` is
only ever replaced wholesale.

---

## 11. Troubleshooting

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| Exit code **3**, `SOURCE-FAILED` | The source could not deliver (missing file, empty/again missing drop folder, unreachable API). | The previous `latest.json` is intentionally untouched. Check the source path / connectivity. Gaia keeps running on the last good snapshot. |
| Exit code **2**, `QUARANTINED` | The translated snapshot failed validation. | Read the listed errors and the file in `data/inbox/quarantine/`. Usually a translation-mapping gap for a new export shape. `latest.json` is unchanged. |
| Warnings like `… missing or unreadable` | A signal was absent or unparseable in the reading. | Expected, honest behaviour — the value became an absence, not a fabricated number. Investigate the sensor/export if it persists. |
| Mojibake (`Kålaberga` shows as `K�laberga`) in the console | The terminal's code page, **not** the data. | Set `PYTHONUTF8=1` (and `chcp 65001` on Windows). The files on disk are always real UTF-8. |
| `ModuleNotFoundError: collector` / `greenhouse_brain` | Run from the wrong directory, or Python path not set. | Run from the repo root, or use `python -m collector.collect`. The test suite and entry points bootstrap the path themselves. |
| `'python' is not recognised` / opens Microsoft Store | Only the Windows Store alias is present. | Use the real interpreter at `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`, or add it to PATH. |
| `history/` not growing across rapid runs | Multiple runs share the same `assembled_at` second, so they archive to the same filename. | Expected. At the real once-a-morning cadence every run produces a distinct history file. |
| A `.tmp` file left in `data/inbox/` | A crash *during* a write (rare). | Safe to delete; the atomic write means `latest.json` is still the last complete snapshot. |

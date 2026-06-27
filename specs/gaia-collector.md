# Spec — Gaia Collector v1

**Status:** Draft v1 · Sprint (first real Synopta↔PTP-OS integration).
**Related:** [`specs/greenhouse-snapshot.md`](greenhouse-snapshot.md) (the output contract),
[`specs/greenhouse-provider.md`](greenhouse-provider.md),
[`adr/ADR-002-provider-abstraction.md`](../adr/ADR-002-provider-abstraction.md),
[`docs/dispatch-runtime-investigation.md`](../docs/dispatch-runtime-investigation.md)
(why a local file-drop bridge is the cleanest seam),
[`integrations/`](../integrations/).

> This spec defines a **component and its behaviour**, not a final file format. The
> illustrative shapes are for clarity. The Collector's *output* is the already-canonical
> [Greenhouse Snapshot](greenhouse-snapshot.md); this spec does not redefine it.

## 1. Purpose

The Gaia Collector is the **first real bridge between Synopta and PTP-OS.** It runs locally
on the Windows machine beside Synopta, reads greenhouse data from Synopta by the safest
available method, and writes it out as a **Canonical Greenhouse Snapshot** to
`data/inbox/latest.json` — the file Gaia already knows how to consume.

It exists so that *acquiring* greenhouse reality (messy, vendor-shaped, occasionally
failing) is cleanly separated from *reasoning about* it (the Brain). The Brain stays
unaware that Synopta exists; it only ever sees a Snapshot.

## 2. What the Collector is — and is not

**It is** an acquisition component: read → translate → validate → save → log → diff.

**It is NOT, by hard constraint:**
- not biological reasoning (no Plant State, Stress, Disease Risk — those are *latent* and
  inferred downstream; see [`BIOLOGY.md`](../BIOLOGY.md), snapshot Principle 2);
- not a recommender (it never advises);
- not AI (no model calls, no inference);
- not allowed to invent a value to fill a gap (snapshot Principle 4 / §10);
- not part of the Brain — it is a separate process that only writes a file.

If a future change would put any of the above inside the Collector, the boundary has leaked
and must be fixed rather than worked around.

## 3. Where it sits

```
        Synopta  (Hortimax SynDesk / server / export)
            │
            ▼
   ┌─────────────────────────────────────────────┐
   │  Gaia Collector  (this component)            │
   │    Source.fetch() ── the ONLY vendor seam    │   ← all messiness contained here
   │    translate → validate → diff → write → log │
   └───────────────────────┬─────────────────────┘
                            ▼
        data/inbox/latest.json   ── a Canonical Greenhouse Snapshot
                            │
                            ▼
   import_snapshot() → SnapshotProvider → Context/Decision/Language/Morning  (UNCHANGED)
```

The Collector reuses [`greenhouse_brain/snapshot.py`](../app/greenhouse_brain/snapshot.py)
and [`greenhouse_brain/snapshot_importer.py`](../app/greenhouse_brain/snapshot_importer.py)
to *validate* its own output, which is the strongest possible guarantee that what it writes
is exactly what Gaia can read. It adds no new snapshot model.

## 4. The Source seam (how Synopta is read)

The single point where Synopta's reality enters. It mirrors the existing transport seam
(`DispatchTransport.fetch() -> dict`) so the rest of the Collector never knows which source
produced the raw reading.

```
SynoptaSource:
  label: str                 # for logs/provenance, e.g. "fixture", "drop-folder"
  fetch() -> dict            # raw, vendor-shaped greenhouse reading (or raises SourceError)
```

v1 ships two implementations; more plug in later **without changing anything above the seam**:

| Source | Role | Status |
| --- | --- | --- |
| `FixtureSource` | A bundled captured reading. Offline, deterministic — proves the pipeline today. | v1 |
| `DropFolderSource` | Watches a folder for the newest export file Synopta (or a scheduled job) drops. | v1 (ready; needs a real export path) |
| `ApiSource` | A sanctioned Synopta/Hortimax data API. | Future — when access is confirmed |

The live-source decision (API vs scheduled Export) is deliberately deferred; the seam means
that decision changes one class, nothing else (see the dispatch-runtime investigation).

**Safety:** the Collector never connects to the live control bus (AMQP/RabbitMQ) or the
process controller, and never drives the Synopta GUI / OCR. Reading is file- or API-based and
read-only.

## 5. Responsibilities (the contract)

1. **Read** from Synopta via a `SynoptaSource` (safest available; fixture/export in v1).
2. **Translate** the raw reading into a Canonical Snapshot — field mapping and unit
   normalisation only, no interpretation.
3. **Validate** the Snapshot against the canonical contract (§7). A malformed snapshot is
   never published.
4. **Save** the valid Snapshot as `data/inbox/latest.json`, archiving the previous one
   (snapshots are immutable records of a moment — Principle 9).
5. **Log** every collection event, with enough detail to debug (§8).
6. **Detect changes** since the previous snapshot and record them.
7. **Never invent** a missing value. Absence is represented honestly (`null` + an absence
   note, or a `coverage.not_observed` entry), never coerced to zero.
8. **Preserve uncertainty.** Each observation carries provenance, method, and a confidence
   derived from source reliability/recency — never a biological judgement.
9. **Continue on partial failure.** One unreadable value becomes one honest gap; it does not
   abort the collection. A total source failure leaves the previous `latest.json` untouched.
10. **Produce clear logs** suitable for debugging by a human.

## 6. Translation rules (raw → Snapshot)

- Map each vendor signal to an observation with the canonical `kind`, `unit`, and the
  reading's own `captured_at`; set `source` and `method: measured` for instrument values.
- Normalise units and number formats (e.g. European comma decimals, stray unit suffixes)
  inside the Collector, exactly as the provider layer already does — the Snapshot carries
  clean canonical values only.
- **Confidence is provenance-based, not biological:** a healthy sensor reading is `high`; a
  reading from a house whose control system raises a *sensor-fault* alarm is `low` (the alarm
  itself is carried as a separate observation). No threshold ever implies a plant judgement.
- Facility **structure** (zone id, name, stage, crop) is known configuration, supplied from
  [`collector/facility.json`](../collector/facility.json), not sensed each time (snapshot §5e).
- A configured zone with no reading this cycle is still listed in `structure`, and its
  absence is declared in `coverage.not_observed` — "looked, saw nothing" is distinct from
  "didn't look".
- `assembled_at` is the Collector's own UTC assembly time; `captured_at` is the reading's
  time. They legitimately differ (snapshot §7).

## 7. Validation rules

A Snapshot is publishable only if:
- the **Snapshot-level required fields** are present: `greenhouse_id`, `assembled_at`,
  `provenance`, `coverage` (snapshot §6);
- every present **observation** carries `subject`, `kind`, `captured_at`, `source`,
  `method`, `confidence`, and either a value (+`unit` if quantitative) or an explicit
  `absence` marker;
- it round-trips through the existing `import_snapshot()` without loss.

Validation reuses the Brain's own importer and `Snapshot.coverage()` /
`reality_confidence()`. A snapshot that fails validation is written to a quarantine path and
logged as an error; `latest.json` is **not** overwritten, so Gaia never consumes a bad file.

## 8. Logging

Every run appends one structured JSON line to `data/logs/collector-YYYYMMDD.jsonl` and prints
a calm human summary. A log record carries: run time, source label, fetch outcome,
observation count, per-signal warnings (what couldn't be read and why), coverage %, reality
confidence, the change summary, output path, and overall status (`published` /
`quarantined` / `source-failed`).

## 9. Change detection

The Collector diffs the new snapshot's observations against the previous `latest.json`
(before overwriting it) at the **observation level only** — appeared, disappeared, and
value-changed per `subject`+`kind`, plus alarm and coverage changes. It reports *what changed*
in the data; it never says what a change *means* (that is the Brain's job). On the first ever
run there is nothing to compare to, which is stated plainly rather than treated as an error.

## 10. Running it

```
python collector/collect.py                       # default source (fixture), writes data/inbox/latest.json
python collector/collect.py --source drop-folder --path <dir>
python collector/demo_pipeline.py                 # Synopta → Collector → Snapshot → Gaia, end to end
```

The Collector is a plain local program: no install, no dependencies, no keys for the v1
fixture/drop-folder sources.

## 11. Open questions (resolved in review, not assumed)

1. **Live source:** does Synopta/Hortimax expose a sanctioned API, or do we rely on a
   scheduled Export drop? Decides whether `ApiSource` or `DropFolderSource` becomes primary.
2. **Real export shape:** the exact fields/format of a real Synopta export, to finalise the
   translation mapping (v1 uses the established vendor shape as a stand-in).
3. **Cadence:** how fresh must `latest.json` be — once each morning, or on a schedule? Decides
   whether the Collector is run by Task Scheduler, a loop, or on demand.
4. **CO₂/light and other signals:** which the houses actually have, so coverage gaps are
   declared accurately rather than guessed.

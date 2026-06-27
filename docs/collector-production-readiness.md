# Gaia Collector — Production Readiness Report

**Date:** 2026-06-27 · **Scope:** `collector/`, its tests, the CI workflow, and the shared
`app/greenhouse_brain/units.py` refactor. **Verdict:** **production-ready** for the
fixture / drop-folder scope. The codebase is shaped so that going live requires only a single
new `SynoptaSource` module; no live integration is included, by design.

**Evidence:** 54 automated tests pass (`python -m unittest discover -s collector/tests`); CI
runs them on every push (`.github/workflows/collector-tests.yml`) on Python 3.11 and 3.12; the
Brain's existing entry points and the Collector demo all run unmodified.

---

## 1. Architecture review — the six mandated properties

| Property | Holds? | How it is enforced |
| --- | :--: | --- |
| **Deterministic** | ✅ | `to_snapshot(raw, facility, assembled_at)` is a pure function of its inputs. The only wall-clock value, `assembled_at`, is *injected* into translation (so tests pin it). No randomness, no hidden state. |
| **Observable** | ✅ | Every run appends a structured JSONL log and prints a human summary; warnings list exactly what could not be read; exit codes distinguish published / quarantined / source-failed. |
| **Modular** | ✅ | One responsibility per module: `sources/` (acquire), `translate` (map), `validate` (check), `changes` (diff), `log` (record), `collect` (orchestrate). |
| **Pluggable** | ✅ | Acquisition is behind `SynoptaSource.fetch()`; selection is composition-time (`make_source`). A new source is one module + one line. |
| **Provider-based** | ✅ | Vendor data never crosses upward as vendor shapes: the Collector emits a Canonical Snapshot, which Gaia consumes through `SnapshotProvider`. Matches ADR-002 and the snapshot spec ("Providers produce Snapshots"). |
| **Cannot make biological decisions** | ✅ | No latent state (Stress/Disease/Plant State), no recommendations, no thresholds-as-judgement. An alarm is carried as a fact; confidence is an *observation-quality* signal, never a plant judgement. Enforced by `test_translate` and review. |

**Architectural violations found: none material.** Two notes, documented rather than hidden:
- *`sys.path` reuse:* the Collector imports the Brain by adding `app/` to the path (`_paths.py`)
  rather than as an installed package — pragmatic for a zero-dependency repo; revisit if the
  project adopts packaging.
- *Confidence heuristic is coarse* (high/medium/low from a sensor-fault alarm). Acceptable per
  the snapshot spec; richer source-reliability modelling is future work.

### Compliance with the trio (VISION.md · CLAUDE.md · BIOLOGY.md)
- **VISION.md** — "data enters only through the Provider Layer" and "the value must outlive any
  source": satisfied by the Snapshot output + source seam. Read-only; no actuation ("trust
  before automation").
- **CLAUDE.md** — reality before assumptions (honest absence), observation before inference,
  ask-before-assuming (source + Python install were confirmed), prefer simplicity (shared
  primitives), protect the architecture (reuse, no redesign).
- **BIOLOGY.md** — the Collector touches none of the biological model. It records observations;
  all inference of latent plant state happens downstream in the engines. *"When the plant and
  the instruments disagree"* is a reasoning concern the Collector deliberately leaves alone.

---

## 2. Security review

Read-only acquisition with a small, well-understood surface. Threats considered and mitigated:

| Threat | Exposure | Mitigation |
| --- | --- | --- |
| **Path traversal** | `DropFolderSource` lists a configured folder. | It only ever reads files *inside* the operator-set folder (`os.listdir` + `os.path.join`); `_source_file` is recorded as a basename only. No path comes from untrusted input. |
| **Malformed JSON** | Source files may be corrupt. | `json.JSONDecodeError` is caught and converted to `SourceError`; the run fails safe (exit 3), `latest.json` untouched. Tested. |
| **Invalid / partial snapshot published** | A bad snapshot could mislead Gaia. | Two-layer defence: validation via Gaia's own importer (invalid → quarantine, never published), and **atomic write** (temp file + `os.replace`) so a reader never sees a half-written `latest.json`. Tested. |
| **Race condition** (two collectors, or read-during-write) | Concurrent runs / Gaia reading mid-write. | Atomic `os.replace` means the last writer wins cleanly and readers always see a complete file. History filenames are timestamp-keyed. |
| **Resource exhaustion** | A huge/hostile file in the drop folder. | `DropFolderSource` rejects files over 16 MB before parsing (`SourceError`). Tested. |
| **Encoding attacks / mojibake** | Non-UTF-8 bytes in a source file. | All reads are strict UTF-8; `UnicodeDecodeError` → `SourceError`. All writes are UTF-8 (`ensure_ascii=False`). Tested. |
| **Injection** | — | No shell, SQL, `eval`, or template execution anywhere. Data is parsed as JSON and only ever read. |
| **Secret leakage** | Future API source will need credentials. | None are in the code today. The documented pattern for `ApiSource` takes URL/key from environment variables, never committed. The discovered Synopta AMQP `admin:admin` bus is **deliberately not used**. |

**Residual risks:** the live `ApiSource` (future) will introduce credential handling and TLS
trust decisions — to be reviewed when written; a malicious actor with write access to the drop
folder could feed crafted (but still validated) data — mitigated operationally by folder
permissions.

---

## 3. Performance review

Profiled with 200 full collections plus a single-run `cProfile` (fixture source):

- **~5.8 ms per full collection** (read → translate → validate → diff → archive + atomic write
  → log). `latest.json` is ~3.6 KB.
- **Hotspot:** the two disk writes, dominated by `fsync` — a *deliberate* durability cost that
  guarantees the atomic-write property. Everything else is sub-millisecond.
- **No repeated parsing:** the source is read once, the previous snapshot once; translation runs
  once; no object is built twice.
- **No unnecessary object creation** of note; the data set is tiny (single-greenhouse).

**Findings / choices:**
- Archiving on every publish is intentional (immutable history); repeated runs within one second
  collapse to a single history file, so there is no churn at real cadence.
- `fsync` is kept for safety over the ~milliseconds it costs — correct trade-off for a
  once-a-morning job.

No optimisation is warranted; the workload is trivially small and readability is preserved.

---

## 4. Code quality

- **Duplication removed:** number parsing (was triplicated) and vent→airflow logic (was
  duplicated across two providers) now live once in `greenhouse_brain.units` and are reused by
  both the Brain and the Collector.
- **Naming & comments:** modules and functions are single-purpose and named for intent;
  comments explain *why* (honesty rules, atomicity) in the repo's voice, not *what*.
- **Complexity:** the orchestrator reads top-to-bottom as six numbered stages; helpers are
  small. No function is doing two jobs.
- **Reuse over reinvention:** validation uses Gaia's own importer; the snapshot model is the
  Brain's own.

---

## 5. Scorecard (1–10)

| Area | Score | Why · Remaining risks · Future work |
| --- | :--: | --- |
| **Architecture** | **9** | Clean acquisition/reasoning split; reuses provider + snapshot seams; the six mandated properties all hold. *Risk:* unproven against a real Synopta shape. *Future:* prove it by adding `ApiSource`. |
| **Reliability** | **9** | Fail-safe on every path (source-fail keeps last good; invalid → quarantine; atomic publish; one bad value → one gap), all tested. *Risk:* no live-data exposure yet. *Future:* shadow-run against real exports. |
| **Maintainability** | **9** | Small modules, intent-revealing names, per-folder READMEs, shared primitives. *Risk:* docs/code drift over time. *Future:* keep the spec and doc updated as the source mapping firms up. |
| **Documentation** | **9** | Spec + narrative doc (lifecycle, pipelines, troubleshooting, add-a-provider) + folder READMEs + this report. *Risk:* drift. *Future:* a short CHANGELOG when the live source lands. |
| **Testing** | **9** | 54 dependency-free tests across translation, validation, malformed input, missing fields, sensor failure, change detection, snapshot compatibility, provider failures, and UTF-8; run in CI on 3.11/3.12. *Risk:* no coverage metric; real-export untested. *Future:* add coverage reporting and a captured real-export fixture. |
| **Extensibility** | **9** | The headline strength: live source = one module + one line + a mapping check. *Risk:* the seam is only exercised by fixtures so far. *Future:* the `ApiSource` will confirm it. |
| **Performance** | **9** | ~5.8 ms/run, no redundant work; cost is intentional durability. *Risk:* untested at high cadence / large payloads (not expected). *Future:* none needed now. |
| **Security** | **9** | Read-only, atomic publish, size + UTF-8 guards, no live bus, no secrets, no injection surface. *Risk:* future credential handling in `ApiSource`. *Future:* security-review the live source when written. |
| **Operational readiness** | **7** | Exit codes, structured logs, troubleshooting guide, and CI are in place. *Risks:* the scheduled run (Task Scheduler) is not yet wired; there is no failure alerting or log rotation; Python is not on PATH on the host. *Future:* wire a scheduled task, add simple failure alerting (e.g. on exit 2/3) and log rotation, and put Python on PATH. |

**Composite:** strong and shippable for its scope; operational wiring and the live provider are
the remaining, clearly-scoped steps.

---

## 6. What remains before PTP-OS can monitor the greenhouse live

1. **Confirm the access method** — sanctioned Synopta/Hortimax API, or a scheduled export drop.
2. **Implement one `SynoptaSource` module** for it (+ one line in `make_source`).
3. **Confirm the field mapping** in `translate.py` against a *captured real* export, and add it
   as a fixture + translation test.
4. **Wire operations** — a scheduled morning run, failure alerting, and log rotation.

Nothing above the source seam needs to change. That is the point of this sprint.

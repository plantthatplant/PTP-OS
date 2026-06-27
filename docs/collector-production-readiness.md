# Gaia Collector — Production Readiness Report

**Date:** 2026-06-27 · **Scope:** `collector/` (Gaia Collector v1) and the shared refactor in
`app/greenhouse_brain/units.py`. **Verdict:** production-ready for the fixture / drop-folder
scope; the live Synopta source is the one remaining gated step, and is intentionally deferred.

Evidence: 48 automated tests pass (`python -m unittest discover -s collector/tests`); the Brain's
existing entry points (`ask.py`, `import_snapshot.py`, `demo_live_dispatch.py`,
`demo_provider_swap.py`) and the Collector demo all run unmodified after the refactor.

---

## 1. Architectural compliance — VISION.md & CLAUDE.md

Every principle, checked against the code.

### CLAUDE.md — Core Principles
| # | Principle | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Reality before assumptions | ✅ | Missing values become honest absence, never 0 (`translate.py`; `test_units`, `test_translate`). |
| 2 | Biology before software | ✅ | No biological logic in the Collector; biology stays latent and downstream. |
| 3 | Observation before inference | ✅ | Alarms/readings carried as observations; no conclusions emitted. |
| 4 | Ask before assuming | ✅ | Stopped to confirm the source method and the Python install before acting. |
| 5 | Learn from outcomes | ➖ N/A | Acquisition layer; it *feeds* the learning loop but does not learn. No deviation. |
| 6 | Prefer simplicity | ✅ | Small single-purpose modules; shared primitives instead of copies. |
| 7 | Explain uncertainty | ✅ | Per-observation confidence + snapshot coverage / reality-confidence. |
| 8 | Highest-value-first | ✅ | This is the agreed highest-value work (real integration, not new reasoning). |
| 9 | Every sprint betters the grower | ✅ | Connects Gaia to the real greenhouse — the prerequisite for daily usefulness. |
| 10 | Protect the architecture | ✅ | Reuses the provider/snapshot seam; the duplication refactor was explicitly requested. |
| 11 | Daily usefulness | ✅ | A morning collection produces the file the brief is built from. |
| 12 | Build for Kålaberga first | ✅ | Facility config and fixture model the real houses. |

### VISION.md — defining constraints
| Constraint | Status | Evidence |
| --- | --- | --- |
| Data enters only through the Provider Layer | ✅ | Collector produces a Snapshot; `SnapshotProvider` serves it. Vendor shape never crosses the boundary. |
| The value must outlive any source | ✅ | The `SynoptaSource` seam; swapping sources changes one module. |
| Biology before technology | ✅ | No technology decision overrides plant reality; none is made here. |
| Trust before automation | ✅ | Read-only; no actuation, no live control bus, no OCR. |

### docs/project-rules.md
| Rule | Status | Evidence |
| --- | --- | --- |
| Every external system through a provider | ✅ | Synopta enters via the source seam → Snapshot → provider. |
| Business logic independent of vendor | ✅ | All vendor specifics contained in `sources/` and the `translate.py` mapping. |
| One prompt = one feature | ➖ N/A | No prompts/AI in the Collector. |
| Document everything important | ✅ | Spec, narrative doc, folder READMEs, this report. |
| Specification before implementation | ⚠️ Minor | Spec and code were produced in the same session under direct instruction (see Deviations). |

---

## 2. Deviations and open items (full, honest list)

1. **Live Synopta source not implemented (by instruction).** `DropFolderSource` needs a real
   export path; `ApiSource` is not written. The bridge is proven on a fixture, not on live
   Synopta. *This is the intended remaining step, gated on confirming the access method.*
2. **The raw export shape is assumed, not captured.** `sample_synopta_export.json` models the
   established vendor shape; the real export/API may differ, requiring a mapping adjustment in
   `translate.py` (spec open question #2).
3. **Spec and code in one session.** Project rules prefer a reviewed spec first; here both were
   delivered together under explicit direction. Flagged, not hidden.
4. **No continuous integration.** Tests are comprehensive but run manually; there is no CI
   pipeline or coverage measurement in the repo yet.
5. **Coarse confidence model.** Confidence is a high/medium/low heuristic (a sensor-fault alarm
   → low). Acceptable per the snapshot spec, but simple; richer source-reliability modelling is
   future work.
6. **Reuse via `sys.path` injection.** The Collector imports the Brain by adding `app/` to the
   path (`_paths.py`) rather than as an installed package — pragmatic for a zero-dependency
   repo, but not a packaged distribution.
7. **Prior-turn cleanup applied.** `.claude/settings.local.json` had been committed; it is now
   untracked and git-ignored.

None of these are correctness defects in the shipped scope; items 1–2 are the substance of the
next step.

---

## 3. Scores (1–10)

| Area | Score | Rationale |
| --- | :---: | --- |
| **Architecture** | **9** | Clean acquisition/reasoning separation; reuses the provider + snapshot seams; new source = one module. Not 10 until proven against real Synopta. |
| **Maintainability** | **9** | Small, single-responsibility modules; names and comments in the repo's voice; READMEs per folder; shared primitives remove triplication. |
| **Reliability** | **8** | Fail-safe paths tested — dead source keeps the last good snapshot, invalid → quarantine, one bad value → one gap; logging never raises. Held back by no live-data exposure and no CI. |
| **Extensibility** | **9** | The headline strength: the source seam makes the live provider a single new module + one registration line. < 10 until an `ApiSource` actually exercises it. |
| **Documentation** | **9** | Spec, full narrative doc (incl. a step-by-step "add a source"), folder READMEs, this report. |
| **Testing** | **8** | 48 dependency-free tests across translation, validation, failure, change-detection, and snapshot compatibility, plus integration runs in a temp dir. No coverage metric / CI / real-export tests yet. |
| **Security** | **8** | Read-only; no live control bus (the discovered `admin:admin` AMQP is untouched); no OCR; no secrets in code. Future `ApiSource` must take credentials from the environment; drop-folder only parses JSON. |
| **Performance** | **9** | One small file read + a linear transform per run; negligible cost. Not 10 only because it is untested at high cadence / large payloads. |

**Composite:** strong. The Collector is ready to run daily on the fixture/drop-folder path; the
codebase is shaped so that going live is additive, not invasive.

---

## 4. Recommendation

Ship the Collector. Treat the live integration as the next, separate unit of work: confirm
whether Synopta exposes a sanctioned API or a scheduled export, then add the one
`SynoptaSource` module and confirm the field mapping against a captured real sample. Consider
adding a minimal CI run of `unittest` to guard the contract over time.

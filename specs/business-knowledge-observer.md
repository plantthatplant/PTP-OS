# Spec — Business Knowledge Observer (Google Drive)

**Status:** Draft v1 · implemented in [`collector/observers/`](../collector/observers/).
**Related:** [`rfc/RFC-004-observer-network.md`](../rfc/RFC-004-observer-network.md),
[`specs/observer-network.md`](observer-network.md),
[`specs/greenhouse-snapshot.md`](greenhouse-snapshot.md) (the Canonical Observation envelope).

## 1. Purpose

The greenhouse computer tells Gaia **what is happening**. Google Drive tells Gaia **what was
supposed to happen**. The Business Knowledge Observer reads the greenhouse's planning
spreadsheets — crop/production plans, bench allocation, profitability, capacity, financial
assumptions — and reports them as **Canonical Observations of intention**. The gap between
intention and reality is where biological and business insight lives.

## 2. Hard rules

- **Intention, not truth.** The spreadsheets are *plans*. **Reality always has priority.** A
  plan observation never overwrites a reality observation.
- **Conflict → Knowledge Gap, never a correction.** When a plan disagrees with what is observed,
  raise a question ("planned occupancy no longer matches reality", "expected harvest date appears
  unrealistic"); never silently reconcile.
- **No biological reasoning.** The observer parses and reports. The Brain is unchanged.
- **Provenance, time, confidence, absence preserved.** Every observation records its source file,
  the plan's last-modified time (`captured_at`), `method: imported`, a confidence (plans are
  `medium` by nature, lower if stale), and honest absence for tables it cannot read.

## 3. What it produces (observation kinds)

Per the Observer Network, the output is the standard Canonical Observation envelope. Kinds carry
the intention via an `expected-` / `planned-` prefix:

| Kind | Subject | From |
| --- | --- | --- |
| `expected-occupancy` (%) · `planned-benches-active` · `benches-delayed` | zone | plan dashboard "BELÄGGNING PER VÄXTHUS" |
| `expected-harvest` · `expected-harvest-date` | zone | plan dashboard "KOMMANDE LEVERANSER" |
| `expected-revenue` (kr) · `expected-labour` (FTE) · `planned-growing-area` (m²) | site | profitability "INDATA – BOKSLUT" |

Crop-level `expected-profitability` (portfolio/BCG) is recognised as future work — reported as
absence until that sheet's mapping is confirmed, rather than guessed.

## 4. Plan vs reality (the value)

[`plan_vs_reality.compare(plan_obs, reality_obs, now)`](../collector/observers/plan_vs_reality.py)
is a **mechanical** comparison (numbers, dates, categories) — not biology. For each plan fact it
finds the matching observed fact (same subject + base kind) and, if they diverge beyond a 10%
tolerance (or a planned date has passed), emits a **Knowledge Gap** question. It never mutates
reality. Examples it raises today, on the real files:

- *"h2: planned occupancy (53%) differs from observed (30%) — which is right?"*
- *"h1: the planned harvest date (2026-07-17) has passed — did it happen, or is the schedule slipping?"*

These become biologically and operationally valuable questions for the Companion to surface only
when worth it (the existing Knowledge-Gap / Interaction economics decide that).

## 5. Interface

```
GoogleDriveObserver(paths).observe() -> List[CanonicalObservation]   # intention
plan_vs_reality.compare(plan, reality, now) -> List[KnowledgeGap]    # divergence → questions
```

Plan observations are kept in their own stream (`data/inbox/plan-latest.json`), **separate from
reality** (`data/inbox/latest.json`), so intention can never be mistaken for observation.

## 6. Today vs future

- **Today:** reads `.xlsx` files from disk (kept current by the Google Drive desktop client or a
  download), with a dependency-free standard-library reader
  ([`collector/xlsx_read.py`](../collector/xlsx_read.py)).
- **Future:** the live Google Drive API is a *transport* behind this same observer — when a
  document changes, Gaia receives updated observations automatically, with no manual import. The
  observations it produces do not change; only how the file is fetched does. (Same seam principle
  as the Collector's sources.)

## 7. Out of scope

No actuation, no biology, no editing the spreadsheets, no overwriting reality, no new Snapshot
format. Crop-level profitability parsing and live Drive sync are named future work, not built
here.

# Sprint 1 — Shortcuts and What Replaces Them

The first Greenhouse Brain works: you can ask *"How is the greenhouse today?"* and get a
useful, health-first, honestly-hedged answer (`app/`). It was built for **learning, not
completeness** — so it takes many deliberate shortcuts. This document names every one and
what should later replace it, so no shortcut is mistaken for a finished decision.

The honesty principle from the canon applies to ourselves: the prototype *says* in every
answer that it runs on mock data. This is the long form of that confession.

## The four big replacements (as requested)

### → Synopta (and Claude Dispatch before it)
- **Done (the swap):** `ClaudeDispatchProvider` now exists and implements the **same**
  `GreenhouseProvider` interface, translating a Claude Dispatch / Synopta extract into the
  domain model. The swap was proven (`app/demo_provider_swap.py`) with **zero changes to the
  Context, Decision, Language, or Morning Analysis engines** — the abstraction held (ADR-002).
- **Transport is now live (over a stand-in endpoint).** `transport.py` adds `HttpDispatchTransport`
  — a real HTTP GET, parsed at request time — selected by config (`PTP_DISPATCH_URL`). Proven by
  `app/demo_live_dispatch.py` against a local server standing in for the Claude Dispatch endpoint
  (no real greenhouse/Synopta is reachable here). The translation layer was **not** changed; only
  ingestion wiring (`__init__`) plus a `_normalise` guard that absorbs live messiness (comma
  decimals, missing/partial houses) so the engines only see clean domain objects. **To go fully
  live: change the URL and add the API key — nothing else.**
- **The footer label is now actively wrong, and left so on purpose.** On the live run *and* the
  snapshot-importer run the briefing still prints "mock data" / "no live Dispatch feed yet",
  because `data_source` and the caveat list are hard-coded in `MorningAnalysisEngine`. The last
  two milestones were told **not to touch Morning Analysis**, so it wasn't — flagged here instead.
  The fix (provider supplies its own label/caveats) is the recommended immediate follow-up.

### → Gaia daily companion + learning loop (Sprint 3)
- **Done:** `app/gaia.py` (`morning` / `walk` / `evening`) — the daily ritual a grower could
  use, built **only** from existing engines plus an experience/lifecycle layer (`lifecycle.py`,
  `dialogue.py`, `views.py`). Every recommendation becomes an Experiment, is followed to its
  outcome in the Evening Review, and is kept as a memory; the next morning recalls it (`↻`) and
  surfaces yesterday's longer-window experiments on the walk. No engine, provider, or data-model
  change.
- **NL parsing is keyword-based.** Walk/evening answers are mapped to outcomes by keywords
  (`better`/`worse`/`still`…), so an answer like "fine" reads as *unknown*. Real natural-language
  understanding (and the conversational Language Engine of decision-capture) replaces this later.
- **Persistence is the minimal local store** (`data/experiments-open.json`, `data/memories.jsonl`)
  — still the stand-in, not the Memory Engine. Confidence steps along a fixed ladder; there is no
  cross-experiment pattern-mining yet (that is the Learning Loop's next stage).
- **Confidence/`data_source` footer** on the older renderers still mislabels source; the new
  `views.py` brief avoids it. The engine-owned label remains the one sanctioned-but-unmade fix.

### → Greenhouse Snapshot importer (live observations)
- **Done:** `app/import_snapshot.py` reads a canonical Greenhouse Snapshot
  (specs/greenhouse-snapshot.md), converts it (`snapshot.py` / `snapshot_importer.py`), and runs
  the **unchanged** engines via `SnapshotProvider`. It reports missing values (never invented),
  observation coverage %, and an overall reality confidence (= data quality × coverage). A
  near-empty snapshot still yields a brief — missing data lowers confidence, never errors.
- **Sample input is ours.** No real live-observation JSON was provided, so `app/sample_snapshot.json`
  stands in (canonical format, with deliberate nulls). Point the importer at a real file to replace it.
- **Targets-by-stage still live in the provider** (agronomic knowledge, not observation) — the
  Knowledge Platform gap is unchanged.
- **Coverage is intentionally tiny.** Only the 7 core climate signals are mapped; everything
  else is honest absence. So the Claude Dispatch analysis is leaner than the mock's (no
  desiccation/toning/opportunity/curiosities) — data coverage, not architecture.
- **One additive domain change, disclosed:** an optional `timestamp` field on `ClimateReading`
  (to carry signal #1). Additive, default `None`, read by no engine.
- **One cosmetic gap left on purpose:** the briefing footer still prints "mock data" even on the
  Claude Dispatch run, because the `data_source` label is hard-coded in `MorningAnalysisEngine`.
  Correcting it would mean editing Morning Analysis — which this milestone was told **not** to
  touch — so it was left and flagged. The fix later: let the provider supply its own label/caveats.
- **Still missing:** real polling, staleness handling, unit normalisation edge cases, the
  provider error taxonomy, and the conformance test suite (S1-04) that would *prove*
  substitutability rather than demonstrate it once.

### → Plant observations
- **Shortcut:** the brain sees almost no plant. It reasons from **climate plus a handful of
  hand-written human notes** (condensation, "cuttings unrooted", "batch soft"). Plant State,
  Stress, and Disease Risk are *inferred from the environment*, and the answer says so.
- **Replace with:** a real source of plant/observation/stage data — the grower's morning
  observations entered directly (the cheapest, most trustworthy first source), and later
  camera/vision. This is the single biggest gap, and the open question in both operational
  specs. Until it exists, the brain is honestly "reads the house," not "has seen the plants."
- **Also missing:** growth-stage tracking and expected timelines per batch (stage is a fixed
  label on the mock zone, not a tracked, advancing state).

### → Memory Engine
- **Shortcut:** there is **no memory**. The "rising three mornings" trend is a hard-coded
  list in the mock provider; the latest Morning Analysis is cached to `app/.state/` as a
  single JSON file (`store.py`) so `ask.py` can serve what `morning.py` prepared — but that
  cache keeps only the most recent analysis, links nothing to outcomes, and learns nothing.
  There is no "yesterday baseline", no outbreak history, no record of whether a recommendation
  helped. Every morning starts from nothing.
- **Replace with:** the Memory Engine — at minimum the **write-path** (record each
  assessment and its confidence so calibration can begin, backlog S1-11), then the
  **read-path** (history and learned response feeding Context), which RFC-001 deliberately
  defers. Change-detection ("what changed since yesterday?") needs at least a stored prior
  snapshot. The `app/.state/` cache is a stand-in for the *storage* mechanic only — not the
  learning.

### → Decision Library
- **Shortcut:** the reasoning is **five hand-written `if` rules** in `decision_engine.py`
  (disease setup, desiccation, suspect reading, toning window, recovered transient). They are
  transparent and faithful to the philosophy, but they are not a catalogue, not data-driven,
  and not extensible without editing code.
- **Replace with:** a real **Decision Library** — decision/assessment *types* with declared
  structure, evidence requirements, and confidence rules, that the Decision Engine consults
  (backlog S1-08 builds the first proper one). The five rules here are the seed of its first
  few entries.

## Other shortcuts taken (smaller, but real)

**Stack & engineering**
- **Language/runtime not formally chosen (S1-00).** Built in Python 3, stdlib only, because
  it runs on this machine with zero install and lets us validate reasoning today. The `.gitignore`
  and earlier pseudocode lean Node/TypeScript; this choice is a prototype decision, not a
  product commitment, and deserves its own ADR.
- **No tests, no CI, no provider conformance suite** (S1-01, S1-04). The conformance suite
  that *proves* the Synopta swap is safe does not exist yet; correctness here rests on reading
  the output, not on tests.
- **No build, packaging, or config/dependency-injection.** Components are wired directly in
  `brain.py`.

**Input / intent**
- **No real intent understanding.** v1 recognises one question by keyword and otherwise says
  so. The input-side interpreter named as missing in specs/greenhouse-brain-v1.md (Step 0) is
  not built.

**Knowledge & signals**
- **Species/stage targets are hard-coded** on the mock zones — there is no Knowledge Platform.
  Real targets per species/stage/time-of-year are needed for Context to be meaningful beyond
  this scenario.
- **Derived signals are minimal.** VPD and dew point are computed and real; 24-hour average
  temperature, day/night difference, light sum, and leaf-wetness *duration* are not yet used.
- **The day-ahead outlook is a placeholder** inside the mock provider — a stand-in for a real
  Weather provider. The "protect the cuttings this afternoon" priority rests on it, which is
  why that item carries lower confidence.

**Morning Analysis, opportunities & curiosities**
- **The Brain is proactive but on a manual trigger.** `morning.py` must be run to produce the
  day's analysis; nothing schedules it. A real deployment would run it automatically before
  the day starts (and the daily-operating-cycle's continuous loop replaces a single run).
- **Opportunities and curiosities are a few transparent heuristics**, like the decision rules
  (within-range trend, a consistent oddity, a follow-up on a logged change). They are the seed
  of a real learning capability, not the thing itself — curiosities are raised but never
  followed up automatically, and answering one would need the Memory Engine and plant
  observations.

**Reasoning & confidence**
- **Confidence is a small heuristic, not calibrated.** Levels (High/Medium/Low) come from
  simple corroboration rules; the system has no track record of its own accuracy yet (a
  cold-start system cannot be calibrated — which is exactly why the Memory write-path matters
  from day one).
- **Ranking scales are qualitative and fixed.** The tier/window/value ordering encodes the
  first-useful-decision method faithfully, but the thresholds are judgement, not tuned.
- **Specialist agents and the AI COO are implicit.** The single Decision Engine plays all the
  lenses at once; the agent structure of RFC-003 is not yet separated out (correctly — it is a
  configuration over this one engine, to be drawn out later, not duplicated).
- **The decision hierarchy lives in prose, not in one authoritative place.** It should be
  promoted to an ADR, since the ranking here and the future AI COO both depend on it.

**Language / interface**
- **Template renderer, no AI model.** Calm phrasing is deterministic string assembly (ADR-001
  permits this for simple cases). An AI-backed Language Engine slots in behind the same
  `LanguageRenderer` interface — with one versioned prompt (S1-09) — without touching reasoning.
- **Output is plain text to a terminal.** It is structured-first internally (a `Briefing`
  object), so a screen or voice/glasses surface can render the same briefing later; no such
  surface is built.

## What this prototype already gets right (so it is not thrown away)

- Data enters **only** through the Provider Layer; the rest of the code never sees the mock.
- Reasoning is **model-independent and fully explainable** — every claim carries its evidence.
- Language is **isolated and replaceable**.
- The answer is **health-first, calm, prioritised, and honest** about what it cannot see.
- The seams that matter (provider, language renderer, the briefing structure) are real, so the
  replacements above are substitutions, not rewrites.

## What we learned (Sprint 1 reflection)

- **The flow holds.** Philosophy → reasoning → answer survives contact with running code; the
  pipeline produced a genuinely useful morning answer.
- **The binding constraint is plain:** without plant observations, the brain reasons about the
  *house*, not the *plants*. Resolving where observations come from is the highest-leverage
  next step — above any production API.
- **Honesty is cheap and valuable.** Making the brain confess its mock data and inferred
  plant-state in every answer cost nothing and makes the prototype trustworthy to demo.
- **Two prose-only decisions are now load-bearing** and should become ADRs: the **stack
  choice**, and the **decision hierarchy**.

## Suggested next steps (Sprint 1 continued)

1. **Replace plant-state guesswork with a grower-observation input** — let the grower tell the
   brain what they saw; the cheapest real plant data, and it fits "trust before automation."
2. **Wire `ClaudeDispatchProvider`** behind the existing interface; keep the mock as the
   conformance/test fixture.
3. **Add the Memory write-path** so assessments are recorded and calibration can start.
4. **Promote the decision hierarchy and the stack choice to ADRs.**
5. **Extract the first real Decision Library entry** from the hand-written rules.

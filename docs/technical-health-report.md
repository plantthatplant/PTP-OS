# Technical Health Report — toward v1.0

A Chief-Architect review of the PTP OS / Gaia codebase (`app/`, ~2,500 lines of Python),
read in full. The goal is not elegance; it is **a system that can still evolve five years
from now.** No code was changed: a deliberate scan for a critical defect (crash, data loss,
correctness break in normal single-greenhouse use) found **none**, so per the sprint rule
nothing was implemented. Everything below is debt to schedule, not an emergency.

First, the assets worth protecting — because a review that only lists faults misleads:

- **The Provider abstraction is real and proven.** Mock → Claude Dispatch (fixture) → Claude
  Dispatch (live HTTP) → imported Snapshot all ran the *same* engines unchanged. This is the
  project's strongest decision and must not be eroded.
- **The engines are model-independent and legible.** Every recommendation states its evidence,
  confidence, and biological reasoning. No black box. This is rare and valuable.
- **The learning loop actually closes.** Recommendation → experiment → outcome → memory →
  next-morning recall (`↻`) works end to end, with an evolving confidence trajectory.
- **Honest-absence discipline.** Missing data lowers confidence rather than crashing or being
  invented — consistently, with coverage/reality-confidence surfaced.

These are the things to defend while paying down the debt below.

---

## Issues

Each: *why it exists · why it matters · smallest improvement · now or postpone.*

### Duplicated concepts

**1. Stage→climate targets defined in three places.**
`claude_dispatch_provider.py`, `snapshot_provider.py`, and `mock_provider.py` each hard-code the
same propagation/vegetative/finishing target bands.
- *Why it exists:* there is no Knowledge boundary; each provider needed targets, so each copied them.
- *Why it matters:* "what good climate is" is the most change-prone agronomic knowledge; three copies
  drift, and 500 greenhouses with different crops will multiply the copies.
- *Smallest improvement:* one shared `knowledge.targets_for(stage, crop)` module both providers import.
- *Verdict:* **Postpone** — fold into the Knowledge-boundary work (it's the seed of the Knowledge Platform), not urgent at one house.

**2. Confidence has three vocabularies.**
`decision_engine` emits `Low/Medium/High` (+ ad-hoc `"Medium-high"`); `lifecycle._LADDER` and
`views.py` *each re-declare* the four-step ladder verbatim; `snapshot._CONF_WEIGHT` uses lowercase
`high/medium/low` weights.
- *Why it exists:* confidence was added module-by-module across sprints, never centralised.
- *Why it matters:* confidence is the spine of the whole learning/calibration story; inconsistent
  scales make it impossible to compare or aggregate, and the verbatim-duplicated ladder will drift.
- *Smallest improvement:* one `confidence.py` defining the scale, the ladder step, and the weight map;
  everyone imports it.
- *Verdict:* **Postpone, but soon** — small, low-risk, and it underpins the learning subsystem.

### Overlapping responsibilities

**3. Two renderers.** `language_engine.py` (`render_morning/render_status`) and `views.py`
(`render_brief/render_evening`) both turn analysis into text; the product uses `views`, the older
entry points use `language_engine`.
- *Why:* `views` was added in Sprint 3 for a nicer brief without touching the Language Engine ABC.
- *Why it matters:* two presentation paths to keep in sync; the "Language Engine" abstraction is
  half-bypassed, so the seam meant to host the future AI renderer isn't where the real rendering lives.
- *Smallest improvement:* make `views` the implementation *behind* the `LanguageRenderer` interface,
  or retire `language_engine`'s renderers. Pick one home.
- *Verdict:* **Postpone** — converge when the AI-backed renderer is built (that's the natural moment).

**4. Two orchestrators.** `brain.py` (`GreenhouseBrain`) and `gaia.py` (`cmd_morning`) both compose
provider → analysis → render.
- *Why:* `GreenhouseBrain` (Sprint 1) predates the `gaia` CLI (Sprint 3) and survives for `morning.py`/`ask.py`.
- *Why it matters:* two paths drift; a reader can't tell which is canonical.
- *Smallest improvement:* make `gaia` the one entry point; have `morning.py`/`ask.py` call into it (or drop them).
- *Verdict:* **Postpone** — harmless now; tidy when trimming entry points.

**5. `store.py` is a god-module.** Twelve functions across six unrelated concerns (analysis cache,
feedback log, walk answers, yesterday-signals, experiments, memories, questions).
- *Why:* it began as "a minimal cache, NOT the Memory Engine" and absorbed every persistence need since.
- *Why it matters:* it's now the de-facto data layer with no boundaries; it is exactly where the real
  Memory Engine will have to be carved out, and a single grab-bag makes that carving harder.
- *Smallest improvement:* split into `cache` / `learning-store` / `dialogue-store` behind small
  interfaces — even if all still write JSON for now.
- *Verdict:* **Postpone to the Memory-Engine sprint**, but treat this file as the seam.

### Unclear boundaries & weak abstractions

**6. The Provider contract and the Greenhouse Snapshot have diverged. (The important one.)**
The spec (`greenhouse-snapshot.md`) says *every provider produces a Greenhouse Snapshot*. The code's
`GreenhouseProvider` instead exposes `get_latest_climate()→{ClimateReading}`, `get_observations()→[Observation]`,
`get_outlook()→Outlook` — the older multi-method shape that predates the Snapshot. The canonical
`Snapshot` exists, but only the import path uses it, and `SnapshotProvider` adapts Snapshot *backwards*
into the old domain objects.
- *Why it exists:* the Provider abstraction (Sprint 0–1) was designed before the Snapshot spec (Sprint
  late), and they were never reconciled.
- *Why it matters:* there are **two ingestion data models**, and the canonical one isn't the contract.
  This is the single biggest obstacle to a clean v1.0 and to multi-tenant scale.
- *Smallest improvement:* make `GreenhouseProvider.get_snapshot() -> Snapshot` the one contract; let the
  Context Engine read a Snapshot directly; retire the multi-method shape over time.
- *Verdict:* **Address before v1.0** (not now — no defect). The highest-priority architectural fix.

**7. Two Observation models.** `domain.Observation` (flat: zone/type/text) and
`snapshot.SnapshotObservation` (the full envelope: value/unit/source/method/confidence/verbatim). The
importer flattens the envelope into the flat form before the engines see it.
- *Why:* the flat `Observation` is from Sprint 1; the envelope is the Snapshot spec.
- *Why it matters:* provenance and per-observation confidence — the things the Decision Philosophy says
  must travel with evidence — are **dropped at the boundary**, so the engines can't weigh evidence by
  source/recency as designed.
- *Smallest improvement:* converge on the envelope as the single observation type (ties to #6).
- *Verdict:* **Address with #6** — same reconciliation.

**8. Knowledge lives inside providers/engines.** Targets (#1) and the Decision Engine's six hard-coded
`if`-rules are agronomic knowledge embedded in code.
- *Why:* a deliberate, legible Sprint-1 stand-in for the Knowledge Platform / Decision Library.
- *Why it matters:* every new crop or decision type is a code edit; 500 houses can't each need a deploy.
- *Smallest improvement:* move targets and decision-types to data the engines read (the Decision Library
  spec already anticipates this).
- *Verdict:* **Postpone** — fine and legible at one house; required before broad multi-crop scale.

### Unnecessary complexity

**9. Six overlapping entry-point scripts** (`gaia.py`, `morning.py`, `ask.py`, `feedback.py`,
`import_snapshot.py`, plus two demos). `gaia` subsumes most.
- *Why:* each sprint added its own CLI before `gaia` unified them.
- *Why it matters:* surface area to maintain and explain; unclear which is "the product."
- *Smallest improvement:* keep `gaia` + the two demos; fold the rest into `gaia` subcommands.
- *Verdict:* **Postpone** — low cost; tidy opportunistically.

### Future maintenance risks

**10. Persistence is flat files, single-greenhouse, full-rewrite.** `experiments-open.json` /
`questions-today.json` / `yesterday-signals.json` are rewritten whole; memories/feedback are appended
JSONL. No indexing, no concurrency control, no greenhouse partitioning, no schema version.
- *Why:* the "minimal store" was right for a one-house prototype.
- *Why it matters:* it cannot carry 500 houses × years of records; concurrent runs would race; there is
  no migration path as record shapes change.
- *Smallest improvement:* define a storage *interface* now (records keyed by greenhouse + id + version)
  even while the implementation stays simple — so the swap later is localized.
- *Verdict:* **Address before v1.0 / before multi-tenant.**

**11. No automated tests; no provider conformance suite.** The spec promised a conformance suite to
*prove* substitutability (S1-04); it was demonstrated once, never tested.
- *Why:* sprints optimised for visible value; tests were deferred.
- *Why it matters:* a system meant to evolve for a decade cannot be safely changed without tests; the
  provider swap — the core guarantee — is currently protected by hope, not by CI.
- *Smallest improvement:* a conformance test every provider must pass, plus unit tests on the Decision
  Engine rules. Start small.
- *Verdict:* **Begin now-ish** — the highest-value non-feature work; low cost, compounding payoff.

**12. Identity & time are string-derived.** Experiment ids are `exp-{date}-{zone}-{kind}` from
`snapshot.assembled_at[:10]`; two runs the same date dedupe by id.
- *Why:* expedient in Sprint 3.
- *Why it matters:* multiple runs per day, audit, and event-ordering all need real ids/timestamps; this
  will quietly corrupt the learning record at scale.
- *Smallest improvement:* explicit record ids + real timestamps; append-only events, not rewrites.
- *Verdict:* **Address with the Memory-Engine / storage work.**

*(Spec-ahead-of-code is noted but not a fault: the Curiosity Engine, Decision Library, and Daily
Dialogue are specified beyond what's built. That is intended sequencing, not debt — provided the specs
are treated as design intent, not as claims of working software.)*

---

## Technical Health Report — subsystem scores (1–10)

| Subsystem | Score | One-line justification |
| --- | --- | --- |
| **Architecture** | 7 | Layering and the Provider seam are genuinely good and proven; pulled down by the Provider/Snapshot divergence (#6) and the god-store (#5). |
| **Domain Model** | 6 | Clean, readable dataclasses; but two Observation models (#7), three confidence vocabularies (#2), and knowledge embedded in code (#8). |
| **Snapshot** | 6 | Well-specified, honest about absence, carries coverage/confidence; but it is *not* the provider contract and is flattened on ingest (#6, #7). |
| **Providers** | 7 | The strongest part — real swaps proven, transport seam clean; minus duplicated targets (#1) and the backwards `SnapshotProvider` adaptation. |
| **Memory** | 4 | Works and is honest about being a stand-in; flat-file, single-tenant, un-indexed, full-rewrite (#10, #12). The biggest scale gap. |
| **Decision Engine** | 6 | Deterministic, model-independent, legible; but rules hard-coded (#8) and output quality coupled to input richness. |
| **Learning** | 6 | The loop genuinely closes and confidence evolves; weak persistence, no pattern-mining yet, curiosities still transient. |
| **Maintainability** | 5 | Small, well-documented modules; dragged down by duplication, two renderers/orchestrators, and no tests. |
| **Extensibility** | 6 | Provider seam excellent; but two ingestion models, knowledge-in-code, and single-tenant storage cap it. |
| **Testing** | 2 | Near-zero automated tests; the promised provider conformance suite does not exist. The clearest weakness. |

---

## "If this had to support 500 commercial greenhouses over ten years, what would you change before v1.0?"

Five changes — and, as importantly, four things to *not* touch.

**Change, in priority order:**

1. **Unify ingestion on the Greenhouse Snapshot (#6/#7).** Make `get_snapshot() -> Snapshot` the single
   provider contract and let the engines read a Snapshot directly, carrying the full observation envelope
   (provenance + per-observation confidence) end to end. One ingestion model is the foundation everything
   multi-tenant rests on.
2. **Replace the flat-file store with a real, multi-tenant Memory Engine (#5/#10/#12).** Durable, indexed,
   concurrency-safe, **partitioned by greenhouse**, append-only/event-sourced, with versioned records and
   real ids/timestamps. Define the interface before v1.0 even if the first implementation is modest.
3. **Make multi-tenancy a first-class dimension.** Every record, every piece of knowledge, every snapshot
   keyed by greenhouse (and crop). Today the system implicitly assumes one house (one `yesterday-signals.json`,
   one `experiments-open.json`).
4. **Extract Knowledge as data (#1/#8).** Targets, tolerances, and decision types out of provider/engine
   code into per-crop/per-greenhouse data, so 500 diverse houses never mean a code change or a deploy.
5. **Build the test + provider-conformance harness (#11).** A decade of change is impossible to maintain
   safely without it; the conformance suite is what keeps the Provider guarantee true as the system grows.

**Do not change (protect these):** the Provider abstraction; the model-independent, legible engines; the
learning-loop *design* (recommendation → experiment → outcome → memory → recall); and the honest-absence /
confidence-and-coverage discipline. These are the assets that make the system worth scaling — and the
reasons it can.

**Bottom line:** the *thinking* (architecture, domain, learning design) is strong enough to build a v1.0
on; the *plumbing* (one ingestion model, real multi-tenant storage, knowledge-as-data, tests) is what must
be paid down first. None of it is on fire — which is exactly why now, before scale, is the time to do it.

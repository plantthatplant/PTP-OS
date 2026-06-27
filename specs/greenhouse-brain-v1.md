# Spec — Greenhouse Brain v1

**Status:** Draft v1 · the blueprint for the first working Greenhouse Brain (for review
before implementation).
**Related:** [`docs/architecture.md`](../docs/architecture.md),
[`docs/biological-model.md`](../docs/biological-model.md),
[`docs/decision-philosophy.md`](../docs/decision-philosophy.md),
[`docs/cultivation-intelligence-model.md`](../docs/cultivation-intelligence-model.md),
[`rfc/RFC-003-layered-specialist-agent-architecture.md`](../rfc/RFC-003-layered-specialist-agent-architecture.md),
[`specs/greenhouse-provider.md`](greenhouse-provider.md),
[`adr/ADR-004-morning-intelligence-default-interface.md`](../adr/ADR-004-morning-intelligence-default-interface.md)

> This spec describes a **reasoning pipeline**, not software. It traces, step by step,
> what happens inside PTP OS between the moment a grower asks a question and the moment
> the answer is finished. Interfaces are illustrative; the point is the *reasoning*.

## 1. Purpose

Define exactly what PTP OS does — every internal reasoning step — when a grower asks the
single most important first question:

> **"How is the greenhouse today?"**

This is the smallest complete expression of the whole product: observe reality, assemble
the relevant picture, reason about it biologically, decide what matters, and explain it
calmly with honest confidence. If PTP OS can answer this one question well, every later
capability is an extension of the same pipeline. This document is therefore the blueprint
for the first working Greenhouse Brain.

## 2. Scope

**In scope.** The full path from utterance to answer for an open, whole-greenhouse status
question: intent, gathering reality, assembling context, biological reasoning, specialist
synthesis, prioritisation, explanation, delivery, and capturing the interaction for
learning.

**Honest v1 boundary.** The first Greenhouse Brain sees mostly *climate and structure*
(what the greenhouse data provider supplies) plus whatever *human observations* exist. It
can therefore reason richly about the **environment** and about **environment-driven risk**
(stress potential, disease-favourable conditions), but it must be **honest that it cannot
yet directly see most plant state** — there is no live plant-vision or dense crop
registration in v1. Per the Decision Philosophy, the correct behaviour where the plant
itself is unseen is to *say so*, reason from the best available proxy, and recommend
observation — not to fabricate confident plant verdicts. v1 is "the brain that reads the
house honestly," not "the brain that has already seen every plant."

**Out of scope (v1).** Acting on the greenhouse (actuation); commerce, finance, energy, and
weather providers (noted as graceful degradations); multi-turn conversation; voice/glasses
rendering specifics (output stays screen-independent so they remain possible).

## 3. Design stance (carried from the canon)

- **Optimise the plant, not the climate.** The answer is about plant wellbeing; climate is
  evidence, never the subject. (Biological Model.)
- **Latent before observed.** Plant State, Stress, Disease Risk are inferred, never read.
  Every estimate carries confidence and uncertainty and is defensible by its evidence.
- **Reason in relationships, trends, and context** — not single numbers. (Cultivation
  Intelligence Model.)
- **One brain, many lenses.** All reasoning lives in the Core Intelligence Layer; the
  specialist agents are scoped consumers of it; the AI COO composes, it does not reason.
  (RFC-003.)
- **Calm, prioritised, explained, honest.** Lead with the answer; surface the few things
  that matter; show confidence; say "I don't know" when true. (Decision Philosophy, ADR-004.)

---

## 4. The reasoning pipeline, step by step

Each step is described with the eight facets requested: **information required · service ·
internal questions · uncertainties · recommendations · information ignored · memories
consulted · biological principles.**

### Step 0 — The utterance

The grower speaks: *"How is the greenhouse today?"* Nothing has been interpreted yet.

- **Information required:** the raw question; who is asking; when; which greenhouse they are
  responsible for; the time of day (a morning question and an evening question differ).
- **Service:** *Intent Interpretation* (input-side understanding). **Note:** the architecture
  as drawn only defines the Language Engine for *output*. Understanding the grower's
  question is an input capability the architecture does not yet name — see Missing
  Capabilities §6.1. It belongs in the Core Intelligence Layer, before Context.
- **Internal questions:** What is actually being asked — a broad status assessment, not a
  specific metric. What scope (whole greenhouse, all zones). What horizon ("today" = current
  state plus what the day will bring). What is the grower's intent (decide where to focus
  this morning).
- **Uncertainties:** Ambiguity of "today" (now? next 24h?); which greenhouse if more than
  one; whether the grower wants the calm overview (default) or a deep dive.
- **Recommendations generated:** none yet — this step only frames the request.
- **Information ignored:** the literal phrasing; politeness tokens; anything implying a
  narrow metric when the question is plainly a broad one.
- **Memories consulted:** the grower's role and defaults (which house, preferred depth);
  the convention that the default answer is the calm Morning-Intelligence overview.
- **Biological principles:** none directly — but the frame set here ("assess plant wellbeing
  across the house, now and for the day ahead") commits the rest of the pipeline to reason
  about *plants*, not *climate*.

**Output of step:** a structured internal request — *{ intent: status-assessment, subject:
greenhouse G, scope: all zones, horizon: now + today, audience: grower, depth: overview }.*

### Step 1 — Gather reality

Fetch the current state of the world relevant to the request.

- **Information required:** greenhouse structure (zones, benches); latest climate per zone
  (temperature, humidity, CO₂, light); short climate history (last 24–48h for trend and
  averages); any recent human/camera observations; **(future providers, if present)** outdoor
  weather and forecast, energy price, orders/readiness — absent in v1.
- **Service:** **Provider Layer** (`GreenhouseProvider` → `ClaudeDispatchProvider`), returning
  Domain Model types only. (See greenhouse-provider spec.)
- **Internal questions:** What can I actually see right now? How fresh is each reading? Which
  zones/benches are sensed and which are dark? What did I fail to retrieve?
- **Uncertainties:** Staleness (how old is each reading); coverage gaps (un-sensed zones,
  un-scouted benches); sensor reliability/calibration; **the large gap that there is little
  direct plant observation** — most plant state is unseen. Absence is represented as
  absence, never as a fabricated value.
- **Recommendations generated:** none yet — but data gaps are *flagged* so later steps can
  turn them into "go look" recommendations.
- **Information ignored:** raw vendor shapes, units, and ids (normalised at the boundary);
  metrics irrelevant to a status overview; readings already known to be from faulty sensors.
- **Memories consulted:** sensor reliability history; known coverage gaps; the prior snapshot
  ("yesterday's state") to enable change detection later.
- **Biological principles:** *the plant leads the instruments* — climate is a lagging,
  partial proxy, so what we gather is evidence about conditions, not a verdict on plants.

**Output of step:** a normalised, timestamped picture of conditions + an explicit list of
what is missing or stale.

### Step 2 — Assemble context (the heart)

Turn raw conditions into a relevant, biological picture per zone and per batch.

- **Information required:** the gathered conditions; species/stage targets and tolerances
  (Knowledge); each batch's growth stage and expected timeline; derived biological signals;
  Memory of this house's history and prior outcomes; yesterday's snapshot for change.
- **Service:** **Context Engine** (Core Intelligence Layer), drawing on the **Knowledge
  Platform** and **Memory Engine**. The specialist lenses (Step 3) consume what it assembles.
- **Internal questions:** What is normal for this species, at this stage, at this time of
  day and year? What has *changed* since yesterday? What is *trending*? Which excursions were
  transient (recovered) and which are sustained? What is the day about to bring (light load,
  heat, a damp dark spell)? Which signals agree, and which conflict?
- **Derived signals to compute:** VPD and dew point (transpiration and condensation risk);
  24-hour average temperature and day/night difference (development pace and morphology);
  light sum so far and expected (growth supply); rates of change and trends; leaf-wetness /
  condensation likelihood.
- **Uncertainties:** the latent-state gap (conditions known, plant state inferred); variance
  across a batch; how far to trust species norms vs this house's learned response; confidence
  of each derived signal given its inputs' freshness and coverage.
- **Recommendations generated:** none yet — context *frames* candidates (deviations, rising
  risks, transitions due) but does not decide.
- **Information ignored:** normal diurnal variation within tolerance; a single transient
  excursion that recovered; precise values that do not change the biological meaning;
  out-of-tolerance readings from sensors flagged unreliable.
- **Memories consulted:** this zone's outbreak/risk history ("this corner molds in these
  conditions"); how this species/batch responded to similar conditions before; prior
  decisions and their outcomes (where the Memory read-path exists — see §6.5); the baseline
  of yesterday/last week.
- **Biological principles:** *development vs growth* and *temperature follows light*;
  *meaning is conditional on context* (humidity read with airflow and leaf temperature);
  *duration and repetition over magnitude* (a running total of small stresses); *recovery is
  the diagnostic*; *the disease triangle* (host + pathogen + favourable environment);
  *thresholds and non-linearity* near limits; *lag and acclimation*.

**Output of step:** a structured **context** — per zone/batch: conditions vs targets, derived
signals, trends vs baseline, candidate concerns and opportunities, each tagged with evidence
and provisional confidence; plus an explicit uncertainty ledger.

### Step 3 — Specialist lenses read the context

Each specialist agent examines the *same* assembled context through its concern, requesting
the relevant decision types from the shared engines. No agent holds its own reasoning or
model (RFC-003).

- **Information required:** the assembled context, sliced to each agent's scope.
- **Service:** **Specialist Agents Layer** over the **Decision Engine** + **Decision Library**.
  v1 agents:
  - **Climate Keeper** — conditions vs targets, VPD, dew point, 24h average, trend; "is the
    environment within the optimal biological range, now and for the day?"
  - **Plant Doctor** — disease/pest risk from environment + any sightings; "are conditions
    aligning toward a known risk for this crop/stage?"
  - **Plant Biologist** — stage, development-vs-growth balance, readiness trajectory; "is the
    crop developing in step with its light and on track for its date?" *(Degrades honestly
    where plant data is thin.)*
  - *(Future: Energy Optimizer, Production Planner, etc. — absent in v1.)*
- **Internal questions (per agent):** Within my concern, what matters today? What is
  changing? What is the limiting factor? What would I need to observe to be sure?
- **Uncertainties:** each agent declares its own confidence and the gaps in its concern
  (e.g. Plant Doctor: "no recent scouting on benches 3–5").
- **Recommendations generated:** each agent proposes *structured* candidate findings and, where
  warranted, recommendations — each with rationale, cited evidence, confidence, urgency, and
  the biological goal it serves and trade-off it accepts. Many agents will correctly propose
  *nothing* ("all within range").
- **Information ignored:** anything outside the agent's scope (the Climate Keeper does not opine
  on readiness); low-salience items below the agent's attention threshold.
- **Memories consulted:** concern-specific history (Plant Doctor reads outbreak history; Plant
  Biologist reads this cultivar's development pattern).
- **Biological principles:** each agent applies the principles of its domain — Climate Keeper on
  VPD/transpiration and temperature-follows-light; Plant Doctor on the disease triangle and
  leaf-wetness duration; Plant Biologist on development vs growth and stage-appropriate goals.

**Output of step:** a set of structured, evidence-bearing findings and candidate
recommendations, each scoped, confidence-rated, and goal-named.

### Step 4 — Reason and decide

The Decision Engine turns candidate findings into sound assessments and only-warranted
recommendations, applying the Decision Philosophy.

- **Information required:** all specialist findings; the decision hierarchy and inviolable
  constraints; confidence thresholds; reversibility/stakes of any candidate action.
- **Service:** **Decision Engine** (Core Intelligence Layer).
- **Internal questions:** Which concerns are real vs noise? What is the *one* limiting factor
  worth naming? Is each candidate recommendation *expected to improve plant outcomes*? Is it
  reversible and low-regret, or should it wait for more evidence? Does the confidence justify
  acting, or is the right output "observe"? Which goal does each serve, at what cost?
- **Uncertainties:** explicitly carried forward, not collapsed; where confidence is low on a
  high-stakes item, the decision is to *gather evidence*, not act.
- **Recommendations generated:** for a status question, mostly **assessments** plus a small set
  of recommendations where warranted — preferring *prevention* (head off a rising risk),
  *observation* (scout/measure to resolve uncertainty), and *patience* ("hold and re-observe")
  over intervention. "Do nothing" is a valid, explicit output.
- **Information ignored:** candidate actions that fail the "improves expected plant outcome"
  test; interventions that stack on a recovering plant; anything violating an inviolable
  constraint (off the table regardless of benefit).
- **Memories consulted:** outcomes of similar past decisions ("last time we chased this
  transient swing it cost energy and helped nothing"); calibration of past confidence.
- **Biological principles:** *prevention over correction*; *stable over maximum growth*; *act on
  the limiting factor*; *reversible, staged actions under uncertainty*; *do nothing is valid*;
  *match the plant's timescale*; *optimise health, not setpoints*.

**Output of step:** a set of decided assessments and recommendations, each with rationale,
evidence, confidence, urgency, goal, and trade-off — still structured, not prose.

### Step 5 — Compose the operating picture (AI COO)

Synthesis into one calm, prioritised picture. The AI COO orchestrates; it does not reason.

- **Information required:** all decided assessments/recommendations; their confidence and
  urgency; the decision hierarchy for conflict resolution; the attention budget.
- **Service:** **AI COO** (Specialist Agents Layer, orchestrator role).
- **Internal questions:** What are the few things that truly matter today? Where do specialists
  conflict, and who wins under the hierarchy (e.g. Plant Doctor over Energy Optimizer)? What is
  duplicated and should be merged? What is the single headline state of the house? What can be
  safely *left unsaid* to protect attention?
- **Uncertainties:** the overall confidence of the day's picture; explicitly which parts are
  well-evidenced and which are inferred or unseen.
- **Recommendations generated:** a ranked shortlist — by convention **about three** priorities,
  each with its reason and recommended action or observation; plus the overall verdict.
- **Information ignored:** everything below the salience threshold; resolved/duplicate items;
  anything that would add noise without changing what the grower should do.
- **Memories consulted:** what this grower considers worth surfacing; recent items already
  raised (do not interrupt twice for the same issue).
- **Biological principles:** *the greenhouse is one connected organism* (a climate item is also a
  disease and a readiness item); priorities ordered by the health-first hierarchy.

**Output of step:** a single structured **briefing** — overall state + ranked priorities, each
carrying reasoning, confidence, and (where relevant) a recommended next step; plus an honest
"what I cannot see / what I'm unsure about."

### Step 6 — Explain

Render the structured briefing into calm, clear language. No decisions are made or changed
here (ADR-001).

- **Information required:** the structured briefing; the audience and channel (screen now,
  voice/glasses later); the requirement to lead with the answer and show confidence.
- **Service:** **Language Engine** (Core Intelligence Layer), via a single versioned briefing
  prompt (one prompt = one feature).
- **Internal questions:** What is the one-line answer? How do I state each priority with its
  reason and confidence, plainly? How do I express uncertainty honestly without alarm? What is
  the smallest, calmest complete answer?
- **Uncertainties:** communicated, not hidden — ranges and qualifiers, the reason for the
  doubt, and what would reduce it ("I can't see the plants on benches 3–5 directly; worth a
  look").
- **Recommendations generated:** none new — it *phrases* the decided ones; it must not invent or
  upgrade them.
- **Information ignored:** internal structure, scores, and jargon; raw numbers except where they
  aid the grower; anything the briefing marked as suppressed.
- **Memories consulted:** the grower's preferred tone and level of detail.
- **Biological principles:** none directly — but the language must stay faithful to the biology:
  it speaks of plant wellbeing and risk, not of setpoints met.

**Output of step:** the finished answer — calm, prioritised, explained, honest — structured
first so it renders on screen today and by voice/glasses later.

### Step 7 — Deliver and remember

- **Information required:** the finished answer; a record of the question, the assessment, the
  evidence, and the confidence given.
- **Service:** delivery to the **User**; **Memory Engine** write-path records the interaction.
- **Internal questions:** What did we claim today, and how sure were we — so that when outcomes
  arrive, we can check ourselves and calibrate?
- **Uncertainties:** flagged items become candidate things to revisit ("re-observe in N days").
- **Recommendations generated:** optionally, a follow-up to close the loop later (scout, re-check).
- **Information ignored:** nothing of consequence — even "all normal" is worth remembering as a
  baseline.
- **Memories consulted:** none read here; this is the write side (RFC-001 learning loop).
- **Biological principles:** *never waste an outcome* — today's honest assessment is tomorrow's
  training, the foundation of becoming a better grower over time.

---

## 5. Complete sequence diagram

```
Grower        Intent        Provider      Context       Knowledge/    Specialist     Decision      AI COO        Language
 │            Interp.        Layer         Engine        Memory        Agents         Engine                      Engine
 │              │              │             │              │             │              │             │             │
 │─"How is the greenhouse today?"──────────▶│             │              │             │              │             │
 │              │ parse intent, scope, horizon            │              │             │              │             │
 │              │─structured request──────▶ │             │              │             │              │             │
 │              │              │◀─gather reality (structure, latest+recent climate, observations)─────│             │
 │              │              │─conditions + gaps──────▶ │              │             │              │             │
 │              │              │             │─targets, stage norms, history?─▶│       │              │             │
 │              │              │             │◀─species/stage targets, memory, baseline│              │             │
 │              │              │             │ compute VPD, dew pt, 24h avg, light sum, trends         │             │
 │              │              │             │ filter noise; flag transient vs sustained; build ledger│             │
 │              │              │             │─assembled context──────────▶│             │             │             │
 │              │              │             │              │   Climate Keeper │         │             │             │
 │              │              │             │              │   Plant Doctor   │─candidate findings──▶ │             │
 │              │              │             │              │   Plant Biologist│ (scoped, w/ confidence)│             │
 │              │              │             │              │             │              │ reason: real vs noise;    │
 │              │              │             │              │             │              │ limiting factor; confidence│
 │              │              │             │              │             │              │ gating; prevention/observe │
 │              │              │             │              │             │              │─decided items──▶│         │
 │              │              │             │              │             │              │   prioritise (≈3), resolve │
 │              │              │             │              │             │              │   conflicts by hierarchy,  │
 │              │              │             │              │             │              │   dedupe, headline state   │
 │              │              │             │              │             │              │─structured briefing──────▶│
 │              │              │             │              │             │              │             │  render calm,│
 │              │              │             │              │             │              │             │  honest,     │
 │              │              │             │              │             │              │             │  prioritised │
 │◀──────────────── finished answer (overall state + ~3 priorities + what I can't see) ───────────────────────────│
 │              │              │             │              │ write-path: record question, assessment, confidence  │
 │              │              │             │              │◀──────── remember for learning (RFC-001) ────────────│
```

## 6. Missing capabilities required to make this operational

Everything the pipeline above assumes but does **not** yet exist. Marked **[BLOCKING]** (v1
cannot run without it) or **[DEGRADE]** (v1 can run, but honestly diminished, until it
exists). Backlog references point to `docs/sprint-1-backlog.md`.

### 6.1 Input / intent understanding
- **[BLOCKING] An Intent Interpretation capability.** The architecture defines the Language
  Engine for *output* only. Understanding the grower's question (NL → structured request) is
  unspecified. v1 can start with a single hard-wired intent ("status overview"), but the gap
  must be named and owned. *New spec needed.*

### 6.2 Data sources
- **[BLOCKING] A live `GreenhouseProvider` (`ClaudeDispatchProvider`)** returning real
  structure + climate. (Backlog S1-03/04/05/06.)
- **[BLOCKING] A source of plant/batch/stage/observation data.** ClaudeDispatch supplies
  *climate*; the pipeline needs batch identity, growth stage, and human observations. Today
  there is no defined source. Until there is, plant-state reasoning **[DEGRADE]s** to "inferred
  from environment, plant unseen." *Decision needed: where do observations and stage come
  from in v1?*
- **[DEGRADE] Weather/forecast, energy, and orders providers** — needed for a *complete* "and
  here's what today will bring / what's due to ship" answer. Absent in v1; their absence must
  be stated, not hidden.

### 6.3 Knowledge
- **[BLOCKING] A Knowledge Platform with species/stage targets, tolerances, and norms.** The
  Context Engine compares conditions to "what is good for this species at this stage" — that
  reference does not exist yet. v1 needs at least a minimal target set for our main crops.
- **[BLOCKING] Derived-signal computation** (VPD, dew point, 24h average temperature, day/night
  difference, light sum, trends). Specified nowhere; central to biological reasoning. *New
  spec needed.*
- **[DEGRADE] Stage-tracking / expected-timeline knowledge** per species, to judge "ahead / on
  track / behind."

### 6.4 Reasoning
- **[BLOCKING] Latent-state estimation method (v1).** How conditions (+ any observations) become
  a provisional Plant State / Stress / Disease-Risk estimate. v1 can be transparent heuristics
  (e.g. environment-conduciveness for disease, VPD-based transpiration strain) — but the method
  must be specified, with its confidence.
- **[BLOCKING] Confidence & uncertainty computation.** A concrete v1 rule for forming confidence
  from quantity, quality, recency, coverage, and agreement — and for representing the two kinds
  of uncertainty. Required for honesty and for confidence-gating. *New spec needed.*
- **[BLOCKING] Noise / saliency rules.** Thresholds for transient-vs-sustained, "what counts as a
  deviation," and "what changed enough to mention." Without these the brain cannot be calm.
- **[BLOCKING] The Decision Library content** — at least the v1 decision/assessment types used
  here (climate-vs-target deviation; disease-risk-rising; readiness-on-track). Only the climate
  type is currently planned (S1-08).

### 6.5 Memory
- **[DEGRADE] A Memory read-path.** RFC-001 defers read-back to a later sprint (Sprint 1 builds
  the write-path only, S1-11). Until it exists, the pipeline runs **without** "this house's
  history" and **without** a "yesterday baseline" for change detection — a real diminishment of
  the answer. Change-detection in particular needs at least a stored prior snapshot.
- **[BLOCKING-for-learning] The write-path itself** (S1-11) to record each assessment and its
  confidence, so calibration can ever begin.

### 6.6 Agents & orchestration
- **[BLOCKING] Specialist agent definitions** (Climate Keeper, Plant Doctor, Plant Biologist) as
  scopes + decision types + objective slices over the shared engines (RFC-003 is still Open).
- **[BLOCKING] AI COO composition logic** — prioritisation, deduplication, and conflict
  resolution by the decision hierarchy. The hierarchy itself should be promoted from prose to a
  recorded decision (the proposed **ADR on the decision hierarchy**) so the COO has an
  authoritative rule.

### 6.7 Language / output
- **[BLOCKING] The Language Engine behind a replaceable model interface + one versioned briefing
  prompt** (S1-09), rendering the structured briefing calmly and honestly, screen-independent.

### 6.8 Cross-cutting
- **[BLOCKING] "I don't know" / graceful-degradation behaviour.** Explicit rules for missing,
  stale, or conflicting evidence, and for the large unseen-plant gap — so v1 is honest by
  construction rather than confidently wrong.
- **[DEGRADE] Calibration / track-record.** A cold-start system has no history of its own
  accuracy; confidence is uncalibrated at first. Acceptable for v1 if stated, and it is why the
  write-path matters from day one.
- **[DEGRADE] Grower identity / greenhouse selection** and preference memory (depth, tone).

## 7. Definition of done — Greenhouse Brain v1

A grower asks *"How is the greenhouse today?"* and receives, from **live** greenhouse data
through the Provider Layer, a **calm, prioritised, explained** answer: a one-line state of the
house, about three things that matter today each with its reasoning and confidence, the
recommended next step where one is warranted (preferring prevention and observation), and an
**honest statement of what the brain cannot yet see**. Every claim traces to its evidence; the
biological reasoning follows the canon; the climate source sits entirely behind
`GreenhouseProvider` (so Synopta later changes nothing above it); and the assessment is recorded
to Memory so the brain can begin, slowly, to calibrate and learn.

## 8. Open questions

1. **Where do plant observations and growth stage come from in v1?** This is the single biggest
   unknown; it decides how much of the "plant" the brain can honestly assess.
2. **How rich should v1 latent-state estimation be** — transparent heuristics only, or more?
   (Lean: heuristics, fully explained, with honest confidence.)
3. **Does v1 need the Memory read-path** for a worthwhile answer, or is a single stored "yesterday
   snapshot" enough to enable change-detection while full read-back waits?
4. **Should the decision hierarchy be recorded as an ADR now**, given the AI COO depends on it?
5. **What is the minimum species/stage target set** for our main crops to make Context meaningful?
6. **How is "today" scoped** when forecast/energy providers are absent — current state only, or a
   limited "day ahead" from climate trend alone?

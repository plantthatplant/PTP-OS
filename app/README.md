# app/ — Gaia (the daily greenhouse companion)

## The daily ritual (start here)

```
python3 app/gaia.py morning      # the beautiful Morning Brief + the few questions for your walk
python3 app/gaia.py walk         # answer them in your own words; closes yesterday's experiments
python3 app/gaia.py evening      # the Evening Review — and commits today as one permanent memory
python3 app/gaia.py memory "what did you learn"   # ask Gaia's long-term memory
```

**Complete operational workflow (`gaia day`).** `python3 app/gaia.py day <morning> [midday] [tomorrow]`
runs the whole lifecycle end to end and narrates it: **Snapshot → Analysis → Knowledge-Gap
questions → Field Conversation → Walk observations → Updated recommendations → Evening Review →
Memory → Learning → Tomorrow's Analysis.** It schedules *when* to raise each question (decision-
changing at the morning chat; others opportunistically where you already are; dropped once
resolved), and a confirming answer **updates the live recommendation's confidence on the spot**
(`lifecycle.reinforce`). Every step shows what Gaia knows, is uncertain about, asks, is told, how
the recommendation changes, what it stores, and what it learned — proving one full working day on
the existing engines alone.

**Knowledge Gap Engine (Sprint 10).** The walk questions are now chosen by **Value of
Information** (`knowledge_gap.py`): Gaia asks only the few questions whose answer would
actually change a decision, and *holds back* the rest (e.g. it won't ask about shading
cuttings it will shade regardless). After each answer it logs whether the interruption was
worthwhile; over time, question kinds that prove unnecessary fall below the bar and stop being
asked — `gaia memory "which questions are valuable"`.

**Gaia Memory (Sprint 9).** Each evening commits **one permanent, append-only Day Memory**
(`data/memory/journal.jsonl`) holding the whole day — snapshot, brief, recommendations,
actions, walk observations, evening review, outcomes, lessons. Nothing is ever overwritten;
every recommendation stays linked to its outcome forever. Ask it in plain words:
`gaia memory "what happened yesterday"`, `"… last friday"`, `"… the last time humidity
exceeded 95"`, `"every disease prevention decision"`, `"what did you learn"` — every answer
comes only from memory.

One day with Gaia is **morning → walk → evening**. Every recommendation becomes an
*experiment* that is followed to its outcome and kept as a *memory*, so each day's advice is
a little wiser than the last:

```
Observation → Reasoning → Recommendation → Action → Outcome → Memory → better next recommendation
```

The morning brief reads the latest Greenhouse Snapshot, runs the (unchanged) Morning
Analysis, shows **what changed since yesterday**, the three priorities / opportunities /
curiosities, recalls what happened last time (`↻`), and asks only the questions that matter.
The Evening Review compares each morning expectation with the action taken and the observed
outcome, forms a lesson, and moves confidence up or down — then stores the whole chain as a
memory.

**Friction-free launch.** `gaia morning` needs no arguments: it reads the live snapshot a feed
drops at `app/data/inbox/latest.json`, falling back to the bundled sample. (Pass a path to
override.) The brief states its real data source honestly — no more "mock data" on a live run.

**Since-yesterday (Sprint 7).** The brief opens with the overnight changes that matter — a
humidity climbing, a vent that closed, a concern that appeared or cleared — the first thing a
head grower looks for, computed by comparing this morning's signals to yesterday's.

> Sprint 3 added only experience and the recommendation lifecycle — no new engine, no provider
> change, no new framework. The Context / Decision / Language / Morning Analysis engines are
> exactly as Sprint 1 left them.

---

## Underlying prototype (Sprint 1)

The first working PTP OS capability — and it is **proactive**: it starts the day on its
own, then answers questions from what it already worked out.

```
python3 app/morning.py     # the Brain's start of day: runs + stores the Morning Analysis
python3 app/ask.py "How is the greenhouse today?"   # answered from that stored analysis
python3 app/feedback.py    # the 30-second review: rate each recommendation
python3 app/import_snapshot.py [snapshot.json]   # run the Brain from a canonical Greenhouse Snapshot
```

No dependencies, no install, no API keys — just Python 3 (stdlib only).

- **`morning.py`** runs the **Morning Analysis**: collect everything → build context →
  identify concerns → identify opportunities → set today's priorities → raise curiosities.
  It prints the full briefing and stores it.
- **`ask.py`** answers *"How is the greenhouse today?"* from the **stored** Morning Analysis
  (summary, three priorities, one concern, one recommendation, confidence) — it does not
  re-analyse. If no analysis was prepared yet, it runs one on demand and says so.
- **`feedback.py`** is the ~30-second morning gut-check: rate each recommendation
  **Correct / Partially / Incorrect**, with an optional one-line *why*. It is **captured**
  (appended to `data/feedback.jsonl`), not analysed and not learned from yet — the start of
  collecting real-world validation. See [`../specs/decision-capture.md`](../specs/decision-capture.md).

A **Curiosity** is something not yet a recommendation — an observation that deserves
attention (a within-range trend, a consistent oddity, a change to follow up). Curiosities
never alarm; they invite a look and become future learning.

## Providers — the same Brain, different data sources

The data source is a **composition-time** choice; the Brain cannot tell the difference.

```
python3 app/demo_provider_swap.py                       # same engines, mock vs Claude Dispatch, side by side
python3 app/demo_live_dispatch.py                       # Morning Analysis from a LIVE HTTP fetch (local stand-in endpoint)
PTP_PROVIDER=claude-dispatch python3 app/morning.py     # daily flow on the captured Dispatch fixture
PTP_PROVIDER=claude-dispatch PTP_DISPATCH_URL=https://… python3 app/morning.py   # …or live, by config alone
python3 app/morning.py                                  # default: mock
```

**Transport vs translation.** `ClaudeDispatchProvider` translates a raw payload into the
domain model; *where that payload comes from* is a separate **transport** (`transport.py`):
`FixtureTransport` reads the bundled sample, `HttpDispatchTransport` GETs live JSON. Swapping
fixture → live is a composition-time choice (set `PTP_DISPATCH_URL`); the translation and
everything above it are untouched. Live-data messiness (comma decimals, missing fields,
partial houses) is absorbed inside the provider, so the engines only ever see clean domain
objects.

- **`MockGreenhouseProvider`** — hand-built domain objects (rich: plant notes, history, outlook).
- **`ClaudeDispatchProvider`** — translates Claude Dispatch's Synopta extract into the *same*
  domain types. v1 supports only the core climate signals (timestamp, house, air temp, RH,
  vent position, outside temp, alarm); everything else is honest absence.
- **`SynoptaProvider`** (future) — slots in behind the same interface; nothing above it changes.

The demo proves the point: both providers run through *one* `MorningAnalysisEngine`, and the
top concern and recommendation come out identical. The outputs are not byte-identical — Claude
Dispatch v1 carries only climate, so it yields a leaner analysis — but that is data coverage,
not architecture.

> This is a **reasoning prototype**, built to validate the flow end to end — not the
> production stack. The implementation language is not yet formally chosen (backlog
> S1-00); Python-with-zero-dependencies was picked so it runs anywhere on day one. See
> [`../docs/sprint-1-shortcuts.md`](../docs/sprint-1-shortcuts.md) for every shortcut and
> what replaces it.

## The pipeline (one small object per architecture layer)

```
Reality -> Provider -> Context -> Decision -> Language -> answer
```

| Folder / file | Architecture layer | What it does |
| --- | --- | --- |
| `greenhouse_brain/domain.py` | Domain Model | The shared concepts (zones, readings, candidates, briefing). |
| `greenhouse_brain/biology.py` | (biological signals) | VPD, dew point — conditions turned into meaning. |
| `greenhouse_brain/providers/` | Provider Layer | `GreenhouseProvider` interface + `MockGreenhouseProvider` + `ClaudeDispatchProvider`. The seam Synopta slots into. |
| `greenhouse_brain/context_engine.py` | Context Engine | Assembles the relevant picture per zone (targets, signals, trend, observations). |
| `greenhouse_brain/decision_engine.py` | Decision Engine | Transparent heuristics -> concerns, opportunities, ranked priorities. No AI. |
| `greenhouse_brain/curiosity_engine.py` | (curiosity) | Notices what's not yet a recommendation — trends, oddities, follow-ups. |
| `greenhouse_brain/morning_analysis.py` | (daily rhythm) | Composes the engines into the Morning Analysis. |
| `greenhouse_brain/snapshot.py` | Greenhouse Snapshot | The canonical structure + coverage / reality-confidence math. |
| `greenhouse_brain/snapshot_importer.py` | (importer) | Raw JSON -> Snapshot, forgiving of missing/messy data. |
| `greenhouse_brain/providers/snapshot_provider.py` | Provider Layer | Feeds a Snapshot to the unchanged engines. |
| `greenhouse_brain/lifecycle.py` | (learning loop) | The Experiment record: recommendation → action → outcome → lesson → memory. |
| `greenhouse_brain/dialogue.py` | (the walk) | Chooses the few questions worth asking today. |
| `greenhouse_brain/views.py` | (experience) | The beautiful Morning Brief and Evening Review. |
| `gaia.py` | (daily companion) | `morning` / `walk` / `evening`. |
| `greenhouse_brain/feedback.py` | (validation capture) | The 30-second review loop. Captures ratings; does not analyse. |
| `greenhouse_brain/store.py` | (local cache + log) | Saves/loads the analysis; appends feedback. A minimal cache, NOT the Memory Engine. |
| `greenhouse_brain/language_engine.py` | Language Engine | Renders the briefing/status calmly. Template now; AI model can replace it behind the same interface. |
| `greenhouse_brain/brain.py` | (composition) | `run_morning_analysis()` and `answer(question)`. |
| `morning.py` / `ask.py` / `feedback.py` | (entry points) | The commands you run. |

> Generated, not source: the latest analysis is cached under `app/.state/` (transient);
> captured feedback is kept under `app/data/feedback.jsonl` (append-only).

## What it honestly is and isn't

It **is** a true end-to-end run of the architecture: data enters only through the
Provider Layer, reasoning is model-independent and explainable, language is isolated and
replaceable, and the answer is health-first and honest about its own confidence.

It **isn't** connected to anything real yet, and it says so in every answer. The reasoning
is the point; the wiring to Synopta, plant observations, Memory, and a real Decision
Library comes next — all behind the seams this prototype already has.

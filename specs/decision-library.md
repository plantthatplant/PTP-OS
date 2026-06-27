# Spec — The Gaia Decision Library

**Status:** Draft v1 · the Sprint-4 core capability (for review before implementation).
**Related:** [`docs/gaia-learning-loop.md`](../docs/gaia-learning-loop.md) (the experiment
record this stores), [`specs/decision-capture.md`](decision-capture.md) (how records get filled),
[`specs/greenhouse-snapshot.md`](greenhouse-snapshot.md) (the evidence and snapshot reference),
[`docs/architecture.md`](../docs/architecture.md) (the Decision Library + Memory Engine services),
[`domain/decision.md`](../domain/decision.md), [`domain/memory.md`](../domain/memory.md).

> This designs a **capability and a record**, not new architecture. The Decision Library is the
> accumulated, queryable form of experience the architecture already names; it stores into the
> Memory Engine and feeds the Decision Engine. No new engine, no provider change.

## 1. Purpose

The Decision Library is **Gaia's accumulated biological experience** — the permanent record of
every recommendation it has ever made and what came of it. It is **not a database of facts.** A
fact is "humidity was 92%." Experience is "the last three times the propagation canopy sat wet and
still, we vented early, it stopped the Botrytis, and we are now confident it works." The Library
stores the second kind.

It exists so that **every recommendation Gaia produces becomes a reusable decision record**, and
so that a future morning can ask *"have we been here before, and what did we learn?"* — and get a
real answer. It is the **long-term memory of Gaia**: the thing that lets it stop repeating mistakes
and start compounding wisdom, the way a grower who has run a house for twenty years simply *knows*
what this crop does.

## 2. Philosophy — experience, not facts

- **A record is a completed experiment, not a row.** It carries the reasoning, the prediction, the
  action, the outcome, the lesson, and the confidence trajectory — everything that makes a grower
  *wiser*, not merely informed (it is the Learning Loop's memory, made queryable).
- **It answers "what did we learn, and how sure are we?"** — never just "what was the value."
- **It is biological and legible.** Indexed by crop, stage, and biological signature; every record
  reads as a sentence a grower would recognise; every claim traces to its evidence.
- **It accumulates into knowledge.** One record is an anecdote; many consistent records, with a
  mechanism, become a pattern, then a prior that strengthens future recommendations (the
  maturation ladder from the canon).
- **Failures are kept, and are precious.** Recommendations that *didn't* work are recorded as
  faithfully as those that did — "which recommendations have repeatedly failed?" is one of the most
  valuable questions the Library answers.
- **It is append-only and honest.** Records are never edited; confidence evolves *across* records,
  so the history of what Gaia believed, and when, stays auditable. Context drift is handled by
  letting old experience decay in weight, never by rewriting it.

## 3. The Decision Record

Every recommendation becomes one record. Its fields (grouped for clarity), with where each comes
from:

**Identity & situation** — *what, where, when*
| Field | Meaning | Source |
| --- | --- | --- |
| **Decision ID** | stable unique id | generated |
| **Date** | when the recommendation was made | morning |
| **Greenhouse** | the site | snapshot |
| **Zone** | the zone | snapshot |
| **Crop / Plant** | species/cultivar (and batch/plant where individual) | snapshot |
| **Growth stage** | propagation / vegetative / finishing … | snapshot |
| **Snapshot reference** | the exact Greenhouse Snapshot the decision was made from | snapshot |

**Evidence** — *what we saw*
| Field | Meaning | Source |
| --- | --- | --- |
| **Biological observations** | the plant signs in play (leaf-wetness, tone, pests, growth…) | snapshot |
| **Climate observations** | the conditions in play (temperature, humidity, VPD, vent…) | snapshot |

**The decision** — *what we advised, and why*
| Field | Meaning | Source |
| --- | --- | --- |
| **Recommendation** | the action proposed | Decision Engine |
| **Why the recommendation was made** | the rationale, in biological terms | Decision Engine |
| **Expected outcome** | the testable prediction (+ window) | Decision Engine |
| **Confidence before the decision** | how sure Gaia was | Decision Engine |
| **Biological principles involved** | the cultivation reasoning invoked | Decision Engine |

**The result** — *what happened, and what we learned*
| Field | Meaning | Source |
| --- | --- | --- |
| **Action taken** | done / modified / skipped (+ note) | dialogue / capture |
| **Actual outcome** | improved / unchanged / worse / unknown (+ evidence, attribution) | dialogue / evening |
| **Lessons learned** | the stated biological lesson | evening (learning) |
| **Confidence after the outcome** | how belief moved | evening (learning) |

**The connections** — *how this sits among everything we've seen*
| Field | Meaning | Source |
| --- | --- | --- |
| **Related previous decisions** | explicit links — a follow-up to, a repeat of, a contradiction of, an earlier decision | Library |
| **Similar situations** | other records with the same situation fingerprint (§4) — "we've been here before" | Library (computed) |

A record is *opened* in the morning (identity, situation, evidence, decision) and *closed* in the
evening (result, learning), then linked into the web of prior experience. That full object — the
whole lifecycle chain — is what the Library stores. (This is exactly the Sprint-3 `Experiment`,
enriched with situation and relational fields.)

## 4. The situation fingerprint — how experience is retrieved

The Library is only useful if a *new* situation can find the *relevant past* ones. So each record
carries a **situation fingerprint** — a biological description of the moment, deliberately
interpretable rather than an opaque vector:

- **Crop & stage** — the primary keys (Monstera at propagation is a different world from Monstera
  finishing).
- **The biological signature** — the conditions and signs that mattered, expressed as *bands and
  categories a grower would use*: humidity band (e.g. ">90%"), VPD band, "canopy wet", "stagnant
  air", "disease-favourable", "heat-stress-likely", a pest present, etc.
- **The concern type** — what the situation was about (disease risk, desiccation, toning…).

Two situations are **similar** when their fingerprints align on crop, stage, and the salient part
of the signature. This is what makes *"have we seen this pattern before?"* and *"what happened the
last time humidity exceeded 95% in propagation?"* answerable in biological terms — and keeps the
answers explainable.

## 5. The questions the Library must answer

The Library is defined by the questions it can answer with *experience*. The four examples, and the
query shapes they generalise to:

- **"What happened the last time humidity exceeded 95% in propagation?"**
  → *situation query*: filter records by stage = propagation and a condition band (humidity > 95%),
  newest first; return the decisions, what was done, the outcomes, and the lessons.
- **"Have we seen this pattern before?"**
  → *similarity query*: take today's situation fingerprint, find past records that match, and report
  what was tried and how it went.
- **"What recommendations have historically worked for Monstera?"**
  → *outcome query by crop*: filter crop = Monstera, outcome = improved; rank by recurrence and
  confidence; return the reliably-good recommendations with their evidence.
- **"Which recommendations have repeatedly failed?"**
  → *failure query*: group records by (situation, recommendation), surface the cells with persistent
  *worse / unchanged* outcomes — the things Gaia keeps getting wrong and must re-examine.

Generalised, the Library answers queries **by situation, by crop/zone/stage, by condition band, by
outcome, by recommendation type, by biological principle, and by similarity** — and, crucially, every
answer is **experience**: the decision *with* its reasoning, outcome, lesson, and confidence
trajectory, not a bare value. A query that returns "humidity was 92%" has failed; one that returns
"here is what we did about high humidity, and whether it worked," has succeeded.

## 6. From records to patterns — how experience becomes knowledge

The Library does not only retrieve; it **aggregates** records into patterns, which is how anecdote
becomes knowledge:

- For each *(situation, recommendation)* cell, the Library can compute the **outcome distribution**
  (how often improved / unchanged / worse) and the **confidence trajectory** (how belief moved across
  repetitions).
- *"Has this worked?"* is then answerable as evidence: "8 times, improved 7, confidence now high."
- *"Repeatedly failed"* is the cells with persistent poor outcomes.
- A pattern earns influence over future recommendations only with **recurrence, consistency, and a
  plausible mechanism** (the canon's gates), and stays **falsifiable and demotable** — a pattern that
  stops predicting loses weight.

This is what feeds the Decision Engine: a candidate recommendation that the Library shows has worked
ten times, here, for this crop, is made with more confidence; one that has repeatedly failed is
flagged or withheld. The learned response of *these* plants steadily replaces the generic prior.

## 7. Which existing components connect to it

The Library is a careful extension, wired to what already exists. Read vs write is explicit:

- **Recommendation production (Morning Analysis / Decision Engine)** — **writes**: every
  recommendation *opens* a record (this is already Sprint-3's experiment creation). The mandate
  "every recommendation becomes a record" is satisfied here.
- **Daily Grower Dialogue + decision-capture + the Evening Review** — **write/complete**: they fill
  Action, Actual outcome, Lessons, Confidence after (already Sprint-3's `gaia walk` / `gaia evening`).
- **The Memory Engine** — the **storage substrate**. The Library is the *experience-organised,
  queryable face* of the records the Memory Engine persists. (Today, the minimal store —
  `app/data/memories.jsonl` — stands in for it.)
- **The Decision Engine** — **reads**: it consults the Library for precedent when forming a
  recommendation, so advice gets better-evidenced and better-calibrated over time. Sprint-3's morning
  **`↻` recall** is the embryonic version of this read.
- **The Greenhouse Snapshot** — supplies the **snapshot reference** and the biological/climate
  observations every record carries.
- **The Knowledge Platform** — where general principles meet local experience; the Library is the
  local, learned half.

No component is redesigned; two are *extended* (records are enriched on write; the Decision Engine's
read of precedent is strengthened), and the existing data flow is unchanged.

## 8. Relationship to the architecture (no redesign)

The architecture already lists a **Decision Library** ("catalog of decision types and their
structure") and a **Memory Engine** ("retains experience; links decisions to outcomes"). This spec
*fills in* that Decision Library with real accumulated experience and clarifies the division of
labour:

- **Memory Engine** = how experience is *stored* (append-only records).
- **Decision Library** = how experience is *organised, queried, and turned into patterns* — the
  read/aggregate face.
- The original "catalog of decision *types*" is **subsumed**: decision types are not hand-authored;
  they *emerge* as patterns from accumulated records. This is the careful extension the architecture
  anticipated, and it is exactly the loop RFC-001 asked to be made first-class.

## 9. Smallest possible Sprint-4 implementation

The prototype already produces closed experiments (`app/data/memories.jsonl`). The smallest real
Decision Library is a **read/aggregate layer over that file plus a few enrichment fields** — no new
storage, no new engine, no provider change.

1. **Enrich the record** (`lifecycle.Experiment`) with the missing situation fields populated from
   the snapshot at experiment-open time: greenhouse, crop, growth stage, snapshot reference, and the
   biological-vs-climate split of the evidence, plus a computed **situation fingerprint** (crop +
   stage + a few condition bands). Small, additive — does not touch any engine.
2. **Add `decision_library.py`** — a pure read layer over `memories.jsonl` with the query functions:
   `last_time(condition, stage)`, `worked_for(crop)`, `repeatedly_failed()`, `similar_to(fingerprint)`,
   plus the aggregation (outcome distribution + confidence trajectory per cell). It loads records and
   returns experience; it writes nothing.
3. **Add a `gaia library` command** (or `gaia ask "<question>"`) that answers the four example
   questions over the accumulated records — the grower-facing way to consult experience.
4. **Upgrade the morning `↻` recall** to use `similar_to(today's fingerprint)` instead of the current
   zone+kind match — so precedent retrieval is biological, not positional. This is the Decision
   Engine reading the Library, kept in the experience layer (no engine edit).

**Deliberately deferred** (named, not done): real natural-language querying; similarity beyond banded
fingerprints; pattern-mining beyond counts and trajectories; and the Memory Engine proper (durable,
indexed storage) — `memories.jsonl` remains the honest stand-in until then.

This is one new read-only module, a handful of additive record fields, one CLI command, and a
one-line upgrade to recall. It makes Gaia able to *consult its own experience* — the smallest step
that turns yesterday's memories into a library Gaia can actually learn from.

## 10. Open questions

1. **Fingerprint granularity** — which condition bands and signs make a "situation," and how coarse
   to keep them so similar moments actually match.
2. **Similarity** — how close is "similar"; banded match now, but what graduates it (weighted match,
   later embeddings) without losing legibility.
3. **Where aggregation lives** — how much pattern computation belongs in the Library vs the Decision
   Engine reading it.
4. **Influence threshold** — how much corroboration lets a pattern actually change a recommendation
   (and how that interacts with "trust before automation").
5. **Retention & drift** — how long experience stays in weight as cultivars, pathogens, and climate
   move; how decay is expressed without rewriting history.
6. **Ownership** — the accumulated experience is the grower's and the company's most valuable asset;
   how it is governed, exported, and (eventually) shared across sites.

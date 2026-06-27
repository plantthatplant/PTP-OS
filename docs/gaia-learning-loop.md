# The Gaia Learning Loop

A core design document. It describes how **Gaia** — the intelligence of PTP OS — turns the
ordinary work of a greenhouse into accumulated biological wisdom, so that the system slowly
becomes a better grower over years. It defines a *lifecycle*, not software.

Sprint 1 proved Gaia can **observe** reality (the Greenhouse Snapshot) and **reason** about it
(the Morning Brief). Sprint 2 must prove Gaia can **learn** from reality. This document is the
design for that.

> Status: v1 · a core design document. It builds on
> [`docs/decision-philosophy.md`](decision-philosophy.md) (the learning maturation, calibration,
> hazards), [`docs/cultivation-intelligence-model.md`](cultivation-intelligence-model.md)
> (how a grower's experience becomes intuition), [`docs/daily-operating-cycle.md`](daily-operating-cycle.md)
> (the Learn and Reflection phases), [`rfc/RFC-001-feedback-and-learning-loop.md`](../rfc/RFC-001-feedback-and-learning-loop.md)
> (the architectural loop), [`specs/decision-capture.md`](../specs/decision-capture.md) (the
> write-path), and [`specs/greenhouse-snapshot.md`](../specs/greenhouse-snapshot.md) (the evidence
> units). Where any later design conflicts with the learning principles here, this document wins.

## 1. Purpose and the central idea

The product's deepest promise is that it learns. This document says exactly how.

**The central idea: every recommendation is a hypothesis.** When Gaia says "increase air
movement in House 1 to prevent disease," it is making a *testable prediction* — "doing this, in
this situation, will produce this biological outcome, within this time." Following that
recommendation to what actually happened is **running the experiment**. The outcome is
**evidence**. Enough corroborated evidence becomes **knowledge**. Knowledge sharpens the next
recommendation. That is the loop:

> **A recommendation becomes an experiment. An experiment produces an outcome. An outcome becomes
> knowledge. Knowledge influences future decisions.**

Run this loop over thousands of completed recommendations across many seasons, and Gaia
accumulates something a great grower has and a new one lacks: a worked-in, evidence-graded
understanding of *how these plants, in this greenhouse, actually respond.*

## 2. Biological learning, not machine learning

This is the defining commitment, and the reason the document exists.

Gaia does **not** learn by fitting weights to data in a black box. It learns the way an
experienced grower does: by accumulating **interpretable, causal, mechanistic, evidence-graded
claims about plants** — each one a sentence a grower could read, question, and act on.

| Machine learning (not this) | Biological learning (this) |
| --- | --- |
| Opaque weights; correlation | Stated biological claims; cause and mechanism |
| Needs huge data volume | Learns from few, well-understood cases — like a grower |
| The model is the knowledge | The *lesson* is the knowledge; any model is replaceable (ADR-003) |
| Hard to explain or contest | Every lesson is legible, defensible by its evidence, and falsifiable |
| Optimises a metric | Optimises the living plant; never a proxy |
| Updates silently | Updates a confidence a human can see and challenge |

So a "lesson" in Gaia is never a number buried in a network. It is a record like: *"For mixed
aroid cuttings at propagation, breaking a wet, stagnant canopy early reduced Botrytis onset —
seen across N mornings, mechanism understood (leaf-wetness duration drives infection),
confidence rising."* That is biology, written down, and improving. The plant — not the data — is
the teacher; data volume only ever serves the biology.

## 3. The lifecycle

Every recommendation opens an **Experiment Record** that travels through six stages and is never
discarded. The record matures, over hours to weeks, from a hypothesis into a permanent memory.

```
        ┌──────────────────────────── the loop ─────────────────────────────┐
        │                                                                    │
   OBSERVATION ─▶ REASONING ─▶ RECOMMENDATION ─▶ ACTION ─▶ OBSERVATION(after)│
   (Snapshot)     (engines)    (the hypothesis)  (done?)   (what changed)    │
        ▲                                                        │           │
        │                                                        ▼           │
        └──── future decisions ◀── MEMORY ◀── LEARNING ◀──── OUTCOME ────────┘
                (knowledge in)    (permanent)  (the lesson)  (verdict)
```

Each stage is specified below with its required content and the reasoning behind it.

### Stage 1 — Recommendation (the hypothesis)

The moment Gaia proposes an action, it records a falsifiable prediction.

| Field | Meaning |
| --- | --- |
| **id** | a unique, stable identifier for this experiment |
| **timestamp** | when it was recommended |
| **subject** | what it concerns (zone / bench / batch / plant) |
| **why recommended** | the rationale, in plain biological terms |
| **supporting evidence** | the cited observations behind it, each with provenance and confidence (from the Snapshot) |
| **expected outcome** | the *testable prediction*: what should change, in which direction, by roughly how much, and **by when** (the observation window) |
| **confidence** | how sure Gaia is — the number that will be checked against reality |
| **biological principles used** | the cultivation reasoning invoked (e.g. disease triangle, leaf-wetness duration, recovery-is-the-diagnostic) |
| **goal & trade-off** | which Biological Goal it serves and what it costs |
| **alternatives** | other actions considered and why not (links to decision-capture) |
| **status** | accepted / modified / rejected / expired |

The decisive addition over a plain recommendation is the **expected outcome with a window**.
Without a prediction there is nothing to test; with one, every recommendation becomes a small,
honest experiment. A recommendation that is *rejected* or *modified* is still an experiment — the
grower's counter-choice, and what follows from it, is evidence too.

### Stage 2 — Action (what was actually done)

Reality rarely matches the plan exactly, and the gaps are informative.

| Field | Meaning |
| --- | --- |
| **who** | the person who acted, or the system (where trusted) |
| **when** | when it was done |
| **completed** | done / partial / skipped / substituted |
| **deviations** | how the action differed from what was recommended (dose, timing, extent, method) |
| **actual action** | what was actually done, in the grower's terms (verbatim where given) |

**Not done is data, not a dead end.** A skipped recommendation whose predicted problem then
arrives is powerful confirmation the recommendation was right. A modified action (the grower did
*less*, or *something else*) is a natural variation that teaches. Gaia records the deviation
honestly and lets the outcome speak.

### Stage 3 — Observation (what changed afterwards)

At the prediction's biological timescale (recovery in hours, toning over days), Gaia gathers what
happened — as ordinary Snapshot observations, time-aligned to the action.

| Field | Meaning |
| --- | --- |
| **after-observations** | the crop's and the climate's state across the window |
| **plant observations** | the living response — turgor, colour, new growth, disease/pest signs, measurements (the ground truth) |
| **climate changes** | how conditions moved after the action |
| **photos / media** | images or clips, referenced and time-stamped |
| **grower comments** | the grower's own read, preserved verbatim |

This is where the *plant* — the integrator, the source of truth — reports the verdict. Climate
changes show the lever moved; plant observations show whether the plant was better for it.

### Stage 4 — Outcome (the verdict)

The window closes; Gaia judges what the action achieved.

| Outcome | Meaning |
| --- | --- |
| **improved** | the plant is measurably better; the prediction held |
| **unchanged** | no clear effect |
| **worse** | the plant declined |
| **unknown** | cannot be judged — not observed, too soon, or too confounded to attribute |

Each verdict carries its **confidence** and the **evidence** behind it, and — critically — an
**attribution note**: did *this action* cause the change, or did other things change at the same
time? **"Unknown" is first-class and common**, and must never be forced into a false verdict. An
outcome's value as evidence is weighted by how cleanly it can be attributed (Stage-2 deviations
and confounders lower that weight).

### Stage 5 — Learning (what Gaia concludes)

The heart of the loop: prediction meets reality, and a lesson forms.

| Field | Meaning |
| --- | --- |
| **conclusion** | the stated biological lesson — a claim about how these plants respond, scoped to cultivar / stage / conditions |
| **confidence change** | whether belief in the underlying principle **increases or decreases**, and by how much — the calibration update (was the expected outcome met?) |
| **reuse** | whether this recommendation should be reused, and under exactly what conditions; or amended; or retired |
| **new questions** | curiosities the result raised — feeding the next experiments (links to the curiosity engine) |

A **hit** (outcome matched prediction) raises confidence modestly. A **miss** — a surprise — is
the richest teacher: it may refine the lesson, narrow its scope, or refute the belief outright.
Lessons are always **scoped, provisional, and demotable**: "true for this cultivar at this stage
in these conditions," never "true everywhere forever." A lesson that stops predicting is
demoted, not defended.

### Stage 6 — Memory (the permanent record)

The completed experiment becomes a **permanent memory**. Memory is **append-only and immutable**
— a correction or a later result is a *new* record, never an edit — so the past stays honest and
the learning stays auditable.

Every memory preserves the full chain, in order, forever:

```
   Observation  →  Reasoning  →  Recommendation  →  Action  →  Outcome  →  Lesson  →  Confidence evolution
   (what we saw)  (why we      (the hypothesis    (what was  (the      (what we   (how belief in this
                  concluded)    + prediction)      done)      verdict)   learned)   lesson moved, over time)
```

**Confidence evolution** is not a single number but a *trajectory*: across many experiments
about the same principle, Gaia records how belief rose and fell — the shape of learning itself.
That trajectory is what lets Gaia say, years on, "I am highly confident about this, and here are
the forty experiments and the mechanism behind it," or "I keep being wrong about that — it needs
re-examining."

Each memory is **provenance-bearing** (every claim traces to its evidence and the grower's
words) and **queryable by situation**, so a future morning that resembles a past one can recall
exactly what was tried and what happened.

## 4. How knowledge influences future decisions

A pile of experiments is not yet wisdom. Knowledge matures along the ladder from the canon, made
concrete for completed experiments:

1. **One experiment is an anecdote.** It informs, but commands little confidence.
2. **A pattern across many experiments becomes knowledge** — when the same
   situation→action→outcome recurs, *consistently*, survives a check for confounders, and has a
   *plausible mechanism*. ("We have seen this twenty times, it holds, and we understand why.")
3. **Robust knowledge becomes a prior that shapes recommendations** — the learned response of
   *these* plants steadily replaces the generic textbook curve. The next recommendation in a
   similar situation is better-evidenced, more confident, and more specific because of every
   experiment before it. It is surfaced *with its provenance*, for the grower to judge — never
   silently automated (trust before automation).

This is the mechanism by which both a recommendation's **content** and its **confidence** improve
over time. When a new situation arises, Gaia recalls the relevant experiments — what it tried,
what happened, how sure it became — and reasons from that lived history, not from assumption.

## 5. The honest hazards (designed for, not hidden)

Biological learning in a working greenhouse is observational, not a controlled laboratory. Gaia
must hold its conclusions with the humility that demands.

- **Confounding / attribution** — the central hard problem (RFC-001's open question): many
  factors move at once, so "we vented and it recovered" may be coincidence. *Mitigations:* record
  confounders, weight outcomes by attribution cleanliness, require recurrence before promotion,
  and prefer deliberate controlled trials (§6) where possible.
- **Selection bias** — Gaia mostly sees outcomes of recommendations that were *taken*; it rarely
  sees what the rejected alternative would have done. Capturing rejected/modified/skipped actions
  (Stage 2) partially recovers the counterfactual; Gaia must never mistake its own apparent
  success rate for truth.
- **The expert is not always right** — a recommendation is a hypothesis, not gospel; the
  *outcome* adjudicates, not the recommender's confidence. Records are blameless, so "I was wrong"
  — the most valuable lesson — is freely recorded.
- **Overfitting to anecdote and recency** — a vivid recent result is not a law; repetition and
  mechanism, not salience, earn promotion to knowledge.
- **Context drift** — biology changes: new cultivars, new pathogens, a shifting climate expire
  old lessons. Everything stays demotable; confidence decays without fresh corroboration.
- **Proxy / Goodhart** — Gaia learns against *plant outcomes* (health, quality, resilience),
  never against a convenient proxy like "hit the setpoint." Learning the wrong target compounds
  into confident error.

## 6. Deliberate experimentation

Most learning is **passive** — capture what happened when a recommendation was followed. But Gaia
should sometimes learn **actively**: propose a small, safe, *reversible* experiment to resolve a
question cleanly — vary one lever, keep a control bench, observe the difference. The Sprint-1
**curiosities** are the seeds of these ("I'm curious whether yesterday's irrigation change reduced
stress" → a designed follow-up). Deliberate experiments are gated by the same ethics as any
action: never experiment on human safety, never risk irreversible harm, keep them low-regret, and
always with the grower's consent. A handful of clean controlled trials can be worth a hundred
confounded observations.

## 7. Timescales — the long arc

The loop runs at three tempos:

- **Per experiment:** hours to weeks — one recommendation followed to its outcome.
- **Per lesson:** a season of repetitions — enough recurrence to graduate an anecdote into
  knowledge.
- **The long arc:** years — thousands of completed experiments compounding into a greenhouse
  intelligence that genuinely knows *these* plants. This is the goal: Gaia becomes a better grower
  not in a training run, but the way a person does — slowly, by paying attention, every day, for a
  long time, and never wasting an outcome. It becomes **institutional memory that outlives any
  individual grower** — the master's hard-won intuition, made explicit, evidence-graded, and
  shared.

## 8. Relationship to the rest of PTP OS

- **RFC-001** asked the architecture to make this loop first-class; this document is its design.
- **decision-capture.md** is the *write-path* — the lightweight, conversational way Stages 1–5
  get filled without burdening the grower. The two are one system: capture is how the loop is fed.
- **greenhouse-snapshot.md** supplies the *evidence units* — every observation in Stages 1 and 3
  is a Snapshot observation, with provenance and confidence.
- **The Memory Engine** is the *home* of the permanent records (Stage 6) and the retrieval that
  closes the loop; this document specifies what it must preserve, not how it is built.
- **The prototype's `feedback.jsonl`** (Sprint 1) is the embryonic write-path — a grower already
  rating recommendations is Stage 4 in its simplest form. Sprint 2 grows that seed into the full
  lifecycle.

The boundary: this is the *lifecycle* design. The storage, the situation-matching/retrieval, and
the conversational capture UI are implementation, specified and built on top of this — never in a
way that contradicts the learning principles above.

## 9. A worked experiment (the whole loop, once)

Following Gaia's recurring House 1 disease recommendation:

- **Observation:** House 1, humidity 92% (high conf), vent closed, canopy wet after sunrise
  (grower, medium conf). *(Snapshot.)*
- **Reasoning:** wet + still + warm on young tissue → the disease triangle is aligning; leaf-wetness
  duration is the driver. *(Engines.)*
- **Recommendation `exp-1043`:** increase air movement and ease humidity now. *Expected outcome:*
  canopy dry by mid-morning, no new Botrytis within 48h. *Confidence: medium* (no trend history
  yet). *Principles: disease triangle, leaf-wetness duration, prevention over correction.*
- **Action:** grower, 07:10, completed; *deviation:* also lifted heat slightly (not recommended).
- **Observation (after):** canopy dry by 09:30; no spotting at 48h; humidity fell. Grower: "dry by
  mid-morning, clean."
- **Outcome:** **improved**, high confidence; *attribution note:* heat was also raised, a mild
  confounder.
- **Learning:** the principle held → confidence **rises** (medium → medium-high); *reuse:* yes, for
  propagation when humidity is high and the canopy is wet; *new question:* did the airflow or the
  heat dry it — worth a clean trial (airflow only) next time.
- **Memory `mem-1043`:** the full chain preserved, immutable, with the confidence trajectory now
  carrying one more rising point. The next time House 1 looks like this, Gaia recalls `mem-1043` —
  and recommends with a little more earned certainty, and a cleaner experiment in mind.

## 10. Open questions

1. **Attribution** — how to score and weight confounded outcomes, and how to nudge toward cleaner
   (controlled) experiments without burdening the grower.
2. **Outcome windows** — how the observation window is set per decision type, and how late/partial
   data is handled.
3. **Graduation thresholds** — how much recurrence and consistency promote an anecdote to knowledge,
   and knowledge to a prior.
4. **Lesson representation** — the vocabulary for a stated biological claim, so lessons are both
   human-legible and machine-retrievable.
5. **Counterfactuals** — how far to model "what the rejected option would have done."
6. **Cold start** — keeping the loop motivating and honest in the early years, before enough
   experiments exist to form strong knowledge.

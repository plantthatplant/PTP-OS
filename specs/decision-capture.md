# Spec — Decision Capture

**Status:** Draft v1 · the foundation for continuous learning (for review before
implementation).
**Related:** [`docs/decision-philosophy.md`](../docs/decision-philosophy.md) (the learning
maturation), [`docs/cultivation-intelligence-model.md`](../docs/cultivation-intelligence-model.md)
(tacit knowledge), [`docs/daily-operating-cycle.md`](../docs/daily-operating-cycle.md)
(Learn / Reflection), [`rfc/RFC-001-feedback-and-learning-loop.md`](../rfc/RFC-001-feedback-and-learning-loop.md),
[`domain/decision.md`](../domain/decision.md), [`domain/memory.md`](../domain/memory.md),
[`domain/recommendation.md`](../domain/recommendation.md)

> This spec designs a **workflow**, not software. It describes how PTP OS turns a grower's
> real decisions into learning material — gently enough that the grower barely notices, and
> structured enough that thousands of such decisions compound into genuine greenhouse
> intelligence. No implementation.

## 1. Purpose

The product's deepest promise is that it *learns* (vision: "learning is the product"). But a
system can only learn what it can observe, and the most valuable thing in the greenhouse —
**the reasoning of an expert grower** — is almost never written down. It lives in their head,
is exercised dozens of times a day, and is lost the moment attention moves on (or the grower
leaves).

Decision Capture exists to change that. Its purpose is simple: **every important grower
decision should become learning material.** Not a log of *what* was done — that is the easy,
worthless part — but a record of *what was seen, what was thought, why this and not that, and
what happened next.* That record is the raw material from which PTP OS becomes a better
grower over time.

## 2. Scope

**In scope.** The workflow by which a decision becomes a structured, outcome-linked,
provenance-bearing learning record: what is captured, how it is captured conversationally and
near-invisibly, how those records mature into knowledge, and how that knowledge improves
future recommendations.

**Out of scope.** Implementation; storage technology; the conversational language model
itself (it sits behind the Language Engine boundary, ADR-001/003); and *acting* on what is
learned automatically (capture informs recommendations; it never auto-acts — "build trust
before automation").

## 3. The governing principle: capture must cost the grower almost nothing

A grower's attention is the scarcest resource in the greenhouse (the same principle that makes
the interface calm). A capture system that *feels* like work will not be used, and an unused
capture system learns nothing. So the first-order design constraint is:

> **The grower should never feel they are filling out a form.** Capture rides on conversation
> and on moments that are already happening — it asks one good question at a calm time, infers
> the rest, and is always optional, interruptible, and answerable in a single word.

Everything below serves that constraint. The system does the structuring; the human only
contributes the part that only a human holds — the *judgement*.

## 4. What a captured decision contains

A **Decision Record** holds seven things. Crucially, PTP OS *already knows most of them* — it
saw the conditions and it made (or the grower took/changed) the recommendation — so most
fields are **auto-filled from context**, and only the genuinely human parts are ever *asked*.

| # | Element | Question it answers | Source |
| --- | --- | --- | --- |
| 1 | **Observation** | What was seen? (conditions, signs, the situation) | **Auto** — the assembled context at decision time. |
| 2 | **Read / judgement** | What did the grower think was going on? | **Asked, gently** — the latent reasoning; the gold. |
| 3 | **Action** | What was done (or deliberately not done)? | **Auto** — the recommendation taken, changed, or the grower's own action. |
| 4 | **Rationale** | Why *this* action? | **Asked** — "why did you…?" |
| 5 | **Alternatives** | What else was considered, and why rejected? | **Asked, lightly** — the usually-lost counterfactual. |
| 6 | **Outcome** | What happened afterwards? | **Auto + asked later** — linked later observations, confirmed by the grower. |
| 7 | **Lesson** | What was learned? Would you do it again? | **Asked at reflection** — the consolidation. |

Two of these deserve emphasis because they are the ones normally lost and the most valuable:

- **Alternatives (5).** Recording *what the grower considered and rejected, and why* is what
  gives PTP OS a shadow of the counterfactual — the road not taken. This directly counters the
  learning hazard named in the Decision Philosophy: a system normally only sees the outcomes of
  actions that were *taken*, so its view of its own success is structurally optimistic.
  Capturing alternatives is how it learns about the options it didn't see chosen.
- **Read / judgement (2).** This is the tacit knowledge the Cultivation Intelligence Model
  calls "the knowing that resists explanation." Capturing it — even partially, in the grower's
  own words — is how intuition slowly becomes explicit.

The grower's **own words are preserved verbatim** alongside any parsed structure. We never
discard the original; the human is the teacher, and their phrasing carries meaning the
structure may miss.

## 5. The capture workflow — three natural moments

Capture is not an event; it is a thread that follows a decision across time, asking at most one
good question at each of three moments that are *already* part of the grower's day. (These map
onto the daily cycle's Observe → Learn → Reflection.)

```
   decision made                  outcome window closes              later, at rest
        │                                  │                                │
   ┌────▼─────┐                      ┌─────▼──────┐                   ┌──────▼──────┐
   │ AT THE   │   ...hours/days...   │ AT THE     │   ...sometimes... │ AT          │
   │ DECISION │ ───────────────────▶ │ OUTCOME    │ ────────────────▶ │ REFLECTION  │
   └────┬─────┘                      └─────┬──────┘                   └──────┬──────┘
   captures 2,4,5                   captures 6                        captures 7
   "Why did you                     "Did the plants                   "Would you make the
    increase ventilation?"           recover?"                         same decision again?"
```

### Moment 1 — At the decision (capture the reasoning while it is fresh)
When the grower acts — especially when they **take, change, or reject** a PTP OS recommendation,
or make a notable move of their own — the system already has the observation and the action. It
needs only the *why*. So, at a calm moment (not mid-task), it asks one light question:

> *"Why did you increase ventilation?"*

From a one-sentence answer it captures the **rationale (4)**, infers the **read (2)**, and — if
the moment allows and the decision was significant — gently probes **alternatives (5)**:
*"Did you consider just venting the roof instead?"* If the grower says nothing, the record is
still valid — partial, not invalid.

### Moment 2 — At the outcome (close the loop)
Every decision type has a biological timescale (recovery in hours; toning over days; a disease
intervention over a week). The system **schedules the follow-up** for when the outcome can
actually be judged, and then asks:

> *"Did the plants recover after you increased ventilation on Tuesday?"*

It also auto-links the later observations and climate it can see. The grower's confirmation
turns those into a real **outcome (6)** with a valence — *helped / hurt / no clear effect* —
and a confidence. This is the half of the loop RFC-001 exists to make first-class.

### Moment 3 — At reflection (consolidate the lesson)
Occasionally, and only for decisions worth it, the system closes with the question that turns an
outcome into a **lesson (7)**:

> *"Would you make the same decision again?"*

A "yes, but sooner" or "no, it was too much" is enormously informative: it captures not just the
outcome but the grower's *updated* judgement — and quietly **calibrates** PTP OS's own
confidence by comparing what it predicted to what happened.

### Which decisions are worth capturing
Not all of them — capturing everything would be noise and burden. The system spends its few
questions where learning concentrates:

- **Overrides** — where the grower *disagreed* with a PTP OS recommendation. The single highest
  learning value: it is the system being corrected by the expert.
- **Surprises** — where the outcome defied expectation (a prediction error).
- **High-stakes or novel decisions** — where the consequence or the unfamiliarity is large.
- **Deliberate experiments** — a logged change the grower wants to evaluate (the prototype's
  "curiosities" become capture threads here).

Routine decisions that merely confirm the expected are **not** interrogated; they are recorded
silently from context, without a question. The rule mirrors the cultivation principle: *protect
attention; surface only what matters.*

## 6. Worked example — one decision, captured across time

Following the prototype's House 1 disease recommendation, captured almost entirely from context
plus three short answers:

- **(auto) Observation:** House 1, humidity 92% vs ≤85%, low airflow, canopy wet after sunrise,
  rising three mornings. **(auto) Action:** grower increased ventilation and air movement at 07:10.
- **Moment 1 —** PTP OS: *"Why did you increase ventilation?"* Grower: *"Canopy was still wet and
  I didn't want Botrytis getting going."* → **Rationale + Read** captured in their words; parsed to
  *intent: prevent disease; mechanism: dry the canopy.* PTP OS: *"Anything you considered instead?"*
  Grower: *"Could've just lifted the heat, but I didn't want to soften them."* → **Alternative**
  captured (heat, rejected to avoid softening).
- **Moment 2 (next day) —** PTP OS: *"Did the canopy dry and the plants hold up after yesterday's
  venting?"* Grower: *"Yeah, dry by mid-morning, no spotting."* → **Outcome:** helped, high
  confidence; auto-linked to the humidity falling and no disease observation.
- **Moment 3 (later) —** PTP OS: *"Would you do the same again?"* Grower: *"Yes, but I'd start the
  airflow overnight next time."* → **Lesson:** action validated; refinement learned (pre-empt
  overnight). PTP OS's own "prevent disease" recommendation is now corroborated *and* improved.

No form was filled. Three short answers, at three calm moments, produced a complete, outcome-linked,
provenance-bearing record.

## 7. From conversation to structured knowledge

A pile of conversations is not knowledge. The maturation — the same ladder as the canon, made
concrete for captured decisions:

1. **Conversation → Decision Record.** Natural-language answers are parsed into structure — the
   subject (zone / batch / species / stage), the levers used, the biological concepts invoked
   (stress, disease risk, toning), the outcome valence and confidence — *while preserving the
   grower's verbatim words and the full context snapshot.* A record can be partial and is
   enriched over time; it is never "incomplete and therefore void."

2. **Records → Pattern (Memory → Knowledge).** When many records about *similar situations* show
   a *consistent* observation → action → outcome, and a *plausible mechanism* explains it, the
   pattern graduates from anecdote to a **learned relationship** — e.g. *"for this cultivar at
   propagation, increasing airflow when humidity is high and the canopy is wet reliably reduced
   disease, across N occasions."* Promotion requires the canon's gates: **recurrence, consistency,
   control for confounders, and mechanism** — not a single vivid story.

3. **Pattern → Prior that shapes recommendations (Knowledge → default).** A robust pattern becomes
   a **prior** the Decision Engine leans on — sharpening understanding, prioritisation, and
   confidence — always **scoped, falsifiable, and demotable**, and **never silently automated**
   (it surfaces as a better-evidenced recommendation, with its provenance, for the grower to judge).

Throughout, **provenance is preserved**: every learned pattern can be traced back to the captured
decisions — and the grower's own words — that produced it. This makes the learning *auditable* and
*explainable*, and lets a pattern be retired cleanly when the records behind it stop holding.

## 8. How thousands of captured decisions improve future recommendations

One captured decision is an anecdote. Thousands are a greenhouse intelligence. Each record is, in
effect, a labelled example linking *situation → expert action → reasoning → outcome* — exactly the
supervision needed to reason like *this* grower in *this* greenhouse. At scale they compound in
distinct ways:

- **Sharper understanding.** The learned environmental response of this crop in this house steadily
  replaces generic textbook curves — the system comes to know how *our* plants actually behave.
- **Better prioritisation.** What this grower treats as urgent versus holdable, and where their
  thresholds sit, are learned from how they actually ranked their mornings.
- **Calibrated confidence.** Every captured outcome is a check against a prediction; over thousands,
  PTP OS learns when its "80% sure" is honest — the calibration discipline made real.
- **Tacit knowledge made explicit.** Thousands of *(cue-combination → judgement → outcome)* records
  are precisely the decomposition of the intuition the Cultivation Intelligence Model said "resists
  explanation." The unexplainable becomes, slowly, the learned.
- **Institutional memory.** Expertise that would walk out the door when a grower leaves is retained —
  directly answering the vision's lament that "much of the relevant knowledge lives in people's heads
  and is lost."
- **Learning from disagreement.** Because overrides and alternatives are captured, PTP OS improves its
  *own* recommendations, not merely confirms them — it learns where it was wrong, which is the only way
  it earns the right to be trusted.
- **Transfer (eventually, carefully).** Patterns robust across contexts can seed a new site or a new
  grower — the path to serving other professional growers — with explicit care that much cultivation
  knowledge is context-specific and must be re-validated locally.

**Honest limits**, stated so they are designed for rather than discovered:
- **Attribution / confounding** — many factors move at once; "we vented and it recovered" may be
  coincidence. Records hold conclusions loosely until repeated or controlled (RFC-001's open problem).
- **Selection bias** — we mostly capture *taken* actions; the alternatives field only partly recovers
  the counterfactual.
- **The expert is not always right** — a captured decision is *evidence*, not gospel; the outcome, not
  the grower's confidence, adjudicates. Capture is blameless precisely so that "I was wrong" — the most
  valuable record of all — is freely given.
- **Context drift** — new cultivars, pathogens, and climate expire old lessons; patterns must stay
  demotable.

## 9. Guardrails and principles

- **A colleague, not a logger.** Capture should feel like an interested coworker asking a good
  question — never like surveillance or paperwork.
- **The grower's words are sacred** — preserved verbatim, never distorted to fit a schema.
- **Blameless and honest** — the goal is learning, not assessment; admitting a mistake must be safe and
  welcomed.
- **Informs, never auto-acts** — learned knowledge becomes better-evidenced *recommendations with
  provenance*, surfaced for human judgement (trust before automation).
- **Optional and interruptible, always** — every question can be deferred, answered in one word, or
  ignored, and is never asked twice.
- **Ownership** — the captured expertise is the grower's and the company's; how it is stored, used, and
  (eventually) shared across sites is theirs to govern.

## 10. Future integrations

- **Language Engine** — hosts the capture conversation (the questions out, the parsing of answers in),
  behind the same replaceable-model boundary; one versioned prompt per capture moment.
- **Memory Engine** — the home of Decision Records, their outcome links, and the matured patterns
  (this spec is the write-path RFC-001 and backlog S1-11 begin).
- **Plant observations** — capture is far richer once the grower's and cameras' plant observations flow
  in; the prototype's honest gap is the same gap here.
- **Decision Library** — captured patterns become new, better-evidenced entries over time.
- **Voice / glasses** — the natural endpoint: capture by spoken word, hands-free, in the greenhouse,
  where the decisions are actually made.

## 11. Open questions

1. **Timing of the questions** — how does PTP OS choose the *calm moment* so a question never
   interrupts work? (End of the morning walk? A daily review? Grower-initiated?)
2. **Outcome windows** — how is "the outcome" time-horizon set per decision type, and how are
   confounders flagged when many things changed at once?
3. **How much to ask** — what is the right cap on questions per day before capture itself becomes a
   burden? (Lean: very few, concentrated on overrides and surprises.)
4. **Parsing fidelity** — how is the grower's natural language turned into structure without losing or
   distorting meaning, and how is the verbatim original always kept?
5. **Whose knowledge** — for multi-grower or multi-site futures, how are individual style, house
   specifics, and transferable truth told apart?
6. **Cold start** — how useful is capture before there are enough records to form patterns, and how do
   we keep it motivating in that early, low-yield phase?

# Spec — The Knowledge Gap Engine

**Status:** Draft v1 · Sprint-10 capability (designed, then implemented small).
**Related:** [`specs/daily-grower-dialogue.md`](daily-grower-dialogue.md) (the walk it speaks
through), [`specs/decision-library.md`](decision-library.md), [`specs/curiosity-engine.md`](curiosity-engine.md),
[`docs/decision-philosophy.md`](../docs/decision-philosophy.md) (value of information, protect
attention), [`docs/gaia-learning-loop.md`](../docs/gaia-learning-loop.md).

> Extends the existing question-selection (`dialogue.questions_for_today`); it does not redesign
> anything. No complex AI — a transparent Value-of-Information heuristic a grower could audit.

## 1. Purpose

Gaia should continuously identify the information that would most improve its biological
decisions — and **ask only when the answer is expected to change a decision.** A missing fact is
not a reason to ask; a *decision that would change* if the fact were known is. The objective:
**minimise interruptions while maximising biological understanding.** Fewer questions every month,
better decisions every month.

## 2. The reasoning process (before every question)

Gaia reasons exactly as an experienced head grower does before bothering a busy colleague:

1. **What do I already know?** (the Snapshot + Memory)
2. **What do I believe is happening?** (the latent inference behind the decision)
3. **What am I uncertain about?** (the confidence on that inference)
4. **Which uncertainty matters most?** (weighted by the stakes of the decision it gates)
5. **Which single observation would reduce that uncertainty the most?** (the most-diagnostic question)
6. **Is asking worth interrupting the grower?** (Value of Information vs the cost of attention)
7. **If yes, ask exactly one question** — specific, located, timed.

Steps 4–6 are the heart: a question is generated only if it survives the Value-of-Information test.

## 3. Value of Information (transparent, no ML)

Each candidate question is scored:

```
VoI = stakes × uncertainty × decisiveness × prior_worth  −  interruption_cost
```

- **stakes** — how consequential the decision is (Critical 1.0 · High 0.8 · Medium 0.5 · Low 0.3).
- **uncertainty** — how unsure Gaia is *now* (Low conf → 1.0 · Medium → 0.6 · Medium-high → 0.3 ·
  High → 0.1). The surer it already is, the less an answer can add.
- **decisiveness** — would the answer actually *change the action or its confidence*? (confirm-an-
  inference 1.0 · ground-truth-a-reading 1.0 · close-a-loop 0.7 · follow-a-curiosity 0.3 ·
  confirm-something-it-would-do-anyway 0.2). **This is the gate that enforces "never ask just
  because information is missing."**
- **prior_worth** — learned: how often *this kind* of question has actually been worthwhile (default
  1.0; §6).
- **interruption_cost** — a flat tax on the grower's attention (≈0.15).

A question is asked only if `VoI > threshold`; the few above threshold are ranked and a small daily
**budget** is kept. The decisive consequence: a cheap, reversible action Gaia would take *regardless*
of the answer scores near zero and is **not asked** — even though the information is "missing."

## 4. Specific over vague

The single most-diagnostic observation, never a broad prompt. Not *"how do the plants look?"* but
*"Do you see condensation on the leaves in House 1?"*. Not *"any pests?"* but *"Have you seen any
thrips on the propagation benches today?"*. Every question is **located** (which house/bench) and
**timed** (now / on the walk / before midday), so it can be answered without thought.

## 5. The Question record

Each question carries: **id · timestamp · related Snapshot · related Decision · biological reason ·
uncertainty being reduced · expected impact on the decision · estimated VoI · suggested location ·
suggested timing · whether it is still relevant if answered later.** Stored with the day.

## 6. After the answer — was it worth it?

When the grower answers, Gaia evaluates and **stores permanently**:

- **Did the answer change the decision?** (flip the action, or its priority)
- **Did confidence increase?** (the inference confirmed or denied)
- **Was the interruption worthwhile?** (VoI realised: it changed or confirmed a high-stakes call)

This becomes an append-only **question log** — the evidence for learning.

## 7. Learning over time

From the log, Gaia aggregates:

- **which question *kinds* are usually worthwhile** vs usually unnecessary → adjusts `prior_worth`,
  so low-yield kinds fall below threshold and stop being asked;
- **which growers answer most accurately** (calibration of the human source);
- **which observations produced the biggest decision improvements.**

The result is the stated objective: **Gaia asks fewer questions each month while making better
biological decisions** — because it has learned which gaps actually matter.

## 8. Integration (existing components only)

- **Morning Analysis** — its concerns/priorities are the *decisions* whose uncertainty the engine
  scores.
- **Walk Mode** — delivers the surviving questions and captures answers (one at a time, located).
- **Memory** — stores the question records and the post-answer evaluations, permanently.
- **Decision Library** — supplies carried decisions to close, and the historical `prior_worth`.
- **Curiosity Engine** — its curiosities enter as low-decisiveness candidates that rarely clear the
  bar today (right: curiosities are investigated patiently, not urgently asked).

## 9. Smallest implementation

A `knowledge_gap.py` that scores each Morning-Analysis decision for VoI, maps it to its single
most-diagnostic question, keeps only those above threshold, and emits the full record; the walk
delivers them and logs the post-answer evaluation; `prior_worth` is read back from the log. It
replaces the flat `questions_for_today` with VoI-ranked questions — no engine, no provider change.

## 10. Open questions

1. **Threshold & budget tuning** — how high to set the bar, and how it flexes with how vulnerable
   the day is.
2. **Decisiveness estimation** — today a per-kind constant; later, learned from how often each kind
   actually flipped a decision.
3. **Grower calibration** — how to weigh a source whose answers have been unreliable without
   discouraging honesty.
4. **Counterfactual VoI** — knowing the *realised* value needs the decision-with-answer vs
   without; how far to model the road not taken.

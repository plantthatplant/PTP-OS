# Spec — Daily Grower Dialogue

**Status:** Draft v1 · the first Sprint-2 capability (for review before implementation).
**Related:** [`docs/gaia-learning-loop.md`](../docs/gaia-learning-loop.md) (the lifecycle this
serves), [`specs/decision-capture.md`](decision-capture.md) (the write-path it uses),
[`docs/daily-operating-cycle.md`](../docs/daily-operating-cycle.md) (the day's rhythm),
[`specs/greenhouse-snapshot.md`](greenhouse-snapshot.md) (answers become observations),
[`docs/decision-philosophy.md`](../docs/decision-philosophy.md) (value of information, protect
attention), [`docs/cultivation-intelligence-model.md`](../docs/cultivation-intelligence-model.md)
(the morning walk).

> This designs a **capability and a daily ritual**, not software — and it adds no new
> infrastructure, no new provider, and no new data model. It composes pieces that already exist
> (Morning Analysis, the Greenhouse Snapshot, the Learning Loop, decision-capture) into the daily
> conversation through which Gaia and the grower improve. Focus: biology, decision quality, and
> learning.

## 1. Purpose

Every other capability has prepared for this one. **The Daily Grower Dialogue is how Gaia and the
Head Grower improve together, every day.** It is a two-way conversation across the working day
that does two things at once:

- **Improves today's decisions** — the grower starts the day with a calm, reasoned briefing, and
  the few observations they feed back sharpen the picture *that same morning*.
- **Improves every future day** — each answer is evidence, and each of today's recommendations is
  followed to its outcome, so Gaia slowly becomes a better grower (the Learning Loop, lived one
  day at a time).

It is the **human surface of the Learning Loop**: the place where Gaia's reasoning meets the
grower's eyes, hands, and judgement, and where both get better for the meeting.

## 2. Principles

- **Protect attention above all.** The grower's attention is the scarcest thing in the
  greenhouse. The dialogue must feel like a sharp colleague, never a form, a log, or a nag.
- **Natural language, both ways.** Gaia asks in plain, calm words; the grower answers however they
  like, in a word or a sentence. Gaia does the structuring.
- **Ask only what matters.** Gaia asks the few questions whose answers would actually change a
  decision or advance learning — and stays silent otherwise (value of information).
- **One question at a time, never twice, always optional.** Any question can be deferred, answered
  in one word, or ignored, and is never repeated.
- **Biology first.** The questions are about plants and the conditions acting on them — what a
  grower would look at on the walk — and they are timed to biological rhythms.
- **Every answer is evidence.** Equal in standing to any sensor, preserved verbatim, carrying
  provenance and confidence.
- **The grower decides; Gaia learns.** Gaia recommends and asks; the grower acts and judges;
  Gaia records and improves. Blameless throughout — "I don't know" and "it didn't work" are
  welcome answers.
- **Hands-free ready.** The morning-walk dialogue is designed to be spoken — it belongs in the
  greenhouse, where the work is.

## 3. The shape of the day

The dialogue is a daily ritual with four moments. Three are light touches on the grower's time;
one (the 06:00 preparation) costs the grower nothing.

```
  06:00            08:00              the morning walk                end of day
  ─────            ─────              ────────────────                ──────────
  Gaia prepares    Grower reads       Gaia asks only the              Gaia asks:
  the Morning      the briefing       observations that matter;       "What actually
  Analysis +       (and may accept/   grower answers in natural        happened?"
  the day's        modify/reject)     language; answers become         -> close the day's
  questions                           evidence AND can update          recommendations into
  (Gaia alone)     (grower)           today's picture (two-way)        outcomes & lessons
```

### Moment 1 — 06:00 · Gaia prepares (alone)
Before anyone arrives, Gaia runs the Morning Analysis (Sprint 1) **and** prepares two more things:
- **the day's questions** — the few observations worth asking on the walk (§4); and
- **the open experiments due today** — recommendations from earlier days whose outcome window has
  now closed and need a "what happened?" ("yesterday's irrigation change").

*Purpose:* the head grower who was already at work before the lights came on — now also arriving
with a short, deliberate list of what to *ask*, not just what to *say*.

### Moment 2 — 08:00 · The grower reads the briefing
The grower opens to the calm briefing: the state of the houses, ~3 priorities, the concern, the
recommendation, the confidence — each with its reasoning visible. Two effects:
- **Decision quality now:** the grower starts the day pointed at what matters.
- **The grower improves:** because the briefing *shows its reasoning*, the grower absorbs Gaia's
  foresight over time ("ah — wet canopy plus closed vent is the disease setup"). Teaching is a
  side effect of explaining.
The grower may also react — **accept, modify, or reject** a recommendation — and each reaction is
the first field of an experiment (decision-capture).

### Moment 3 — The morning walk · Gaia asks what matters
The heart of the dialogue. As the grower walks the crop, Gaia asks its few prepared questions —
spoken, one at a time, in context:

> "Did you see condensation on bench B in House 1?"
> "Any sign of pests in House 2?"
> "Did House 3 firm up at all after yesterday's irrigation change?"

The grower answers naturally ("yeah, still wet up top"; "no, clean"; "a little, still soft").
Each answer does **two jobs at once**:
- **It becomes evidence** — a Snapshot observation (provenance: this grower; method:
  observed-by-human; verbatim preserved), and, where it answers an open experiment, it fills that
  experiment's Observation/Outcome (§5–6).
- **It can update today's picture** — a confirmed wet canopy *raises* today's disease priority and
  its confidence; a clean "no pests" *lowers* a risk Gaia was holding. The walk is not just data
  collection; it sharpens the very morning it happens.

### Moment 4 — End of day · "What actually happened?"
As the day closes, Gaia asks the question that turns work into wisdom: **"What actually
happened?"** For each recommendation in play, it gently closes the loop — was it done, and what
did the plant do in response (§6). This is the calibration moment: did Gaia's predictions hold?
It is also the grower's natural reflection, made productive.

## 4. Which observations matter — the question that decides what to ask

Asking *well* is the whole craft. A dialogue that asks too much is a form; one that asks the wrong
things is noise. Gaia asks the **few questions whose answers would most change a decision or most
advance learning**, and nothing else.

**The kinds of question worth asking:**
- **Confirm an inference Gaia cannot see.** Gaia inferred disease risk from climate; only the
  grower's eyes can confirm the leaf-wetness. *"Did you see condensation?"* — a cheap answer that
  swings a high-stakes call.
- **Resolve an uncertainty that gates a recommendation.** *"Any pests in House 2?"* — if yes, a
  whole different morning.
- **Close an open experiment.** *"Did the plants recover after yesterday's irrigation?"* — the
  outcome of a past recommendation, due now.
- **Ground-truth a suspect signal.** A sensor read cold while the crop looked fine: *"Do the
  plants in House 2 actually look cold to you?"*
- **Follow a curiosity.** The within-range humidity drift, the bench that lags: *"Is bench B still
  running behind A?"*

**How Gaia chooses (value of information):** ask the question whose answer would most change what
the grower should do, or most sharpen a belief Gaia is learning — weighted by the stakes and by
how soon it matters. If an answer wouldn't change a decision or advance a lesson, **don't ask it.**
Anything Gaia already knows, or that is merely nice to know, stays unasked.

**The budget is small.** Most mornings are a question or two, concentrated on the **vulnerable**
(propagation, young roots), the **uncertain** (low-confidence, high-stakes inferences), and the
**due** (experiments whose window has closed). Some mornings ask nothing — and silence, when the
crop is settled, is the correct and respectful output.

**How questions are phrased:** short, specific, biological, answerable in a word, and located
("on bench B", "in House 2"). A good question carries its own context so the grower can answer
without thinking about the system at all.

## 5. Answers as evidence

Every answer, however casual, is captured as evidence — without ever feeling captured.

- It becomes one or more **Snapshot observations**: subject (the zone/bench), kind (leaf-wetness,
  pest-sighting, tone…), value, `method: observed-by-human`, `source: this grower`, a confidence,
  and the grower's **verbatim words preserved**. Human observation ranks equal to any sensor.
- A **negative or null answer is evidence too.** "No pests, all clean" is a real observation that
  lowers a risk. "I didn't get to House 3" is honest absence — recorded as not-observed, never
  forced into a value.
- **Uncertainty is kept.** "Maybe a little wet, hard to say" is captured as a low-confidence
  observation, not rounded up to certainty.
- **Same-day effect:** because answers are observations, they flow straight back into today's
  picture — the morning walk can raise or lower a priority and its confidence on the spot. This is
  the decision-quality half of the dialogue.

No form is filled. The grower talks; Gaia listens, structures, and remembers.

## 6. Closing the loop — turning a day into learning

The dialogue exists so that **every recommendation eventually completes the chain**:

```
   Recommendation → Action → Outcome → Lesson → Memory → Better future recommendation
```

The end-of-day **"What actually happened?"** is where this is serviced, day after day:
- **Action** — was the recommendation done, modified, or skipped? (decision-capture, Stage 2.)
- **Outcome** — improved / unchanged / worse / unknown, with the evidence and an honest attribution
  note (Learning Loop, Stage 4). "Unknown" is fine and common.
- **Lesson & confidence** — did the prediction hold? A hit nudges confidence up; a surprise teaches
  most. Gaia states what it concludes and how its confidence moved (Stage 5).
- **Memory** — the completed experiment is preserved forever, full chain intact (Stage 6).

**Across days, not just within one.** A recommendation with an hours-long window (a disease
prevention) closes the same evening; one with a days-long window (toning, a recovery) is asked
about on the morning its window comes due — which is exactly why a walk question can be *"did the
plants recover after **yesterday's** irrigation?"*. The Daily Dialogue is the surface through which
the multi-day learning loop is patiently serviced, one question at a time.

**Calibration is the quiet reward.** Closing recommendations honestly, every day, is how Gaia
learns whether its "70% sure" is actually right seven times in ten — the discipline that makes its
future confidence trustworthy.

## 7. How both get better — the mutuality

This is the point, so it is stated plainly.

- **The grower improves** because Gaia's briefings *explain themselves* (foresight, absorbed over
  time), because its questions *direct attention* to what matters (a trained eye), and because the
  shared record means nothing learned is ever lost.
- **Gaia improves** because every answer is evidence, every closed recommendation is a completed
  experiment, every honest outcome calibrates its confidence, and the learned response of *these*
  plants steadily replaces generic assumption.
- **Together** they accumulate a shared, growing memory and a relationship of earned trust — fewer
  and better decisions each season. Neither learns as fast alone. The Daily Dialogue is the engine
  of that co-evolution: a grower and an intelligence, walking the same crop, getting better at it
  together, every day.

## 8. Decision quality and biology, kept central

- The dialogue optimises **plant outcomes**, never engagement. Its success is healthier crops and
  better-calibrated decisions — not how much the grower talks to it.
- Its questions are **biological** and its timing matches **biological timescales** (ask about
  recovery when recovery would show, about toning over days).
- It **protects attention** as a feature: most days, it asks little and says less.
- It is **honest** end to end — it surfaces what it cannot see, it accepts "I don't know," and it
  calibrates itself against what actually happened.

## 9. Guardrails

- **Never a form, a nag, or an interrogation.** A few good questions; otherwise silence.
- **One at a time; never twice; always optional and interruptible.**
- **Blameless.** "It didn't work" and "I forgot" are valuable, safe answers.
- **Verbatim preserved; the grower's words are the teacher's words.**
- **The grower always decides** and can overrule Gaia; an override is a learning signal, not an
  argument.
- **Voice/hands-free first** for the walk; the grower should never need a screen mid-crop.
- **The knowledge is the grower's and the company's** — captured for their benefit, theirs to
  govern.
- **Graceful when unanswered.** If questions go unanswered, Gaia asks less, not more, and degrades
  to honest lower-confidence reasoning — it never pesters.

## 10. A worked day

- **06:00** — Gaia prepares the brief (House 1: rising disease risk; protect the cuttings; inspect
  the House 2 reading) and three questions: confirm the House 1 condensation, scout House 2 pests,
  close yesterday's House 3 irrigation experiment.
- **08:00** — the grower reads it; accepts the House 1 venting, notes they'll judge the cuttings at
  midday.
- **Walk** — Gaia: *"Condensation on bench B?"* Grower: *"Yeah, still wet up top."* → confirms the
  disease setup; today's priority and confidence **rise** on the spot; evidence stored. Gaia: *"Any
  pests in House 2?"* Grower: *"No, clean."* → a risk **lowered**. Gaia: *"Did House 3 firm up after
  yesterday's irrigation?"* Grower: *"A little, still soft."* → that experiment's outcome captured
  as *partial*.
- **End of day** — Gaia: *"What happened with the House 1 venting?"* Grower: *"Dry by ten, no
  spotting."* → **outcome: improved**; the disease principle holds; **confidence rises**
  (medium → medium-high); the whole experiment becomes **memory**. Tomorrow, in a similar House 1,
  Gaia recommends with a little more earned certainty — and the grower, having seen the reasoning
  twice, is already reaching for the vents.

That is one turn of two growers — one human, one not — getting better together.

## 11. Open questions

1. **Timing within the day** — how Gaia picks the *calm moment* for each question so it never
   interrupts the work (batched at walk start? surfaced as the grower reaches a zone? grower-pulled?).
2. **The question budget** — how few is right, and how it flexes with how vulnerable/uncertain the
   day is.
3. **Adapting to the grower** — how much the dialogue learns an individual's expertise, pace, and
   what they prefer to judge themselves.
4. **Voice capture fidelity** — turning spoken, dialect-rich answers into faithful observations
   without losing the verbatim.
5. **Persistent non-answers** — the right way to stay useful (and quiet) when a grower rarely
   answers, without losing the learning the loop needs.
6. **Cold start** — keeping the dialogue valuable in the first weeks, before there are many open
   experiments to close or much learned history to draw on.

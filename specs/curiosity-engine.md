# Spec — The Curiosity Engine

**Status:** Draft v1 · the Sprint-5 capability (for review before implementation).
**Related:** [`docs/cultivation-intelligence-model.md`](../docs/cultivation-intelligence-model.md)
(pattern recognition), [`docs/gaia-learning-loop.md`](../docs/gaia-learning-loop.md) (curiosities as
the seeds of experiments), [`specs/decision-library.md`](decision-library.md) (the experience it
mines), [`specs/greenhouse-snapshot.md`](greenhouse-snapshot.md) (the stream it scans),
[`specs/daily-grower-dialogue.md`](daily-grower-dialogue.md) (curiosities on the walk),
[`docs/decision-philosophy.md`](../docs/decision-philosophy.md) (value of information, hazards).

> This designs a **reasoning process**, not software, and not machine learning. It elevates the
> Sprint-1 curiosity heuristic (`app/greenhouse_brain/curiosity_engine.py`) into a persistent,
> evolving engine that forms and tracks hypotheses. It extends the existing system; it adds no new
> engine in the architectural sense and no model.

## 1. Purpose

Until now, Gaia has answered questions. The Curiosity Engine lets it **begin asking them.** It
continuously searches the greenhouse's data — the stream of Snapshots and the accumulated
experience in the Decision Library — for patterns that are **unusual, unexplained, or biologically
interesting**, and turns them into **hypotheses**.

It must **never create alarms.** A curiosity is not "something is wrong"; it is "isn't that
interesting — let's understand it." Its purpose is the most ambitious in the whole system: to help
Gaia **discover biology that humans have not yet noticed** — the quiet relationships a busy grower
walks past, made visible, framed as questions, and patiently investigated until they become
knowledge or are honestly rejected.

## 2. Curiosity, concern, recommendation — the boundary

Three things Gaia can raise, and they must not blur:

- A **concern** says *"act — this threatens the plant"* (Decision Engine; urgent; in the brief's
  priorities).
- A **recommendation** says *"do this"* (an action with an expected outcome).
- A **curiosity** says *"I've noticed something I don't yet understand — let's find out"* (a
  hypothesis; never urgent; investigative).

Curiosities are calm by construction. Even a pattern that *might* turn out to matter is raised as
something to understand, not something to fear. Keeping this line sharp is what lets the Curiosity
Engine be bold (raise lots of interesting wonderings) without ever being alarming.

## 3. What makes Gaia curious

The triggers — the kinds of pattern worth a hypothesis (the user's examples mapped to types):

- **Trends** — a signal drifting consistently, even within the normal range. *"House 2 warms
  faster every morning."* (The drift, not a threshold, is what's interesting.)
- **Peer anomalies** — something behaving unlike its peers under the same conditions. *"This mother
  stock grows slower than genetically similar plants."*
- **Temporal associations** — one thing tending to precede or follow another. *"Thrips outbreaks
  appear to follow three days of high humidity."* (A correlation *noticed* — never a causation
  *asserted*.)
- **Comparative differences** — A outperforming B. *"Irrigation strategy A seems to beat strategy
  B."* (A natural experiment spotted in the data.)
- **Unexplained outcomes** — a recommendation worked or failed in a way the current understanding
  doesn't account for (a surprise from the Learning Loop).
- **Recurring prediction errors** — the Decision Library shows a situation where Gaia keeps being
  wrong. *Why?* is a first-class curiosity.

## 4. The three lenses of the scan

Gaia looks for these patterns through three lenses:

- **Temporal** — across a *series* of Snapshots and memories over days and weeks: trends, lags,
  co-occurrences. (A single Snapshot can't show a trend; the engine reads the stream.)
- **Comparative** — across *peers* at one time: zone vs zone, bench vs bench, this plant vs
  genetically similar plants, strategy A vs B. Difference under like conditions is the signal.
- **Expectation-violation** — across *predictions vs outcomes*: where reality defied what Gaia
  expected (the Learning Loop's surprises and the Decision Library's poorly-predicted cells).

## 5. The reasoning process

For each candidate pattern, Gaia runs the scientific method in a grower's idiom — transparent at
every step:

1. **Notice the oddity.** A trend, a peer difference, a co-occurrence, a surprise — surfaced by one
   of the three lenses.
2. **Frame the hypothesis.** State plainly *what* was noticed and *why it is curious* — which
   expectation it violates or which relationship it suggests.
3. **Offer possible explanations.** Candidate *biological* mechanisms ("House 2 warms faster — west
   glass? a failing screen? a vent lagging? lower thermal mass?"). Several, held loosely — the
   point is to make the hypothesis testable, not to commit.
4. **Propose how to find out.** *Suggested observations* (cheap evidence to gather on the walk) and
   *suggested experiments* (small, safe, reversible tests — vary one lever, keep a control bench).
5. **Score it.** A **confidence** (how strong and consistent the signal is) and a **priority** (how
   *interesting/valuable* the biology would be if true — never urgency).
6. **Surface a few; gather evidence; evolve.** Persist it, raise the highest-value ones calmly,
   gather what the walk and the next Snapshots provide, and update it over time (§7).

The "intelligence" here is the **biological framing and the disciplined evidence-gathering**, not a
model. Every curiosity is a sentence a grower could read, argue with, and go test.

## 6. The Curiosity record

Each curiosity carries:

| Field | Meaning |
| --- | --- |
| **Curiosity ID** | stable unique id |
| **Date created** | when first noticed |
| **Supporting evidence** | the observations / memories that prompted it, with provenance |
| **Confidence** | how strong the signal is so far (and why) — starts low |
| **Why Gaia is curious** | what expectation it violates or relationship it suggests |
| **Possible explanations** | candidate biological mechanisms, held loosely |
| **Suggested observations** | cheap evidence to gather (becomes walk questions) |
| **Suggested experiments** | small, safe, reversible tests to settle it |
| **Priority** | learning value if true — *not* urgency |
| **Status** | Open / Investigating / Confirmed / Rejected |

## 7. The lifecycle — curiosities evolve

A curiosity is not a one-off note; it is a hypothesis that lives and changes as evidence arrives:

```
   Open ──▶ Investigating ──▶ Confirmed ──▶ becomes KNOWLEDGE (into the Decision Library)
     │            │
     └────────────┴────────▶ Rejected ──▶ kept as a REJECTED HYPOTHESIS (we now know it's not so)
```

- **Open** — noticed, evidence thin, confidence low.
- **Investigating** — actively gathering: suggested observations are on the walk, or a suggested
  experiment is running. Each new Snapshot, walk answer, or completed experiment adds or subtracts
  support, and confidence moves.
- **Confirmed** — enough corroboration, *consistency*, and a *plausible mechanism* (the canon's
  gates), ideally clinched by a controlled experiment. The curiosity graduates into **knowledge** —
  a learned relationship that informs future recommendations (it joins the Decision Library's
  patterns).
- **Rejected** — the evidence didn't hold. Kept on the record, because *knowing what is not true*
  is valuable and stops the same hypothesis being re-raised forever.

Confidence evolves as a trajectory, exactly as in the Learning Loop — the history of a curiosity's
rise or fall is preserved, not overwritten.

## 8. Priority and restraint

Scanning many signals will throw up coincidences, and a grower's attention is sacred. So:

- **Priority is learning value, never urgency.** A high-priority curiosity is one that, understood,
  would most improve growing.
- **Surface few.** Most curiosities sit quietly Open, investigated passively. Only the most
  interesting, best-supported ones are raised in the brief or on the walk — a small budget.
- **Dedupe and evolve, don't repeat.** A pattern already raised is *updated* with new evidence, not
  raised again.
- **Silence is fine.** A morning with nothing genuinely curious says nothing.

## 9. Honest hazards (the discipline that replaces ML)

- **Correlation is not causation.** A co-occurrence is a *hypothesis*, stated as one. Confirmation
  needs a mechanism and corroboration — ideally a controlled experiment — not just repetition.
- **Confounding.** Many things move together; the *suggested experiments* exist precisely to
  disentangle them (vary one lever, keep a control).
- **Spurious patterns / multiple comparisons.** Looking at many signals guarantees some chance
  coincidences. The engine is therefore *conservative*: it requires recurrence, prefers mechanistic
  plausibility, and **holds confidence low until corroborated** — and it never floods the grower.
- **Never an alarm.** Even an ominous-looking pattern is a curiosity to investigate, not a concern
  to act on; if it becomes actionable, that is the Decision Engine's job, through a recommendation.
- **Overfitting to anecdote.** One occurrence is a wondering; recurrence and mechanism earn the
  status of knowledge.

No machine learning: patterns are found by **transparent, legible methods** — trend detection, peer
comparison, co-occurrence counting, outcome aggregation over the Decision Library — each producing a
*stated biological hypothesis*. Nothing is a weight in a black box; everything is a sentence and an
experiment.

## 10. Integrations

The Curiosity Engine sits across the system Gaia already has:

- **Snapshot** — the **stream it scans**. Within one Snapshot it compares peers; across a *series*
  it finds trends, lags, and co-occurrences.
- **Memory / Decision Library** — the **experience it mines** for comparative differences,
  surprises, and recurring prediction errors — and the **home a Confirmed curiosity graduates into**
  (a curiosity that becomes knowledge becomes a Library pattern that shapes recommendations).
- **Morning Brief** — where the few highest-value open curiosities surface, calmly, as *"things I'd
  like to understand"* (already present in the prototype; now persistent and status-bearing).
- **Walk Mode** — where a curiosity's **suggested observations become the grower's walk questions**;
  the answers are the evidence that moves the curiosity's status. This closes the loop: notice →
  ask on the walk → gather → confirm or reject.

The flow, end to end: *a quiet pattern in the Snapshots/Library → a hypothesis in the brief → a
question on the walk → evidence → Confirmed (knowledge) or Rejected.* That is Gaia learning biology
no one told it.

## 11. Smallest implementation — begin collecting curiosities immediately

The prototype already *generates* per-morning curiosities (`curiosity_engine.py`) but forgets them.
The smallest real Curiosity Engine makes them **persist, evolve, and draw on accumulated data** — no
ML, no new engine, no provider change.

1. **Persist curiosities** as records with the full lifecycle (the §6 fields, status Open→…), in a
   `data/curiosities.jsonl` — the same minimal-store pattern as memories. This alone means Gaia
   *starts collecting curiosities today*.
2. **Keep the existing single-Snapshot heuristics** (within-range trend, dev-note, change follow-up)
   as Open curiosities — but *deduped against what's already open* (raise once, then evolve).
3. **Add two scans over accumulated data** (both transparent, no ML):
   - a **comparative/peer scan** within a Snapshot (zone vs zone, plant vs similar) for anomalies;
   - a **Decision-Library scan** that turns a repeatedly-failing or repeatedly-surprising cell
     (already a Library query) into a curiosity — *"why does X keep not working for crop Y?"*.
4. **Evolve on each cycle**: re-evaluate open curiosities against new Snapshots / walk answers /
   completed experiments → move confidence and status; on Confirm, write a knowledge note to the
   Decision Library; on Reject, mark and stop re-raising.
5. **Wire to brief + walk**: the brief shows open curiosities with status; the walk turns their
   `suggested_observations` into questions and feeds answers back to the curiosity (the Sprint-3
   walk already turns curiosities into questions — extend it to update the persistent record).
6. **A `gaia curiosities` command** to list them, their evidence, and their status.

**Deliberately deferred:** real statistical pattern-mining (proper trend/association tests),
similarity beyond banded fingerprints, and any learned model. Until then, the scans are simple,
legible heuristics — enough to *begin collecting and evolving real curiosities now*.

## 12. Open questions

1. **Novelty threshold** — how strong/consistent a pattern must be before it becomes an Open
   curiosity, so the engine is interesting without being noisy.
2. **Graduation** — how much corroboration (and what kind of experiment) moves a curiosity to
   Confirmed, and how that interacts with "trust before automation."
3. **Surfacing budget** — how many curiosities to raise, and how to rank learning value.
4. **Comparator validity** — for peer/A-vs-B curiosities, how to judge that the comparison is fair
   (genuinely like-for-like) before trusting the difference.
5. **Decay** — how long an un-resolved curiosity stays Open before it is quietly shelved, and how a
   Confirmed pattern is re-opened if the biology drifts.
6. **Autonomy of experiments** — how far Gaia may *propose* (never run unattended) deliberate
   experiments, and the grower's role in approving them.

# Spec — The Observation Planner (Gaia's active-perception engine)

**Status:** Draft v1 · Sprint 5 (architecture; build deferred — RFC-004 §10). **Decision:**
[`rfc/RFC-004-observer-network.md`](../rfc/RFC-004-observer-network.md). **Concepts:**
[`specs/observer-network.md`](observer-network.md). **Ancestors it generalizes:**
[`specs/knowledge-gap-engine.md`](knowledge-gap-engine.md),
[`specs/daily-grower-dialogue.md`](daily-grower-dialogue.md), and the Field Companion's
Interaction Engine ([`specs/field-companion.md`](field-companion.md)).

> A *meaning*, not software. No code is proposed. This is the contract the engine will satisfy.

## 1. Purpose

The Observation Planner is Gaia's next major engine. **Its purpose is not collecting data — it
is deciding what is worth observing.** Given what the Brain is uncertain about and which
observers exist, it decides:

- **which observation** would most improve biological understanding,
- **who** should perform it,
- **when**, and **why**,
- **at what biological value**, and **at what interruption/operational cost**,
- or that **no observation is worth it** right now.

It is "ask before assuming," generalized from *asking the human* to *tasking any observer* — and
its default, like the Field Companion's, is **silence**.

It holds **no biological reasoning.** It reads the Brain's uncertainties and the observers'
metadata, and emits requests. *If the Planner reasons about plants, the abstraction has leaked.*

## 2. Inputs and outputs

**Inputs**
- **Uncertainties** from the reasoning plane — each: `(subject, latent variable, current
  confidence, stakes, decisiveness, time-window)`. These are exactly the Knowledge-Gap signals,
  generalized: not "a question for the human" but "a thing Gaia is unsure about and that
  matters." Time-window comes from the biology (Botrytis: hours; toning: days).
- **The Observer registry** — observers, their `ObserverCapability`s, and their learned
  `ObservationTrust`, `ObservationCost`, `ObservationLatency`, `ObservationAvailability`.
- **ObservationHistory** — for learned priors (which observers proved worth calling, for what).

**Outputs**
- An **ObservationPlan**: prioritized `ObservationRequest`s with assigned observers, timing, and
  rationale — **and** the explicit "not worth observing" set. Every entry is recorded in
  ObservationHistory with its EVI, cost, and reason.

## 3. The decision: who observes next

For each uncertainty, for each **capable** and **available** observer:

```
EVI(uncertainty, observer) =
      expected_uncertainty_reduction         # how much this observation would move confidence
    × stakes(uncertainty)                     # how much the decision matters
    × decisiveness(uncertainty)               # would the answer actually change an action?
    × trust(observer, capability)             # a low-trust observer reduces uncertainty less
    × quality_prior(observer, capability)     # and a low-fidelity one less still

effective_cost(observer) =
      cost(observer, capability)              # interruption + operational + money + risk (§ cost)
    × latency_penalty(latency vs time_window) # slow observer for an urgent risk ⇒ high penalty

net_value = EVI − effective_cost
```

- **Choose the observer with the highest positive `net_value`** for the highest-value
  uncertainty, subject to availability and the deadline.
- This generalizes the Knowledge Gap Engine's `VoI = stakes × uncertainty × decisiveness × prior
  − interruption_cost`: the human is one observer whose cost is *interruption*; a drone is
  another whose cost is *a flight*; the math is the same, evaluated across observers.

The Planner also chooses **timing** (now / when the observer is at the location / before the
window closes), **sequencing** (batching several requests into one `ObservationSession` — a
single flight or one walk — as a route, not a set), and records **why this observer and not the
others.**

## 4. The decision: no observation is needed

Silence/passivity is a **first-class output**, not a fallback. The Planner issues **no request**
when:
- no observer's `net_value` clears a threshold (the best available observation wouldn't change a
  decision, or its cost exceeds its value); or
- the cheapest action is to *act anyway* (the recommendation is low-regret and reversible, so
  reducing uncertainty isn't worth any cost — BIOLOGY.md: "prefer reversible, low-regret actions
  and re-observe"); or
- the uncertainty is below what matters for any current decision.

This mirrors the Field Companion (silence is default) and the Knowledge Gap Engine (most
questions are never worth asking) — now across every observer.

## 5. What it optimizes (four objectives at once)

| Objective | How the Planner serves it |
| --- | --- |
| **Maximum biological understanding** | EVI is measured in *decision-relevant uncertainty reduced*, weighted by stakes and decisiveness. |
| **Minimum interruption** | Interruption is a first-class cost dimension; silence is the default; human observers are spaced (inherited from the Interaction Engine). |
| **Minimum cost** | Operational/money/risk costs are weighed; the cheapest *trustworthy, timely* observer wins. |
| **Maximum learning** | Information value includes *learning value*: observations that calibrate a low-trust observer or close an open experiment are worth more (as the Knowledge Gap Engine already values "close" questions). Over time, learned trust makes the Planner choose better and **ask less**. |

## 6. Worked example (Gaia thinking aloud)

> **Uncertainty:** Botrytis risk in House 2 — confidence **0.62**, stakes **high**, decisiveness
> **high** (it would change whether I push airflow now), time-window **hours**.
>
> **Options:**
> - **Ask Oskar** (human): trust(leaf-wetness) high, quality high, cost = *one interruption*,
>   latency = "he's on the walk, near House 2 now." → high EVI, low cost → **net_value high.**
> - **Send DJI** (rgb+thermal): trust medium, cost = *a flight (battery, 6 min)* + minor risk,
>   latency ~minutes. → good EVI, higher cost → **net_value medium.**
> - **Lab tissue test:** trust very high, but latency **days** ≫ window → latency penalty huge →
>   **net_value ≈ 0** for *this* decision.
> - **No observation:** acting (more airflow) is cheap and reversible → maybe net_value of *any*
>   observation < threshold → **stay silent and act.**
>
> **Decision:** ask Oskar (highest net_value), *because* he is available at the location, trusted
> for exactly this sign, and nearly free. Record EVI, cost, and the reason. If he weren't on the
> walk, the DJI would win; if airflow were free and harmless, silence would win.

This is precisely a Head Grower's instinct — *who can tell me, how fast, how reliably, and is it
even worth finding out?* — made explicit and auditable.

## 7. Memory and learning (every observation remembered)

For every request — issued, fulfilled, declined, or skipped — the Planner writes an
`ObservationHistory` record (observer-network spec §13): **who observed, why, how, when,
confidence before, confidence after, decision changed?, outcome, worth collecting?** From this:
- **ObservationTrust** is recalibrated (did the observation hold up / agree / predict?).
- The Planner's **priors** shift (an observer/capability that repeatedly proves worthless clears
  the bar less often — the same `prior_worth_by_kind` mechanism the human-only engine already
  uses, generalized per observer).
So the system trends toward **fewer, better-targeted observations** over months and years.

## 8. Boundaries (so it stays safe and small)

- **No biology.** It consumes uncertainties and observer metadata; it never estimates Plant
  State or Disease Risk itself.
- **No observer favoritism in the Brain.** The Planner is the *only* component that reasons about
  observers; the Decision Engine never sees them. Removing an observer changes the Planner's
  options, nothing downstream.
- **Tasks observations, never actions.** No actuation (RFC-004 §9).
- **Build deferred.** Per RFC-004 §10, the Planner is built only when a real *choice between
  observers* exists (e.g. human *or* camera could answer the same uncertainty). Until then the
  existing human-only Knowledge Gap + Interaction logic *is* the Planner with one observer —
  which is why no rework is needed when the second observer arrives.

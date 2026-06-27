# Spec — The Observer Network (concepts)

**Status:** Draft v1 · Sprint 5 (architecture; reviewed before any implementation).
**Defines:** the vocabulary the next decade of Gaia observes reality with. **Decision:**
[`rfc/RFC-004-observer-network.md`](../rfc/RFC-004-observer-network.md). **Engine:**
[`specs/observation-planner.md`](observation-planner.md). **Output contract:** the Canonical
Observation is the existing [`specs/greenhouse-snapshot.md`](greenhouse-snapshot.md) envelope —
this spec does **not** redefine it.

> Meanings, not software. Illustrative shapes are for clarity, not a commitment to a format.
> No code is proposed.

## 0. The one rule above all

**An Observer observes reality and returns Canonical Observations. It performs no biological
reasoning, and the Brain never knows which Observer produced an observation.** Everything below
serves that rule. *If an observer reasons about plants, or if the Decision Engine branches on
observer identity, the abstraction has leaked.*

## 1. Observer

Anything that can observe a facet of greenhouse reality and report it as Canonical
Observations: Synopta, the human grower, Even G2, a DJI drone, fixed cameras, a phone, a weather
service, a thermal camera, a lab, a future humanoid. **None is special.** An Observer is defined
by *configuration*, not by new intelligence:

| Field | Meaning |
| --- | --- |
| **id / class** | stable, vendor-neutral identity (e.g. `observer:synopta-kalaberga`, `observer:grower:oskar`, `observer:dji-m3`) |
| **capabilities** | the `ObserverCapability` records it offers (§2) |
| **tasking modes** | `push` (streams/volunteers observations), `pull` (can be asked via an `ObservationRequest`), or both |
| **availability** | current `ObservationAvailability` (§12) |
| **trust profile** | learned `ObservationTrust` per capability (§9), seeded from priors |
| **provenance identity** | how it appears in an observation's `source`/`chain` — for trust and audit only, never for reasoning |

An Observer never holds Plant State, Stress, Disease Risk, or any latent biology. It may hold
*device* logic (how to fly, how to read a sensor) but no *biological* logic.

## 2. ObserverCapability

One declarative thing an Observer can observe. Capabilities are matched against the Planner's
demand ("what observation about what subject would reduce which uncertainty?").

| Field | Meaning |
| --- | --- |
| **kinds** | observation `kind`s it can produce (air-temperature, relative-humidity, leaf-wetness, rgb-image, thermal-image, pest-presence, EC, pH, …) |
| **subject scope** | which subjects it can reach (site / zone / bench / batch / plant; indoor/outdoor) |
| **method** | `measured` / `observed-by-human` / `vision-inferred` / `lab-analysis` / `forecast` / `derived` (snapshot §8) |
| **quality profile** | intrinsic `ObservationQuality` priors for this capability (§8) |
| **trust profile** | `ObservationTrust` priors, refined by history (§9) |
| **cost profile** | `ObservationCost` priors (§10) |
| **latency profile** | `ObservationLatency` priors (§11) |
| **preconditions** | what must hold to use it (daylight for RGB, flight-permitted, grower present, sample taken) |
| **direction** | **observe-only** (read). Actuation is out of scope (RFC-004 §9). |

### Capability profiles (illustrative)

| Observer | Capabilities (kinds / modalities) | Typical method | Notes |
| --- | --- | --- | --- |
| **Synopta** | climate (air-temp, RH, CO₂, light), irrigation, heating, ventilation, alarms | measured | continuous push; high trust, ~zero cost, seconds latency, but **per-sensor** trust (a faulted sensor → low) |
| **Human grower** | vision, smell, touch, experience, judgement (leaf-wetness, pest sighting, tone, "looks off") | observed-by-human | pull on the walk; high trust, **interruption** cost, latency = "when they pass"; equal rank to sensors (BIOLOGY.md) |
| **Even G2** | display, microphone, speaker, notification | — | a *device of the human Observer*, not an observer of plants; carries requests/answers (Field Companion) |
| **DJI drone** | rgb-image, thermal-image, navigation, autonomous flight (spatial scouting, canopy temperature) | vision-inferred | pull; medium trust, operational cost (battery/flight), minutes latency, weather/daylight preconditions |
| **Fixed cameras** | rgb-image, time-lapse, vision-inferred signs | vision-inferred | push/stream; medium trust, low cost, low latency, fixed viewpoint |
| **Weather service** | outside-temperature, humidity, radiation, wind, precipitation (current + forecast) | measured / forecast | push/pull; site scope; forecast carries its own lower confidence |
| **Laboratory** | substrate/tissue analysis (EC, pH, pathogen ID, nutrients) | lab-analysis | pull; very high trust, money cost, **days** latency |
| **Humanoid (future)** | mobility, manipulation, cameras, touch, thermal sensing, speech | measured / vision-inferred / observed-by-machine | pull; trust unknown→calibrated; reaches bench/plant scope a fixed camera cannot |

The table is illustrative; observers are registered as they become real ("ask, don't assume").

## 3. Observation

The **Canonical Observation** — the existing snapshot envelope (greenhouse-snapshot.md §4),
unchanged: `subject · kind · value (+unit) | absence · captured_at · source · method ·
confidence · notes/verbatim`, plus provenance (`chain`). The Observer Network adds only that
`source` resolves to an **Observer id** and the observation may carry `quality` and `trust`
provenance so fusion (§6) and the Brain can weigh it. It remains **immutable**; a correction or
re-look is a *new* observation.

## 4. ObservationRequest

A demand the Planner issues to reduce a specific uncertainty. It describes **what** is needed,
not yet **who** (until assigned):

`id · target (subject + kind/latent it informs) · purpose (the decision/uncertainty it serves) ·
deadline (driven by the biology's time window) · expected_value (EVI) · cost_ceiling ·
min_quality / min_trust · created_at · status`. Observer-agnostic by design — any capable
observer could fulfill it.

## 5. ObservationPlan

The Planner's output: the prioritized set of `ObservationRequest`s with **chosen observers**
(assignments), timing, and rationale — **and** the explicit set of uncertainties it decided are
**not worth observing**. The plan optimizes understanding / interruption / cost / learning
(planner spec §3). A plan is a *decision about perception*, recorded like any decision.

## 6. ObservationSession & conflict fusion

**ObservationSession** — a bounded execution context in which one Observer fulfills one or more
requests: a drone flight, a grower's walk, a Synopta polling cycle, a lab batch. Lifecycle
`planned → active → complete | aborted`; it records the cost and latency actually incurred and
the observations produced.

**Fusion / conflicting observations.** When several observations describe the same `subject` +
`kind` near the same time, they are combined **at Snapshot assembly, not in the Decision
Engine** (which stays observer-blind):
- **Corroboration raises confidence** — independent observers agreeing is real evidence.
- **Conflict raises *uncertainty*, never silently picks a winner** — the fused value is weighted
  by `trust × quality × recency`, and residual disagreement *lowers* the fused confidence.
- **All observations are preserved** as evidence (immutability); the fused view is a derived
  observation with `method: derived` and a transparent basis.
This is the snapshot spec's "combining corroboration is the engines' job," made concrete.

## 7. Representing uncertainty

Two layers, kept distinct:
1. **Per-observation confidence** = `ObservationQuality × ObservationTrust × recency` (§8, §9).
   The Observer Network owns this.
2. **Latent-variable confidence/uncertainty** (Plant State, Botrytis risk, …) — owned by the
   one brain, formed *from* the observations and their confidences.
**Absence is first-class** (snapshot §10): *known-absent* (no observer can/did see it), *stale*
(old observation), *unknown* (never observed) — never coerced to a value. The Planner reads this
absence as the demand it works to reduce.

## 8. ObservationQuality

The intrinsic fidelity of a specific observation/result, independent of who produced it:
resolution/precision, freshness, completeness/coverage, and method fidelity (a calibrated sensor
vs a phone glance vs a low-res frame at dusk). Quality is a property of *this* observation;
trust is a property of the *observer*. Both feed confidence.

## 9. ObservationTrust

How much to believe a given **Observer for a given capability** — **learned**, not declared:
- seeded from a prior (sensor class, human experience, device spec);
- updated from `ObservationHistory`: did its past observations *hold up* (match later reality),
  *agree* with corroborating observers, and *predict* correctly (did decisions based on them turn
  out right)?
- degraded by known failure modes (the faulted *Sensor Box 002* → trust for that channel drops,
  exactly as the Collector already flags).
Trust is per `(observer, capability, subject-class)`, so one bad sensor doesn't taint a good one.

## 10. ObservationCost

The full cost of obtaining an observation, multi-dimensional, normalized to one comparable scale
for planning (a small, auditable normalization — like the VoI weights): **interruption** (human
attention/cognitive load — the Field Companion's currency), **operational** (drone battery/flight
time, camera compute, staff time), **money** (lab fees), and **risk** (flying near structures,
disturbing a crop). The Planner weighs value against this total.

## 11. ObservationLatency

Time from request to the observation being available — and it is *biological* latency that
matters: Synopta ~seconds, a fixed camera ~seconds, the grower "when they next pass," a drone
minutes (launch + fly), a lab **days**. The Planner judges latency against the biology's time
window: a three-day lab result is worthless for a Botrytis decision due this morning, however
trustworthy.

## 12. ObservationAvailability

Whether/when an Observer can act *now*: online/offline, within working hours, weather/daylight,
location/reachability, battery, permissions, do-not-disturb. A perfectly capable, trusted,
cheap observer that is **unavailable** cannot be tasked now — availability gates the Planner's
choices before value is even compared.

## 13. ObservationHistory

The permanent memory of **every** observation and **every** request — issued, fulfilled,
declined, or deliberately skipped. For each: **who** observed, **why** (the uncertainty/decision),
**how** (capability/method), **when**, **confidence before**, **confidence after**, **did the
decision change?**, **outcome**, and **was it worth collecting?** This is both the training data
for `ObservationTrust` and the learning loop (RFC-001 / lifecycle): it is how Gaia learns which
observers are worth calling, for what, and when — and therefore how it learns to **observe less
and understand more**. It extends, and is stored beside, the existing interaction/experiment
memory.

## 14. What stays out (so the contract is safe to adopt now)

- **No biology in any Observer or in the Planner.** Reasoning lives once, in the core.
- **No actuation.** Observers are read-only; control is a separate, later, trust-gated concept.
- **No observer identity in the Decision Engine.** Identity is provenance, used by fusion and the
  Planner *before* reasoning, never inside it.
- **No new Snapshot format.** The Canonical Observation already describes *reality*, not the
  machine that saw it — which is why observers not yet invented already fit it.

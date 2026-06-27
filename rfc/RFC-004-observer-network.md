# RFC-004 — The Observer Network: how Gaia observes reality

**Status:** Open · Sprint 5 (architecture only; no implementation). Promote to **ADR-005 —
Observer Network** on acceptance, then update [`docs/architecture.md`](../docs/architecture.md).
**Related:** [ADR-002](../adr/ADR-002-provider-abstraction.md) (providers),
[RFC-002](RFC-002-provider-taxonomy.md) (provider taxonomy),
[RFC-003](RFC-003-layered-specialist-agent-architecture.md) (one brain, many consumers),
[RFC-001](RFC-001-feedback-and-learning-loop.md) (learning loop),
[`specs/greenhouse-snapshot.md`](../specs/greenhouse-snapshot.md) (the Canonical Observation),
[`specs/observer-network.md`](../specs/observer-network.md) (the concept contracts),
[`specs/observation-planner.md`](../specs/observation-planner.md) (the new engine).

> This RFC defines a *structure and its meaning*, not software. No code is proposed. The job is
> to give the next decade of Gaia an architecture it can safely grow on.

## 1. The question has changed

Until now the architecture answered **"how does Gaia *receive* data?"** — the Provider Layer
(ADR-002): Synopta and Claude Dispatch behind one interface, producing a Canonical Snapshot.

Sprint 5 asks a larger question: **"how does Gaia *observe reality*?"** These are not the same.
Receiving data assumes a feed. Observing reality assumes *many possible observers*, each able to
look at a different facet of the greenhouse, with different trust, cost, speed, and availability
— and assumes Gaia can **choose** which of them to call upon, or to call upon none.

Reality can be observed by Synopta, a human grower, Even G2 glasses, a DJI drone, fixed
cameras, a phone, a weather service, a thermal camera, a lab, or a humanoid not yet invented.
**None of these is special. Each is simply an Observer.** The architecture must treat them as
interchangeable behind one contract — exactly as ADR-002 made vendors interchangeable — and add
the one thing the Provider Layer never had: a way to **decide who should observe next, and
whether observing is worth it at all.**

## 2. Decision

Adopt the **Observer Network**: a generalization of the Provider Layer across every kind of
observer, plus a new core engine — the **Observation Planner** — that turns the Brain's
uncertainty into observation tasks. It rests on three separated planes:

```
              ┌──────────────────────────────────────────────────────────┐
              │  REASONING PLANE — the one brain (observer-independent)    │
              │  Context → Decision → confidence/uncertainty → Language    │
              │  consumes ONLY Canonical Observations; emits the           │
              │  uncertainties it would most like reduced                  │
              └───────▲───────────────────────────────────┬──────────────┘
   Canonical          │ observations (in)                   │ uncertainties (demand)
   Observations       │                                     ▼
              ┌────────┴───────────┐         ┌──────────────────────────────────────┐
              │ OBSERVATION PLANE  │         │  TASKING PLANE — Observation Planner   │
              │ observers →        │         │  which observation most improves        │
              │ Canonical          │◀────────│  understanding? who? when? why?         │
              │ Observations →     │ Observa- │  …or is no observation worth it?        │
              │ Snapshot (fused)   │ tion-    │  issues ObservationRequests             │
              └────────┬───────────┘ Requests └──────────────────┬─────────────────────┘
                       │                                          │ assigns
            ┌──────────┴──────────────────────────────────────────┴───────────┐
            │  OBSERVER NETWORK  (interchangeable behind the Observer contract) │
            │  Synopta · Human(+Even G2) · DJI · Cameras · Weather · Lab · …    │
            │  Humanoid(not yet invented) — registered, never special           │
            └───────────────────────────────────────────────────────────────────┘
```

- **Observation plane** (data in): every Observer produces **Canonical Observations** (the
  existing snapshot envelope, [`specs/greenhouse-snapshot.md`](../specs/greenhouse-snapshot.md)
  §4). They are *fused* into a Snapshot (conflicts → uncertainty, corroboration → confidence;
  §6 below). This **generalizes ADR-002**: a Provider is just an Observer that streams measured
  climate.
- **Reasoning plane** (the one brain): unchanged in spirit (RFC-003). It consumes only Canonical
  Observations and **never knows which Observer produced them**. As a by-product of reasoning it
  exposes its **uncertainties** — the latent variables it is unsure about and that matter
  (e.g. *Botrytis risk in House 2, confidence 0.62, high stakes, time-sensitive*).
- **Tasking plane** (active perception — the new **Observation Planner** engine): reads those
  uncertainties and the Observer registry, and decides **which observation would most improve
  biological understanding, who should perform it, when, and why — at what value and what cost —
  or that no observation is worth the interruption.** It issues **ObservationRequests**;
  results return on the observation plane and update confidence. A closed loop.

The full concept contracts are in [`specs/observer-network.md`](../specs/observer-network.md);
the engine in [`specs/observation-planner.md`](../specs/observation-planner.md). This RFC is the
decision and its justification.

## 3. What it generalizes (we are protecting the architecture, not replacing it)

| Existing thing | Becomes, under the Observer Network | Still true |
| --- | --- | --- |
| **Provider Layer** (ADR-002) | An Observer that produces measured observations via continuous pull | The substitutability test (swap vendors with no core change) — now for *all* observers |
| **Provider taxonomy** (RFC-002) | Observer *capability profiles* (climate, vision, environment, lab…) | Families as guidance; resolves RFC-002's open question "do cameras belong in the provider model?" — **yes, as Observers** |
| **Collector** | The Synopta Observer's adapter + Snapshot assembly | The Source seam = an Observer's tasking/fetch |
| **Field Companion** | The **human Observer's** request/response channel + interaction economics | Even G2 is one device for one observer; nothing depends on it |
| **Knowledge Gap + Interaction engines** | The **human-only ancestors** of the Observation Planner (same VoI math, one observer) | The Planner generalizes them across *all* observers |
| **Memory / lifecycle** (RFC-001) | **ObservationHistory** + Observer **trust** calibration | Confidence before/after, worthwhile, permanent records |
| **Canonical Snapshot** | The fused set of Canonical Observations | The envelope is unchanged; it already anticipated many observers (§13 of its spec) |

No founding ADR is violated. ADR-001 (reason vs. language), ADR-002 (substitutable sources),
ADR-003 (model-independent core), ADR-004 (morning intelligence) all hold; the Observer Network
sits *with* them and widens ADR-002 from "providers" to "observers."

## 4. The questions this architecture must answer (and where)

| Question | Answered by | In short |
| --- | --- | --- |
| What is an Observer? | spec §1 | Anything that can observe a facet of reality and return Canonical Observations; defined by configuration, holds no biological reasoning. |
| What is an Observation? | spec §3 | The existing Canonical Observation envelope — one provenance- and confidence-bearing fact. Unchanged. |
| What capabilities can an Observer possess? | spec §2 | Declared `ObserverCapability` records: which observation *kinds*, over which *subjects*, by which *method*, with quality/trust/cost/latency/availability priors. |
| What makes observations trustworthy? | spec §6, §9 | `ObservationTrust` (learned per observer×capability) × `ObservationQuality` (intrinsic fidelity) × recency, plus cross-observer corroboration and transparent provenance. |
| How is uncertainty represented? | spec §7 | Per-observation confidence (quality×trust×recency) feeding the Brain's own latent-variable confidence/uncertainty; absence is first-class (known-absent / stale / unknown). |
| How are conflicting observations handled? | spec §6 | Fused by trust×quality×recency at assembly; disagreement *raises* uncertainty, never silently picks a winner; all observations preserved as evidence. |
| How does Gaia decide who observes next? | planner §3 | The Planner maximizes Expected Value of Information **minus** cost across capable, available observers, respecting latency vs. the biology's time window. |
| How does Gaia decide no observation is needed? | planner §4 | When no observer's net value clears the threshold — silence/passivity is a first-class output (as with the Companion and Knowledge Gap engine). |

## 5. The Observation Planner — Gaia's next major engine (summary)

Its purpose is **not** collecting data; it is *deciding what is worth observing, by whom, when,
and why.* It optimizes four things at once: **maximum biological understanding, minimum
interruption, minimum cost, maximum learning.** It thinks, literally:

> *"I believe Botrytis risk in House 2 is increasing. My confidence is only 0.62. The cheapest
> way to reduce that uncertainty is to ask Oskar (he's on the walk, he can see the canopy, I
> trust him for leaf-wetness). Sending the DJI would also work but costs a flight and 6 minutes.
> Or — the risk window is wide and acting is cheap, so no observation is worth the interruption."*

Three gates compound (each inherited, not invented): the VoI of the uncertainty, the EVI−cost of
the best observer for it, and interruption/operational spacing — and the learned trust priors
update from outcomes so the Planner gets better and asks less. Full design:
[`specs/observation-planner.md`](../specs/observation-planner.md).

## 6. Designed for ten years — thousands of greenhouses, hundreds of observer types

- **Observers are configuration, not new reasoning** (RFC-003 ethos). A new observer type is a
  registry entry (capabilities + trust/cost/latency/availability), not a code change in the
  Brain. Hundreds of types cost breadth, not reasoning surface.
- **The Brain is observer-blind.** The Decision Engine consumes `(kind, value, confidence)` and
  never branches on observer identity; identity lives only in provenance, used for trust and
  audit *before* the observation reaches reasoning. Two observers of the same plant yield one
  fused estimate with one confidence.
- **Per-greenhouse registries.** Each site has its own Observer registry and trust history; the
  architecture is identical across thousands of sites because observers, not sites, vary.
- **Robots not yet invented** join as observers with novel capabilities; the contract is the
  *Canonical Observation*, which is about reality (a temperature, a wet leaf, an image), not
  about the machine that saw it — so it already fits sensors that don't exist yet.

## 7. The two final questions (the architecture is not finished unless both are "yes")

**"If DJI disappeared tomorrow, would Gaia still work?"** — **Yes.** A drone is one Observer.
Removing it from the registry removes its capabilities from the Planner's options; the Planner
routes those uncertainties to other observers (the human, a fixed camera) or decides no
observation is worth it, and the affected facets are honestly represented as lower confidence /
known-absent. **Nothing in the Brain depended on DJI**, so nothing in the Brain changes. Gaia
runs, with honestly reduced perception.

**"If a humanoid appeared tomorrow, could Gaia use it without changing the Brain?"** — **Yes.**
Register it as an Observer with its capabilities (mobility, manipulation, cameras, touch,
thermal, speech), its trust/cost/latency/availability priors, and its tasking mode. The Planner
can immediately consider it when choosing who observes next; its outputs arrive as Canonical
Observations the Brain already knows how to consume. **No Decision Engine change, no new
reasoning, no new Snapshot format.** The humanoid is just a very capable new pair of eyes (and
hands, later — see §9 actuation).

Both answers are "yes" *by construction*, because observers are interchangeable behind the
Canonical Observation contract — the same property ADR-002 proved for vendors, now extended to
all of reality's observers.

## 8. Evaluation against every project principle

| Principle | How the Observer Network honors it |
| --- | --- |
| **Reality before assumptions** | The whole architecture is about observing reality; missing observations are honest absence, never fabricated. The Planner reduces *assumption* by acquiring *observation* — but only when worth it. |
| **Biology before software** | Observers and the Planner hold **no biology**; biology stays in the one brain. The Planner's value function is *biological understanding gained*, and latency is judged against the *biology's* time window (Botrytis now ≠ a lab result in three days). |
| **Observation before inference** | Made structural: an entire *plane* for observation, separate from the reasoning plane that infers. Observations are preserved as evidence; inference (and conflict resolution as uncertainty) is downstream. |
| **Ask before assuming** | The Planner *is* "ask before assuming," generalized: it decides when an observation (from any observer) is worth acquiring to resolve uncertainty — and when to stay silent. |
| **Learn from outcomes** | `ObservationHistory` + `ObservationTrust` calibrate every observer from whether its observations held up, agreed, and changed decisions; the Planner learns to choose better observers and to ask less. |
| **Prefer simplicity** | One contract (Canonical Observation) for all observers; one engine (the Planner) generalizing two existing ones (Knowledge Gap + Interaction) rather than adding parallel logic. New observers are config, not code. |
| **Explain uncertainty** | Every observation carries provenance, quality, trust, and confidence; every Planner decision records EVI, cost, and why this observer (or why silence). Conflicts surface as explicit uncertainty. |
| **Highest-value-first** | The Planner's core rule is maximize EVI − cost; the default is *no observation*. The most decision-relevant uncertainty, observed by the cheapest trustworthy available observer, wins. |
| **Every sprint betters the grower** | Gaia gains *active perception*: it can marshal the right eyes for the right question at the right cost — the defining skill of a Head Grower who knows when to walk the house, when to send someone, and when to leave it alone. |
| **Protect the architecture** | Generalizes ADR-002 and reconciles RFC-002/RFC-003 without violating any ADR; the Brain stays observer-independent; reasoning is defined once. The two final questions both pass. |

No principle is weakened. If review finds one that is, this RFC is **not** ready and must be
redesigned before promotion to an ADR.

## 9. Scope, risks, and open questions

**In scope:** observation (perception) only — read. **Out of scope (deliberately):**
**actuation** (a drone *spraying*, a humanoid *moving a plant*). Actuation is a separate future
concept (an *Actor* mirror of Observer), gated by "trust before automation"; the Observer
contract is read-only so the network can be adopted now without any control risk. The Planner
*tasks* observations, never actions.

**Risks:**
- *Premature breadth* — defining observer families we never populate (the RFC-002 warning).
  Mitigation: ship the contract; register observers only as real ones arrive (Synopta + human
  exist today). 
- *Planner as god-object* — it could accrete reasoning. Mitigation: it holds **no biology**; it
  reads uncertainties and observer metadata and outputs requests. *If the Planner reasons about
  plants, the abstraction has leaked.*
- *Trust bootstrapping* — a new observer has no history. Mitigation: start from declared priors,
  widen its observations' uncertainty until calibrated, corroborate against trusted observers.
- *Cost commensurability* — interruption vs. battery vs. money vs. risk on one scale. Mitigation:
  a small, legible normalization (like the VoI weights a grower could audit), refined by history.

**Open questions:** (1) the exact cost normalization across dimensions; (2) whether the
Observation Planner is one engine or the Decision Engine emitting demands + a thin scheduler;
(3) how a single ObservationSession spanning many requests (a drone flight, a walk) is
optimized as a route, not just a set; (4) when actuation is introduced, whether Observer and
Actor share a registry; (5) how trust transfers across similar observers (one DJI's calibration
informing another's prior).

## 10. Migration strategy (no construction now)

1. **Adopt as model.** On acceptance, record **ADR-005 — Observer Network**, update
   [`docs/architecture.md`](../docs/architecture.md) to show the three planes, and state the
   normative definition of Observer / Canonical Observation / Observation Planner.
2. **Re-describe what exists** in the new vocabulary with zero code change: Synopta = the first
   Observer; the human (via the Field Companion) = the second; the Collector = the Synopta
   Observer's adapter; the Knowledge Gap + Interaction engines = the Planner's current,
   human-only behavior.
3. **Build the Planner only when a second observer type makes a choice real** — i.e. when there
   is genuinely more than one observer that could answer the same uncertainty (e.g. human *or*
   camera). Until then, "ask, don't assume": the existing human-only logic stands.
4. **No core rework later**, because the contract — *observers are interchangeable behind the
   Canonical Observation; the Brain is observer-blind; the Planner tasks, never reasons* — is
   fixed now, before any observer or the Planner is written.

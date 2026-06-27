# Chief Architect Review — RFC-004 Observer Network

**Status:** Adversarial review · gate before promoting RFC-004 → ADR-005. **Stance:** I am an
external systems architect with no attachment to this design. My job is to **break it**, not
defend it. Assume it must survive **twenty years** and become the operating system for
biological production. Every weakness below states **why it is a weakness**, the **smallest
improvement**, and **now vs. postpone**. No implementation.

**Verdict up front:** the *core invariant* survives (observers are interchangeable behind the
Canonical Observation; the Brain is observer-blind; tasking is separated from reasoning). But the
RFC as written is **too synchronous, too greedy, and too unconstrained** to be called 20-year
architecture. It **survives conditionally** — on folding in the eight "fix now" items in §X
before it becomes ADR-005. None of them changes the core; that they can be absorbed *without*
changing the core is itself the strongest evidence the core is right.

Severity key: **[Core]** threatens the invariant · **[Structural]** shapes the contract, cheap
now/expensive later · **[Operational]** real but implementable later.

---

## 1. Scalability — **[Structural]**

- **Planning is combinatorial and the RFC hides it.** "Choose the best observer" is
  O(uncertainties × observers); batching requests into one drone flight/walk is an
  orienteering/vehicle-routing problem (NP-hard). At hundreds of observer types this is not
  free, and the RFC says "as a route, not a set" without owning the cost.
  *Smallest fix:* state the planner is **per-site, greedy top-K** with an explicit complexity
  bound; routing optimization is a named later concern, not implied. **Now** (one sentence
  prevents an accidental global optimizer).
- **ObservationHistory grows without bound** and trust is implied to be computed from it.
  *Smallest fix:* specify trust as a **maintained running statistic** (sufficient stats, decay),
  not a replay of full history; history is archival/audit. **Now** (contract-level).

## 2. Simplicity — **[Structural]**

- **Thirteen first-class concepts + a new engine before a second observer exists.** RFC-002's own
  warning (premature breadth) applies to RFC-004. Several "concepts" are really *attributes*:
  `ObservationCost / Latency / Availability / Quality` are fields of a Capability/Observer, not
  entities; treating them as first-class inflates surface area and invites ceremony.
  *Smallest fix:* **tier the model** — a minimal built contract (Observer, ObserverCapability,
  Observation, ObservationRequest, ObservationHistory) and demote Cost/Latency/Availability/
  Quality/Trust to *attributes*, with Plan/Session/Result as derived. **Now** (it's free to
  re-tier on paper; expensive once code reifies thirteen types).

## 3. Biological correctness — **[Core-adjacent]**

- **Greedy EVI is biologically myopic.** BIOLOGY.md is explicit: biology *lags and acclimates*,
  *prevention beats correction*, *the disease triangle is read predictively before symptoms*. A
  per-cycle "maximize EVI − cost" optimizer under-observes slow-building risks: at any instant the
  marginal EVI is low, so monitoring never wins — yet the *option value* of early detection is
  enormous. A naive planner would stop watching a quiet Botrytis setup and be surprised.
  *Smallest fix:* define EVI over a **decision horizon/window**, not the immediate decision, and
  give known seasonal/triangle risks a **monitoring-cadence floor** (a minimum observation rate
  independent of instantaneous EVI). **Now** (this is the difference between a Head Grower and a
  reactive dashboard — it is the product's whole thesis).
- **The uncertainty contract is under-specified.** The planner can only price latency/stakes if
  the Brain emits *horizon* and *irreversibility*, not just confidence. RFC-004 lists
  `(subject, latent, confidence, stakes, decisiveness, time-window)` but doesn't make
  irreversibility/horizon explicit.
  *Smallest fix:* add **irreversibility** and **horizon** to the uncertainty record. **Now**
  (it's the linchpin interface between the two planes).

## 4. Long-term maintainability — **[Structural]**

- **A 20-year universal contract with no versioning.** The Canonical Observation and the
  capability schema will evolve; there is no stated version/compat rule. One day a field changes
  and a decade of stored observations becomes ambiguous.
  *Smallest fix:* add a **schema version** to observations and capabilities, and a
  backward-compatibility rule (additive-only; deprecate, never repurpose). **Now** (retrofitting
  versioning onto years of data is the classic unfixable mistake).
- **High-dimensional observations strain "one value + confidence."** A thermal frame, a point
  cloud, a hyperspectral scan, a genomic assay don't fit a scalar value. The envelope allows a
  media reference, but the *semantics* of derived features are unstated.
  *Smallest fix:* state the rule **raw media are referenced; the Brain reasons on derived-feature
  observations that `chain` back to the media** (pixels never reach the Decision Engine). **Now**
  (contract clarity; cheap).

## 5. Extensibility — **[Structural]**

- **No ontology governance for `kind`.** If observation kinds are free-form, two observers or two
  greenhouses name the same thing differently and fusion/reasoning fragment; if fixed, new
  sensors can't speak. This is the snapshot spec's open question #1, unresolved and now load-
  bearing at fleet scale.
  *Smallest fix:* a **stable core ontology + namespaced extensions + an alias/mapping registry**.
  **Now** (it is the interoperability backbone; the cost of divergence compounds per site).

## 6. Failure modes — **[Operational + one Structural]**

- **Observation storms / feedback oscillation.** An observation changes an inference, which
  creates a new uncertainty, which triggers another observation… the loop has no stated damping
  beyond a per-cycle threshold. *(Structural)*
  *Smallest fix:* a **per-uncertainty observation budget + cool-down + diminishing-returns stop**.
  **Now** (a one-paragraph rule prevents pathological loops and runaway cost).
- **Trust poisoning / systematically bad observer.** Corroboration handles a single faulted
  sensor; it does not handle a systematically biased or adversarial observer whose trust lags
  reality. *(Operational)*
  *Smallest fix:* **require corroboration for high-stakes decisions resting on a single
  low-history observer**; add outlier detection later. **Now** state the rule; **postpone** the
  detector.
- **Dangling sessions.** A tasked observer goes offline; the result never returns. *(Operational)*
  *Smallest fix:* **session timeout → re-plan**. **Postpone** (implementation), but name it now.

## 7. Distributed systems — **[Core-adjacent — the biggest real gap]**

- **The RFC is written as if synchronous and single-node.** Thousands of greenhouses, observers
  across flaky networks, cloud+edge. Three concrete breaks:
  1. **Clock skew is real and we have already seen it** (Synopta controller vs PC differed by an
     hour). A Snapshot "at a moment in time" cannot assume coherent `captured_at` across observers.
  2. **The Snapshot is presented as an atomic assembly** but observations arrive asynchronously;
     it is really an **eventually-consistent projection**.
  3. **Where does the planner run?** Unspecified. If central/cloud, it is a SPOF and needs
     connectivity greenhouses don't reliably have.
  *Smallest fix (all three):* declare the architecture **edge-first**: the planner runs **per
  site** and **degrades to local human-only logic when disconnected**; the Snapshot is an
  **eventually-consistent projection**; every observation records its **clock source**, and the
  system **never assumes global order**. **Now** (these are framing sentences that change how the
  whole thing is built; retrofitting distribution is a rewrite).

## 8. Robotics — **[Core-adjacent]**

- **"Read-only observer" breaks the moment a robot must *move or touch to observe*.** A drone
  flying, a humanoid lifting a leaf to see beneath it — these are physical actions performed *in
  order to* observe. Modeling such an agent as a stateless "returns observations" box hides
  navigation, battery trajectory, collision avoidance, and safety.
  *Smallest fix:* split the concern — the **Planner tasks intent (what/why)**; the **Observer
  adapter owns execution and safety (how)**; and distinguish **observation-incidental actuation**
  (movement within a safety envelope, part of observing) from **intervention actuation** (changing
  the greenhouse — the deferred Actor). **Now** (the observe/act line is conceptual and load-
  bearing; getting it wrong invites either paralysis or unsafe action).

## 8b. Autonomous actuation (the deferred Actor) — **[Structural]**

- **The optimization frame models soft trade-offs, not hard constraints.** EVI − cost is fine for
  "ask or stay silent." It is *unsafe* for actuation and even for risky observation (a drone near
  people): some things must **never** happen regardless of value.
  *Smallest fix:* introduce a **hard-constraint filter** (safety, quiet hours, budget caps,
  permissions) applied **before** optimization, distinct from costs. **Now** for observation
  (drones/robots already need it); the full Actor stays **postponed**.

## 9. AI evolution — **[Structural]**

- **The design bets on legible hand-weighted VoI for 20 years.** That is right for trust today
  and wrong as a permanent bet: a future learned value function may plan better. Conversely, if a
  model is dropped into the planner casually, it will smuggle biology in (the leak ADR-003 guards).
  *Smallest fix:* put the planner's **value function behind an interface** — transparent heuristic
  now, replaceable by a learned/auditable model later — with **explainability required** (every
  request must state why). **Now** (one interface sentence preserves both ADR-003 and future
  optionality). The Brain↔Planner contract (uncertainties in, observations out) is already
  model-agnostic — keep it.

## 10. Future hardware / sensors — **[Operational]**

- **Streams don't fit "discrete fact."** Continuous video and 1 Hz × 1000 sensors will swamp a
  fact-per-observation model if piped raw.
  *Smallest fix:* state that **observers summarize streams into observations at the edge**; the
  Brain consumes derived observations, never raw streams. **Now** (contract clarity); volume
  handling **postpone**.

## 11. Multiple greenhouses — **[Structural]**

- **Site isolation forfeits fleet learning.** Per-site trust registries are right for privacy and
  blast-radius, but a sensor model's calibration or a disease pattern learned at one site should
  inform others. The RFC gives isolation with no fleet tier.
  *Smallest fix:* **two-tier knowledge** — site-local trust + a shared **observer-class prior**
  learned across the fleet (federated; raw site data stays local). **Now** state the two tiers;
  **postpone** the federation mechanics. (Also flag multi-tenant data isolation as a first-class
  requirement.)

## 12. Multiple growers — **[Operational]**

- **The human is modeled as one trusted entity.** Real sites have several growers, shifts,
  different skill, and humans who disagree.
  *Smallest fix:* humans are **plural first-class observers with individual trust profiles**;
  human–human conflict uses the same fusion (trust-weighted, disagreement → uncertainty); the
  planner chooses *which* human to interrupt (right person, right question, right moment). **Now**
  (cheap — the model already supports many observers; just say humans are many, not one).

## 13. Conflicting observations — **[Core-adjacent]**

- **Trust-weighted fusion can launder truth into a blurred average.** When a sensor says "dry"
  and a grower says "wet," averaging is *wrong* — one is right, or they measure different scales.
  Numeric fusion of categorical/biological signals can hide the real signal.
  *Smallest fix:* for categorical/biological conflicts, **do not average** — raise uncertainty and
  treat the conflict itself as a **high-EVI trigger for a tie-breaking observation**. **Now**
  (state the rule; it changes fusion behavior and aligns with "the plant is ground truth").

## 14. Autonomous observation — **[Structural]**

- **Autonomy without governance becomes nuisance or hazard.** Unbounded self-tasking over-
  observes, costs money, annoys, flies drones unsafely.
  *Smallest fix:* a **policy/governance layer** (budgets, quiet hours, safety envelopes, rate
  limits, **human veto**) the planner must obey, separate from its value function. **Now** (the
  guardrail that makes autonomy trustable; trivial to specify, essential to the product).

## 15. Human factors — **[Structural]**

- **The design optimizes interruption cost but not the *relationship*.** Constant autonomous
  observers can feel like surveillance; growers may defer and **deskill**; alarm/ask fatigue
  erodes trust; "why is the drone flying / why am I being asked?" must always be answerable.
  *Smallest fix:* require **per-request explainability**, a grower-controlled **autonomy level**
  (from "ask me everything" to "act and tell me"), and an explicit design goal of **growing**
  grower skill, not replacing it. **Now** (these are principle-level requirements — "trust before
  automation," "calm and honest" — and belong in the contract, not as afterthoughts).

---

## X. The "fix now" set (conditions for ADR-005)

Eight amendments, all framing/contract sentences, none touching the core invariant:

1. **Edge-first + eventually-consistent** Snapshot; planner per site; degrade to local logic
   offline; record clock source; never assume global order. (§7)
2. **Horizon-aware, prevention-weighted value** + monitoring-cadence floor for known risks; add
   **irreversibility + horizon** to the uncertainty contract. (§3)
3. **Hard-constraint/governance layer** (safety, quiet hours, budgets, permissions, human veto)
   applied before optimization. (§8b, §14)
4. **Schema versioning + additive-only compatibility** for observations and capabilities. (§4)
5. **Core ontology + namespaced extensions + alias registry** for `kind`. (§5)
6. **Conflict rule:** don't average categorical biology; conflict is a tie-break trigger. (§13)
7. **Tier the concepts** (minimal built contract; Cost/Latency/Availability/Quality/Trust as
   attributes); **trust as running statistic**; **streams summarized at the edge**. (§1, §2, §10)
8. **Observe/act boundary** (incidental vs intervention actuation; adapter owns execution+safety)
   and **per-request explainability + autonomy level**. (§8, §9, §15)

**Postpone (named, not built):** routing optimization, the federation mechanism, outlier/anti-
poisoning detection, session-timeout/retry, the full Actor for intervention actuation.

---

## The final question

**"If Gaia becomes the world's operating system for biological production, would the Observer
Network still be the correct architecture?"**

**Yes — and more so at world scale than at one greenhouse — provided the eight amendments land.**

Why it is right, stated as plainly as I can while trying to disprove it:

- **The thing it makes invariant is the thing that lasts.** Observers, vendors, sensors, robots,
  and AI models will all change many times in twenty years. *Reality being observed by
  interchangeable observers, and intelligence consuming canonical observations rather than
  observers,* is the one relationship that does **not** change. Betting the architecture on that
  invariant — and on biology, not hardware, as the subject — is betting on the only constant.
- **Every attack I could mount was absorbed without touching the core.** Distribution, robotics,
  AI evolution, fleet learning, conflicting humans — each needed a *refinement at the edges*
  (how observations are assembled, governed, valued, versioned), not a change to "observers are
  interchangeable; the Brain is observer-blind; tasking is separate from reasoning." An
  architecture whose core can swallow its own critiques is, by definition, the right core.
- **The durability tests scale.** "If DJI disappears, does Gaia work? If a humanoid appears, can
  Gaia use it without changing the Brain?" Both answers stay *yes* whether there is one greenhouse
  or a million, because they follow from the invariant, not from any current observer.

Where it would be **wrong** — and would need redesign, not amendment — is only if a future world
made the core invariant false: if intelligence had to be **fused with** specific observers to
work (e.g. an end-to-end model that cannot separate perception from reasoning and outperforms any
separable design by a margin that matters). I judge that unlikely for *biological* production,
where auditability, trust, safety, and the plant-as-ground-truth demand exactly the separation
this architecture enforces. If that world arrives, the contract (uncertainties in, observations
out) is the clean seam at which to re-evaluate — so even the exit is designed.

## Recommendation

**Promote to ADR-005 — conditionally:** fold the eight "fix now" amendments into RFC-004 first
(they are additive clarifications, reviewable in one pass), then promote. Do **not** promote the
RFC as currently written: it would enshrine a synchronous, greedy, unconstrained reading that the
next twenty years would punish. With the amendments, it is sound enough to build a decade on.

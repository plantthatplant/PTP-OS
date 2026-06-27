# Biological Model

> **A core design document.** This document does not describe software. It
> describes **how PTP OS understands plants** — the biological concepts the system
> reasons with. Everything technical (the Context, Decision, and Language engines,
> the domain model, the providers) exists to serve the understanding described
> here. When software design and this document disagree, this document wins. That
> is what "biology before technology" means in practice.
>
> Status: v1 · written in Sprint 0 as a foundation for all later reasoning work.

## How to read this document

PTP OS does not "control a greenhouse." It cares for **living organisms** that
grow, sense, strain, recover, and respond on their own biological timescales. A
greenhouse is merely the set of levers we have to influence them. The concepts
below are the vocabulary of plant care: what we are actually trying to understand
and improve.

Each concept is described in four parts, deliberately and consistently:

1. **What it means biologically** — the plant science, in plain terms.
2. **How AI should reason about it** — the stance PTP OS should take (not code).
3. **Which observations influence it** — what evidence updates our understanding.
4. **Which recommendations can affect it** — the levers that change it.

A note used throughout: most of these properties are **latent** — they cannot be
measured directly. We never *see* "stress" or "growth potential"; we *infer* them
from observable signs. PTP OS should therefore treat them as estimates that are
always provisional, always carrying confidence and uncertainty (the last two
concepts), and always improvable as more is observed.

The biological concepts map to entities in the [domain model](../domain/) —
especially [Observation](../domain/observation.md),
[Climate Reading](../domain/climate-reading.md),
[Recommendation](../domain/recommendation.md),
[Decision](../domain/decision.md), and [Memory](../domain/memory.md) — but the
concepts come first; the entities are how we record them.

---

## 1. Plant State

**What it means biologically.** Plant State is the integrated, current physiological
condition of a plant or batch: its vigor, turgor (water status), photosynthetic
activity, structural sturdiness, and freedom from damage or disease. It is the
"how is this plant actually doing, right now" summary that an experienced grower
forms at a glance — the synthesis of many signals into one judgment. It is not a
single number; it is a condition with several dimensions that usually move
together but can diverge (a plant can be growing fast yet structurally weak).

**How AI should reason about it.** Treat Plant State as a **latent variable
estimated from evidence**, never as something directly read from a sensor. Maintain
a current best estimate per batch (and per plant where it matters), acknowledging
that a batch is heterogeneous — the estimate describes a distribution, not a clone.
State should be expressed in biological terms ("turgid, vigorous, slightly
hardened") rather than as a raw score, and every estimate should be defensible by
pointing to the observations behind it. State is the anchor most other reasoning
hangs from: stress, recovery, and growth potential are all read relative to it.

**Which observations influence it.** Visual signs (leaf color, gloss, turgor,
presence and quality of new growth, internode length), growth measurements (height,
leaf count, mass), the recent climate context the plant has experienced, and any
pest or disease findings. Human notes count as observations of equal standing to
sensors.

**Which recommendations can affect it.** Nearly all of them — climate adjustments,
irrigation and nutrition changes, spacing, pest/disease intervention. The point of
almost every recommendation is to move Plant State toward the
[Biological Goals](#8-biological-goals) for its stage.

---

## 2. Growth Stage

**What it means biologically.** Growth Stage is the plant's developmental phase —
for our production, roughly: cutting/propagation, rooting and establishment,
vegetative growth, generative/finishing, and ready/hardening for dispatch. Each
stage has **different needs and different vulnerabilities**. A freshly stuck cutting
needs high humidity and gentle light to avoid desiccation before it has roots; a
finishing plant needs cooler, firmer conditions to build sturdiness. The plant's
biology changes what "good" even means.

**How AI should reason about it.** Stage must be **context for every other
judgment**: the same Climate Reading or symptom means different things at different
stages. PTP OS should track each batch's stage, the expected timeline for that
stage (by species), and whether the batch is ahead, on track, or behind. It should
reason about **stage transitions** as significant events (e.g. moving from
propagation to vegetative), and recognize that targets, tolerances, and risks all
shift at those boundaries. Stage is also the backbone of scheduling and of
connecting biology to commerce (when a batch will be ready for an
[Order](../domain/order.md)).

**Which observations influence it.** Time since propagation, root development,
leaf/node count, height, branching, onset of flowering or other generative signs,
and overall morphology relative to species norms.

**Which recommendations can affect it.** Stage-transition decisions (declare a
batch moved to finishing), stage-appropriate climate setpoint changes, hardening
regimes, timing of taking cuttings from mother plants, and declaring a batch ready
to ship.

---

## 3. Stress

**What it means biologically.** Stress is the physiological strain a plant
experiences when conditions exceed its capacity to cope — too hot or cold, too dry
or waterlogged, too much or too little light, nutrient imbalance, or biotic
pressure (pests, pathogens). Crucially, stress exists on a spectrum: **mild,
transient stress can be harmless or even beneficial** (a controlled stress firms up
a finishing plant), while **sustained or severe stress causes damage** that may be
reversible or permanent. Plants show stress through stomatal closure, wilting, leaf
temperature changes, discoloration, stalled growth, and abscission.

**How AI should reason about it.** The goal is **early detection and correct
attribution**. PTP OS should aim to catch sub-clinical stress — strain that is
present before it is obvious — by reading combinations of signals (e.g. high VPD
plus rising leaf temperature plus slowed growth). It must distinguish **transient
from sustained** stress (a midday wilt that recovers by evening is not the same as
chronic water stress), estimate **severity and reversibility**, and attribute
stress to its likely **driver** so the right lever is pulled. It should also weigh
whether a stressor is acceptable for the stage (deliberate hardening) versus
harmful. Over-reacting to normal transient strain is itself a failure mode.

**Which observations influence it.** Climate excursions outside target ranges, VPD
and leaf-temperature signals, visible wilting or color change, growth-rate
slowdown, and pest/disease observations. Recent history matters: duration of an
excursion is as important as its magnitude.

**Which recommendations can affect it.** Corrective climate moves (cooling,
heating, humidification, ventilation), shading or supplemental lighting changes,
irrigation adjustments, and removing biotic stressors via pest/disease
intervention.

---

## 4. Recovery

**What it means biologically.** Recovery is the plant's return toward a healthy
state after a stressor is removed or damage is sustained. It is governed by
biology, not by us: it **takes time, often lags behind the corrected condition, and
may be only partial**. A wilted plant rehydrates in hours; tissue scorched by heat
or light does not un-scorch — the plant must grow past the damage over days or
weeks. Resilience (the capacity to recover) depends on the plant's prior state,
stage, and the severity of the insult.

**How AI should reason about it.** PTP OS should reason about a **recovery
trajectory and its timescale**, and set realistic expectations rather than
expecting instant improvement once conditions are fixed. A key principle is to
**avoid over-correction and intervention whiplash**: stacking new changes on top of
a recovering plant can do more harm than patience. The system should monitor
whether recovery is actually occurring (are stress indicators trending the right
way?) and escalate only if it is not. Recovery reasoning is also where
[Memory](../domain/memory.md) earns its keep: how this species/batch recovered from
similar insults before informs what to expect now.

**Which observations influence it.** The trend (not just the level) of previously
elevated stress indicators, resumption of healthy new growth, restored turgor, and
stabilizing growth rate over successive observations.

**Which recommendations can affect it.** Holding **stable, gentle conditions**;
explicitly *not* intervening further (a valid recommendation); supportive nutrition;
and time itself — a recommendation may be "wait and re-observe in N days."

---

## 5. Growth Potential

**What it means biologically.** Growth Potential is the plant's capacity for future
growth given its genetics, stage, current state, and available resources. Biology
sets a ceiling (a species and stage can only grow so fast and so well), and the
**most limiting factor** determines how much of that ceiling is reached — light,
CO₂, water, nutrients, temperature, or space (Liebig's law of the minimum: the
scarcest resource caps the outcome, no matter how abundant the others). A healthy
plant in good conditions has headroom; a stressed or resource-limited plant does
not.

**How AI should reason about it.** Reasoning here is about **opportunity, not
problems**. PTP OS should estimate achievable growth under the current trajectory
versus what is possible, and **identify the limiting factor** — the one change that
would unlock the most growth. It should think in terms of source–sink balance
(enough light/CO₂ to supply growth, enough sink capacity to use it) and avoid
pushing growth the plant cannot structurally support (fast, soft, weak growth is
not the goal). Growth Potential is what turns PTP OS from reactive (fix stress) to
proactive (realize potential), always bounded by the [Biological
Goals](#8-biological-goals).

**Which observations influence it.** Current vigor and Plant State, stage, light
levels (and CO₂ where measured), spacing/density, and species norms for the stage.

**Which recommendations can affect it.** Acting on the limiting factor — adjusting
light or CO₂, optimizing nutrition, re-spacing benches to reduce competition, or
climate tuning to widen the favorable window — without compromising sturdiness.

---

## 6. Disease Risk

**What it means biologically.** Disease (and pest) risk is the likelihood of onset
or spread, governed by the **disease triangle**: a susceptible host, the presence of
a pathogen or pest, and an environment that favors it — all three must coincide.
Many greenhouse diseases are driven by environment: high humidity, prolonged leaf
wetness, condensation, and poor airflow create conditions for fungal and bacterial
disease; warmth and dryness favor certain pests like spider mites. Risk is dynamic
and **spatial** — it spreads from plant to plant and bench to bench.

**How AI should reason about it.** The stance is **predictive and preventive**, not
merely reactive. PTP OS should continuously assess whether conditions are becoming
conducive to known risks for the current crop and stage, raise risk *before*
symptoms appear, and reason about **contagion** — if a pest is seen on one bench,
neighboring batches are now higher-risk. It should fold in
[Memory](../domain/memory.md) (this zone has a history of mildew in these
conditions) and balance the cost of preventive action against the cost of an
outbreak, consistent with "build trust before automation" (recommend scouting and
prevention, escalate to intervention with evidence).

**Which observations influence it.** Humidity and leaf-wetness duration,
temperature, airflow/ventilation status, direct pest or disease sightings,
crop susceptibility by species/stage, and prior outbreak history from memory.

**Which recommendations can affect it.** Lowering humidity and improving airflow,
adjusting irrigation timing to avoid prolonged leaf wetness, preventive biological
controls, isolating or moving affected batches, and scheduling **scouting tasks**
to convert uncertainty into observation.

---

## 7. Environmental Response

**What it means biologically.** Environmental Response is the relationship between
the conditions a plant experiences and how its physiology reacts — the plant's
"transfer function" from environment to biology. Photosynthesis responds to light,
CO₂, and temperature along **non-linear curves with optima and saturation points**;
transpiration tracks VPD; growth and morphology respond to the integral of
conditions over time, with **lags and acclimation** (a plant adjusts to a sustained
change rather than responding instantly). The same nudge produces different
responses depending on stage, prior conditioning, and current state.

**How AI should reason about it.** This is the concept where PTP OS most needs to
**learn rather than assume**. Generic species response curves are a starting point,
but the real response of *this* crop, in *this* greenhouse, should be learned from
paired observations of conditions and outcomes over time. PTP OS should reason
that responses are **dynamic, lagged, and non-linear** — avoiding the naive
assumption that hitting a setpoint instantly produces the desired biological
effect — and should prefer **gradual, ramped changes** the plant can acclimate to
over abrupt swings. Environmental Response is the natural home of the learning loop
discussed in [RFC-001](../rfc/RFC-001-feedback-and-learning-loop.md): linking past
[Decisions](../domain/decision.md) to their biological outcomes is exactly how
these response relationships are refined.

**Which observations influence it.** Time-aligned pairs of [Climate
Readings](../domain/climate-reading.md) and plant responses (growth, turgor, color,
stress indicators), accumulated across days and batches; outdoor
[Weather](../domain/weather.md) as external context.

**Which recommendations can affect it.** Setpoint tuning informed by the learned
response, ramping changes gradually, and choosing the timing of changes to match
the plant's daily and developmental rhythms.

---

## 8. Biological Goals

**What it means biologically.** Biological Goals define what "good" means for the
plant, in biological terms, given commercial intent. The goal is almost never
**maximum growth**; it is a **healthy, sturdy, high-quality, resilient plant that is
ready at the right time**. These objectives can conflict: pushing for speed can cost
sturdiness; maximizing size can delay readiness or reduce quality. Good growing is
the deliberate balancing of these goals for each species and stage.

**How AI should reason about it.** Biological Goals are the **objective function**
for all of PTP OS's reasoning — the target every Plant State estimate is compared
against and every recommendation is justified by. PTP OS should reason about goals
as **multi-objective and stage-specific** (quality, timing, resilience, resource
efficiency), make trade-offs **explicit** rather than silently optimizing one
dimension, and tie biological goals to commercial reality (a batch reserved for an
[Order](../domain/order.md) has a hard readiness date). Because goals are the
yardstick, they must be stated clearly enough that a recommendation can always
answer "which goal does this serve, and at what cost to the others?"

**Which observations influence it.** Quality indicators measured against species
and market standards (sturdiness, form, color, size), readiness relative to
schedule, and resource cost (energy, inputs) of getting there.

**Which recommendations can affect it.** All recommendations are, ultimately, means
of moving the plant toward its Biological Goals; the document's value is that each
one should name the goal it advances and the trade-off it accepts.

---

## 9. Confidence

**What it means biologically.** Confidence is not a property of the plant — it is a
property of **PTP OS's claim about the plant**. Because every biological assessment
above is inferred from incomplete evidence, each one is more or less trustworthy
depending on the evidence behind it. A state estimate built on fresh, corroborated,
high-quality observations deserves more confidence than one built on a single stale
reading.

**How AI should reason about it.** **Every estimate and every recommendation should
carry an explicit confidence**, derived from the quantity, quality, recency, and
consistency of supporting evidence, and from whether [Memory](../domain/memory.md)
corroborates it. Confidence must be **communicated honestly** to the grower, never
hidden behind false certainty. It should also **gate action**: higher-stakes or
less reversible recommendations require higher confidence, and this is the
mechanism behind "build trust before automation." When confidence is low, the
right output is often to **recommend gathering more evidence** (a scouting or
measurement task) rather than to act.

**Which observations influence it.** Sensor reliability and calibration,
observation recency and spatial coverage, agreement among independent signals
(sensor + human + camera), and historical accuracy of similar past assessments.

**Which recommendations can affect it.** Recommendations that **increase evidence** —
scouting, additional measurements, closer monitoring — raise confidence; acting
without resolving low confidence should be reserved for low-regret, reversible
moves.

---

## 10. Uncertainty

**What it means biologically.** Uncertainty is the broader space of what PTP OS does
not and sometimes cannot know. It has two roots: **irreducible biological
variability** (plants differ, biology is noisy — aleatoric uncertainty) and
**incomplete knowledge** (gaps in observation or in our understanding of the
response — epistemic uncertainty, which more data can reduce). Confidence is about a
*specific claim*; uncertainty is the *general unknown* surrounding the whole
picture. The two are related but distinct: you can be confident about a
well-evidenced fact while large uncertainty remains about the system as a whole.

**How AI should reason about it.** PTP OS should **represent uncertainty
explicitly** rather than collapsing to a single confident answer, and let it shape
behavior: under high uncertainty, **prefer reversible, low-regret actions**, stage
interventions, and re-observe — rather than making large, hard-to-undo changes.
Uncertainty should **grow with time** since the last relevant observation and with
variance across a batch, and **shrink when we observe**. The system should avoid
**false precision** (a confident-sounding recommendation built on thin evidence is
a trust hazard) and should make uncertainty a first-class part of how it explains
itself: "here is what I think, here is how sure I am, and here is what I don't yet
know."

**Which observations influence it.** Coverage gaps (un-sensed zones, un-scouted
benches), variance among plants in a batch, conflicting signals, and elapsed time
since the last observation of a subject.

**Which recommendations can affect it.** Recommendations that **acquire information**
(scouting, measurement, imaging) directly reduce uncertainty; choosing conservative,
reversible, staged actions is how PTP OS acts *well* while uncertainty remains.

---

## Why PTP OS should optimise plant health, not greenhouse conditions

This is the most important design commitment in this document, and the reason it
exists.

It is tempting to define success as **keeping the greenhouse at target
conditions** — hold temperature, humidity, CO₂, and light at their setpoints and
declare victory. PTP OS deliberately rejects this as its objective. Greenhouse
conditions are **means, not ends.** They are some of the levers we have; they are
not what we are trying to produce. What we are trying to produce is **healthy,
high-quality plants delivered on time.** Optimising the levers instead of the
outcome is optimising a proxy — and proxies mislead.

Several reasons make this concrete:

**The plant is the integrator, and it is the source of truth.** A plant's condition
reflects everything acting on it — climate, water, nutrition, pests, handling,
genetics, and history — integrated over time. Conditions that look perfect on a
dashboard can still yield poor plants (because of a factor the dashboard doesn't
show), and imperfect-looking conditions can yield excellent plants. If we optimise
to the dashboard, we are flying by our instruments while ignoring the patient.

**The same conditions are not equally good for every plant.** As Growth Stage,
Environmental Response, and Biological Goals make clear, the "right" condition
depends on stage, species, current state, and prior conditioning. A fixed setpoint
is, at best, right for one plant at one moment. Optimising conditions assumes a
universal optimum that biology does not provide; optimising plant health adapts to
the plant in front of us.

**Conditions are one input among many.** Climate is not the only thing that
determines plant health — irrigation, nutrition, pest pressure, spacing, and
handling all matter, and several of these are not "greenhouse conditions" at all. A
system organised around conditions structurally under-weights everything else; a
system organised around plant health naturally weighs all of them, because they all
show up in the plant.

**Optimising conditions risks "teaching to the test."** If the objective is to hit
setpoints, PTP OS would learn to hit setpoints — even when doing so does not help,
or actively harms, the plant (e.g. fighting a transient excursion that the plant
would shrug off, at real energy cost). Optimising plant health keeps the system
honest: an action is only good if the *plant* is better for it.

**It is the only objective that lets the system truly learn.** The learning loop
(see [Memory](../domain/memory.md) and
[RFC-001](../rfc/RFC-001-feedback-and-learning-loop.md)) only produces wisdom if the
thing we measure outcomes against is the thing we actually care about. Learning
"which conditions kept the room on setpoint" is worthless; learning "which decisions
produced healthier plants" compounds into genuine greenhouse intelligence.

**It keeps PTP OS independent of any provider or sensor.** Reasoning about plant
health — a biological reality — rather than about a particular vendor's climate
readings reinforces the architecture's core stance (see
[ADR-002](../adr/ADR-002-provider-abstraction.md) and
[ADR-003](../adr/ADR-003-business-logic-independent-from-ai.md)). Sensors and
providers come and go; the plant remains the subject.

In short: **greenhouse conditions are how we help; plant health is what we are
helping.** PTP OS treats conditions as adjustable levers in service of an objective
defined entirely in terms of the living plant. Every concept in this document
exists to keep that objective in view — to understand the plant well enough, and
honestly enough about our own confidence and uncertainty, to make it healthier over
time.

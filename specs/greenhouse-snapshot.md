# Spec — The Greenhouse Snapshot

**Status:** Draft v1 · a fundamental specification (for review before implementation).
**Related:** [`specs/greenhouse-provider.md`](greenhouse-provider.md),
[`adr/ADR-002-provider-abstraction.md`](../adr/ADR-002-provider-abstraction.md),
[`docs/biological-model.md`](../docs/biological-model.md),
[`docs/decision-philosophy.md`](../docs/decision-philosophy.md) (evidence, confidence,
absence), [`domain/observation.md`](../domain/observation.md),
[`domain/climate-reading.md`](../domain/climate-reading.md).

> This spec defines a **structure and its meaning**, not software. The illustrative shapes
> below are for clarity, not a commitment to a format or language.

## 1. Purpose

The Greenhouse Snapshot is the **single, canonical description of greenhouse reality at a
moment in time.** Every way we ever acquire data — a Synopta API, a Claude browser
extraction, a CSV import, a grower's spoken note, a camera, a weather feed — produces
*exactly this structure*. Nothing downstream (the Context Engine, the reasoning, the
Brain) knows or cares which acquisition method produced it.

It exists so that the value PTP OS builds rests on **reality, not on any source of reality.**
Sources come and go; the greenhouse remains. The Snapshot is how the greenhouse speaks to
the system in one stable, source-independent voice.

It is the *normative target* of every Provider (see the Provider spec): a Provider's job is
to turn whatever it has into a Greenhouse Snapshot. This document defines what that
Snapshot is.

## 2. Philosophy

Ten principles. They are the spec; the fields are downstream of them.

1. **It describes the greenhouse, not a sensor or a vendor.** Read on its own, a Snapshot
   should be intelligible to a grower who has never heard of Synopta or Dispatch. It is the
   greenhouse's reality, written down.
2. **Observation, not interpretation.** A Snapshot records *what was observed* — a
   temperature, a wilted leaf, a closed vent, a few spots on a leaf. It does **not** record
   what those mean. Plant State, Stress, Disease Risk, Growth Potential are **latent** and
   are *inferred downstream* by the engines (see the Biological Model); they never live in a
   Snapshot. The Snapshot is evidence; the meaning is derived from it.
3. **Every datum carries its provenance and its confidence.** There are no bare numbers. A
   value is always wrapped with *where it came from, when it was true, how it was obtained,
   and how much to trust it.* This wrapper (§4) is the heart of the design.
4. **Absence is first-class and honest.** Missing is not zero, and not an error. A Snapshot
   states plainly what it does *not* know — un-sensed zones, un-scouted benches, stale
   values — and never fabricates to fill a gap (§10).
5. **Source-agnostic and substitutable.** Any acquisition method yields the same structure,
   so one can replace another with no change above the Provider Layer (ADR-002).
6. **Partial and progressive.** Completeness is a spectrum, not a requirement. A Snapshot
   may carry only climate, or only one human note, or only a camera frame, and still be
   valid and useful. A leaner Snapshot yields leaner reasoning — honestly — not an error.
7. **Time lives on the datum, not just the Snapshot.** The values in a Snapshot were
   captured at *different* moments. Each carries its own capture time; the Snapshot carries
   the time it was *assembled* (§7).
8. **Canonical units and identifiers.** All values are normalised to the domain's canonical
   units and stable PTP OS identifiers at the boundary. A Snapshot never carries a vendor's
   field names, units, or ids.
9. **A Snapshot is an immutable record of a moment.** It is not edited; a correction or a
   later reading is a *new* Snapshot (or a new observation). This keeps the past honest and
   makes the learning loop auditable.
10. **Human observations rank equal to instruments.** A grower's "the canopy is still wet"
    is a first-class observation, carried and weighted like any sensor reading (Biological
    Model). The Snapshot is not a sensor dump; it is everything observed, by anyone or
    anything.

## 3. What the Snapshot is — and is not

**It is:** a point-in-time, provenance- and confidence-bearing collection of *observations*
about one greenhouse and its surroundings, plus the structural context those observations
attach to.

**It is not:**
- not an interpretation (no latent biology, no scores like "stress = 0.7");
- not a recommendation or a decision;
- not vendor-shaped (no Synopta/Dispatch concepts);
- not required to be complete;
- not a database schema — it is a meaning, which a schema may later serve.

## 4. The observation envelope — the universal unit

Everything in a Snapshot that asserts something about reality — a climate reading, an
equipment state, a pest sighting, a growth measurement, a weather value — shares one spine.
This is what makes the Snapshot uniform across wildly different sources.

An **observation** carries:

| Field | Meaning | Required? |
| --- | --- | --- |
| **subject** | what it is about: the greenhouse, a zone, a bench, a batch, a plant, or a piece of equipment — referenced by stable id and its place in the hierarchy | required |
| **kind** | what is being observed (e.g. air-temperature, humidity, vent-position, leaf-wetness, pest-sighting, plant-height, outside-temperature) | required |
| **value** | the observed value — quantitative (with **unit**), categorical (e.g. `open`/`closed`, `active`/`clear`), textual (a human note), or a **reference to media** (an image/clip) | required *or* an explicit absence (§10) |
| **unit** | canonical unit, when the value is quantitative | required if quantitative |
| **captured_at** | when this observation was true / taken (UTC) | required |
| **source** | provenance — what produced it (a sensor, a person, a camera, a model, an import), abstracted from any vendor | required |
| **method** | how it was obtained: `measured`, `observed-by-human`, `derived`, `vision-inferred`, `imported`, `forecast` | required |
| **confidence** | how much to trust this observation, and ideally why (§9) | required |
| **notes / verbatim** | free text; for human observations, the original words preserved exactly | optional |

This envelope is why a temperature from an API and a grower's spoken note can sit side by
side in one structure and be reasoned about consistently. A quantitative climate reading is
simply an observation whose `kind` is a climate metric and whose `method` is `measured`.

## 5. Structure of a Snapshot

A Snapshot has a small envelope and then the observations, grouped by what they describe.

```
GreenhouseSnapshot
├── identity & time          (which greenhouse; when assembled)   ── required
├── provenance summary       (which sources contributed)          ── required
├── coverage                 (what is present vs known-absent)     ── required
├── structure                (greenhouse → zones → benches; the layout observations attach to)
├── environmental state      (the conditions the plants experience)        — observations
├── equipment state          (the levers and their positions; alarms)      — observations
├── biological observations  (observed signs from/about the plants)        — observations
└── external context         (weather, energy — the surroundings)          — observations
```

The four content groups are just **views over a set of observations**, organised by subject
and kind. The same envelope (§4) underlies every entry in all four.

### 5a. Environmental state — what the plants experience
The conditions in the growing space: air temperature, relative humidity, CO₂, light
(intensity and, where known, the day's accumulation), air movement, and surface/leaf
temperature where available. Derived quantities a grower reasons in — **VPD**, **dew
point** — may be included as observations with `method: derived`, provided their derivation
is transparent and they carry the confidence of their inputs. Canonical units (e.g. °C,
%RH, ppm, µmol·m⁻²·s⁻¹, kPa). Each value is located in the hierarchy (usually per zone).

### 5b. Equipment state — the levers
The state of the apparatus that *causes* the environment: vents (position), screens
(drawn/open), heating (pipe temperature / demand), fans, irrigation valves and recent
irrigation events, supplemental lighting, CO₂ dosing — and **alarms** raised by the control
system. Equipment state is kept distinct from environmental state because one is the *cause*
and the other the *effect*: a closed vent (equipment) and high humidity (environment) are
two different observations, and the reasoning needs both. An alarm is an observation whose
`kind` is `alarm` with a category and text; it does not, by itself, assert what is wrong —
it is a signal to be weighed.

### 5c. Biological observations — observed signs, never inferred state
What was actually *seen* about the living plants — by a grower, or by a camera. For example:
leaf colour and gloss, turgor or wilting, the quality and spacing of new growth, root
condition, visible lesions or pests, growth measurements (height, leaf/branch count),
flowering or other phenological signs, tone, and readiness notes. These may be quantitative
(a measured height), categorical (`wilted`/`turgid`), textual (a grower's sentence,
verbatim), or a media reference (a leaf photo). **Crucially, these are observations, not
conclusions:** the Snapshot records "a few brown spots on lower leaves, bench 3", *not*
"disease risk high." The leap from sign to meaning is the engines' job, downstream, and is
where confidence and uncertainty about the *plant* are formed. Biological observations are
sparse and irregular by nature, and the Snapshot must represent that without penalty
(§6, §10).

### 5d. External context — the surroundings
Conditions outside the grower's direct control that nonetheless act on the crop: **weather**
(outside temperature, humidity, solar radiation, wind, precipitation — current and, as
distinct observations with `method: forecast`, predicted), and **energy** (price,
consumption, supply events). These describe the greenhouse's environment-of-the-environment
and are carried as observations like any other, located at the greenhouse (or site) level.

### 5e. Structure — the frame
The layout the observations hang on: the greenhouse, its zones, and its benches, by stable
id and containment (greenhouse → zone → bench), plus the crop/stage context where known.
Structure changes slowly and may be supplied as known configuration rather than freshly
sensed; the Snapshot references it so every observation has a place.

## 6. Required vs optional fields

**Required at the Snapshot level** (the minimum for a valid Snapshot):
- the **greenhouse identity** it describes;
- the **assembled_at** time;
- a **provenance summary** (which sources contributed); and
- a **coverage** statement (what is present and what is known-absent).

Everything else is **optional** — and that is deliberate, per Principle 6. A Snapshot with
only three climate readings is valid. A Snapshot that says "nothing new observed since the
last one, here is what remains un-sensed" is valid. There is no required metric, no required
zone, no required biological observation.

**Required *within* any observation that is present** (per §4): subject, kind, captured_at,
source, method, confidence, and either a value (+unit if quantitative) or an explicit
absence marker. An observation missing these is malformed; an observation that is simply
absent is fine.

This two-level rule is the whole tension resolved: the *container* demands honesty about
identity, time, provenance, and coverage; the *contents* are free to be as partial as
reality is.

## 7. Timestamps

Time is layered, and the layers must not be confused:

- **captured_at** (per observation) — when *that value* was true or taken. The values in one
  Snapshot routinely have different capture times; a climate reading may be seconds old while
  a scouting note is hours old.
- **assembled_at** (per Snapshot) — when this coherent view was composed. A Snapshot is "the
  greenhouse as best assembled at `assembled_at`, from observations captured at various times
  at or before it."
- **freshness / staleness** — derivable from `captured_at` and a clock, and meaningful per
  observation: a value's trustworthiness decays with age, fast for fast-moving signals
  (turgor) and slowly for slow ones (cultivar norms). The Snapshot need not compute staleness,
  but it must carry the `captured_at` that lets the engines judge it.

All times are **UTC** at the boundary; local presentation is a rendering concern. Forecast
observations carry both the time they were *made* and the time they are *for*.

## 8. Provenance

Every observation declares where it came from, abstractly — never as a vendor identity, but
as enough to trace and to weigh:

- **source** — the producing agent: a named sensor/channel, a person, a camera, a model, or
  an import — identified stably, vendor-neutrally.
- **method** — `measured` / `observed-by-human` / `derived` / `vision-inferred` / `imported`
  / `forecast`. Method matters to the reasoning: a measured number and a human glance are
  weighed differently (Decision Philosophy, Evidence).
- **chain** (optional) — when data passed through stages (e.g. a control system → an
  extraction → the Snapshot), the chain may be recorded so a value is auditable end to end.

Provenance exists so that the system can *weigh evidence honestly* (the same value is worth
more from a calibrated sensor than from a guess), *explain itself* (every claim traces to its
evidence), and *debug* (a wrong value can be followed to its origin). It is also what keeps
the Snapshot vendor-free while remaining traceable: the *fact* that a value came from a
particular channel is recorded; the vendor's shape is not.

## 9. Confidence

Each observation carries a **confidence** — how much this *observation* deserves to be
trusted. It is distinct from, and feeds, the engines' later confidence in their *inferences*:
the Snapshot is honest about its evidence; the engines are honest about their conclusions.

Confidence in a Snapshot derives from properties the acquisition layer knows: the
**reliability** of the source (a calibrated sensor vs a flaky one vs an estimate), the
**method** (measured vs inferred-by-vision vs a human's quick read), and **recency**. It may
be expressed simply (e.g. high / medium / low) and, where useful, with a short basis ("sensor
flagged suspect", "single human glance", "model estimate"). Corroboration *across*
observations (sensor + human + camera agreeing) is real evidence too, but combining it is the
engines' job; the Snapshot supplies the per-observation confidences they combine.

A Snapshot must never launder uncertainty into false precision: a doubtful value is carried
*with low confidence*, not silently dropped or silently trusted.

## 10. Missing values

The most important honesty in the Snapshot. Missing data is represented explicitly, and the
distinctions are kept:

- **Known-absent** — we do not observe this (no sensor in that zone, that bench wasn't
  scouted). Recorded as absence *with* its scope, so the engines can say "I can't see this"
  rather than assume.
- **Stale** — we have a value, but it is old. Carried as the last-known observation with its
  `captured_at`; the engines decide whether age has made it useless.
- **Unknown ≠ zero.** A missing CO₂ value is not 0 ppm; a missing humidity is not 0 %RH. The
  Snapshot never coerces absence to a number.
- **Partial subjects.** A zone may have temperature but not light; a batch may have a human
  note but no measurement. Partial is normal.

The **coverage** statement at the Snapshot level summarises this: what was observed, and what
is known to be un-observed, so a reader can tell the difference between "all clear" and "not
looked at." Fabricating a value to fill a gap is the one thing a Snapshot may never do.

## 11. Illustrative shape (not a commitment)

```
GreenhouseSnapshot:
  greenhouse_id: "gh-…"                      # required
  assembled_at:  "2026-06-27T05:48:00Z"      # required (UTC)
  provenance:    [ {source: "climate-feed-A", method: measured},
                   {source: "grower:oskar",  method: observed-by-human} ]   # required
  coverage:      { zones_present: ["z1","z2","z3"],
                   not_observed:  ["z3 light", "z2 benches un-scouted"] }   # required

  structure:                                 # optional
    zones: [ {id: "z1", name: "House 1", benches: ["b1","b2"], stage: "propagation"} ]

  observations:                              # all optional; each follows the §4 envelope
    - {subject: "z1", kind: air-temperature, value: 24.2, unit: "°C",
       captured_at: "…:05:47Z", source: "climate-feed-A", method: measured, confidence: high}
    - {subject: "z1", kind: relative-humidity, value: 92, unit: "%RH",
       captured_at: "…:05:47Z", source: "climate-feed-A", method: measured, confidence: high}
    - {subject: "z1", kind: vent-position, value: "closed",
       captured_at: "…:05:47Z", source: "climate-feed-A", method: measured, confidence: high}   # equipment
    - {subject: "z1", kind: leaf-wetness, value: "canopy wet after sunrise",
       captured_at: "…:05:40Z", source: "grower:oskar", method: observed-by-human,
       confidence: medium, verbatim: "bench B still wet up top"}                                  # biological
    - {subject: "z2", kind: air-temperature, value: null, absence: known-absent,
       captured_at: null, source: "—", method: measured, confidence: n/a}                         # missing, honest
    - {subject: "site", kind: outside-temperature, value: 11.0, unit: "°C",
       captured_at: "…:05:30Z", source: "weather", method: forecast, confidence: low}             # external
```

Note what is *absent* from the example: any field called `stress`, `disease_risk`, or
`recommendation`. Those are conclusions, formed later, from this evidence.

## 12. Relationship to the rest of PTP OS

- **Providers produce Snapshots.** This spec is the canonical output the Provider spec
  refers to; a Provider maps its source into a Greenhouse Snapshot and nothing else.
- **The domain model's `Observation` is the unit; the Snapshot is the assembled set.** A
  `ClimateReading` is a specialised observation (a measured climate metric). The prototype's
  `ClimateReading` / `Observation` / `Outlook` are early, partial expressions of this
  structure; this spec canonicalises them.
- **The engines consume Snapshots and produce understanding.** The Context Engine assembles a
  Snapshot (plus memory) into context; the Decision Engine infers latent biology and decides.
  The boundary in Principle 2 is exactly the boundary between this spec and the reasoning specs.

## 13. Future integrations — all become a Greenhouse Snapshot

Each of these is *only* an acquisition method; each produces the identical structure:

- **A Synopta (or other) API** — measured climate/equipment observations, high confidence.
- **Claude browser extraction** — the same observations, read from a portal; method `measured`
  but possibly lower confidence, with the extraction recorded in provenance.
- **CSV / spreadsheet imports** — historical or manual data, method `imported`.
- **Manual observations** — a grower's notes, method `observed-by-human`, verbatim preserved.
- **Cameras** — images (media references) and vision-derived signs, method `vision-inferred`.
- **Weather providers** — external context, current and `forecast`.

None of them appears anywhere in the structure. They appear only in `provenance`.

## 14. Open questions

1. **Granularity of `kind`** — a fixed vocabulary of observation kinds, or an open set with a
   small required core? (Lean: a stable core, extensible at the edges.)
2. **Derived observations in the Snapshot vs in the engine** — should VPD/dew point live in
   the Snapshot (as `derived`) or be computed by the Context Engine? Either is defensible;
   the rule is that if derived values are carried, their basis and confidence travel with them.
3. **Identity of subjects over time** — how stable batch/plant ids are maintained as plants
   move, merge, or are discarded (ties to the domain model).
4. **How much history a Snapshot references** — purely "now", or may it carry a short tail
   (e.g. a trend) — and if so, is that a property of the Snapshot or assembled by the engine
   from many Snapshots? (Lean: the Snapshot is "now"; trends are the engine's, from a series.)
5. **Confidence scale** — the canonical vocabulary (categorical vs numeric) and how acquisition
   layers are expected to set it consistently.
6. **Media handling** — how images/clips are referenced and how vision-derived observations
   link back to the frame they came from.

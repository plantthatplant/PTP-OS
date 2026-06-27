# Gaia Companion — Experience Architecture (Even G2 first surface)

**Status:** Sprint 6 design · architecture & experience only, **no code**. **Builds on:**
[`specs/field-companion.md`](../specs/field-companion.md) (the device-independent Companion +
8 primitives + interaction modes + silence-default Interaction Engine — already built),
[`rfc/RFC-004-observer-network.md`](../rfc/RFC-004-observer-network.md) (observers),
[`docs/even-g2-capability-map.md`](even-g2-capability-map.md) (the researched hardware reality),
[`VISION.md`](../VISION.md), [`BIOLOGY.md`](../BIOLOGY.md), [`CLAUDE.md`](../CLAUDE.md).

> Designed from the **grower's cognition** outward, not from software. The greenhouse is the
> operating environment; the glasses are one interface; **the Brain is unchanged.**

## 0. The thesis (and a challenged assumption)

The brief says "Even-first." The hardware research says otherwise, and I'll argue the honest
case: **Even G2 is the right *primary ambient surface*, but the Companion must be glance-first
and multi-surface, not Even-first.** Why, from the evidence ([capability map](even-g2-capability-map.md)):

- **No camera** → the glasses cannot *observe* the crop. Imaging comes from the phone, fixed
  cameras, or a drone. The glasses are *the human observer's I/O*, not an observer of plants.
- **No speakers** → Gaia cannot *talk*; it shows a short line on a one-eye green HUD. Output is
  silent visual text; voice is the grower's way *in*.
- **Monocular, 27.5° FOV, monochrome, 1200 nits** → a tiny, sunlight-readable canvas: perfect
  for *one calm thought*, useless for *reading or capture*.

So the glasses are the **"tap on the shoulder + one sentence + show me where."** Anything that
must be *read, captured, compared, or reviewed* belongs on the **phone** (capture & depth) or
**desktop** (analysis). Treating Even G2 as the whole product would force reading and capture
onto a surface that physically cannot do them well. **Glance-first, multi-surface** is the
correct frame; Even G2 is the most important surface, not the only one.

This is not a detour from the architecture — it *is* the architecture: the Field Companion is
already device-independent (eight primitives behind `CompanionDisplay`), and the Observer Network
already says Even G2 is a device of the human observer. Sprint 6 makes the *experience* explicit.

## 1. Interaction philosophy

**Default to silence.** The grower is an expert at work; Gaia is the quiet colleague who speaks
only when it helps. The Interaction Engine already enforces this: speak only when the expected
biological value beats the (context-aware) interruption cost, with spacing. The glasses' very
hardware reinforces it — silent, tiny, single-thought.

**When Gaia speaks vs stays silent**
- **Silent (the norm):** observing, accumulating context, nothing decision-changing here-and-now.
- **Speak (rare, earned):** a high-value, located, time-sensitive thing — confirm an inference
  it can't see, flag a real alert, answer a question the grower asked, guide a procedure step.
- **Never:** speak because data is missing; repeat; narrate; show numbers to be shown.

**What belongs inside the glasses vs phone vs desktop** — the *surface-responsibility* rule:

| Need | Surface | Why |
| --- | --- | --- |
| A glanceable prompt / confirmation / one-line alert / "look here" navigation | **Even G2** | one thought, hands-free, in sunlight |
| Capturing an observation that needs a **camera** or more than a word | **Phone** | the glasses have no camera; longer notes need a keyboard/voice-to-text screen |
| Reading the **full morning brief**, a list, a trend, the evening review | **Phone** | reading/scrolling has no place on a 27.5° HUD |
| Analysis, history, calibration, planning across days/sites | **Desktop** | depth and breadth, seated work |
| Continuous monitoring with **no one wearing glasses** | **Phone/desktop notification** | the channel must not assume glasses are on |

Rule of thumb: **the glasses carry the *interruption*; the phone carries the *information*.** If
a message would make the grower stop and read, it is not a glasses message.

## 2. A whole workday (what Gaia does in each phase)

| Phase | Grower is… | Gaia behavior | Surface · mode |
| --- | --- | --- | --- |
| **Morning brief** | at the bench / coffee, before the walk | Offers the prioritized, explained day — *read in full on the phone*; the glasses show only the one headline + today's single top priority | Phone (full) + Even G2 (headline) · `MORNING_WALK` |
| **Walking inspection** | walking the houses | Mostly **silent**. Surfaces *one* located, time-sensitive question/look when value beats cost; spaced | Even G2 · `KNOWLEDGE_GAP` / `SILENT_MONITORING` |
| **Spot observation** | sees something (a leaf, condensation) | Grower says "Hey Even, note: bench B canopy still wet" → captured as an observation; if a photo helps, Gaia suggests *"add a photo?"* → phone camera | Even G2 (voice-in) → Phone (camera) · observation capture |
| **Asking Gaia** | wants to know something | "Hey Even, how is House 2?" → one-line answer on the HUD; *"more on phone"* if depth is needed | Even G2 (voice-in, one-line out) + Phone (depth) |
| **Receiving an alert** | anywhere | A critical, here-and-now item (e.g. a faulted sensor, a fast-moving risk) → one warning line; detail on phone | Even G2 · `ALERT` |
| **Harvest** | picking to order | Quiet; on request, *"House 3 — reserved for order #1043, dispatch in 4 days"*; flags if quality/tone isn't ready | Even G2 (on request) + Phone (order detail) |
| **Propagation** | taking/sticking cuttings | Step guidance one line at a time (`NAVIGATION`/procedure); confirms mother-stock condition observation | Even G2 (steps) + Phone (batch record) |
| **Packing** | grading & boxing | Quiet; surfaces dispatch readiness / quality notes only if decision-relevant | Phone (lists) + Even G2 (exceptions) |
| **End-of-day review** | sitting down | What was expected vs what happened, what was learned, what confidence moved — *read on phone/desktop*; the glasses say only *"Day reviewed — 1 thing to confirm tomorrow"* | Phone/Desktop (full) + Even G2 (closing line) · `EVENING_REVIEW` |

Across all phases the **modes** are the ones the Field Companion already defines; Sprint 6 only
binds each phase to a mode and a surface.

## 3. Observation workflow — how reality enters Gaia

Every input becomes a **Canonical Observation** and flows through the Observer Network; nothing
new is invented for reasoning. The glasses' role is narrow and honest (voice-in only).

| Input channel | Observer | Method | Enters via |
| --- | --- | --- | --- |
| **Voice note on the walk** ("canopy still wet, bench B") | human grower (Even G2 mic) | `observed-by-human` (verbatim preserved) | Companion → Canonical Observation |
| **Phone camera photo** of a symptom | human grower (phone) | `vision-inferred` (derived features) + media reference | phone Companion → Observation |
| **Ring/temple gesture answer** (yes/no/not sure) | human grower | `observed-by-human` (confirmation) | Companion → updates confidence (`reinforce`) |
| **Phone typed/voice note** (longer) | human grower (phone) | `observed-by-human` | phone Companion → Observation |
| **Drone scan** (RGB/thermal) | DJI observer | `vision-inferred` | Observer Network → Observation |
| **Fixed camera** | camera observer | `vision-inferred` | Observer Network → Observation |
| **Synopta climate/alarms** | Synopta observer | `measured` | Collector → Snapshot |
| **Future humanoid** | humanoid observer | `measured`/`vision-inferred`/`observed-by-machine` | Observer Network → Observation |

**Merging:** observations about the same subject+kind+time are **fused at Snapshot assembly**
(Observer-Network §6): corroboration raises confidence, conflict raises uncertainty (and may
itself trigger a tie-breaking observation), all originals preserved as evidence. The grower's
spoken "the canopy is wet" and a sensor's "humidity 92%" are *different observations of the same
reality*, weighed by trust×quality×recency — **the human ranks equal to the sensor** (BIOLOGY.md).
Crucially, **the glasses capture the human's words; the human's eyes are the sensor.**

## 4. Even G2 capability map

Fully documented with evidence in [`docs/even-g2-capability-map.md`](even-g2-capability-map.md).
The load-bearing facts: monocular green HUD (27.5°, 1200 nits), **no camera**, **no speakers**,
4 mics + "Hey Even", input via voice + R1 ring + temple tap, geomagnetic sensor, ~2-day battery,
phone app, an "Even Hub" dev portal whose **SDK terms are the one true unknown**.

## 5. Companion as a platform (no Even-specific assumptions)

The Companion is a *platform*; **Even G2 is one Companion surface**, swappable like any device.
This already exists in code shape: `CompanionDisplay` (eight primitives) + per-device adapters.
Sprint 6 names the surfaces and adds a **Surface Router**.

```
        Gaia Brain (unchanged) ─▶ Interaction Engine ─▶ CompanionMessage (device-independent)
                                                              │
                                                   ┌──────────▼───────────┐
                                                   │   SURFACE ROUTER      │  choose the surface(s)
                                                   │  (by urgency, need-to- │  that fit this message
                                                   │   read, capture, who's │  in this moment
                                                   │   wearing what)        │
                                                   └──────────┬───────────┘
   ┌───────────────┬───────────────┬───────────────┬─────────┴───────┬───────────────────┐
   ▼               ▼               ▼               ▼                 ▼                   ▼
 Even G2        iPhone          Apple Watch      Desktop           DJI*               Humanoid*
 (ambient out   (capture +      (ambient        (analysis,        (*observer,        (*observer +
  + voice-in)    depth + read)   notify, wrist)  history)          not an output)     ambient out)
```

- **Surface Router** is the new experience concept: given a `CompanionMessage` + context (is the
  grower walking? hands busy? does it need reading or a camera? which devices are present?), it
  routes to the surface(s) that fit. Same rule as §1's table, made a component. It holds **no
  biology** — pure presentation routing.
- **Surfaces declare capabilities** (can-render-line, can-capture-image, can-read-long,
  can-notify, can-voice-in) exactly as observers declare capabilities — so a new surface is a
  registry entry, not a code change. **No Even-specific assumption leaks above the adapter.**
- **DJI and humanoids are observers, not just surfaces** — they appear in the Observer Network
  (input), and a humanoid may *also* be an output surface (it can speak/show). The platform
  cleanly allows a device to be an observer, a surface, or both.
- **Degrade gracefully:** if no glasses are worn, the Router falls back to phone/watch; if the
  phone is away, the glasses still carry the interruption. (Edge-first, per RFC-004 review §7.)

## 6. UX principles (the design language)

1. **Default to silence.** Silence is the product working well. (Hardware agrees: no speaker.)
2. **One thought at a time.** One message, one screen, one decision. Never overload vision.
3. **The interruption on the glasses, the information on the phone.** If it must be read, it is
   not a glasses message.
4. **Biology before software.** Every word means something biological that the Brain produced;
   the surface never invents meaning.
5. **Confidence before certainty.** Show how sure, and why; never fake precision. Absence is
   stated, not hidden.
6. **Always explain *why*.** Every prompt/alert can answer "why am I seeing this?" (on the phone
   if it needs space). Why · evidence · confidence · what's missing.
7. **Respect attention.** Interruptions are expensive and spaced; the grower controls the
   **autonomy level** (ask-me-everything → act-and-tell-me).
8. **The grower stays the expert.** Gaia augments judgment, never replaces it; design for
   *growing* skill, not dependence (anti-deskilling — review §15).
9. **Provenance is visible.** The grower can always see *who/what* observed (sensor, me, drone),
   because trust depends on it — but the Brain never reasons on it.
10. **Calm and honest, hands-free, sunlight-readable.** The greenhouse, not the office, is the
    design context.

## 7. Future scenarios (walked through surfaces + modes + observers)

1. **The grower notices a leaf.** "Hey Even, note: brown spots, lower leaves, bench 3." →
   `observed-by-human` observation captured; Gaia: *"Noted. Add a photo?"* → phone camera adds a
   `vision-inferred` observation chained to the note. Confidence in any related concern updates.
   Glasses stay quiet after.
2. **DJI discovers possible Botrytis.** Drone scan → `vision-inferred` observation raises a
   disease-risk uncertainty. The Observation Planner judges value vs cost: the grower is near
   House 2 → cheapest confident resolution is to **ask the human**. Glasses: *"House 2 — canopy
   wet near bench 3?"* → grower answers via ring → `reinforce` moves confidence → *"Good — I no
   longer need to ask."* (Exactly the Sprint-4 demo, now triggered by a drone.)
3. **Gaia asks for confirmation** (general): only when EVI > cost, located, spaced, one line, a
   tiny fixed answer set — never free text on glasses.
4. **Gaia guides propagation.** `NAVIGATION`/procedure: one step per glance ("take 8–10 cm tip
   cuttings"; on ring-tap → next). Mother-stock condition captured as an observation; the batch
   record is written on the phone.
5. **Irrigation anomaly.** Synopta `measured` observations + a fixed-camera `vision-inferred`
   pooling sign conflict with "irrigation ran" → fusion raises uncertainty → Planner asks the
   human to glance, or routes a phone alert if no glasses are worn. Never auto-acts (trust before
   automation).
6. **Training new employees.** A new grower wears glasses; Gaia's autonomy level is set higher
   ("show me more"); it offers more `NAVIGATION`/explanation, and *their* observer trust starts
   from a lower prior, widening until calibrated. The expert's glasses stay quiet. The same Brain
   serves both — different *surface autonomy*, not different intelligence.
7. **Multiple growers collaborate.** Each is a distinct human observer with individual trust;
   the Router interrupts the *right* person (nearest, most trusted for this, not in do-not-
   disturb); human–human disagreement fuses like any conflict and can trigger a tie-break look.

## 8. Roadmap (ranked by value to a Head Grower)

**Must exist for MVP** (the calm walking colleague, today's value):
1. **Confirm the Even Hub SDK** — what a 3rd party may render/read (the gating dependency).
2. **Even G2 ambient adapter over the real SDK** — the Field Companion's `_send_to_device` made
   live (one-line text out; voice + ring in).
3. **Phone Companion** — the capture & depth surface: full morning brief, photo capture, longer
   notes, evening review. (Required *because* the glasses can't read or capture.)
4. **Surface Router v1** — glasses-for-interruption / phone-for-information.
5. **Voice-note → Canonical Observation** and **ring-answer → `reinforce`** end to end.
6. **A real live observation source** (Sprint-4 dependency: Synopta export/API) so the brief is
   real, not fixture.

**Useful later:**
7. Apple Watch as a lightweight ambient/notify surface (when glasses are off).
8. Phone-camera as a first-class `vision-inferred` observer (symptom photos with derived features).
9. Autonomy-level control + per-grower profiles & trust.
10. Desktop analysis/history surface.

**Research only:**
11. Drone (DJI) observer integration + the Observation Planner (needs a real *choice* of observer).
12. On-glasses glyph/iconography (pending capability confirmation).
13. Cross-site/fleet trust priors (federated learning).

**Future vision:**
14. Humanoid as observer + output surface.
15. Actuation (the deferred Actor; trust-gated) — never in this experience layer.

**Honest gating note:** items 1–2 depend entirely on Even Realities' SDK terms (Unknown). If the
SDK does not permit a third party to render arbitrary one-line messages and receive voice/ring
events, the **phone becomes the MVP surface** and Even G2 slots in unchanged the moment the SDK
allows — which is precisely why the Companion is a platform and not an Even-first build.

## 9. Why this is the world's best wearable interface for biological production

Because it is the *least* interface. It respects the two things a Head Grower guards most —
**attention** and **judgment** — by defaulting to silence, speaking one earned sentence at a
time, putting the interruption where the eyes already are and the information where it can be
read, and always being able to explain why. It treats the glasses as a calm colleague's voice,
not an app; it keeps the grower the expert; and because every surface and every observer is
interchangeable behind the same contracts, it will still be the right interface when the glasses,
the phone, and the robots have all been replaced.

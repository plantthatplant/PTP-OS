# Spec — Gaia Field Companion

**Status:** Draft v1 · Sprint 4 (design-first; reviewed before code). **Related:**
[`specs/knowledge-gap-engine.md`](knowledge-gap-engine.md),
[`specs/daily-grower-dialogue.md`](daily-grower-dialogue.md),
[`docs/gaia-learning-loop.md`](../docs/gaia-learning-loop.md),
[`docs/daily-operating-cycle.md`](../docs/daily-operating-cycle.md),
[`VISION.md`](../VISION.md) ("no layer assumes a screen").

> The Companion is **not** a new brain. It is Gaia's *presence in the greenhouse* — the thin,
> device-independent layer that decides **when to speak and when to stay silent** while the
> grower walks, using only what the engines already produced.

## 1. Purpose

Help a Head Grower make **better biological decisions while walking** — hands-free, in
sunlight, one glance at a time. The goal is not to display data; it is to feel like an
experienced Head Grower is walking beside you: mostly quiet, occasionally invaluable.

## 2. Hard boundaries

- **Consumes Gaia's output only.** The Companion reads Morning Analysis (priorities, concerns,
  confidence), Knowledge-Gap Questions (already VoI-scored), open Experiments, and the
  Snapshot. It **performs no biological reasoning** and invents no biological content — every
  word of meaning originates in the engines.
- **Device-independent.** The Brain never knows which device is connected. The Companion
  exposes abstract primitives (§5); a device adapter (Even G2 today; Android, AR, voice,
  robot tomorrow) only *translates* them. **Nothing in Gaia depends on Even G2.**
- **Silence is the default.** Interruptions are expensive. The Companion speaks only when the
  **expected biological value of an interaction exceeds its (context-aware) interruption
  cost** — never merely because information is missing.
- **Reuse, don't duplicate.** It builds on `knowledge_gap` (VoI), `workflow`
  (timing/location/`interrupt_now`), `lifecycle` (`reinforce`, confidence ladder), and
  `store` (persistence/learning). It adds *interaction economics*, not biology.

## 3. Architecture

```
        Gaia Brain (engines — UNCHANGED)
   morning_analysis · knowledge_gap (VoI) · workflow · lifecycle · curiosity · store
        │  produces: priorities, concerns, confidence, VoI questions, experiments, snapshot
        ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │  FIELD COMPANION  (new; consumes Gaia output only)                  │
 │                                                                    │
 │   WalkContext   location · clock · ticks-since-last-interruption    │
 │        │                                                           │
 │        ▼                                                           │
 │   Interaction Engine  → next interaction OR silence                 │
 │        reuses workflow.surface / interrupt_now / matches_location,  │
 │        knowledge_gap VoI components, lifecycle.reinforce            │
 │        adds: EVI-vs-context-cost gate + interruption spacing + mode │
 │        │                                                           │
 │        ▼                                                           │
 │   CompanionDisplay  (device-independent primitives, §5)             │
 │        │                                                           │
 │   InteractionRecord → store (permanent memory) + worthwhile learning│
 └────────────────────────────┬───────────────────────────────────────┘
                              ▼
     Device adapters (translate primitives → device; no Gaia logic)
     EvenG2Display      ConsoleDisplay        (future: Android, AR, voice, robot…)
```

The Brain imports nothing from the Companion. The Companion imports nothing from any device.
Both inversions are what keep Gaia device-independent.

## 4. The Interaction Engine

One method conceptually: **`decide(walk_context) -> Interaction | None`**. `None` means
silence (the common case). It never recomputes biology; it schedules and prices.

**Inputs (all Gaia-produced or interaction-context):** the day's VoI questions, priorities,
concerns, current confidence, open experiments; current location, time, and how long since the
last interruption.

**Decision:**
1. **Alerts first.** A critical, time-sensitive item for *here* (e.g. a faulted sensor in this
   zone, or a `workflow.interrupt_now` question) may speak immediately, bypassing spacing.
2. **Otherwise**, among questions that match this location (`workflow.surface`), take the one
   with the highest **EVI** (Expected Value of Information = the pre-interruption product Gaia
   already computed: stakes × uncertainty × decisiveness × prior).
3. **Price the interruption** with a context-aware cost: the engine's base interruption cost,
   raised when the grower was interrupted recently (spacing). 
4. **Speak only if `EVI > effective_cost`.** Else **stay silent**.

**On an answer:** route through `lifecycle.reinforce` (confirm/scout) or `apply_outcome`
(close) so the **recommendation's confidence updates** (before → after); then a brief
**confirmation** ("Thank you. That increased my confidence." / "Good — I no longer need to ask
about House 2."). The full record is stored, and the *worthwhile* signal feeds
`store.append_question_eval` → `prior_worth_by_kind` (so low-value question kinds stop clearing
the bar over time — the system learns to ask **less**).

### InteractionRecord (stored permanently in memory)
`question_id · timestamp · snapshot_ref · decision_id/experiment_id · reason · uncertainty ·
evi · interruption_cost · confidence_before · confidence_after · worthwhile` — plus context:
`mode · primitive · urgency · location · wording_shown · answered · answer`.

## 5. Device-independent interface

`CompanionDisplay` (abstract) — every method takes a small `CompanionMessage` (id, kind,
**headline** ≤ ~40 chars, optional short detail, urgency, needs_response, options):

`show_message · show_priority · show_question · show_status · show_navigation ·
show_confirmation · show_warning · show_summary`

A device adapter implements these for its hardware. **EvenG2Display** renders one message to
the tiny heads-up display; **ConsoleDisplay** renders to a terminal "screen" for development.
Adding a device = one new adapter; no change above it.

## 6. Small-display design rules (binding)

One message visible · maximum readability · hands-free · walking · bright sunlight · **no
scrolling, no menus, no typing**. Every message normally fits **one screen**: a short headline,
optionally one short detail line, and for questions a tiny fixed answer set (e.g. yes/no/not
sure) chosen by glance/gesture/voice — never free text on-device.

## 7. Interaction modes

`MORNING_WALK` (brief summary) · `INSPECTION` (a located priority/look) · `KNOWLEDGE_GAP`
(a VoI question) · `OBSERVATION_CONFIRMATION` (acknowledge an answer, update confidence) ·
`ALERT` (a warning) · `NAVIGATION` (where to look next) · `SILENT_MONITORING` (default —
nothing) · `EVENING_REVIEW` (what was expected vs happened, what was learned). A mode selects
which primitive(s) and flow apply; it adds no biology.

## 8. One greenhouse walk (the demonstration)

Morning Brief → walk starts → **silence** → at House 2 the engine surfaces the *one*
biologically valuable question (highest EVI, location-matched, cost-cleared) → grower answers →
`reinforce` raises confidence → InteractionRecord + memory updated → confirmation ("I no longer
need to ask about House 2") → **silence** resumes → walk finishes → Evening Review → learning
(`prior_worth_by_kind` updates).

## 9. Will this make Gaia a better Head Grower? (the test every feature must pass)

Yes, and specifically: it **lowers cognitive load** (silence by default; one glance), **asks
fewer but better questions** (EVI gate + spacing + learned priors), **raises decision quality**
(answers update confidence in real time, in the field), and **remembers** (every interaction is
evidence). Anything that fails this test is postponed (§ Founder Review).

## 10. Out of scope (postponed, with reasons)

- **Real Even G2 SDK transport** — the adapter formats to the device's display contract; the
  final "send bytes to the glasses" call is the only remaining piece (no device to test here).
- **On-device input beyond a tiny fixed answer set** — typing/menus violate §6.
- **Any biological inference in the Companion** — forbidden by design (§2).

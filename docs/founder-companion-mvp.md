# Founder Companion — MVP for Oskar at Kålaberga

**Status:** Sprint 7 · the smallest Gaia Companion Oskar would wear every day. **Goal:** within
weeks, Oskar *voluntarily* puts on Even G2 because Gaia gives real value — not because it is
clever. **Build discipline:** every feature must pass one test — *"Would Oskar miss this tomorrow
if it disappeared?"* If no, it isn't built. Builds on what already exists: the Brain
([`app/`](../app/)), the Field Companion ([`specs/field-companion.md`](../specs/field-companion.md)),
the Collector ([`docs/gaia-collector.md`](gaia-collector.md)). No new architecture, no RFC/ADR.

## 0. Two honest constraints (they shape the whole MVP)

- **The Even G2 SDK terms are unknown** ([`even-g2-capability-map.md`](even-g2-capability-map.md)).
  Until Even Realities confirms a third party can render a line and read voice/ring, **the phone
  is the primary buildable surface and the glasses are a one-line preview.** The instant the SDK
  lands, the glasses adapter is a swap — the experience above it does not change.
- **There is no live Synopta API yet** ([`synopta-discovery-report.md`](synopta-discovery-report.md)).
  The MVP runs on the **morning screen-read snapshot** (the interim bridge already proven) or a
  Collector export. Real-data quality improves the day Synopta export/API is enabled; nothing
  above the Snapshot changes.

These are stated so the MVP is real, not aspirational. What follows is buildable now and useful
to one grower.

## 1. The first five things Gaia should actually do

Ranked by founder value. If only one shipped, it would be #1.

1. **A morning brief worth opening.** Before Oskar arrives: today's *one* priority, *one* concern,
   the confidence, and *what changed since yesterday*. Read in full on the phone; one headline on
   the glasses. (This is the daily reason to engage.)
2. **Walk with him in silence, speak once when it matters.** During the walk Gaia is quiet, then
   surfaces the *single* highest-value, located question ("House 1 — canopy wet?") only when the
   value beats the interruption — and the answer updates Gaia's confidence on the spot.
3. **Capture a spoken observation with zero friction.** "Hey Even, note: bench B still wet up
   top" → stored as evidence (verbatim), instantly, no menus.
4. **Flag a real alarm he'd want *now*.** A Synopta sensor fault or a fast-moving risk → one
   warning line on the glasses, detail on the phone. (We already saw two faulted sensors live —
   exactly the thing a grower wants surfaced.)
5. **An evening review that closes the loop.** What was expected vs what happened, what Gaia
   learned, and the *one* thing to check tomorrow. On the phone.

Each earns its place: remove any one and Oskar's day is measurably worse.

## 2. What Gaia must absolutely never do (MVP)

- **Never change anything in the greenhouse.** Read-only. No actuation, no setpoints, no commands
  to Synopta or the controller.
- **Never invent a value or fake certainty.** Honest absence; always show confidence; "I don't
  know" is allowed.
- **Never interrupt without earned value.** No nagging, no repeats, no data dumps, no notifications
  for their own sake.
- **Never put something to *read* on the glasses,** and never require typing on the glasses.
- **Never reason about biology in the Companion.** The Brain reasons; the Companion only relays,
  times, and records.

## 3. Glasses vs phone · automatic vs confirm

| | **Even G2 (the interruption)** | **iPhone (the information)** |
| --- | --- | --- |
| Carries | one headline, one question, one alert line, one nav cue | full brief, the *why*, photo capture, notes, evening review, history |
| Never | anything that must be read or scrolled | — |

| **Automatic (no asking)** | **Requires the grower (confirmation/input)** |
| --- | --- |
| Assemble the snapshot, compute the brief, detect changes, surface an alarm, stay silent, write memory | Answer a knowledge-gap question (yes/no/not sure), add a spoken note, mark a recommendation done/skipped in the evening |

Note: in a read-only MVP, "confirmation" means *the grower confirming Gaia's inference*, never
*Gaia asking permission to act* (it never acts).

## 4. User journey (Oskar's day, end to end)

> **06:00 — before arrival.** Gaia has assembled the morning snapshot and prepared the brief.
> Oskar glances at his phone over coffee: *"Kålaberga — watch House 1. 1 priority, confidence
> medium."* He reads the one priority and why.
>
> **06:30 — the walk.** He puts on the glasses. Silence through House 3. Near House 1 the glasses
> show: *"House 1 — canopy wet?"* He answers with a ring tap: *no*. Glasses: *"Good — I no longer
> need to ask about House 1."* He sees brown spots on bench 3 and says *"Hey Even, note: brown
> spots, lower leaves, bench 3."* Glasses: *"Noted. Photo? (phone)"*. He snaps one on the phone.
> Silence resumes.
>
> **09:00 — an alarm.** Glasses: *"House 2 — temp sensor reading invalid."* He checks the phone
> for detail, trusts his own eyes instead, moves on.
>
> **Through the day.** Harvest, propagation, packing — Gaia stays quiet, answering only when asked
> ("Hey Even, how is House 2?") with one line, depth on the phone.
>
> **18:00 — evening.** On the phone: what was expected vs happened, the canopy answer raised
> confidence and stood down a false alarm, *one thing to confirm tomorrow.* Gaia learned.

## 5. Screen-by-screen — the Even G2 experience

The glasses only ever show **one line** (a short second line at most). Each is a CompanionMessage
primitive ([`specs/field-companion.md`](../specs/field-companion.md)) the grower already has.

| Moment | Glasses shows (one line) | Input |
| --- | --- | --- |
| Morning headline | `= Kålaberga: watch House 1` | — |
| Today's priority | `› Today: House 1 — airflow now` | — |
| A question | `? House 1 — canopy wet?` + `[ yes / no / not sure ]` | ring / voice |
| Confirmation | `✓ Good — no need to ask House 1` | — |
| A spoken note ack | `✓ Noted. Photo? (phone)` | ring / voice |
| An alarm | `! House 2 — sensor reading invalid` | — |
| Navigation | `→ Next: look at House 2` | — |
| Ask Gaia (answer) | `· House 2 — settled, conf medium` | "Hey Even, how is House 2?" |
| Closing line | `= Day reviewed — 1 to confirm tomorrow` | — |

Design rules (from the hardware): monochrome, sunlight-bright, glanceable; no scrolling, no
menus, no reading. If it doesn't fit one line, it goes to the phone.

## 6. The iPhone experience (the information surface)

The phone is where Oskar *reads and captures*. Calm, one screen per thing, lead with the answer.

- **Morning brief (full):** summary · today's priority with *why · evidence · confidence · what's
  missing* · what changed since yesterday · the day's few questions.
- **Now / status:** current snapshot at a glance per house; reality confidence; what's un-observed.
- **Capture:** a big "Add observation" — voice-to-text note + optional photo (the camera the
  glasses lack). One tap.
- **Evening review:** expected vs happened; confidence moves; what was learned; tomorrow's one
  check.
- **Why card:** for any prompt, "why am I seeing this?" with the full reasoning.

The phone never tries to be the glasses (no live walk interruptions) and the glasses never try to
be the phone (no reading).

## 7. Notification philosophy

- **Silence is the default and the feature.** A quiet day means Gaia is working, not broken.
- **Three tiers only:** (1) *glanceable* — appears on the glasses in-context, no buzz; (2)
  *worth a beat* — a single alarm line; (3) *for later* — sits in the phone brief, never
  interrupts. There is no tier four.
- **One at a time, spaced.** Never two interruptions in quick succession (the Interaction Engine
  already enforces spacing).
- **Earned, explained, dismissible.** Every interruption beat the value-vs-cost bar, can answer
  "why," and never repeats once acknowledged.
- **Off means off.** Glasses removed → nothing is lost; it waits on the phone.

## 8. Voice interaction (input only — the glasses have no speaker)

- **Wake + intent:** "Hey Even, …". Two verbs cover the MVP: **note** ("note: …" → an
  `observed-by-human` observation, verbatim) and **ask** ("how is House 2?" → one-line status,
  depth on phone).
- **Answering a question:** a single spoken word from the tiny fixed set (yes / no / not sure /
  better / same / worse) or a ring tap. **No free-form dictation of decisions.**
- **Output is never spoken** (no speaker) — Gaia replies as one line on the HUD. Voice is how
  Oskar talks *to* Gaia; the HUD is how Gaia answers.
- **Confirm-back for notes:** a captured note is echoed as one line so Oskar knows it was heard.

## 9. Daily workflow (what runs when)

| When | Runs automatically | Surface |
| --- | --- | --- |
| Pre-dawn | assemble snapshot (screen-read/Collector) → Morning Analysis → brief + the day's questions | — (prepared) |
| Morning | serve brief | phone (full) + glasses (headline) |
| Walk | silence; surface the one valuable question; capture notes; flag alarms | glasses |
| Anytime | answer "Hey Even, how is …?" | glasses (line) + phone (depth) |
| Evening | close experiments, compute what was learned, tomorrow's one check | phone |
| Overnight | persist interactions & outcomes to memory | — |

## 10. MVP backlog — ranked strictly by founder value

**Must exist for the MVP (in this order):**
1. **Daily companion runner** — one command/flow that ties snapshot → Brain → Companion across
   morning/walk/evening on real(-ish) data. *(Built this sprint — §12.)*
2. **Phone surface (information)** — full brief, status, capture, evening review. *(Phone renderer
   built this sprint; native iOS app is the build-plan step.)*
3. **Glasses one-line surface** — the interruption/confirmation/alert lines. *(Adapter exists;
   live transport gated on SDK.)*
4. **Spoken note → Canonical Observation** and **ring/voice answer → confidence update**.
   *(Engine exists; wired in the runner.)*
5. **A real morning data source** — the Synopta screen-read snapshot daily (interim), then the
   export/API. *(Interim proven; production gated on Synopta access.)*

**Useful later:** Apple Watch as a quiet fallback surface · phone photo as a first-class
vision observation · autonomy-level control · richer "why" cards.

**Research only:** drone/fixed-camera observers + the Observation Planner · on-glasses glyphs
(pending capability test) · fleet learning.

**Future vision (explicitly not now):** humanoids, actuation, scale, multi-site.

Everything below "Must exist" fails the *"would Oskar miss it tomorrow?"* test today.

## 11. Build plan (weeks, not quarters)

1. **Week 1 — make the day real on the PC.** The daily companion runner (built §12) runs each
   morning on the greenhouse PC from the screen-read snapshot; Oskar reads the brief on the PC/
   phone browser, "walks" it, reviews in the evening. Value lands immediately, no SDK, no API.
2. **Week 2 — phone in his pocket.** Wrap the phone surface as a simple mobile view (local web
   page served on the LAN, or a thin app) so the brief/capture/evening live on his phone.
   *Decision needed: simplest path (web view vs native) — pick the one that ships fastest.*
3. **Week 3 — glasses, if the SDK allows.** Confirm Even Hub SDK terms; if a third party may
   render a line + read ring/voice, implement the live transport in the existing
   `EvenG2Display._send_to_device`. If not, stay on phone and revisit — the experience is
   unchanged either way.
4. **Continuous — better data.** Push Synopta to enable a scheduled export so the snapshot is
   live and complete, replacing the screen-read interim.

**Decisions Oskar/we must make:** (a) phone path — web view vs native (ship-fastest wins); (b)
who pursues the Even SDK confirmation; (c) who enables the Synopta export. None blocks Week 1.

## 12. What was built this sprint (minimum necessary)

Only the smallest code that makes the day real today, reusing everything:
- A **phone surface** renderer (the *information* surface) alongside the existing glasses (Even
  G2) and console adapters — so the same device-independent messages render richly on the phone
  and as one line on the glasses.
- A **daily companion runner** that composes the existing Collector/Brain/Field-Companion into
  Oskar's actual day — morning brief (phone + glasses headline), the silent walk with one
  earned question, spoken-note capture, and the evening review — on the real morning snapshot.

No speculative features were added. Each line of new code serves one of the five things in §1.

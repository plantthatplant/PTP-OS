# Gaia Field Companion — Founder Review

**Date:** 2026-06-27 · **Sprint 4.** What we built, why it makes Gaia a better Head Grower, and
an honest score against Gaia's ten principles. The demonstration is one complete greenhouse
walk on a simulated Even G2 (`python companion/demo_walk.py`); 11 Companion tests pass and the
Collector's 54 are unaffected.

## What we built

A **device-independent Field Companion** that is Gaia's presence in the greenhouse during a
walk. It consumes only what the engines already produce (priorities, concerns, confidence,
VoI-scored questions, experiments) and adds **interaction economics** — deciding *when to
speak and when to stay silent*, in what words, with what urgency — then records every
interaction permanently. It contains **no biological reasoning** and depends on **no device**.

The demonstrated walk:

> Morning Brief → walk starts → **silence (House 3)** → **one question (House 1: "canopy
> wet?")** → grower: *"No, the canopy is dry now"* → confidence **Medium → Low** (a false
> alarm stood down) → *"Good — I no longer need to ask about House 1"* → **House 2 question
> SILENCED** (lower value, too soon after the last) → **silence (House 3)** → Evening Review:
> *asked 1, stayed silent 1, 1 confidence update* → learning.

## Why this makes Gaia *biologically* better

- It moves Gaia's intelligence **to where the biology actually is** — the plant, in the house,
  in the grower's eyes. The one thing software cannot see (is the canopy actually wet?) is
  exactly what it asks, and the answer **updates the biological confidence in real time**
  (`lifecycle.reinforce`), so the recommendation reflects the plant, not just the climate.
- It strengthens the **observation-before-inference** discipline: the grower's answer is stored
  as an observation; the confidence move is the inference, kept separate and auditable.
- It feeds the **learning loop**: every interaction is permanent evidence, and "was it worth
  asking?" updates `prior_worth_by_kind`, so Gaia's *future* questions get better.

## Why it reduces cognitive load

- **Silence is the default.** On the demonstrated walk, three of four locations were silent.
  The grower is never handed a dashboard or a form — at most one glanceable line.
- **One screen, one glance, hands-free.** Every message fits the tiny HUD (≤ 40 chars, no
  scrolling, no menus, no typing). The grower keeps their hands and eyes on the plants.
- The Companion carries the bookkeeping (what to check, what was answered, what changed), so the
  grower carries only the judgement.

## Why it asks *fewer* questions than before

Three gates compound, all reusing existing logic:
1. **Daily VoI filter** (`knowledge_gap`): most candidate questions never qualify (3 held back
   vs 2 kept in the demo).
2. **EVI-vs-context-cost** at the moment of asking: only if expected value beats the cost.
3. **Interruption spacing**: a recent interruption inflates the next one's cost — which is
   exactly why the House 2 question was silenced (EVI 0.5 < cost 0.6).
4. **Learned priors**: question kinds that prove low-value clear the bar less often tomorrow.

The result is *fewer but better* questions — and the system trends toward asking even less.

## Why it feels like walking with an experienced Head Grower

An experienced colleague walks beside you mostly in silence, then says the one thing that
matters — *"take a look at House 2"*, *"is the canopy still wet?"* — listens, updates their
view, and tells you when they're satisfied (*"good, I don't need to worry about that now"*).
That is precisely the texture here: calm, sparing, specific, and it remembers. The wording in
the demo (*"Good — I no longer need to ask about House 1"*) is that colleague, not a UI.

## Score against Gaia's ten principles (1–10)

| # | Principle | Score | Why |
| --- | --- | :--: | --- |
| 1 | Reality before assumptions | 9 | Invents nothing; consumes engine output; honest absence preserved. |
| 2 | Biology before software | 10 | Zero biology in the Companion — enforced by design and tests. |
| 3 | Observation before inference | 9 | Answers stored as observations; confidence moves kept separate. |
| 4 | Ask before assuming / show uncertainty | 10 | The core: ask only when valuable; every record carries uncertainty + confidence before/after. |
| 5 | Learn from outcomes | 9 | Every interaction stored; worthwhile feeds learned priors; answers update experiments. |
| 6 | Prefer simplicity | 9 | No new engine; reuses workflow/knowledge_gap/lifecycle/store; small modules. |
| 7 | Explain uncertainty | 9 | Each interaction records reason, EVI, cost, uncertainty, confidence before/after. |
| 8 | Highest-value-first | 10 | Silence default + EVI>cost gate + spacing → only the highest-value interruption. |
| 9 | Every sprint betters the grower | 9 | Field presence with fewer, better questions and real-time confidence. |
| 10 | Protect the architecture | 10 | Device-independence enforced (Brain ⟂ Companion ⟂ device, both tested); reuse not duplication. |

**No principle is weakened.** Sprint is complete. Composite ≈ **9.4 / 10**.

## Honest limitations (postponed, with reasons)

- **Real Even G2 transport** — the adapter formats to the device's one-line contract; the only
  remaining piece is the SDK call in `EvenG2Display._send_to_device` (no glasses reachable here).
- **Live location** — the walk consumes a location signal; wiring a real positioning source
  (beacon/zone tag) is a device/ops concern, behind the same seam.
- **On-device input** is a tiny fixed answer set by design (no typing/menus on a HUD).

## What this unlocks next

With the Collector (data in) and the Companion (intelligence out, in the field) both proven, the
remaining gates are external: the live Synopta/HortOS feed (Sprint 4 discovery) and the real
device transport. Neither requires changing Gaia's core — exactly as the architecture intends.

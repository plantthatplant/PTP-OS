# Unified Morning Intelligence (Sprint 9)

**Status:** built. **Goal:** Gaia stops feeling like several systems and starts feeling like one
Head Grower. **What changed:** a **Knowledge Fusion** layer
([`app/greenhouse_brain/fusion.py`](../app/greenhouse_brain/fusion.py)) that merges everything
Gaia already knows into one understanding, and a Companion/morning that speaks it with one voice.

## The Knowledge Fusion layer

Not a new AI and not new reasoning — a **synthesis** layer. It takes the outputs that already
exist — Morning Analysis (reality), the Business Knowledge Observer (intention), plan-vs-reality
gaps, Memory, overnight changes, and the day's worth-asking questions — and:

- **merges** them into one narrative (the "one thought"),
- **resolves** which thing leads (a *critical* reality concern → else a plan deviation → else the
  top priority → else "settled"),
- **prioritises** one action, **summarises** one explanation, **chooses** one question,
- **never invents**, and **keeps provenance internally** (so the grower never hears
  "Synopta says… the spreadsheet says…").

It answers, in one voice: *what is happening · what was supposed to happen · what changed · what
worries me · what can wait · what to do first · what to observe · what to ask · what I learned
yesterday that matters today.*

## Three mornings — before vs after

Run: `python companion/demo_mornings.py`. Each shows the disconnected "before" and the unified
"after".

**1 · A normal day**
> *After:* "Kålaberga is on plan and settled this morning — nothing needs you first."
One calm line instead of four green dashboards.

**2 · A delayed-production day** (no climate alarm — the slip is plan-vs-reality)
> *Before:* Synopta: climate in range · Spreadsheet: H2 expected 500 × Anthurium · Plan check:
> harvest date passed · Memory: H2 ran two weeks behind.
> *After:* "**House 2 is behind plan — the planned harvest date (2026-06-22) has passed.
> Yesterday's record supports this — House 2 ran about two weeks behind under the same climate
> last cycle. The schedule looks at risk; reality has not met the plan.**"

**3 · A disease-risk day** (the real House 1 sample)
> *Before:* Synopta: rising disease risk · Spreadsheet: H1 plan · Memory: wet canopy preceded
> Botrytis · Knowledge Gap: is the canopy wet?
> *After:* "**House 1 rising disease risk (humid, stagnant, wet canopy). Meanwhile the plan
> expected 60 × Femtunga (Pentas) around 2026-07-17. Yesterday's record supports this — a wet
> canopy on bench B preceded Botrytis two cycles ago. A wet, still, warm canopy on young tissue
> is how propagation is lost — the classic Botrytis / damping-off setup.**"
> · do first: increase air movement now · ask today: is the canopy wet? · one question, not four.

The difference from today's output: **the grower no longer assembles four systems in their
head.** Reality, intention, and memory arrive pre-merged, with one priority and one question.

## Everything now speaks with one voice

- **Morning Brief:** the phone shows the fused narrative + one priority + one question; the
  glasses show one headline ([`companion/daily.py`](../companion/daily.py)).
- **Companion:** one priority, one explanation, one recommendation — not multiple notifications.
- **Memory & Knowledge Gap:** consumed by fusion, not surfaced separately — the lesson that
  matters today is woven in; the single highest-value question becomes "ask today".
- **Business Knowledge:** intention (plan) is woven against reality; a divergence becomes the
  lead or the question — never an overwrite.

## Does Gaia now feel like one Head Grower?

**Yes — one mind.** The test is whether a grower could tell which system each sentence came from.
After fusion they can't: the morning is one paragraph in one voice, with one thing to do and one
thing to confirm, and the provenance is kept inside Gaia for trust and audit, not paraded at the
grower. A real Head Grower doesn't say "the climate computer reports… and the plan says… and I
recall…"; they say "House 2 is behind, and I don't think the weather will save the schedule —
go look." That is now what Gaia says.

Where it is still maturing (honest): the synthesis is deterministic templating, so its prose is
sound but not yet supple; richer phrasing is a Language-Engine concern (ADR-001), behind the same
structured `UnifiedBrief`. The *understanding* is unified now; the *eloquence* improves later
without changing the one-mind contract.

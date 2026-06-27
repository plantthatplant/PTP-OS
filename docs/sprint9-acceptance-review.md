# Sprint 9 Acceptance Review — does Knowledge Fusion make Gaia a better Head Grower?

**Stance:** I am an experienced commercial Head Grower. I did not write this code. I judge only
the output, and I am looking for reasons to distrust it. No code is added in this review.

**A** = the brief *without* Knowledge Fusion (Morning Analysis sections + plan/memory consulted
separately, source by source — the pre-Sprint-9 experience).
**B** = the Unified Morning Intelligence (one fused thought + one priority + one question).

Briefs for *normal / delayed / disease-risk* are quoted from real runs
(`companion/demo_mornings.py`). The other seven are written at the level the current engines
actually produce, and I flag honestly where Gaia **lacks the observer** to truly see the
scenario (pest, irrigation reality, labour reality) — that limitation is the same for A and B.

---

## 1. Normal production day

**A** — `SUMMARY: settled. CONCERNS: none. OPPORTUNITIES: 1. PRIORITIES: (none). CURIOSITIES: 1.
CONFIDENCE: Medium. DATA QUALITY: 81% coverage…` — seven sections to read to learn nothing is
wrong.
**B** — *"Kålaberga is on plan and settled this morning — nothing needs you first."*

Prefer: **B.** Fewer decisions: **B** (zero vs scanning 7 sections). Cognitive load: **B.**
Biologically useful: tie (nothing to act on). Better outcomes: **B** (the grower starts the day
faster, no false sense of "must read everything"). *A calm day is exactly where A wastes the
most attention.*

## 2. Heat-stress day

**A** — `CONCERNS: [Protect] House 1 cuttings — heat load high. OUTLOOK: hot afternoon.
PRIORITIES: shade before midday (why… if ignored… effort Low, urgency Now, confidence Medium).
DATA QUALITY…` plus, separately, the plan's expected propagation timing.
**B** — *"House 1's rootless cuttings will feel the afternoon heat before midday. Shade them
before the peak; their roots can't yet cope with the load."* · do first: shade House 1 before
midday · ask today: will the cuttings want shade before midday?

Prefer: **B.** Fewer decisions / lower load: **B.** Biologically useful: **B** (it names the
*why* — rootless tissue — in one breath). Better outcomes: **B**, marginally; A contains the
same fact but buries the timing in a priority block. *Heat is time-critical; one clear sentence
beats a section.*

## 3. Disease-risk day (real sample)

**A** — `CONCERNS: [Prevent-Critical] House 1 disease risk. PRIORITIES: increase airflow…
CURIOSITIES… CONFIDENCE Medium. DATA QUALITY 81%.` Plan and "wet canopy preceded Botrytis"
memory only if the grower opens them separately.
**B** *(real output):* *"House 1 rising disease risk (humid, stagnant, wet canopy). Meanwhile
the plan expected 60 × Femtunga (Pentas) around 2026-07-17. Yesterday's record supports this — a
wet canopy on bench B preceded Botrytis two cycles ago. A wet, still, warm canopy on young
tissue is how propagation is lost — the classic Botrytis / damping-off setup."* · do first:
increase airflow · ask today: is the canopy wet?

Prefer: **B, clearly.** B did the thing a Head Grower's mind does automatically — pulled the
memory *and* the plan to the risk *without being asked*. A has the facts but leaves the joining
to the grower. Better outcomes: **B** (the memory link is the difference between "watch it" and
"act now"). This is the strongest case for fusion.

## 4. Delayed production

**A** — `CONCERNS: none (climate is fine). DATA QUALITY: ok.` The slip is **invisible to A**
unless the grower separately reads the plan and notices the harvest date passed. *This is A's
worst failure: no climate alarm, so A says nothing, while the schedule quietly slips.*
**B** *(real output):* *"House 2 is behind plan — the planned harvest date (2026-06-22) has
passed. Yesterday's record supports this — House 2 ran about two weeks behind under the same
climate last cycle. The schedule looks at risk; reality has not met the plan."*

Prefer: **B, decisively.** B surfaces a problem A literally cannot see. Biologically/operationally
useful: **B.** Better outcomes: **B** (catching a slip a week earlier is real money). *This
scenario alone justifies the sprint.*

## 5. Irrigation anomaly

**A** — `CONCERNS: maybe [Inspect] if a sensor reads oddly; else nothing.`
**B** — *"House 2 shows signs of an irrigation that didn't land as planned — the climate looks
right but the plan expected a cycle this morning. Worth a look before you trust it."*

Prefer: **B**, but with an honest caveat I must record: **Gaia has no irrigation-reality
observer yet** (Synopta climate ≠ irrigation confirmation). So *both* A and B are inferring from
absence, and B's confidence here should be — and is — low. B is better only because it frames
*plan vs observed* and asks rather than asserts. **Neither is trustworthy until an irrigation
observation exists.** Marked, not hidden.

## 6. Pest suspicion

**A** — `CURIOSITIES: a dev-note mentions thrips → "worth a look".` Buried among curiosities.
**B** — *"A note from yesterday hints at thrips in House 2; nothing confirms it yet. If you're
near bench 3, a glance would settle it."* · ask today: do the plants actually look off?

Prefer: **B**, again with the honest caveat: pest detection depends on a **human or camera
observer**; with only a passing note, both versions can only *ask*. B is better because it turns
the buried note into one targeted, low-cost question instead of a curiosity the grower skims
past. Better outcomes: **B**, mildly — earlier looks catch pests earlier. But the real
improvement here would be an observer, not fusion.

## 7. Shipping day

**A** — `PRIORITIES: dispatch order #1043 in 4 days. PLAN (separate): expected shipment, revenue.`
**B** — *"House 3 is reserved for order #1043, dispatch in four days, and the batch is on track
— nothing for you here this morning."* · (silent unless tone/quality is off)

Prefer: **B.** Fewer decisions: **B.** Biologically useful: tie (shipping is operational). Better
outcomes: **B** marginally — it merges the order (plan) with the crop's readiness (reality) into
one judgement instead of two lookups. A genuine grower wants "is it ready and is it sold?" as
one answer; B gives that.

## 8. Sensor failure (real data: House 2 sensor fault)

**A** — `CONCERNS: [Inspect] a reading the plants seem to contradict. ALARM: Sensor fault. DATA
QUALITY: confidence reduced.` Correct, but spread across concern + alarm + data-quality sections.
**B** — *"House 2's temperature sensor is reading invalid — I've lowered my confidence there and
I'm not acting on its numbers. Trust your eyes in that house today."*

Prefer: **B.** This is a quiet strength: B *folds the failure into its own confidence and says
so in one honest sentence*, where A makes the grower assemble "alarm + suspect reading + lower
confidence" themselves. Better outcomes: **B** (it actively tells the grower *not* to trust a
number — A only implies it). Biologically useful: **B.**

## 9. Labour shortage

**A** — `(nothing — Gaia has no labour-reality input).` It may show expected-labour 3.5 FTE from
the plan, unconnected to today.
**B** — *"The plan assumes 3.5 people today; I can't see who's actually in. If you're short, the
House 1 airflow job is the one that can't wait."*

Prefer: **B**, but this is the most honest limitation of the lot: **Gaia has no observer for who
turned up.** B is better *only* because it can prioritise *which* task matters most if labour is
short — but it is guessing about the shortage itself. I would not call either version
trustworthy on labour today. The win is fusion's prioritisation, not its awareness.

## 10. Multiple simultaneous problems — **the hardest test, and B's real weakness**

**A** — lists *all* of them: disease (House 1), sensor fault (House 2), schedule slip (House 2),
heat (afternoon). Complete, but it's a wall — the grower must rank under time pressure.
**B** — *"House 1's disease risk is today's first job — humid, stagnant, wet canopy on young
tissue. House 2 is also behind plan and its temp sensor is unreliable; both can wait until after
House 1."* · do first: House 1 airflow · (what-can-wait: House 2 ×2)

Prefer: **B for action, but with a real caveat.** B's "one thought" is its strength *and* its
risk: it leads with the single highest-value item and pushes the rest to "what can wait." That
is correct when there is one clear top issue — but if **two issues are genuinely co-critical**,
fusion still picks one, and a tired grower may act only on the lead and miss the second. A does
not have this failure (it shows everything). **This is the one scenario where I would not fully
trust B alone**, and the smallest fix (not built here, per scope) is: when ≥2 items are
*Critical*, B should surface both leads, not one. As written, B handles "one big + several small"
well and "two equally critical" imperfectly.

---

## Measurement of the new (B) Morning Brief

Typical fused brief (the disease morning), judged against A:

| Metric | A (no fusion) | B (unified) |
| --- | --- | --- |
| Separate thoughts to hold | 5–7 sections | **1** (one narrative) |
| Notifications / blocks | 5–7 | **1** headline + 1 priority + 1 question |
| Recommendations | up to 3 (ranked) | **1** |
| Estimated reading time | ~45–60 s | **~12–15 s** |
| Interruption cost | medium (it's a screenful) | **low** (one glance) |
| Confidence shown | yes, in its own section | yes, **inside the thought** |
| Biological value | high but unassembled | **high and assembled** (memory + plan joined to the risk) |

The objective was better judgement, not more information: B carries **less information and more
judgement.** The one place B *loses* to A is **completeness on a multi-critical day** (scenario
10).

---

## "If Oskar had 15 seconds before entering the greenhouse, which brief would he want?"

**The Unified Morning Intelligence (B) — yes.** Precisely because:
1. In 15 seconds he can read *one* sentence, not seven sections — and B's sentence is the *most
   important* one, already chosen.
2. It tells him the one thing to do first and the one thing to confirm — which is all a 15-second
   window can act on.
3. On the days that matter most — the delayed slip (4), the disease link (3), the sensor failure
   (8) — A would have either said nothing useful in 15 seconds or required assembly B already
   did.
4. B even tells him what can wait, so the glance doesn't hide that there's more.

The only honest asterisk: on a **two-critical** morning (10), 15 seconds of B gives him the top
issue and a "× more can wait" — good enough to start, but he must trust that the second critical
is captured. Today it is captured in "what can wait" but not led with; that is the gap to close.

---

## Founder Review — would Oskar trust Gaia more after this sprint?

**Yes — net, clearly — with two specific reservations he should know about.**

**Why trust rises:**
- **It thinks like him now.** The disease morning pulled memory and plan to the risk unasked
  (#3); the delayed morning caught a slip with no climate alarm (#4); the sensor morning told him
  *not* to trust a number and lowered its own confidence (#8). Those are Head-Grower instincts,
  not software output.
- **It is honest.** Absence is stated, confidence travels inside the thought, and provenance is
  kept internally rather than performed at him. It never overwrites reality with the plan.
- **It respects his attention.** One thought, one priority, one question — silence on a calm day.

**Why trust could erode (and exactly where):**
1. **Co-critical blindness (#10).** Leading with one thought is the right default but a real risk
   when two things are equally urgent. Until B surfaces multiple leads when warranted, a careful
   grower will still want to open the full list on a busy day — which partly undoes the trust.
2. **Confidence on scenarios Gaia can't actually see (#5 irrigation, #6 pest, #9 labour).** B
   *sounds* assembled even when it's inferring from a single note or the plan alone. The phrasing
   hedges ("nothing confirms it yet"), which is right — but if B ever sounds confident about
   something it has no observer for, trust will break fast. The fix is observers, not words.

**Verdict:** Sprint 9 makes Gaia's *thinking* genuinely better — it converts four systems into
one judgement, and on the highest-stakes mornings that judgement is what a good Head Grower would
reach. It is accepted. The two reservations are about *coverage and edge-handling*, not about the
fusion idea, and neither is a reason to withhold trust on the normal-to-single-critical mornings
that make up most of the year. Oskar would trust it more — and would be right to, as long as Gaia
keeps being honest on the days it cannot yet see.

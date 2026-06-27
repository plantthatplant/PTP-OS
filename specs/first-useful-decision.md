# Spec — The First Useful Decision

**Status:** Draft v1 · the first operational workflow for Sprint 1 (for review before
implementation).
**Related:** [`specs/greenhouse-brain-v1.md`](greenhouse-brain-v1.md),
[`docs/cultivation-intelligence-model.md`](../docs/cultivation-intelligence-model.md),
[`docs/decision-philosophy.md`](../docs/decision-philosophy.md),
[`docs/biological-model.md`](../docs/biological-model.md)

> This document describes a **reasoning process**, not software. It is written so that a
> grower could follow it by hand, with no system at all, and arrive at a sound plan for the
> morning. If PTP OS does this well, it has delivered its first real value: **one better
> decision every morning.**

The question this capability answers:

> **"What should I do during the next two hours?"**

The previous spec answered *"How is the greenhouse today?"* — an assessment. This one turns
that assessment into **a ranked plan of action for the next two hours**, prioritised entirely
for the long-term health of the plants. It is the moment PTP OS stops describing and starts
helping.

---

## 1. Purpose and stance

A grower has limited hands, limited attention, and a crop that will not wait. The first
useful thing an intelligence can do is answer, honestly and well: *of everything I could do
in the next two hours, what should I actually do, in what order, and what can wait?*

Four commitments shape every part of this reasoning:

- **Optimise long-term plant health, never speed.** The plan is ranked by biological
  consequence, not by what is quick or easy. Effort is used only to *pack the two hours*,
  never to decide what matters. (Decision Philosophy.)
- **Prevention beats correction.** The highest-value morning work is usually the cheap action
  that stops tomorrow's expensive problem — not the visible fix for today's symptom.
- **Protect the most vulnerable and the whole population.** Unrooted cuttings, young roots,
  and the laggards of a batch carry more risk than the thriving average.
- **Doing nothing is a real, sometimes top, recommendation.** Patience with a recovering crop
  is an action, and over-reacting is a failure mode.

---

## 2. The reasoning process (followable by hand)

This is the mental sequence an excellent head grower runs on the morning walk. Each phase
states what the grower is doing and the internal questions PTP OS should ask in the same place.

### Phase 1 — Re-read the house and what changed overnight
Begin from the current state of the greenhouse (the "How is the greenhouse today?"
assessment) and from memory of the last few days.
- *Internal questions:* What changed overnight? What is different from previous mornings? What
  did the night and the coming day's weather just do, or are about to do, to the crop? Where
  is the crop most vulnerable right now?

### Phase 2 — Surface candidate actions, by type
List everything that *could* be done, sorted into the grower's natural categories. The
categories matter because they carry different priority:
- **Protect** — acute threats where delay causes fast or irreversible biological harm.
- **Prevent** — rising risks where a small action now avoids a large loss later.
- **Observe** — inspections that resolve uncertainty or catch the unusual early.
- **Progress** — time-bound steering and transitions (toning, spacing, taking cuttings).
- **Maintain** — necessary routine that tolerates timing.
- **Hold** — deliberate non-action where patience serves the plant.

*Internal questions:* Which plants need attention first? Is there anything that cannot wait?
Which actions reduce future problems rather than fixing current ones? Is there anything I
should inspect personally? Is anything unusual compared with previous days? Is there
uncertainty that should trigger a manual inspection?

### Phase 3 — Characterise each candidate
For every candidate, the grower forms eight judgements (the per-recommendation record in §3):
why it exists, the supporting information, the biological principles in play, the expected
outcome, the risk if ignored, confidence, effort, and value. Crucially this includes the
honest **confidence** in whether the issue is even real — because low confidence on something
that matters does not become an action, it becomes an *inspection*.

### Phase 4 — Rank for long-term plant health
Apply the ranking method in §4. The output is an ordered list, top to bottom, by biological
priority — independent of how quick or slow each item is.

### Phase 5 — Fit the two hours, defer the rest, flag the eyes-on
Walk down the ranked list:
- do the must-do-now items first, regardless of effort;
- fill the remaining time with the highest-value work that fits;
- give every deferred item an explicit *"safe to wait until ___"*;
- mark what the grower should **inspect personally**, and what uncertainty should **trigger a
  manual check before acting**;
- and if the best use of the next two hours is light — because the crop is settled or
  recovering — say so, rather than inventing busywork.

---

## 3. The record for every recommendation

Every recommendation PTP OS makes carries the same eight fields. This is the unit a grower can
read and judge.

| Field | What it answers |
| --- | --- |
| **Why this recommendation exists** | The biological situation that calls for it. |
| **What information supports it** | The evidence — conditions, observations, trends, memory — and how fresh and corroborated it is. |
| **Biological principles** | The cultivation reasoning that makes it sound. |
| **Expected outcome** | What improves for the plant if it is done. |
| **Risk if ignored** | What the plant loses, and how fast, if it is not. |
| **Confidence** | How sure we are it is real and that the action helps (Low / Medium / High). Low confidence + high stakes → inspect, don't act. |
| **Estimated effort** | Rough hands-and-time cost. Used only to schedule, never to rank. |
| **Estimated value** | Expected long-term plant-health benefit (Low / Medium / High / Critical). |

---

## 4. The ranking method

Rank by biological priority, in this order. This is a guide to judgement, not a formula — but
two growers following it should reach nearly the same plan.

**Rate three things for each candidate:**
- **Consequence** if the underlying issue is left unaddressed: None · Low · Moderate · High ·
  Severe (severe = irreversible loss or lasting damage to plant health/quality).
- **Window** — how fast it worsens or how soon an opportunity closes: Days · Today · Hours · Now.
- **Confidence** it is real and the action helps: Low · Medium · High.

**Then order by these tiers (higher tier always outranks lower):**

0. **Safety, legality, honesty — always first, never traded.** (Rarely the binding item in a
   two-hour crop plan, but it sits above everything.)
1. **Protect — cannot wait.** Acute threats whose *window* is Now/Hours and whose *consequence*
   is High/Severe and *irreversible if delayed* (a crop about to cook, drown, or wilt past
   recovery; an outbreak actively spreading). Rank within by severity × irreversibility of
   waiting.
2. **Prevent — the expensive future problem.** A small action now that removes a rising risk
   (the disease setup before any spot; the soft crop before a bright afternoon). Prevention
   outranks correction of equal stakes, because its leverage is higher and it defends long-term
   health. This is where a great grower spends their best morning attention.
3. **Inspect — resolve high-stakes uncertainty.** Where consequence is High but confidence is
   Low, *going to look* is itself a top action. Never act hard on thin evidence; never ignore a
   serious maybe.
4. **Progress — time-bound biology.** Steering and transitions with a closing window (toning
   before dispatch, taking cuttings, spacing before crowding harms). Rank by how soon the window
   shuts and the cost of missing it.
5. **Maintain — routine that tolerates timing.** Fill remaining time; defer freely with a date.
6. **Hold — deliberate non-action.** Named explicitly so the grower knows it was *considered and
   chosen*, not forgotten.

**Tie-breakers within a tier, in order:** higher long-term plant-health value → prevention over
correction → (for actions) higher confidence, but high-stakes + low-confidence routes to Tier 3
inspection → finally, value-per-effort, to choose among genuine equals.

**Speed is never a ranking criterion.** A slow, high-value action outranks a fast, low-value
one, always. Effort enters only in Phase 5, to pack the two hours.

---

## 5. Worked example — a real morning

So the method is concrete, here is one morning at a propagation-and-finishing nursery. Early
summer; a clear, bright, hot day is forecast; the night was cool and clear. The houses: **H1**
propagation (bench A: 2-day unrooted cuttings under mist; bench B: week-two cuttings just
rooting), **H2** young plants growing on (plus the mother-plant block), **H3** a finishing batch
reserved for a shipment in **four days**.

What the morning surfaces, each as a full record:

**A. Air is stagnant and humid in H1; dawn condensation lingering on bench B.**
- *Why:* Overnight humidity sat very high with almost no air movement; free water is sitting on
  young, soft foliage with no airflow to dry it. *Info:* H1 humidity high for several hours
  overnight, low air movement, visible canopy condensation past sunrise; this house has molded
  before in these conditions (memory). *Principles:* the disease triangle (susceptible young
  tissue + ever-present spores + a wet, still, warm microclimate); leaf-wetness *duration*
  drives infection; prevention over correction. *Expected outcome:* break the leaf-wetness and
  stagnation → infection risk falls sharply for pennies. *Risk if ignored:* Botrytis/
  damping-off can take a propagation bench in a day or two, and propagation losses are
  unrecoverable. *Confidence:* High (classic setup, corroborated by memory). *Effort:* Low
  (air movement on, a crack of venting as light rises, avoid re-wetting). *Value:* **Critical.**

**B. Bench A unrooted cuttings face a hot, bright afternoon.**
- *Why:* Cuttings with no roots cannot replace water lost to transpiration; a bright hot
  afternoon will push them past recovery if the mist/shade strategy isn't set *before* the peak.
  *Info:* clear hot day forecast; bench A is 2-day unrooted stock; current mist/shade set for a
  mild day (memory of yesterday's settings). *Principles:* a plant with no root has no buffer;
  protect the most vulnerable; *anticipate* the afternoon rather than react to the wilt;
  reversible/staged. *Expected outcome:* cuttings ride the peak turgid and keep forming roots.
  *Risk if ignored:* irreversible loss of the most fragile stock by mid-afternoon. *Confidence:*
  High. *Effort:* Low (set shade/mist for the peak now). *Value:* **Critical.**

**C. H3 finishing batch is still a touch soft, four days from dispatch.**
- *Why:* A batch that ships in four days isn't yet toned; cool nights are available to harden it
  so it travels and performs in the customer's hands. *Info:* H3 plants slightly soft/lush;
  dispatch in 4 days; cool clear nights in the forecast. *Principles:* toning/hardening as
  beneficial stress; quality is judged after dispatch (shelf life); the window is closing.
  *Expected outcome:* a firmer, more resilient plant that survives transport and the shelf.
  *Risk if ignored:* a soft batch ships, looks fine leaving, fails at the customer — the costliest
  kind of quality failure. *Confidence:* Medium-High. *Effort:* Low–Medium (begin cooler/drier/
  airflow regime; start today). *Value:* **High.**

**D. An H2 temperature reading looks oddly low — but the plants look fine.**
- *Why:* The reading disagrees with neighbouring zones and with the crop's healthy appearance;
  the sensor may be drifting or misplaced. *Info:* one zone reads cold; adjacent zones normal;
  plants turgid and normal-coloured (the plant, the ground truth, disagrees with the instrument).
  *Principles:* the plant leads the instruments; resolve uncertainty before acting; never chase a
  number the crop contradicts. *Expected outcome:* either a corrected/relocated sensor or a real
  cold spot found — either way, truth restored. *Risk if ignored:* acting on a false reading
  (heating a house that's fine) harms plants and wastes energy; or missing a real cold spot.
  *Confidence:* Low on the reading → **inspect.** *Effort:* Low (walk and check). *Value:*
  Medium (mostly protects against a wrong action).

**E. A few plants on H3's vent-edge look off-colour vs the block.**
- *Why:* Could be a harmless edge microclimate or the first sign of trouble; worth a 60-second
  look. *Info:* small number, near the vent edge, slightly off vs a uniform block. *Principles:*
  trouble has a geography (edges/vents); catch it while it's a whisper; read the population, not
  the average. *Expected outcome:* early catch or honest all-clear. *Risk if ignored:* a small
  real problem becomes a block-wide one. *Confidence:* Low → **inspect.** *Effort:* Very low.
  *Value:* Medium.

**F. Rooted batch in H2 is getting slightly crowded.**
- *Why:* Density is starting to cost light and airflow per plant; not yet harmful. *Info:* canopy
  beginning to close; no stretch or disease yet. *Principles:* space for quality and airflow; act
  before crowding does damage — but the window is days, not hours. *Expected outcome:* better
  light, airflow, uniformity. *Risk if ignored:* slow — stretch and disease risk over the coming
  days. *Confidence:* High. *Effort:* Medium (a real job). *Value:* Medium.

**G. Mother block is due a routine feed; cuttings could be taken.**
- *Why:* Routine upkeep and propagation supply. *Info:* schedule. *Principles:* steady mother-plant
  care; tolerant of a day's timing. *Expected outcome:* maintained productivity. *Risk if ignored:*
  negligible over a day. *Confidence:* High. *Effort:* Medium. *Value:* Low-Medium.

**H. A brief overnight temperature dip in H1 — already recovered; plants turgid.**
- *Why:* A transient excursion that self-corrected by dawn. *Info:* short dip overnight, normal by
  sunrise, crop turgid and unmarked. *Principles:* recovery is the diagnostic; transient ≠
  sustained; do not stack a correction on a plant that already recovered; avoid intervention
  whiplash. *Expected outcome:* none needed. *Risk if ignored:* none. *Confidence:* High. *Effort:*
  None. *Value:* **Hold — none.**

### The ranked two-hour plan

| Rank | Action | Tier | Value | Effort | Confidence |
| --- | --- | --- | --- | --- | --- |
| 1 | **B —** Set H1 bench-A mist/shade for the hot afternoon (protect unrooted stock) | Protect | Critical | Low | High |
| 2 | **A —** Break stagnation/leaf-wetness in H1, ease humidity as light rises (prevent disease) | Prevent | Critical | Low | High |
| 3 | **D + E —** Walk H2's cold reading and H3's vent-edge plants (resolve uncertainty) | Inspect | Med | Low | Low→ |
| 4 | **C —** Begin hardening the H3 dispatch batch (toning, window closing) | Progress | High | Low-Med | Med-High |
| 5 | **F —** Space the crowding H2 batch | Maintain | Med | Med | High |
| 6 | **G —** Feed mother block / take cuttings | Maintain | Low-Med | Med | High |
| — | **H —** Hold: do nothing about the recovered overnight dip (chosen, not forgotten) | Hold | — | None | High |

*Reasoning for the order.* Ranks 1–2 protect the most vulnerable stock and prevent an
unrecoverable loss; both are cheap and certain, and both must happen on this morning's walk
before the day's heat and the wet canopy do their damage — they top the list because of
*consequence and window*, not because they are quick (they happen to be). Rank 3 is an
inspection, placed high because two High-consequence items rest on Low confidence — the grower
goes and looks before trusting a number or acting on a hunch. Rank 4 is genuinely important but
its window is days, so it sits below the cannot-wait work. Ranks 5–6 are real but timing-tolerant
and are deferred with a date if the two hours fill. **H is listed and held** — naming the
non-action is part of the discipline.

*Fitting two hours:* items 1, 2, and 3 together are well under an hour and are done first. The
remaining time goes to starting 4 (high value, the window is closing). 5 and 6 are deferred —
*safe to wait until tomorrow* — and noted, not crammed in. Notice the plan never once used
"fast" as a reason; the quickest jobs rose to the top only because they also mattered most.

---

## 6. What would the world's best grower notice that a beginner would miss?

These are the hidden patterns that separate the plan above from a beginner's — the cues PTP OS
should eventually learn to recognise. A beginner reacts to what is loud and visible. A master
reads what is quiet and consequential:

- **The disease that hasn't happened yet.** A beginner sees a healthy bench; the master sees the
  *setup* — humidity, stillness, and lingering leaf wetness — and acts a day before the first
  spot. Most of protecting a crop is recognising favourable conditions, not symptoms.
- **The trouble that is still hours away.** A beginner waters when plants wilt; the master sets
  the afternoon's shade and mist at dawn, because they can feel the bright day coming for the
  rootless cuttings. The best action is often taken before the problem exists.
- **The running total of small insults.** A beginner remembers the one dramatic night; the master
  tracks the third mild humidity spike in a row, knowing accumulation can harm more than a single
  large event.
- **The plant that disagrees with the instrument.** A beginner trusts the number and heats the
  house; the master trusts the turgid, healthy crop and suspects the sensor. The plant is the
  ground truth; the readout is a proxy.
- **The recovering plant that must be left alone.** A beginner sees yesterday's stress and
  intervenes again; the master recognises a crop already on the mend and does *nothing*, because
  another change now would do more harm than patience.
- **The laggards, not the average.** A beginner judges the crop by its best plants; the master
  reads the weakest and the unevenness, because the batch ships — and fails — as a population.
- **The geography of trouble.** A beginner scans the middle of the block; the master checks the
  vent edge, the low damp corner, the densest patch — where problems always begin.
- **The closing window.** A beginner finishes a crop when it looks ready; the master starts
  toning four days out, because quality and shelf life are built in the days *before* dispatch,
  not on dispatch day.
- **The root before the leaf.** A beginner reads the canopy; the master reads the root zone and
  the newest growth first, where the plant shows its hand earliest.
- **The transient that needs no response.** A beginner chases every excursion; the master knows
  which dip is normal diurnal variation that recovered, and refuses to over-react — protecting
  both the plant and their own attention.
- **The cheap-now-versus-expensive-later trade.** A beginner does the satisfying visible job; the
  master does the small dull preventive one, because they price the future problem it avoids.
- **The morning light as the day's instruction.** A beginner runs yesterday's settings; the
  master reads the coming weather and steers the whole day to it before it arrives.

The thread: a beginner optimises the visible and the immediate; a master optimises the
*consequential and the long-term*, and reads *situations that precede problems* rather than
problems themselves. Teaching PTP OS to see these is teaching it to prioritise like a master.

---

## 7. Field procedure (the one-page version)

So a grower could literally carry this and follow it without any system:

1. **Walk and re-read.** What changed overnight? What is the day about to bring? Where is the
   crop most vulnerable?
2. **List what could be done**, tagging each: Protect · Prevent · Observe · Progress · Maintain ·
   Hold.
3. **For each, judge:** consequence if left (None→Severe), window (Days→Now), confidence
   (Low→High), and roughly its value and effort.
4. **Rank by biological priority:** safety first; then cannot-wait protection; then prevention of
   future problems; then inspect anything high-stakes you're unsure of; then time-bound progress;
   then routine; and name what you're choosing to hold. **Never rank by speed.**
5. **Fill the two hours** top-down: must-do-now first, then the highest-value work that fits;
   defer the rest with a "safe until" date; flag what to inspect personally; and if the crop is
   settled, keep the morning light.
6. **Remember** what you decided and why, so tomorrow you can see whether it worked.

---

## 8. Self-review

The test set for this document: **"If this document disappeared tomorrow, could another AI — or
another grower — still learn how a world-class grower prioritises work?"**

*First pass — honest weaknesses found:*
- The principles were clear, but a reader could not have *reproduced the ranking* — two people
  would have ordered the same morning differently. **Fixed** by adding the explicit ranking method
  (§4) with rateable axes and ordered tiers, plus tie-breakers.
- It risked being read as "rank by value/effort," which would smuggle speed back in. **Fixed** by
  separating *ranking* (biological priority, §4) from *scheduling* (effort, Phase 5) and stating
  plainly that speed is never a ranking criterion.
- It was abstract. **Fixed** by the worked morning (§5) showing eight real candidates, the eight
  fields each, and the resulting ranked plan with the reasoning for the order — including a held
  non-action.
- The "hidden patterns" risked being a list of cues with no organising idea. **Fixed** by naming
  the thread: beginners optimise the visible and immediate; masters optimise the consequential and
  long-term, and read situations that *precede* problems.
- It assumed a system. **Fixed** by the one-page field procedure (§7), so the reasoning is usable
  with nothing but a notebook.

*Answer after revision:* **Yes.** A reader with no other context could take §§2–4, work any
morning's observations through the records of §3, rank them by §4, schedule by Phase 5, and
arrive at a sound, health-first plan — and §6 would teach them what to *look for* to get better at
it. The document carries both the *method* and the *judgement* behind it.

*Remaining honest limits* (for the next revision, not blockers): the rating scales are
qualitative — they encode judgement, deliberately, rather than false numerical precision; and the
worked example is one crop-context — more worked mornings (a disease event, a heat emergency, a
quiet settled day) would broaden the learnable range. Both are improvements to add as the real
crop teaches us, consistent with keeping cultivation knowledge supple rather than frozen.

## 9. Open questions

1. **Where do the candidate observations come from in v1** (the same unresolved plant-observation
   source as the Greenhouse Brain spec)? Without human/plant observations, this workflow reasons
   mostly from environment and is honest about it.
2. **How is the two-hour window itself chosen** — fixed, or sensitive to the grower's day and the
   crop's urgency?
3. **Should deferred items auto-resurface** on the morning their "safe until" date arrives?
4. **How much should the plan adapt to the individual grower** — their skill, their crop knowledge,
   what they prefer to judge themselves?

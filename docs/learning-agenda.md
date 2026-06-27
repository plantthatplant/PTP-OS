# Gaia's Learning Agenda — becoming an apprentice Head Grower at Kålaberga

**Status:** Sprint 10 · learning design only. **No code, no engines, no architecture.** The
goal is that *every real greenhouse day improves Gaia* — not through new algorithms, through
experience.

## 0. Gaia already has a way to learn (build on it, don't rebuild it)

The learning loop exists: every recommendation becomes an **Experiment** with a testable
prediction; the day adds an action and outcome; the evening forms a **lesson** and moves
**confidence** up or down; it is kept forever as **memory**
([`lifecycle.py`](../app/greenhouse_brain/lifecycle.py),
[`store.py`](../app/greenhouse_brain/store.py)). And `prior_worth_by_kind()` already learns which
*kinds of questions* are worth asking. So Gaia can already turn outcomes into belief. This sprint
decides **what it should spend that machinery learning, in what order** — and which **hardcoded
assumptions** should be retired as reality teaches the truth.

The binding principle is Kålaberga's own (BIOLOGY.md): *"Generic species curves are priors, not
truth — the real response of this crop in this house is learned."* Everything below is the
disciplined application of that one sentence.

---

## 1. Assumption Audit — where Gaia assumes what reality could teach

Each row is a *prior currently hardcoded*. "Convert" = stop treating it as fixed; let the
learning loop replace it from Kålaberga's own outcomes.

| Assumption (today) | Where | Learnable? | Observable? | Measurable? | Verdict |
| --- | --- | --- | --- | --- | --- |
| **Climate targets per stage** (propagation 22–26 °C/70–85%; veg 20–24/60–75; finishing 18–22/55–70) | `snapshot_provider._TARGETS_BY_STAGE`, `claude_dispatch._CONFIG` | yes | yes (outcome vs setpoint) | yes | **Convert** — the single biggest prior; learn the *real* good per house × crop |
| **Disease-risk rule** (humid + stagnant + wet canopy ⇒ risk) | decision rules | yes | yes (did loss follow?) | partly | **Convert** — calibrate the trigger to Kålaberga's actual Botrytis events |
| **Heat-load threshold** (≥26 °C ⇒ high) | `get_outlook`/decision | yes | yes | yes | **Convert** — learn the crop's real heat tolerance & recovery |
| **Airflow bands** (vent ≤0 low, ≤40 normal) | `units.airflow_from_vent` | yes | yes | yes | **Convert (low priority)** — refine from canopy-drying outcomes |
| **VoI weights & interruption cost** (`_STAKES/_UNCERT/_DECISIVE`, cost 0.15, budget 3) | `knowledge_gap.py` | yes | yes | yes | **Partly converted** — `prior_worth_by_kind` learns; extend to per-grower interruption cost |
| **Confidence step size** (±1 ladder) & **confidence weights** (high 1.0/med .65/low .35) | `lifecycle.step`, `snapshot._CONF_WEIGHT` | yes | yes (calibration) | yes | **Convert** — learn how much an outcome *should* move belief |
| **Interruption spacing** (2 ticks, ×4 penalty) | `interaction_engine.py` | yes | yes (was it worthwhile?) | yes | **Convert** — learn Oskar's real tolerance |
| **Plan = medium confidence**; a missed plan date ⇒ "delay" | business observer / `plan_vs_reality` | yes | yes (actual propagation speed) | yes | **Convert** — learn real timelines so the plan's dates become trustworthy |
| **Sensor reliability** (fault alarm ⇒ low) | collector / provider | yes | yes (cross-observer agreement) | yes | **Convert** — build a per-sensor trust/drift map (e.g. Sensor Box 002) |
| **Afternoon outlook is a placeholder** | `domain.Outlook`, `get_outlook` | — | **yes (observe)** | yes | **Replace with observation** — a weather observer, not a guess |

**Roadmap consequence:** none of these should remain on the roadmap as *fixed numbers to tune by
hand*. They become **learning targets** (or, for the outlook, an **observation target**). Tuning
them in code is the anti-pattern; learning them from Kålaberga is the product.

---

## 2. The Learning Agenda (ranked by expected biological value)

For each: **current confidence**, **how reality improves it**, **which observer**, **how often**,
**expected time to learn**, **biological value**. Ranked highest-value first.

| # | Learning objective | Conf. now | How reality improves it | Observer | Cadence | Time to learn | Bio value |
| --- | --- | :--: | --- | --- | --- | --- | :--: |
| 1 | **Per-house × per-crop climate response** (the real "good") | Low | outcome (quality/speed) vs the setpoints actually run | Synopta (climate) + human (quality) | continuous + weekly | 1–2 seasons | **Very High** |
| 2 | **Disease progression** (when a wet canopy actually becomes loss) | Low | record each wet-canopy morning + whether Botrytis/damping-off followed | human/Companion (+ camera later) | per event | a handful of events (1 propagation season) | **Very High** |
| 3 | **Propagation speed** (rooting time per crop; the bench-A-vs-B gap) | Low–Med | log stick→root→ready dates per batch vs plan | human + Business Knowledge (plan) | per batch | 2–3 batches (~6–12 wk) | **High** |
| 4 | **Plant quality & readiness** (tone, uniformity, finish) | Low | grower's quality call at finish, vs climate history | human/Companion (+ camera) | weekly + at dispatch | 1 season | **High** |
| 5 | **Shipping/quality-after-dispatch** (quality in the customer's hands) | Low | dispatch outcome + any complaint, linked to the batch | dispatch record + customer (no observer yet) | per shipment | ~10–20 shipments | **High** |
| 6 | **Recovery dynamics** (after heat / after irrigation — the diagnostic) | Low | observe the stress event then track recovery time | Synopta + human | per event | several events | **Med–High** |
| 7 | **Bench productivity** (sellable plants / m² / cycle, per house) | Med | occupancy (plan) × actual finished count × area | Business Knowledge + dispatch | per cycle | 1–2 cycles | **Med** |
| 8 | **Sensor trust / drift** (which sensors to believe) | Med | cross-observer disagreement over time | Synopta vs human/camera | continuous | weeks | **Med** |
| 9 | **Interruption worth** (per kind, per grower) | Med | "was that worth asking?" already captured | Companion (Oskar) | every interaction | days–weeks (fast) | **Med** |
| 10 | **Heat-stress tolerance** (the real threshold for these crops) | Low | hot days + observed damage/none + recovery | Synopta + human | per hot spell | 1 summer | **Med** |
| 11 | **Labour efficiency** (tasks per FTE vs the 3.5-FTE plan) | Low | who worked, what got done | (no observer yet) | daily | a season | **Low–Med** |
| 12 | **Customer complaints** (the hardest, most honest quality signal) | Low | complaints linked back to batch/house | (no observer yet) | per complaint | a year | **Med (gated)** |

**Reading the ranking:** the top of the list (climate response, disease, propagation speed,
quality) is where Kålaberga's outcomes most change Gaia's *biological* judgement. The bottom
(labour, complaints) is high-value but **gated on observers Gaia does not yet have** — so they
are learning objectives *and* observation requests, not things code can unlock.

---

## 3. Learning Dashboard (design, not implementation)

A calm, one-screen view — the grower's window into *Gaia's own apprenticeship*. It answers four
questions, from data the learning loop already writes (experiments, lessons, confidences,
question-evals); **nothing new is built — this is the view.**

```
 GAIA — LEARNING (this month)
 ─────────────────────────────────────────────────────────────
 ▸ GOT BETTER AT            confidence ↑ this month
     House 1 disease timing   Low → Medium   (3 events, 2 predictions held)
     Pentas rooting time      Low → Medium   (2 batches logged)
 ▸ STILL UNCERTAIN          biggest gaps by value
     Real climate setpoints (House 2, Viola)        confidence Low
     Quality-after-dispatch                         confidence Low (no signal yet)
 ▸ CURRENTLY LEARNING       open experiments
     5 open · 12 closed · 9 lessons kept
     next due: House 2 schedule slip (confirm vs plan)
 ▸ WOULD ACCELERATE LEARNING   the cheapest uncertainty to close
     1 grower confirmation (canopy wet?) · 1 finish-quality note (House 3)
     [later] 1 camera count to calibrate occupancy vs plan
```

Design rules: it shows **trends, not raw data**; it is honest about what is *not* yet learnable
(no observer → "no signal yet", never a fabricated score); and "would accelerate learning" is
exactly the Observation-Planner question (which observation, by whom, would most reduce
uncertainty) — surfaced for the grower, never auto-acted. It is a *read*, on the phone/desktop,
never an interruption on the glasses.

**Calibration is the trust metric.** The one number worth watching: *of the predictions Gaia
made, how many held?* A rising hold-rate is proof the apprentice is learning; a flat one says it
is guessing. That belongs at the top of this dashboard once enough experiments have closed.

---

## 4. One year inside Kålaberga — what Gaia should then know (ranked by founder value)

If Gaia spends a year here, observing every day, it should know what it cannot today:

1. **The real setpoints — what "good" actually is for each house × crop.** The generic curves
   replaced by Kålaberga's own learned response. *Founder value: the highest — it makes every
   morning's reasoning true rather than textbook.*
2. **Trustworthy timelines.** Real rooting and finishing times per crop, so the production plan's
   harvest/shipment dates stop being hopeful and become reliable — and "behind plan" means it.
3. **Calibrated disease early-warning.** When a wet canopy at Kålaberga actually becomes loss
   (and when it safely doesn't), so the disease prompt fires on the real risk, not the rule.
4. **Which crops truly pay.** Profitability (the STJARNA/HUND portfolio) confirmed against real
   yield, quality, and space use — so space goes to what earns it.
5. **A quality memory.** What climate history produced sellable, well-toned plants vs soft or
   uneven ones — the link from how it was grown to how it shipped.
6. **A sensor trust map.** Which instruments to believe, which drift (Sensor Box 002 and its
   kin), so Gaia weighs evidence correctly without being told.
7. **Oskar's own working rhythm.** When he wants to be interrupted and when not — so the silence
   is tuned to him, not to a constant.
8. **Recovery signatures.** How these crops bounce back from heat and irrigation stress — the
   diagnostic that separates training stress from harm.
9. **(Gated) Labour and customer truth.** Real task throughput and real complaints linked to
   batches — high value, but only once those observers exist.

The shape of the year: **#1–#3 are the apprenticeship.** A Head Grower earns trust by being
reliably right about *this* greenhouse's climate, timing, and disease — and that is precisely
what a year of Kålaberga's outcomes, fed through the existing learning loop, would teach Gaia.

---

## 5. The one honest constraint

**Learning is gated by observation.** Gaia can only learn what some observer reports the outcome
of. Today it observes climate (Synopta), the grower (Companion), and intention (Google Drive) —
so objectives 1–3, 6, 8, 9 can start *now*, with no new code. Objectives 4–5, 10–12 need a
quality/dispatch/labour observer before reality can teach them. So the most valuable *non-code*
investments this year are: (a) **Oskar logging finish-quality and propagation milestones** as
spoken notes (he already can), and (b) **a dispatch/complaint record** feeding back to the batch.
Those two habits would unlock most of the agenda — no engine required, exactly as this sprint
intends.

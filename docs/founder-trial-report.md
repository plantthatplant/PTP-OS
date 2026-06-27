# Founder Trial Report — Gaia at Kålaberga (Sprint 8)

**One question governs everything here:** *would Oskar voluntarily keep using this tomorrow?*
This report is grounded in a real instrumented run of the full day
([`companion/daily.py`](../companion/daily.py)) on Kålaberga's morning snapshot, not a mock-up.

**Honest setup caveats (so the findings are trustworthy):**
- The day ran on the **greenhouse PC** with the **rich morning snapshot**; the live screen-read
  snapshot is thinner (outside-weather only) until Synopta export/API is enabled.
- The **glasses are simulated as a one-line preview** (Even SDK terms still unconfirmed). The
  *experience and the data are real*; the *device transport is not yet*.
- No new engines or architecture were built — only integration, friction cuts, and
  instrumentation, per the sprint.

---

## 1. Founder Trial Report

**The day, as it actually ran:**

| Phase | What happened | Verdict |
| --- | --- | --- |
| 06:30 Morning brief | Phone: one short summary + the single priority (House 1 disease risk, with action + confidence). Glasses: **one line** ("Kålaberga: watch House 1"). ~30s read. | **Keep** — the reason to engage |
| 07:00 Walking inspection | Silence at House 3; **one earned question** at House 1 ("canopy wet?"). Oskar: *no*. Gaia stood down its own disease-risk concern. | **Keep** — the day's best moment |
| 08:30 Propagation | Silent. A spoken note captured with **no follow-up prompt** ("✓ Noted."). | **Keep** |
| 10:00 Shipping | Silent; on a *pull* ("how is House 3?") returned one line. | **Trim** — answer was filler |
| 12:00 Unexpected problem | **One alert line** (House 2 sensor fault, real, from Synopta) + detail on phone. | **Keep** — exactly what a grower wants surfaced |
| 14:00 Second inspection | Silence (spacing held; nothing new worth a word). | **Keep** |
| 17:00 Evening review | Phone: day reviewed, House 1 confidence Medium→Low (a false alarm stood down), one note. | **Keep** |

**Measured (this run):** 1 question asked · 1 held (silenced) · 0 unanswered · **2 interruptions**
(1 question + 1 alert) · 1 note · **5 phone cards (~100 words, ~30s reading)** · 2 walking phases ·
**~12 min time saved (est.)** · 1 confidence move · 2 interactions remembered.

**Would Oskar keep using it tomorrow? — Yes, for four of the five core things.** The morning
brief (30s vs a ~12-min manual scan), the single canopy question, the real sensor-fault alert,
and the calm silence all earned their place: each changed what he'd do or saved a check. The
spoken note is a *yes* **only once voice works on the real device** (gated). The shipping pull is
a *no* in its current filler form. Net: **the spine is genuinely useful today; two things need
trimming and the device/data gates need closing.**

---

## 2. Friction Report

**Cuts already made this sprint (and felt in the numbers):**
- Removed the morning "questions I may ask" list from the phone — pure reading, zero action.
- Dropped the "Photo? (phone)" prompt after a note — a note is now one silent ack.
- Trimmed the priority card (no "if-ignored" wall in the daily view).
- **Fixed the biggest one mid-trial:** the morning glasses showed *four stacked lines*; now it
  is **one line**. (Reading on the glasses is the cardinal sin; it's gone.)
- Kept the entire mid-day silent unless something was genuinely worth a word.

**Remaining friction (ranked):**
1. The morning phone **summary sentence is still ~2 lines** — could be one.
2. The **shipping pull** returns generic text ("settled, dispatch on track") — friction without
   value; should say "nothing notable" or nothing.
3. **No day-to-day continuity yet** — yesterday's note and the stood-down concern don't shape
   today's brief, so Oskar carries that memory, not Gaia.

**Friction score: low.** Total reading ~30s; interruptions 2, both earned; typing 0; menus 0.

---

## 3. Biggest annoyance

**The morning used to read like a screen, on the glasses.** Four lines stacked on a 27.5° HUD is
not a glance — it's homework. *(Fixed this sprint: morning glasses is now one line; the brief
lives on the phone.)* If one annoyance remained, it's the **filler pull answer** — Gaia speaking
to fill a silence it should have kept.

---

## 4. Biggest surprise

**The most valuable moment was Gaia being wrong — and being corrected.** The single canopy
question let Oskar *stand down a false Botrytis alarm* (confidence Medium→Low). The value wasn't
Gaia telling him something; it was Gaia **asking, listening, and dropping its own concern.** And
the instrument **mis-measured it**: "confidence gained" counts only up-steps, so the day's best
outcome registered as **+0**. We were measuring the wrong direction.

---

## 5. What Gaia should STOP doing

1. **Stop speaking to fill silence** (the generic shipping answer) — say "nothing notable" or
   nothing.
2. **Stop counting only confidence-*up* as value** — standing down a false alarm is a win, not a
   zero.
3. **Stop putting more than one line on the glasses, ever** — already enforced for the morning;
   keep it enforced everywhere.
4. **Stop showing the full action sentence on the glasses** (it truncates) — the phone has room.

---

## 6. What Gaia should START doing

1. **Carry the day across days.** Yesterday's note ("mother stock prime") and the stood-down
   House 1 concern should shape *today's* brief and today's one question ("yesterday the canopy
   was dry — still dry?"). This is the learning loop's whole point and needs no new engine — just
   reading the memory Gaia already writes.
2. **Measure value both directions** — track *uncertainty reduced* (false alarms avoided count).
3. **Answer pulls honestly** — "nothing notable in House 3" beats filler.
4. **Offer "why?" on demand** (phone) instead of pushing reasoning in the morning.

---

## 7. Top ten improvements, ranked by real founder value (7-day, no new engines/hardware)

| # | Improvement | Why it makes tomorrow better | Effort |
| --- | --- | --- | --- |
| 1 | **Day-to-day continuity** — yesterday's note + stood-down concern feed today's brief & question | Turns Gaia from a daily reset into a colleague who *remembers*; the single biggest "keep using it" lever | M (reuse memory) |
| 2 | **Run on the live snapshot daily** (screen-read/Collector), not the sample | Makes it *real*, not a demo | S (wire path) |
| 3 | **Honest pulls** — "nothing notable" instead of filler | Protects trust; a colleague who only speaks when it helps | S |
| 4 | **Measure value both directions** (false alarms avoided) | We can't improve what we mis-measure | S |
| 5 | **One-line morning summary on phone too** (tighten the read to ~15s) | Less reading, same value | S |
| 6 | **Alert hygiene** — only new/actionable alarms; suppress repeats of the same fault | The sensor-fault alert is gold; a repeated one is noise | S |
| 7 | **"Why?" on demand** (ring → phone), not pushed | Less morning reading; depth when wanted | M |
| 8 | **Confirm the Even SDK** so the one-line glasses path is real | Unblocks the actual on-glasses trial | M (external) |
| 9 | **Note reliability** — voice round-trip + quick edit on phone | Capture is only worth it if it never drops a word | M |
| 10 | **Weekly value digest** (questions asked/held, minutes saved, false alarms avoided) | Lets Oskar *see* the value accruing — drives the habit | S |

**The three that decide the trial:** #1 (continuity), #2 (live data), #3 (honest pulls). Ship
those this week and Gaia stops being a thing Oskar tries and becomes a thing he reaches for.

---

## What was built this sprint (only friction + instrumentation)

- **Instrumentation** ([`companion/metrics.py`](../companion/metrics.py)) — the day measured:
  questions asked/held/unanswered, interruptions, reading time, walking phases, confidence moved,
  recommendations, interactions remembered, time saved; persisted to `data/day-metrics.jsonl`.
- **The integrated day** ([`companion/daily.py`](../companion/daily.py)) — all seven phases in one
  runner, with the friction cuts above, on real data, routed by *phone = information, glasses =
  interruption*.

No architecture, no new engines, no speculative features, no future hardware — as required. The
54 collector + 11 companion tests still pass.

# Gaia's First Working Day at Kålaberga

An **operational walkthrough**, not a new design. It introduces no architecture and invents no
system — it sequences the components Gaia already has into one complete working day, 06:00 to
18:00, as if Gaia were employed today as the Head Grower at Kålaberga. Where the day needs
something that does not yet exist, it flags the **smallest possible addition** and nothing more.

The point is to prove a simple thing: **Gaia can complete one entire working day.**

> Components used (all existing): the Greenhouse Snapshot + importer; the Morning Analysis
> (Context → Decision → Curiosity engines); the Decision Library (recall); the recommendation
> lifecycle (`Experiment` → memory); the Morning Brief, Walk, and Evening Review (`gaia
> morning/walk/evening`); the Daily Grower Dialogue; the Daily Operating Cycle's tempos; and the
> Decision Philosophy's rules on attention, confidence, and silence.

The house: **Kålaberga** — H1 propagation (aroid cuttings), H2 growing-on (+ the mother stock),
H3 finishing (batch reserved for order #1043, ships in 4 days).

---

## 05:50 · Before anyone arrives — *prepare*

Gaia starts the day alone, in the dark, the way a head grower who came in early would.

- **It takes in reality.** It ingests the latest **Greenhouse Snapshot** (climate, equipment,
  whatever human/plant observations exist), honest about what is missing.
- **It thinks.** It runs the **Morning Analysis** — assembles context, infers the latent biology
  (Plant State, Stress, Disease Risk), and produces the day's concerns, opportunities, and
  priorities. *Nothing here is new; it is the Sprint-1 pipeline on the latest Snapshot.*
- **It opens the day's experiments.** Every recommendation becomes an **Experiment** record
  (observation → reasoning → recommendation → expected outcome → confidence), per the lifecycle.
- **It consults its memory.** For each priority it **recalls the Decision Library** (`↻`): *"last
  time House 1 looked like this, we vented early, it worked, confidence now medium-high."*
- **It reviews its curiosities.** It evolves the persistent curiosities and picks the few worth a
  look today.
- **It prepares the few questions that matter** for the walk (confirm what it can't see, scout a
  real risk, follow a curiosity, close yesterday's due experiments).
- **It assembles the Morning Brief** — calm, prioritised, explained.

> **What happens before anyone arrives:** Gaia observes, reasons, opens experiments, recalls
> experience, evolves curiosities, and writes the brief. **And then it waits.** It sends nothing.
> The brief sits ready for 08:00. Silence is the default; the grower's attention is not yet spent.

*Smallest addition needed:* a **05:50 trigger** to run this unattended (today `gaia morning` is
run by hand). See §Additions.

---

## 06:00–08:00 · The house wakes — *hold and watch*

The crew is not in yet. Gaia keeps **observing** on the fast loop — new Snapshots as they arrive —
and compares them against the morning's picture. It does **not** interrupt.

> **When Gaia stays silent:** almost always. Through these two hours it says nothing, because
> nothing it could say would change a decision before the grower arrives.
>
> **The one exception — when Gaia notifies:** if a genuinely acute, *action-changing* threshold
> crosses before anyone is in (a heating failure, a cold-night excursion past the safety floor for
> the propagation house), Gaia sends **one** calm notification — per the rule *"only interrupt when
> action changes the outcome, and never twice for the same thing."* This morning, nothing crosses.

*Smallest addition needed:* a **push channel** for that rare interruption (today Gaia is pull-only).

---

## 08:00 · The grower arrives — *brief and explain*

The grower opens to the **Morning Brief**: the one-line state of Kålaberga, the **three priorities**
(H1 disease prevention; protect the H1 cuttings before the afternoon; inspect the odd H2 reading),
the **opportunity** (take cuttings from the vigorous H2 mother stock), the **curiosity** (bench B
keeps lagging bench A), the **few walk questions**, and the honest **reality confidence / coverage**.
Each item shows its reasoning, so the brief also *teaches*.

- The grower can **accept, modify, or reject** any recommendation; each reaction is recorded as the
  first step of that experiment (decision-capture).
- Gaia answers follow-ups **if asked**. Otherwise it stays quiet. It does not narrate.

---

## 08:15 · The morning walk — *ask, but only what matters*

As the grower walks the crop, Gaia asks its **few prepared questions**, one at a time, in plain
words — this is **when Gaia asks questions**, and almost the only time it does:

- *"House 1 — did you see condensation or a wet canopy?"* (confirm an inference it can't see)
- *"House 2 — do the plants actually look off, or just the reading? Any pests?"* (scout / ground-truth)
- *"Bench B — still running behind A? Any difference in the medium?"* (follow the curiosity)

The grower answers naturally. Each answer is **stored as evidence** (a Snapshot observation,
verbatim preserved) and can **update today's picture on the spot** — a confirmed wet canopy *raises*
the H1 disease priority and its confidence; a clean "no pests" *lowers* a risk. The curiosity's
suggested observation is gathered here, nudging it from Open toward Investigating.

> **When Gaia asks:** on the walk, the few questions whose answers change a decision or advance a
> lesson — and nowhere else. A settled morning would ask nothing at all.

---

## 10:00 · Mid-morning — *monitor; mostly silence*

Gaia keeps watching the incoming Snapshots against the morning's predictions (the fast loop).

- **Silence is the rule.** It does not report that things are fine.
- **It notifies only if a decision changes.** The morning predicted a hot, bright afternoon for the
  rootless H1 cuttings. As the light climbs and that prediction firms up, *if the protective shading
  has not been set*, Gaia sends **one** quiet nudge: *"the H1 cuttings will want their shade within
  the hour."* If the grower already handled it on the walk, Gaia says nothing.

> **What decisions Gaia postpones:** anything **low-confidence and not urgent** (it waits and
> re-observes rather than act or pester); anything whose **window hasn't arrived** (H3 toning is a
> days-long call, not today's); and anything **awaiting evidence** (the H2 sensor verdict waits on
> the grower's walk finding). Postponed items are tracked as open experiments, not forgotten.

*Smallest addition needed:* a **midday monitoring pass** that re-imports the latest Snapshot,
compares it to the morning's open experiments, and decides whether one notification is warranted —
reusing the existing engines. See §Additions.

---

## 12:00 · Midday — *re-evaluate against the peak*

At the day's heat-and-light peak, Gaia re-checks the **vulnerable** first (the propagation house).

- If the protective action was taken and the cuttings are riding the peak turgid → **silence**, and
  it quietly notes the favourable evidence against the experiment.
- If a morning prediction is **drifting** (the canopy never fully dried), it does not raise an alarm;
  it **notes it for the evening review** and, only if it now changes an action, sends one nudge.
- It continues to **postpone** the days-window calls (toning, the cuttings opportunity) — their time
  is not now.

---

## 13:00–16:00 · Afternoon — *gather outcomes quietly; update memory as it learns*

Through the afternoon Gaia is mostly silent and mostly *watching outcomes become observable*.

- The H1 disease-prevention window (hours) closes: the later Snapshots show humidity fallen and the
  canopy dry. Gaia records this as the **observed outcome** against that experiment — **memory is
  updated continuously, as outcomes become observable**, not only at day's end.
- The cuttings held through the peak: another experiment's outcome, captured.
- Nothing that does not change a decision is surfaced. The grower works undisturbed.

> **When Gaia updates Memory:** incrementally through the day as each experiment's window closes and
> its outcome becomes observable — and definitively at the evening close (below).

---

## 17:30 · Evening Review — *learn and reflect*

As the day ends, Gaia produces the **Evening Review** automatically — the comparison, for every
recommendation that came due today:

> Morning expectation → Action taken → Observed outcome → Lesson → Updated confidence

- For outcomes it observed itself (the disease canopy drying), it fills them in. For anything it
  could not see, it asks the grower the end-of-day **"what actually happened?"** — a few close
  questions, no more.
- It forms a **lesson** for each, and moves **confidence** up or down (a held prediction nudges it
  up; a surprise teaches most).
- **It updates Memory definitively:** each closed experiment becomes a **permanent memory** in the
  Decision Library, its confidence trajectory extended.
- **It evolves the curiosities:** the day's evidence moves bench-B's lag from Open toward
  Investigating (or, if the medium difference explained it, toward Confirmed/Rejected).
- **It checks itself:** were today's predictions calibrated? (the quiet reward that makes tomorrow's
  confidence trustworthy.)

> **When Gaia reviews today's outcome:** at the evening review — having already gathered much of the
> evidence quietly through the day.

---

## 18:00 · Hand-off to tomorrow — *what tomorrow inherits*

Gaia closes the day by deciding **what is sent to tomorrow's Morning Brief**:

- **Carried-open experiments** — H3 toning and the mother-stock cuttings (days-long windows) stay
  open and become **tomorrow's walk close-questions**.
- **Updated memory and confidence** — today's new memories mean tomorrow's `↻` recall on a similar
  House 1 will speak with a little more earned certainty.
- **Open / Investigating curiosities** — carried forward as tomorrow's curiosity candidates, with
  their suggested observations queued for the walk.
- **Postponed decisions** with a "safe until" date — resurface on the morning they come due.
- **Today's Snapshot and accumulated observations** — become the **baseline for tomorrow's
  change-detection** ("what changed overnight").

Then Gaia goes quiet for the night. The slow loop has already done its work — the learning is
written. Nothing more is invented; tomorrow it simply runs the same day again, a little wiser.

---

## The day's questions, answered at a glance

| Question | Answer |
| --- | --- |
| **What happens before anyone arrives?** | Observe the Snapshot, run Morning Analysis, open experiments, recall the Library, evolve curiosities, write the brief — then wait, silently. |
| **What does Gaia prepare?** | The Morning Brief, the day's experiments, the recalled precedent, and the few walk questions. |
| **When does Gaia ask questions?** | On the morning walk, the few that change a decision or advance a lesson — and almost nowhere else. |
| **When does Gaia stay silent?** | By default — through the night, the early morning, and all afternoon — whenever nothing it could say would change a decision. |
| **When does Gaia notify the grower?** | Only when an action-changing situation crosses (an acute risk, a prediction firming that needs action now) — one calm message, never twice. |
| **What decisions does Gaia postpone?** | Low-confidence non-urgent calls, days-window calls (toning), and anything awaiting evidence — all tracked as open experiments. |
| **When does Gaia update Memory?** | Continuously as outcomes become observable through the day, and definitively at the evening close. |
| **When does Gaia review today's outcome?** | At the 17:30 Evening Review, on evidence largely gathered quietly during the day. |
| **What is sent to tomorrow's Morning Brief?** | Carried experiments, updated memory/confidence, open curiosities, postponed decisions, and today's Snapshot as the new baseline. |

---

## What was missing — the smallest additions (nothing more)

The *reasoning* of the whole day already exists. To run it as a real employee, unattended, three
pieces of **operational glue** are missing — small, and not architecture:

1. **A daily scheduler/trigger.** Today `gaia morning / walk / evening` are run by hand. The
   smallest addition is a clock that fires the existing commands (05:50 prepare, a midday pass, 17:30
   review) and refreshes the Snapshot — exactly the file-drop/cron bridge already identified in the
   Dispatch investigation. No new logic.
2. **A midday monitoring pass (`gaia midday`).** A thin command that re-imports the latest Snapshot,
   re-runs the existing Morning Analysis, compares it to the morning's open experiments, and decides
   whether *one* notification is warranted. It introduces no engine — only the "compare to this
   morning and decide whether to speak" step.
3. **A single notification channel.** So Gaia can deliver that rare action-changing nudge (and stay
   silent otherwise). The prototype is pull-only; the smallest addition is one push sink, gated by the
   existing notification rule ("interrupt only when action changes the outcome").

Everything else in this day — the observing, reasoning, recommending, asking, learning, remembering,
and the discipline of silence — is already built or specified. Gaia can complete a working day. These
three small pieces let it do so without a human running the commands.

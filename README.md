# PTP OS

**An AI-native operating system for professional greenhouse production.**

PTP OS is a digital greenhouse intelligence that helps growers make better
decisions, improves plant quality, reduces manual analysis, and continuously
learns from experience. It is built for Plant That Plant first, and designed to
eventually serve other professional growers.

This repository is the **single source of truth** for PTP OS. Product direction,
architecture, domain model, decisions, and specifications all live here. If it is
not written down here, it is not yet part of PTP OS.

---

## Start here

| If you want to understand... | Read |
| --- | --- |
| Why PTP OS exists | [`docs/vision.md`](docs/vision.md) |
| How PTP OS understands plants | [`docs/biological-model.md`](docs/biological-model.md) |
| How PTP OS should think | [`docs/decision-philosophy.md`](docs/decision-philosophy.md) |
| How the best growers think | [`docs/cultivation-intelligence-model.md`](docs/cultivation-intelligence-model.md) |
| How PTP OS runs through a day | [`docs/daily-operating-cycle.md`](docs/daily-operating-cycle.md) |
| How Gaia learns over years | [`docs/gaia-learning-loop.md`](docs/gaia-learning-loop.md) |
| How we work | [`docs/project-rules.md`](docs/project-rules.md) |
| How the system is structured | [`docs/architecture.md`](docs/architecture.md) |
| How Synopta data reaches Gaia | [`docs/gaia-collector.md`](docs/gaia-collector.md) |
| How Gaia walks the greenhouse with you | [`specs/field-companion.md`](specs/field-companion.md) |
| What we are building and when | [`docs/roadmap.md`](docs/roadmap.md) |
| The concepts the system reasons about | [`domain/`](domain/) |
| Why key decisions were made | [`adr/`](adr/) |
| Proposed architecture changes under discussion | [`rfc/`](rfc/) |
| How a component must behave | [`specs/`](specs/) |
| Project terminology | [`docs/glossary.md`](docs/glossary.md) |

---

## Repository layout

```
ptp-os/
├── docs/           Product & engineering documentation (vision, rules, architecture, roadmap)
├── specs/          Technical specifications — written before any feature is implemented
├── domain/         The domain model: the entities PTP OS reasons about
├── adr/            Architecture Decision Records — the "why" behind structural choices
├── rfc/            Requests for Comments — proposed architecture changes under review
├── prompts/        Versioned prompts (one prompt = one feature)
├── integrations/   External data providers and services (Claude Dispatch today, Synopta tomorrow)
├── services/       Internal engines and supporting services (Context, Decision, Language, Memory, ...)
├── app/            The first working Greenhouse Brain (Sprint 1 prototype)
├── collector/      Gaia Collector — local Synopta → Canonical Snapshot bridge (+ its tests)
├── companion/      Gaia Field Companion — device-independent walk interface (+ its tests)
└── data/           Runtime output the Collector writes and Gaia reads (generated; git-ignored)
```

Each folder contains its own `README.md` explaining its purpose and conventions.

## Run it

The first working capability — ask the greenhouse how it is:

```
python3 app/ask.py "How is the greenhouse today?"
```

No install, no dependencies, no API keys. It runs the full reasoning pipeline on mock
data and returns a summary, three priorities, one concern, one recommendation, and a
confidence. See [`app/README.md`](app/README.md) and
[`docs/sprint-1-shortcuts.md`](docs/sprint-1-shortcuts.md).

Collect greenhouse data from Synopta into the Canonical Snapshot Gaia consumes:

```
python collector/demo_pipeline.py    # Synopta → Collector → Snapshot → Gaia, end to end
```

Walk a whole day with the Founder Companion (phone brief + silent glasses walk + evening):

```
python companion/daily.py            # Oskar's day across phone + Even G2 surfaces
```

See [`collector/README.md`](collector/README.md), [`docs/gaia-collector.md`](docs/gaia-collector.md),
and [`specs/gaia-collector.md`](specs/gaia-collector.md).

---

## The architecture in one line

```
Reality → Provider Layer → Context Engine → Decision Engine → Language Engine → User
```

Supporting services: Memory Engine, Decision Library, Knowledge Platform, Morning Intelligence.

The **Provider Layer** isolates the rest of the system from where greenhouse data
comes from. Today it is backed by Claude Dispatch; tomorrow by the Synopta Pro
API. That swap must not change anything downstream. See
[`specs/greenhouse-provider.md`](specs/greenhouse-provider.md).

---

## How we build

These principles are non-negotiable and explained in
[`docs/project-rules.md`](docs/project-rules.md):

- Biology before technology.
- Build trust before automation.
- One prompt = one feature.
- Every Friday should demonstrate real value.
- AI should explain its reasoning.
- AI should learn from outcomes.
- Keep interfaces calm and simple.
- Business logic stays independent of any AI model. The AI provider is always replaceable.

---

## Project status

**Sprint 0 — Foundation (complete).** Repository structure, core documentation, the
domain model, the founding ADRs, the intelligence canon (biological model, decision
philosophy, cultivation intelligence, daily operating cycle), and the greenhouse
provider specification.

**Sprint 1 — First working Greenhouse Brain (in progress).** A grower can ask *"How
is the greenhouse today?"* and receive a useful, health-first answer from the full
reasoning pipeline running on mock data (`app/`). Shortcuts taken — and what replaces
them (Synopta, plant observations, Memory Engine, Decision Library) — are recorded in
[`docs/sprint-1-shortcuts.md`](docs/sprint-1-shortcuts.md).

See [`docs/roadmap.md`](docs/roadmap.md) for what comes next.

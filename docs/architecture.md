# Architecture

> Status: v1 (Sprint 0). This document describes the agreed architecture. Proposed
> changes are not edited in here directly — they go through an
> [RFC](../rfc/) and, once accepted, an [ADR](../adr/) before this document is
> updated.

## Overview

PTP OS turns greenhouse **reality** into **trusted, explained guidance** for the
grower, and learns from what happens next. It is organized as a one-directional
pipeline with supporting services around it.

```
            ┌─────────────────────────────────────────────┐
            │                  Reality                     │
            │  climate, plants, people, orders, weather…   │
            └─────────────────────┬───────────────────────┘
                                  │
                          Provider Layer            ← all external systems enter here
                                  │   (maps external data → Domain Model)
                                  ▼
                          Context Engine            ← assembles the relevant picture
                                  │
                                  ▼
                          Decision Engine           ← reasons; produces Recommendations
                                  │
                                  ▼
                          Language Engine           ← explains in calm, clear language
                                  │
                                  ▼
                                User                ← Morning Intelligence / G2 glasses

  Supporting services (used across the pipeline):
  Memory Engine · Decision Library · Domain Model · Morning Intelligence
```

## Layers

### Reality
Everything happening in and around the greenhouse: climate, plant development,
people and tasks, orders and shipments, weather and energy. PTP OS never touches
reality directly — only through providers.

### Provider Layer
The single entry point for every external system. A provider's job is to answer a
question about reality and return it **as the [Domain Model](../domain/)** — never
in a vendor's own shape. This is what keeps the rest of the system independent of
any specific source.

- Greenhouse data: `ClaudeDispatchProvider` today → `SynoptaProvider` later.
- Future providers: Shopify (commerce), Fortnox (finance/HR), Weather, Cameras,
  energy.

See [`specs/greenhouse-provider.md`](../specs/greenhouse-provider.md) and
[ADR-002](../adr/ADR-002-provider-abstraction.md). The question of how to organize
*heterogeneous* providers (climate vs. commerce vs. finance) is raised in
[`rfc/`](../rfc/) for deliberate review.

### Context Engine
Assembles the current, relevant picture of the greenhouse from observations,
memory, and knowledge. It decides *what matters right now* and hands a coherent
context to the Decision Engine. It contains business logic and is independent of
any AI model.

### Decision Engine
**Reasons** over context to produce [Recommendations](../domain/recommendation.md)
with explicit rationale. This is where domain logic and judgment live. It produces
structured decisions, not prose. See
[ADR-001](../adr/ADR-001-separate-reasoning-from-language-generation.md).

### Language Engine
**Explains.** It turns structured recommendations and decisions into calm, clear
language for the grower. This is the layer most likely to use an AI model — and it
is deliberately isolated so the model is replaceable (see
[ADR-003](../adr/ADR-003-business-logic-independent-from-ai.md)). It does not make
decisions; it communicates them.

### User
The grower. The primary interface is **Morning Intelligence**; the experience is
designed to extend to hands-free interfaces such as Even G2 glasses, so no layer
assumes a screen. See
[ADR-004](../adr/ADR-004-morning-intelligence-default-interface.md).

## Supporting services

| Service | Responsibility |
| --- | --- |
| **Memory Engine** | Retains experience; links decisions to outcomes so the system learns over time. |
| **Decision Library** | Catalog of decision types and their structure, used by the Decision Engine. |
| **Domain Model** | The shared vocabulary (entities) the whole system operates on. See [`domain/`](../domain/). |
| **Morning Intelligence** | The default interface: the daily briefing that delivers value to the grower. |

## Cross-cutting principles

- **Business logic is independent of AI models.** AI is a capability the Language
  Engine (and possibly others) may use, never a dependency of core logic.
- **Every external system communicates through a provider.** No service talks to a
  vendor API directly.
- **Reasoning is separate from language.** Deciding and explaining are different
  responsibilities in different layers.
- **The architecture does not assume a screen.** Output is structured first,
  rendered second.

## Known open questions

The current pipeline is drawn one-directional, but the product must *learn from
outcomes* — which implies a feedback loop from reality/decisions back into memory
and future context. How that loop is represented architecturally is captured for
review in [`rfc/`](../rfc/) rather than assumed here.

## Future integrations

Synopta (greenhouse data), Shopify (orders/customers), Fortnox (finance, HR),
Weather, Cameras, and Even G2 glasses. All enter through the Provider Layer; none
change the layers above it.

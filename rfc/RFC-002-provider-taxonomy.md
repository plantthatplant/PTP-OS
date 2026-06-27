# RFC-002 — A taxonomy for heterogeneous providers

**Status:** Accepted in principle · Sprint 0 review. The conventions below are
adopted as guidance for new providers; this RFC will be promoted to an ADR once
validated against a second real provider integration.

## Context / the critique
ADR-002 establishes that *every* external system enters through the Provider Layer.
The future integration list is diverse: Synopta (greenhouse climate), Shopify
(commerce), Fortnox (finance/HR), Weather, Cameras, energy. These differ
fundamentally — in data shape, cadence (continuous vs. event vs. request),
direction (read vs. write), and semantics.

The risk: treating them all as one undifferentiated "provider" leads either to a
bloated single interface that fits none of them well, or to ad-hoc per-vendor
interfaces with no shared discipline. Either way the clean substitutability we want
(e.g. Claude Dispatch → Synopta) could erode as unrelated concerns pile into the
same abstraction.

## Current design
- One conceptual Provider Layer; one specified interface so far
  (`GreenhouseProvider`).
- No stated guidance on how *different kinds* of providers relate.

## Proposed improvement
Adopt a **small family of provider interfaces grouped by data concern**, sharing
common conventions but not forced into one signature:

| Provider family | Concern | Examples | Typical mode |
| --- | --- | --- | --- |
| Greenhouse / Climate | environment & structure | Claude Dispatch, Synopta | continuous read |
| Commerce | orders, customers | Shopify | request/sync read |
| Finance & HR | costs, employees | Fortnox | request/sync read |
| Environment | external conditions | Weather | forecast/read |
| Vision | imagery & derived observations | Cameras | stream/event |
| Energy | usage, price, supply | metering/spot price | event/read |

Shared conventions across all families (the "provider contract"):
- Return **Domain Model** types only; no vendor types leak.
- Normalize units and timestamps at the boundary.
- Declare **capabilities** explicitly.
- Map vendor errors to a common provider error taxonomy.
- Pass a shared **conformance test** for the family.

`GreenhouseProvider` (already specified) becomes the first member of this taxonomy;
nothing about it changes.

## Benefits
- Each domain gets an interface that fits it, without a lowest-common-denominator
  mega-interface.
- Shared conventions preserve substitutability and testability everywhere.
- New integrations have a clear pattern to follow → faster, safer onboarding.

## Risks
- Premature taxonomy: we have only one provider today; the categories may be wrong
  until real integrations arrive.
- Over-abstraction if we define families we never populate.

## Migration strategy
1. Treat this as **guidance, not construction.** Adopt the conventions; do not
   build interfaces for families until a real integration needs them.
2. When the second provider arrives (likely Weather or Shopify in a later sprint),
   define that family's interface then, validating the taxonomy against reality.
3. Record the accepted taxonomy as an ADR once it has survived a second real
   provider.

## Open questions
- Should write/actuation be a *capability flag* within a family or a separate
  interface entirely?
- Do Cameras belong in the provider model or in a dedicated ingestion pipeline
  feeding Observations?
- Where do cross-domain joins happen (e.g. "orders vs. ready batches") — Context
  Engine, presumably, not the providers?

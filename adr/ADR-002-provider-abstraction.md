# ADR-002 — Provider abstraction for external systems

**Status:** Accepted · Sprint 0

## Context
PTP OS depends on external systems for its view of reality. The first greenhouse
data source is **Claude Dispatch**; it will later be replaced by the **Synopta
Pro/API**. Beyond climate data, future sources include Shopify (commerce), Fortnox
(finance/HR), Weather, Cameras, and energy data.

If the core system talked to these vendors directly, every vendor change — and
especially the planned Claude Dispatch → Synopta swap — would ripple through the
whole codebase. Vendor-specific shapes, units, and quirks would contaminate
business logic.

## Decision
All external systems are accessed exclusively through a **Provider Layer**. Each
external system has a **Provider** that implements a stable internal interface and
maps the vendor's data into the **Domain Model**. The rest of PTP OS depends only
on the interface and the domain model — never on a vendor.

- Greenhouse data: `ClaudeDispatchProvider` today, `SynoptaProvider` later, behind
  the same interface (see [`specs/greenhouse-provider.md`](../specs/greenhouse-provider.md)).
- Other domains get their own provider interfaces as they are introduced.

## Consequences
- Swapping Claude Dispatch for Synopta is a localized change behind the interface;
  nothing above the Provider Layer changes. This is the architecture's key test.
- Vendor quirks (auth, units, field names, polling) are contained at the edge.
- Each provider is independently testable; the core can run against fakes.
- Cost: designing good, vendor-neutral interfaces is real work, and a poorly
  designed interface can leak vendor assumptions. Interfaces are specified and
  reviewed before implementation.
- Open question (heterogeneous providers): climate vs. commerce vs. finance differ
  enough that they may need distinct interface families — raised in
  [`rfc/RFC-002-provider-taxonomy.md`](../rfc/RFC-002-provider-taxonomy.md).

## Alternatives considered
- **Direct vendor calls from services.** Fastest first integration; makes the
  Synopta swap and every future change expensive and risky. Rejected — it
  contradicts the core product constraint.
- **One generic provider interface for everything.** Simple, but forces unrelated
  domains into one shape and leaks abstractions. Deferred to the RFC; likely a
  small family of interfaces instead.
- **An off-the-shelf integration/iPaaS platform.** Adds a heavy external
  dependency and still needs domain mapping. Rejected for now.

# Project Rules

How we build PTP OS. These rules are binding. They exist so the project stays
maintainable and trustworthy over years, not just sprints.

## Product principles

- **Biology before technology.** The plant's reality leads; technology serves it.
  How PTP OS understands plants is defined in
  [`biological-model.md`](biological-model.md); where software design conflicts
  with it, the biological model wins.
- **Build trust before automation.** Be reliably right and transparent before
  being allowed to act.
- **One prompt = one feature.** Each AI-backed capability is a single, deliberate,
  versioned prompt. No sprawling mega-prompts.
- **Every Friday should demonstrate real value.** Progress is measured by value a
  grower can see, not internal activity.
- **AI should explain its reasoning.** No opaque outputs. A recommendation without
  a rationale is incomplete.
- **AI should learn from outcomes.** Decisions and their results feed memory.
- **Keep interfaces calm and simple.** Lead with the answer. Reduce noise.

## Engineering rules

- **Prefer maintainability over cleverness.** Optimize for the next engineer
  reading the code, not for elegance today.
- **Keep the architecture modular.** Respect layer boundaries (see
  [`architecture.md`](architecture.md)).
- **Business logic is independent of UI** and of any AI model.
- **AI providers are replaceable.** No core logic depends on a specific model or
  vendor. See [ADR-003](../adr/ADR-003-business-logic-independent-from-ai.md).
- **Every external system communicates through a provider.** No direct vendor
  calls from services. See [ADR-002](../adr/ADR-002-provider-abstraction.md).
- **Always think about the next integration.** Synopta is the test case: any
  design that would break when Claude Dispatch is swapped for Synopta is wrong.
- **Explain technical decisions.** Significant decisions become
  [ADRs](../adr/). Significant proposed changes become [RFCs](../rfc/) first.

## Process

- **Specification before implementation.** Every feature gets a
  [spec](../specs/) that is reviewed before code is written.
- **Document everything important.** If a decision, interface, or concept matters,
  it is written down here, not left in someone's head.
- **Architecture evolves deliberately.** Do not change the architecture directly.
  Propose via RFC → accept → record as ADR → update
  [`architecture.md`](architecture.md).
- **Ask, don't assume.** When a requirement is unclear, ask. We never invent
  product features to fill a gap.
- **Highest-value first.** If a requested feature is not the highest-value
  improvement for Gaia, stop and explain why before implementing it. Name what
  would be higher value, and let the decision be made deliberately. (Pure design,
  review, or analysis may proceed, but should still flag a higher-value alternative.)
- **Small, independently deliverable units of work.** Break work into issues that
  can ship and demonstrate value on their own (see the Sprint 1 backlog).

## What we do not do

- We do **not** invent product features. Direction comes from the product, not the
  implementation.
- We do **not** skip documentation to move faster.
- We do **not** leak provider- or model-specific details into business logic.
- We do **not** redesign the product under the guise of engineering.

## Definition of done (for a unit of work)

1. There is a spec, and the work matches it.
2. Layer boundaries and the rules above are respected.
3. It is documented (and any decision recorded as an ADR if significant).
4. It demonstrates real, reviewable value.

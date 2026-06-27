# rfc/

**Requests for Comments.** An RFC is a *proposal* to change the architecture,
written so the team can evaluate it before any change is made. This is how PTP OS
evolves deliberately: we do not edit the architecture directly — we propose,
discuss, decide, and only then record the outcome as an [ADR](../adr/) and update
[`docs/architecture.md`](../docs/architecture.md).

> Why `rfc/` exists separately from `adr/`: ADRs record decisions that have been
> **accepted**; RFCs hold proposals that are still **open**. Keeping them apart
> preserves a clear line between "decided" and "under discussion".

| RFC | Proposal | Status |
| --- | --- | --- |
| [RFC-001](RFC-001-feedback-and-learning-loop.md) | Represent the outcome/learning loop in the architecture | Open (under review) |
| [RFC-002](RFC-002-provider-taxonomy.md) | A taxonomy for heterogeneous providers | Accepted in principle |
| [RFC-003](RFC-003-layered-specialist-agent-architecture.md) | Layered architecture: specialist agents as consumers of one reasoning core | Open (under review) |

> Decisions of record (Sprint 0 review): the `rfc/` directory is a **permanent**
> part of the repository. **RFC-002 is accepted in principle** — its conventions
> guide new providers; it will be promoted to an ADR once validated against a
> second real provider. **RFC-001 remains open** pending review of the learning
> architecture.

## Format
Each RFC contains: **Current design · Proposed improvement · Benefits · Risks ·
Migration strategy** (plus context and open questions as needed).

## Lifecycle
`Open` → `Accepted` (write an ADR, update architecture) or `Rejected`
(kept for the record) or `Superseded`.

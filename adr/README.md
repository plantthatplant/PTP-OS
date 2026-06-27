# adr/

**Architecture Decision Records.** An ADR captures a single significant
decision: the context, the decision itself, and its consequences. ADRs are the
durable "why" behind the structure of PTP OS, so future engineers (including us)
do not relitigate settled choices without understanding the reasoning.

| ADR | Decision | Status |
| --- | --- | --- |
| [ADR-001](ADR-001-separate-reasoning-from-language-generation.md) | Separate reasoning from language generation | Accepted |
| [ADR-002](ADR-002-provider-abstraction.md) | Provider abstraction for greenhouse data | Accepted |
| [ADR-003](ADR-003-business-logic-independent-from-ai.md) | Business logic independent from AI models | Accepted |
| [ADR-004](ADR-004-morning-intelligence-default-interface.md) | Morning Intelligence as the default interface | Accepted |

## Format

Each ADR follows the same structure:

- **Status** — Proposed / Accepted / Superseded (with a link if superseded).
- **Context** — the forces and constraints at the time of the decision.
- **Decision** — what we decided to do.
- **Consequences** — what becomes easier, harder, or constrained as a result.
- **Alternatives considered** — the options weighed and why they were not chosen.

## Conventions

- ADRs are **immutable once accepted**. To change a decision, write a new ADR
  that supersedes the old one, and update the status of the old one.
- Number ADRs sequentially: `ADR-NNN-short-title.md`.
- Keep them short. One decision per record.

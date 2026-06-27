# services/

The internal engines and supporting services that make up PTP OS. These hold the
system's **business logic** and reasoning. They operate on the
[domain model](../domain/) and are deliberately independent of any AI model or
data provider (see
[`adr/ADR-003-business-logic-independent-from-ai.md`](../adr/ADR-003-business-logic-independent-from-ai.md)).

## The pipeline

```
Reality → Provider Layer → Context Engine → Decision Engine → Language Engine → User
```

| Service | Responsibility | Status |
| --- | --- | --- |
| Context Engine | Assemble the current, relevant picture of the greenhouse from observations, memory, and knowledge. | Concept |
| Decision Engine | Reason over context to produce recommendations, with explicit rationale. | Concept |
| Language Engine | Turn structured decisions into calm, clear language for the grower. | Concept |
| Memory Engine | Retain experience; link decisions to outcomes so the system learns. | Designed |
| Decision Library | Catalog of decision types and their structure. | Specified |
| Knowledge Platform | Biological and horticultural knowledge the system draws on. | Concept |
| Morning Intelligence | The primary interface: the daily briefing that delivers value to the grower. | Designed |

(Status reflects the project brief at the start of Sprint 0.)

## Key boundaries

- **Reasoning is separate from language.** The Decision Engine decides; the
  Language Engine explains. See
  [`adr/ADR-001-separate-reasoning-from-language-generation.md`](../adr/ADR-001-separate-reasoning-from-language-generation.md).
- **Services never call a provider directly.** They consume the domain model
  produced behind the Provider Layer.
- **Services never embed model-specific assumptions.** AI is a tool a service may
  use (primarily the Language Engine), never something business logic depends on.

> No service implementation exists yet. Sprint 0 establishes the foundation only;
> each service gets a specification in `specs/` before it is built.

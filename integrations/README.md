# integrations/

External systems PTP OS talks to: greenhouse **data providers** and other
third-party services. Everything here sits at the edge of the system, behind a
stable internal interface, so the core never depends on a specific external
vendor.

## Greenhouse data providers

The Provider Layer is the most important integration point in PTP OS. It answers
one question for the rest of the system: *"What is happening in the greenhouse?"*
— without the rest of the system caring how that answer was obtained.

| Provider | Role | Status |
| --- | --- | --- |
| `ClaudeDispatchProvider` | Initial greenhouse data provider | Planned (Sprint 1) |
| `SynoptaProvider` | Long-term provider via Synopta Pro/API | Future |

The contract both must satisfy is defined in
[`specs/greenhouse-provider.md`](../specs/greenhouse-provider.md). The decision to
abstract providers is recorded in
[`adr/ADR-002-provider-abstraction.md`](../adr/ADR-002-provider-abstraction.md).

> No integration code exists yet. Sprint 0 establishes the foundation only.

## Conventions

- Every integration implements an internal interface defined in `specs/`. The
  rest of the application depends on the interface, never on the vendor.
- Provider-specific quirks (field names, units, auth, polling) are contained
  here and mapped into the [domain model](../domain/) at the boundary.
- Adding or replacing a provider must not require changes outside this folder and
  its configuration. If it does, the abstraction has leaked and needs fixing.

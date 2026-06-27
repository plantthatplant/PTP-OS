# RFC-001 — Represent the outcome/learning loop in the architecture

**Status:** Open · raised in Sprint 0 (architecture critique)

## Context / the critique
The product is explicit that "AI should learn from outcomes" and that Memory links
decisions to results. But the documented architecture is a strictly **one-
directional pipeline**:

```
Reality → Provider → Context → Decision → Language → User
```

Nothing in that diagram shows how a **Decision's outcome flows back** into Memory
and then into future Context and Decisions. The Memory Engine is listed as a
supporting service, but the *loop* — the mechanism that makes the system improve —
is implicit. An architecture that does not draw its most important feedback path
risks that path being under-designed or bolted on later.

This is a critique of the **documentation/model**, not a request to change product
behavior. The behavior is already intended; the architecture should make it
first-class.

## Current design
- Linear pipeline as above.
- Memory Engine present as a side service, with no defined inbound path for
  outcomes or outbound path into Context/Decision.

## Proposed improvement
Make the learning loop explicit as a closed cycle:

```
Reality → Provider → Context → Decision → Language → User
                       ▲            │
                       │            ▼
                    Memory ◀── Outcome capture  (observed results of a Decision)
```

Concretely:
1. Define an **Outcome** path: after a Decision, later Observations are linked back
   to it (this is what `domain/memory.md` describes) via the Memory Engine.
2. Define Memory as an **input to the Context Engine**, so prior experience shapes
   what context is assembled and how the Decision Engine reasons.
3. Document this loop in `architecture.md` as a named flow, not an aside.

No new product feature is introduced — only an explicit architectural
representation of behavior already required.

## Benefits
- The system's core value (learning) is designed deliberately, not incidentally.
- Clear contracts for "how an outcome is recorded" and "how memory informs
  reasoning" — both testable and provider/model-independent.
- Prevents a future scramble to retrofit feedback once features exist.

## Risks
- Adds conceptual surface area early, before there are features to learn from.
- Defining "outcome" rigorously is non-trivial (time windows, attribution of
  effect to a decision vs. confounders).
- Risk of over-engineering a loop we cannot yet validate with real data.

## Migration strategy
1. Adopt this RFC; record as an ADR (e.g. ADR-005 "Explicit learning loop").
2. Update `architecture.md` diagram and add a short "Learning loop" section.
3. Keep implementation deferred: in Sprint 1, only *record* decisions and outcomes
   (Memory write path). The *read-back into Context* is specced and built once
   there is data to learn from.
4. No code rework needed later because the contracts are defined now.

## Open questions
- How is an outcome attributed to a decision when many factors change at once?
- What time horizon defines "the outcome" for different decision types?
- Does outcome capture deserve its own provider concern (e.g. delayed sensor
  data)?

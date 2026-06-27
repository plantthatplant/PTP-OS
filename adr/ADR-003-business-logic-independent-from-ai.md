# ADR-003 — Business logic independent from AI models

**Status:** Accepted · Sprint 0

## Context
PTP OS is AI-native, but AI models change rapidly — versions, vendors, pricing,
and availability all shift. The product's value is its biological knowledge,
operational memory, and domain reasoning. If that value is entangled with a
specific AI model, the product is fragile: a model change could alter behavior
unpredictably, and we could be locked to one vendor.

We also need behavior we can test and trust. Non-deterministic model output inside
core decision paths makes correctness hard to guarantee — which conflicts with
"build trust before automation."

## Decision
**Business logic is independent of any AI model.** AI is treated as a replaceable
capability used at well-defined boundaries — primarily the **Language Engine**, and
optionally as an assistive input elsewhere — never as a dependency of core logic.

- Domain model, Context Engine, Decision Engine logic, Memory, and the Decision
  Library contain no hard dependency on a specific model or vendor.
- Where AI is used, it sits behind an interface and is configurable/replaceable,
  the same way data providers are ([ADR-002](ADR-002-provider-abstraction.md)).
- Reasoning is kept separate from language so the model-using layer is small and
  isolated ([ADR-001](ADR-001-separate-reasoning-from-language-generation.md)).

## Consequences
- We can change or upgrade AI models with minimal, contained impact.
- Core behavior is testable and reproducible independent of model output.
- No vendor lock-in at the heart of the product.
- Cost: we forgo some "let the model just do it" shortcuts and must maintain clear
  boundaries and structured contracts. Accepted deliberately.

## Alternatives considered
- **Model-centric design** (a large model orchestrates decisions directly). Fast
  to prototype; brittle, untestable, vendor-locked, and hard to trust. Rejected.
- **Hard-code one provider's SDK throughout** for convenience. Creates exactly the
  lock-in and fragility this ADR exists to prevent. Rejected.
- **No AI at all** (pure rules). Loses the AI-native value, especially calm
  natural-language explanation. Rejected; instead AI is isolated and replaceable.

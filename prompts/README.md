# prompts/

Versioned prompts used by PTP OS.

Per our principle **one prompt = one feature**, each user-facing capability that
relies on AI is backed by a deliberate, versioned prompt that lives here — not
inlined and forgotten in code. This keeps prompts reviewable, testable, and
independent of the surrounding application logic.

> No prompts exist yet. Sprint 0 establishes the foundation only; prompts are
> added as features are specified and built.

## Why prompts live here

- **Replaceable AI provider.** Prompts are an input to the Language Engine, not a
  property of a model. Keeping them versioned and separate supports swapping the
  underlying AI provider (see
  [`adr/ADR-003-business-logic-independent-from-ai.md`](../adr/ADR-003-business-logic-independent-from-ai.md)).
- **Reasoning vs. language.** Prompts here are primarily for *language generation*
  — turning structured decisions into calm, clear explanations for the grower.
  Reasoning lives in the Decision Engine, not in prose prompts (see
  [`adr/ADR-001-separate-reasoning-from-language-generation.md`](../adr/ADR-001-separate-reasoning-from-language-generation.md)).
- **Traceability.** Versioning prompts lets us connect a given explanation to the
  exact prompt that produced it.

## Conventions (to apply once prompts are added)

- One file per prompt; the filename names the feature.
- Include a version, a short description of the feature it powers, and its
  expected inputs and outputs.
- Treat a prompt change like a code change: reviewed and documented.

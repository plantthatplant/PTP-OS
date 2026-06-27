# ADR-001 — Separate reasoning from language generation

**Status:** Accepted · Sprint 0

## Context
PTP OS must both *decide* what a grower should do and *explain* it in calm, clear
language. These are different responsibilities with different requirements:

- Reasoning needs to be correct, testable, traceable, and biologically grounded.
- Language needs to be clear, warm, and well-phrased for a human (and eventually
  spoken aloud through Even G2 glasses).

If reasoning and phrasing are fused — e.g. an AI model both decides and writes the
answer in one step — we cannot test the logic independently, we cannot guarantee
the explanation reflects the actual reasoning, and the correctness of decisions
becomes tied to a specific language model.

## Decision
Reasoning and language generation are **separate stages in separate layers**:

- The **Decision Engine** reasons over context and emits a *structured*
  Recommendation/Decision, including an explicit rationale, with no concern for
  prose.
- The **Language Engine** takes that structured output and renders it into natural
  language for the chosen interface.

The structured decision is the contract between them. The Language Engine never
makes or alters decisions; it only phrases them.

## Consequences
- Decision logic can be unit-tested without invoking any language model.
- Explanations are guaranteed to derive from the actual structured rationale.
- The interface (screen, glasses, voice) can change without touching reasoning.
- The AI/language model is isolated to one layer and stays replaceable
  (supports [ADR-003](ADR-003-business-logic-independent-from-ai.md)).
- Cost: a defined structured intermediate format must be designed and maintained.

## Alternatives considered
- **Single AI step that decides and writes.** Simplest to build initially, but
  fuses logic with a model, prevents independent testing, and makes the
  explanation unverifiable. Rejected.
- **Reasoning in AI, templated (non-AI) language.** Keeps language deterministic
  but produces stiff, un-calm output and limits multi-interface phrasing.
  Rejected as the default, though templates may be used for simple cases.
- **Language layer allowed to adjust decisions for clarity.** Blurs the boundary
  and reintroduces the verification problem. Rejected.

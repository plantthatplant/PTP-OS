# Recommendation

## Purpose
A suggested action produced by reasoning, **with the explanation behind it**. A
recommendation is the Decision Engine's output and the core of "AI should explain
its reasoning." It is a proposal — not yet an action taken.

## Relationships
- Produced by the **Decision Engine** from context (**Observations**,
  **Climate Readings**, **Memory**, **Species** knowledge).
- About a subject: **Zone**, **Plant Batch**, **Mother Plant**, etc.
- Phrased for the grower by the **Language Engine**.
- May become a **Decision** (accepted/modified/rejected) and spawn **Tasks**.
- Its outcome is later captured in **Memory**.

## Important properties
- Identity: stable id, timestamp.
- Subject reference.
- Suggested action (structured, model-independent).
- Rationale: the evidence and reasoning, with references to supporting
  observations.
- Confidence / urgency.
- Status (open, accepted, modified, rejected, expired).

## Future integrations
- **Language Engine** renders it; the underlying AI model is replaceable
  ([ADR-003](../adr/ADR-003-business-logic-independent-from-ai.md)).
- **Even G2 glasses** — recommendations must render hands-free, so they stay
  structured and screen-independent.

## Examples
- "Lower Zone A night temperature by 2 °C for 3 nights to firm up finishing
  Monstera — RH and growth rate suggest soft growth." (with cited readings)
- "Take cuttings from Mother M-MD-01 this week; it is at peak vigor and Batch
  pipeline is below target."

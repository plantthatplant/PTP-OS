# Memory

## Purpose
Retained experience that links **Decisions** to their **outcomes** over time. Memory
is what makes PTP OS learn rather than merely respond. It is the substrate behind
"AI should learn from outcomes."

## Relationships
- References a **Decision** (and the **Recommendation** behind it).
- References the observed **outcome** (later **Observations** / results).
- About a subject: **Plant Batch**, **Zone**, **Species**, **Mother Plant**, etc.
- Maintained by the **Memory Engine**; consumed by the **Context Engine** and
  **Decision Engine** to inform future reasoning.

## Important properties
- Identity: stable id.
- Decision and recommendation references.
- Subject and relevant context snapshot at decision time.
- Outcome summary and measured effect.
- Learned signal: did the action help, hurt, or have no effect; confidence.
- Time span the memory covers.

## Future integrations
- Feeds future reasoning regardless of AI provider — memory is part of business
  logic, not the model
  ([ADR-003](../adr/ADR-003-business-logic-independent-from-ai.md)).
- **Synopta** history can enrich the context snapshots once available.

## Examples
- "Lowering Zone A night temp by 2 °C firmed up finishing Monstera within 5 days
  with no growth penalty — positive, high confidence."
- "Delaying pest treatment by two days led to spread — negative; act sooner next
  time."

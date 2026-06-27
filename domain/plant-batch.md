# Plant Batch

## Purpose
A group of plants of the same **Species** propagated and managed together as a
single unit through the production cycle. The batch is the primary operational unit
for planning, climate decisions, tasks, and fulfilment.

## Relationships
- Composed of many **Plants**, all of one **Species**.
- May originate from a **Mother Plant** (its cuttings).
- Located across one or more **Benches** in a **Zone**.
- Subject of **Observations**; target of **Recommendations**, **Decisions**, and
  **Tasks**.
- Ultimately fulfils **Orders** (via finished plants) and feeds **Shipments**.

## Important properties
- Identity: stable id, batch code.
- Species and source mother plant (if any).
- Size: plant count (started, current, lost).
- Lifecycle stage and key dates (started, expected ready).
- Current location(s).
- Quality/health summary derived from observations.

## Future integrations
- **Synopta** — environmental history that shaped the batch.
- **Shopify** — available finished plants map to sellable inventory.
- **Cameras** — batch-level visual progress tracking.

## Examples
- "Batch MD-2026-014": 240 *Monstera deliciosa* cuttings started in March,
  currently 228 plants in vegetative stage in Zone B.
- A finishing batch with 96 plants reserved against an open wholesale order.

# Plant

## Purpose
A single cultivated plant. Most production is managed in batches, but the
individual plant matters for mother plants, quality sampling, and traceability.

## Relationships
- Is of a **Species**.
- Usually part of a **Plant Batch**; may be a standalone **Mother Plant**.
- Located on a **Bench** (within a **Zone** / **Greenhouse**).
- Subject of **Observations** (e.g. health, height, flowering).
- May be the source (via a Mother Plant) of cuttings that start new batches.

## Important properties
- Identity: stable id.
- Species reference.
- Batch reference (if any) and current location.
- Lifecycle stage (cutting, young, vegetative, finishing, ready, discarded).
- Health/quality indicators (from observations).
- Key dates (propagated, potted, expected ready).

## Future integrations
- **Cameras** — image-based health and growth assessment.
- **Synopta** — environmental context tied to the plant's location.
- **Shopify** — a finished plant ultimately maps to a sellable product/variant.

## Examples
- A single *Monstera deliciosa* in finishing stage, on Bench C-02, ready in ~2
  weeks.
- A quality-sample plant tracked individually to validate a batch's progress.

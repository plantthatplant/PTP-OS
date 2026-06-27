# Bench

## Purpose
A physical growing surface within a **Zone** where plants are placed. The bench is
the finest-grained location in the physical model and the unit growers use to find
and act on specific plants.

## Relationships
- Belongs to one **Zone** (and thus one **Greenhouse**).
- Holds **Plant Batches** and/or individual **Plants**.
- May be referenced by **Observations**, **Tasks**, and **Recommendations**
  (e.g. "move batch on bench 4").

## Important properties
- Identity: stable id, label/number.
- Parent zone.
- Capacity / dimensions.
- Current occupancy (which batches/plants are on it).
- Optional micro-location data (row/position) for fine placement.

## Future integrations
- **Cameras** — a camera may be associated with a bench for close monitoring.
- **Synopta** — fine-grained sensors, where available, may attach at bench level.

## Examples
- "Bench A-04": a 1.2 × 6 m rolling bench in Zone A holding two propagation
  batches.
- An empty finishing bench reserved for next week's intake.

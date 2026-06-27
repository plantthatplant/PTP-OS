# Observation

## Purpose
A recorded fact about reality at a point in time — the atomic input PTP OS reasons
from. Observations can be measured (a sensor value), seen (a camera or a human
note), or derived. They are the evidence behind every recommendation.

## Relationships
- Made about a subject: **Greenhouse**, **Zone**, **Bench**, **Plant**,
  **Plant Batch**, or **Mother Plant**.
- **Climate Reading** is a specialized Observation.
- Consumed by the **Context Engine**; cited by **Recommendations**.
- May be produced by a person (**Employee**), a sensor, or a **Camera**.

## Important properties
- Identity: stable id.
- Subject reference (what it is about) and location.
- Timestamp (when it was true / recorded).
- Type (climate, health, growth, pest, note, image, …).
- Value/payload and unit (where applicable).
- Source (sensor, employee, camera, derived) and confidence.

## Future integrations
- **Synopta / Claude Dispatch** — sensor-based observations.
- **Cameras** — image observations and their derived assessments.
- All observations arrive **through the Provider Layer**, mapped to this shape.

## Examples
- "Spider mites seen on Batch MD-2026-014, bench B-03" — type: pest, source:
  employee, 2026-06-26 08:10.
- "Leaf temperature 24.1 °C in Zone A" — a climate reading (see
  [`climate-reading.md`](climate-reading.md)).

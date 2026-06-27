# Greenhouse

## Purpose
Represents a physical growing facility operated by Plant That Plant. It is the
top-level physical container for everything PTP OS observes and reasons about, and
the anchor for location, climate, and capacity.

## Relationships
- Contains one or more **Zones**.
- Indirectly contains **Benches** (via Zones), **Plants**, and **Plant Batches**.
- Is the subject of **Climate Readings** and **Observations** (directly or via its
  Zones).
- Associated with **Weather** (external conditions at its location) and
  **Energy Events**.
- Worked in by **Employees**.

## Important properties
- Identity: stable id, name.
- Location: address / coordinates (used to align Weather).
- Structure: list of Zones; total growing area.
- Capabilities: climate-control systems present, energy sources.
- Status: active / inactive.

## Future integrations
- **Synopta / Claude Dispatch** — source of facility-level climate and control
  data via the Provider Layer.
- **Weather** — location used to fetch external conditions.
- **Cameras** — facility may host camera feeds for visual observation.
- **Fortnox** — may relate to the facility as a cost/asset center.

## Examples
- "Greenhouse North" — the main 2,400 m² production facility in Sweden, three
  zones, district-heating + heat-pump, active.
- A small propagation house used only for mother plants and cuttings.

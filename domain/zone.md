# Zone

## Purpose
A controllable sub-area within a **Greenhouse** — typically the unit at which
climate is regulated and crops are grouped. Zones let PTP OS reason about
conditions and decisions at the resolution growers actually manage.

## Relationships
- Belongs to one **Greenhouse**.
- Contains one or more **Benches**.
- Holds **Plant Batches** / **Plants** (placed on its benches).
- Is the subject of **Climate Readings** and **Observations**.
- Referenced by **Recommendations**, **Decisions**, and **Tasks** scoped to it.

## Important properties
- Identity: stable id, name/number.
- Parent greenhouse.
- Climate setpoints / target ranges (temperature, humidity, CO₂, light).
- Area and bench capacity.
- Current crops/batches present.

## Future integrations
- **Synopta / Claude Dispatch** — per-zone sensor and control data.
- **Cameras** — zone-level visual monitoring.
- **Energy** — zone-level heating/lighting contributes to Energy Events.

## Examples
- "Zone A — Propagation": warm, high-humidity zone for young plants.
- "Zone C — Finishing": cooler zone where plants are hardened before shipping.

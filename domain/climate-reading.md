# Climate Reading

## Purpose
A measured environmental value — temperature, humidity, CO₂, light, etc. — at a
location and time. It is a specialized, high-volume kind of **Observation**, called
out separately because climate is central to greenhouse decisions and arrives
continuously.

## Relationships
- Is a specialization of **Observation**.
- Measured for a **Zone** (most common), **Greenhouse**, or **Bench**.
- Compared against **Zone** setpoints and **Species** targets.
- Primary input to climate-related **Recommendations** and **Decisions**.

## Important properties
- Identity: stable id.
- Location reference and timestamp.
- Metric (temperature, relative humidity, CO₂, PAR/light, VPD, …).
- Value and unit.
- Source sensor / provider and confidence.

## Future integrations
- **Synopta / Claude Dispatch** — the main source of climate readings via the
  Provider Layer.
- **Weather** — outdoor readings provide external context for indoor values.

## Examples
- Zone A, 2026-06-26 06:00 — temperature 22.4 °C, RH 78 %, CO₂ 540 ppm.
- A VPD value derived from temperature and humidity for finishing decisions.

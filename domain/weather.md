# Weather

## Purpose
External meteorological conditions at and around a **Greenhouse**. Weather is
context the greenhouse cannot control but must respond to — it drives climate
control effort, energy use, and some operational decisions (e.g. shipping live
plants in a cold snap).

## Relationships
- Associated with a **Greenhouse** (by location).
- Provides external context for **Climate Readings** and climate
  **Recommendations**.
- Influences **Energy Events** (heating/cooling demand) and **Shipment** timing.

## Important properties
- Location reference and timestamp (observed or forecast).
- Kind: current, historical, or forecast.
- Metrics: outdoor temperature, humidity, solar radiation, wind, precipitation.
- Source/provider and confidence.

## Future integrations
- **Weather** provider (external API) via the Provider Layer — both current
  conditions and forecasts.
- Combined with **Synopta** climate data to reason about control effort and
  energy.

## Examples
- "Forecast: −8 °C overnight in 48h" → anticipate heating load and protect
  shipments.
- "Three consecutive overcast days" → adjust supplemental lighting expectations.

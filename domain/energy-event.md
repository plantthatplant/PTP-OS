# Energy Event

## Purpose
A noteworthy change in energy use, cost, or supply relevant to greenhouse
operation — a price spike, a consumption surge, a supply interruption, or a
notable efficiency change. Energy is a major cost and sustainability factor, so
PTP OS reasons about it explicitly.

## Relationships
- Associated with a **Greenhouse** (and possibly specific **Zones**).
- Correlated with **Weather** (heating/cooling demand) and **Climate Readings**.
- May trigger **Recommendations** (e.g. shift lighting to cheaper hours) and
  **Decisions**.

## Important properties
- Identity: stable id, timestamp / time range.
- Type (price change, consumption spike, supply interruption, efficiency change).
- Magnitude and unit (kWh, cost, %).
- Affected greenhouse/zone and likely cause.
- Source/provider.

## Future integrations
- Energy/utility data via a provider (metering and/or spot-price feeds).
- **Weather** correlation for demand forecasting.
- **Fortnox** for cost accounting of energy.

## Examples
- "Electricity spot price spikes 3×, 17:00–20:00 today" → recommend shifting
  supplemental lighting outside the peak.
- "Heating consumption up 40 % overnight" correlated with a cold snap.

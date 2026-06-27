"""Context Engine — assemble the current, relevant biological picture.

It does not decide anything. It turns raw conditions into meaning: compares each
zone to its targets, computes derived signals (VPD, dew point), reads the trend
against recent mornings, and gathers the human observations — so the Decision
Engine reasons over understanding, not numbers. Pure business logic; no AI, no
vendor knowledge (ADR-003).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from . import biology
from .domain import Zone, ClimateReading, Observation, Greenhouse


@dataclass
class ZoneContext:
    zone: Zone
    reading: ClimateReading
    vpd: float
    dew_point: float
    humidity_excess: float      # %RH above the target ceiling (0 if within band)
    temp_deviation: float       # signed degrees outside the target band (0 if within)
    humidity_trend: str         # rising | steady | falling
    observations: List[Observation] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


@dataclass
class GreenhouseContext:
    greenhouse: Greenhouse
    zones: List[ZoneContext]
    outlook_text: str
    outlook_heat_load: str
    outlook_confidence: str


def _trend(history: List[float]) -> str:
    if len(history) < 2:
        return "steady"
    if history[-1] - history[0] >= 4:
        return "rising"
    if history[0] - history[-1] >= 4:
        return "falling"
    return "steady"


class ContextEngine:
    def assemble(self, provider) -> GreenhouseContext:
        gh = provider.get_greenhouse()
        latest = provider.get_latest_climate()
        observations = provider.get_observations()
        outlook = provider.get_outlook()

        zone_contexts: List[ZoneContext] = []
        for zone in gh.zones:
            r = latest.get(zone.id)
            if r is None:
                continue  # a coverage gap is an absence, never a fabricated value

            hmax = zone.targets.humidity_pct[1]
            tmin, tmax = zone.targets.temp_c
            humidity_excess = max(0.0, r.humidity_pct - hmax)
            if r.temp_c > tmax:
                temp_dev = r.temp_c - tmax
            elif r.temp_c < tmin:
                temp_dev = r.temp_c - tmin
            else:
                temp_dev = 0.0

            zc = ZoneContext(
                zone=zone,
                reading=r,
                vpd=biology.vpd_kpa(r.temp_c, r.humidity_pct),
                dew_point=biology.dew_point_c(r.temp_c, r.humidity_pct),
                humidity_excess=round(humidity_excess, 1),
                temp_deviation=round(temp_dev, 1),
                humidity_trend=_trend(provider.get_humidity_history(zone.id)),
                observations=[o for o in observations if o.zone_id == zone.id],
            )

            if r.reliability == "suspect":
                zc.notes.append("climate reading flagged suspect — corroborate before trusting")
            if humidity_excess > 0 and r.airflow == "low":
                zc.notes.append("humid and stagnant — leaf-wetness conditions")
            zone_contexts.append(zc)

        return GreenhouseContext(
            greenhouse=gh,
            zones=zone_contexts,
            outlook_text=outlook.text,
            outlook_heat_load=outlook.heat_load,
            outlook_confidence=outlook.confidence,
        )

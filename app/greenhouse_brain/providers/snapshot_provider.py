"""SnapshotProvider — feed a canonical Greenhouse Snapshot to the existing Brain.

It implements the same GreenhouseProvider interface as every other provider, so the
Context / Decision / Language / Morning Analysis engines run completely unchanged. Its
job is to read observations out of a Snapshot and present them as the domain objects the
engines already consume.

Missing data is handled here, gracefully: a zone without both temperature and humidity
simply yields no climate reading (honest absence) rather than crashing the engine. The
Brain never fails because something wasn't observed.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from ..domain import Greenhouse, Zone, ClimateTargets, ClimateReading, Observation, Outlook
from ..snapshot import Snapshot, SnapshotObservation
from ..units import to_number, airflow_from_vent
from .base import GreenhouseProvider

# Targets are agronomic knowledge (what 'good' is), not observation — so they live with
# the provider, keyed by stage, exactly as for the other providers.
_TARGETS_BY_STAGE = {
    "propagation": ClimateTargets((22, 26), (70, 85), "humid, but avoid prolonged leaf wetness"),
    "vegetative": ClimateTargets((20, 24), (60, 75)),
    "finishing": ClimateTargets((18, 22), (55, 70), "cooler/drier to tone before dispatch"),
    "unknown": ClimateTargets((18, 26), (55, 85)),
}

# Biological/operational observation kinds the existing rules understand.
_RECOGNISED = {"leaf-wetness", "sensor-anomaly", "tone", "order", "mother-stock", "dev-note", "transient"}


# Vendor-neutral number/airflow cleaning is shared (greenhouse_brain.units).
_num = to_number


class SnapshotProvider(GreenhouseProvider):
    name = "snapshot"
    data_source = "imported greenhouse snapshot"

    def __init__(self, snapshot: Snapshot):
        self.snapshot = snapshot

    def _obs(self, subject: str, kind: str) -> Optional[SnapshotObservation]:
        for o in self.snapshot.observations:
            if o.subject == subject and o.kind == kind and o.has_value():
                return o
        return None

    # --- the GreenhouseProvider interface, served from the Snapshot ----------

    def get_greenhouse(self) -> Greenhouse:
        zones = [Zone(id=z.id, name=z.name, stage=z.stage, crop=z.crop,
                      targets=_TARGETS_BY_STAGE.get(z.stage, _TARGETS_BY_STAGE["unknown"]))
                 for z in self.snapshot.zones]
        return Greenhouse(id=self.snapshot.greenhouse_id, name=self.snapshot.greenhouse_name,
                          location="", zones=zones)

    def get_latest_climate(self) -> Dict[str, ClimateReading]:
        out: Dict[str, ClimateReading] = {}
        for z in self.snapshot.zones:
            temp = self._obs(z.id, "air-temperature")
            hum = self._obs(z.id, "relative-humidity")
            t = _num(temp.value) if temp else None
            h = _num(hum.value) if hum else None
            if t is None or h is None:
                continue  # cannot assess climate without both -> honest absence, no crash
            vent = self._obs(z.id, "vent-position")
            alarm = self._obs(z.id, "alarm")
            reliability = "suspect" if (alarm and "sensor" in str(alarm.value).lower()) else "normal"
            co2 = self._obs(z.id, "co2")
            light = self._obs(z.id, "light")
            out[z.id] = ClimateReading(
                zone_id=z.id, temp_c=t, humidity_pct=h,
                co2_ppm=(_num(co2.value) or 0.0) if co2 else 0.0,
                light_ppfd=(_num(light.value) or 0.0) if light else 0.0,
                airflow=airflow_from_vent(vent.value if vent else None),
                source="snapshot", reliability=reliability, hours_old=0.0,
                timestamp=temp.captured_at,
            )
        return out

    def get_humidity_history(self, zone_id: str) -> List[float]:
        return []   # a Snapshot is 'now'; trends come from a series of Snapshots later

    def get_observations(self) -> List[Observation]:
        out = []
        for o in self.snapshot.observations:
            if o.kind in _RECOGNISED and o.has_value():
                text = o.verbatim or (str(o.value) if not isinstance(o.value, bool) else o.kind)
                out.append(Observation(zone_id=o.subject, type=o.kind, text=text,
                                       source=o.source or "snapshot"))
        return out

    def get_outlook(self) -> Outlook:
        for o in self.snapshot.observations:
            if o.kind in ("afternoon-outlook", "outlook", "forecast") and o.has_value():
                text = str(o.value)
                hot = any(w in text.lower() for w in ("hot", "heat", "bright", "warm"))
                return Outlook(text=text, heat_load="high" if hot else "moderate",
                               confidence=(o.confidence or "low").capitalize())
        ot = self._obs("site", "outside-temperature")
        t = _num(ot.value) if ot else None
        if t is None:
            return Outlook(text="no outdoor reading available", heat_load="low", confidence="Low")
        heat = "high" if t >= 26 else ("moderate" if t >= 20 else "low")
        return Outlook(text=f"outside about {t:.0f}C", heat_load=heat, confidence="Low")

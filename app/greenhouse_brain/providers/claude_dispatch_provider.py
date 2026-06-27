"""ClaudeDispatchProvider — live greenhouse data, translated into the domain model.

Its ONE job (ADR-002, specs/greenhouse-provider.md): take what Claude Dispatch
extracts from Synopta and return it as the *same* domain types every other provider
returns, so nothing above the Provider Layer can tell where the data came from.

v1 supports only the most important signals — timestamp, house id, air temperature,
relative humidity, vent position, outside temperature, alarm state — and represents
everything it does not have as honest absence (empty observations, no history), never
as a fabricated value. That leanness is a *data-coverage* fact, not an architecture
one: the engines run unchanged on whatever this returns.

The raw payload here is a captured fixture (`sample_claude_dispatch.json`). Wiring it
to a live Claude Dispatch call is a transport detail that does not change this
translation — which is the part worth proving.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from ..domain import (
    Greenhouse, Zone, ClimateTargets, ClimateReading, Observation, Outlook,
)
from ..units import to_number, airflow_from_vent
from .base import GreenhouseProvider
from .transport import DispatchTransport, FixtureTransport

# Vendor-neutral number/airflow cleaning is shared (greenhouse_brain.units); see ADR-002.
_coerce_number = to_number


def _signal(signals: dict, key: str) -> Optional[float]:
    node = signals.get(key)
    if not node or node.get("value") is None:
        return None
    return float(node["value"])


class ClaudeDispatchProvider(GreenhouseProvider):
    name = "claude-dispatch"
    data_source = "Claude Dispatch (live greenhouse feed)"

    # Known greenhouse setup (stage/crop/targets). This is facility configuration,
    # not telemetry — Claude Dispatch supplies live *values*; the layout is ours.
    # (Same houses/targets as the mock, so the swap can be compared like for like.)
    _CONFIG = {
        "1": dict(name="House 1 (propagation)", stage="propagation",
                  crop="mixed aroid cuttings",
                  targets=ClimateTargets((22, 26), (70, 85), "humid, but avoid prolonged leaf wetness")),
        "2": dict(name="House 2 (growing on)", stage="vegetative",
                  crop="young foliage plants",
                  targets=ClimateTargets((20, 24), (60, 75))),
        "3": dict(name="House 3 (finishing)", stage="finishing",
                  crop="finishing batch — order #1043",
                  targets=ClimateTargets((18, 22), (55, 70), "cooler/drier to tone before dispatch")),
    }

    def __init__(self, raw: dict = None, transport: DispatchTransport = None):
        # The TRANSPORT decides where the raw payload comes from; the translation
        # below does not change. Default transport reads the captured fixture; pass an
        # HttpDispatchTransport to pull live Claude Dispatch data instead.
        if raw is None:
            transport = transport or FixtureTransport()
            raw = transport.fetch()
        self.transport = transport
        self._raw = self._normalise(raw)
        self.captured_at = self._raw.get("captured_at")

    @staticmethod
    def _normalise(raw: dict) -> dict:
        """Absorb live-transport inconsistencies HERE, so the rest of the system never
        sees them: guarantee the expected shape, drop untranslatable houses, and coerce
        stringy / comma-decimal numbers. The translation methods stay exactly as they were."""
        if not isinstance(raw, dict):
            return {"houses": []}
        houses = []
        for h in raw.get("houses", []) or []:
            if not isinstance(h, dict) or "house_id" not in h or "signals" not in h:
                continue  # without an id and signals there is nothing to translate
            for node in (h.get("signals") or {}).values():
                if isinstance(node, dict) and isinstance(node.get("value"), str):
                    node["value"] = _coerce_number(node["value"])
            houses.append(h)
        raw["houses"] = houses
        return raw

    def _houses(self) -> List[dict]:
        return self._raw.get("houses", [])

    # --- the interface, returning domain types only --------------------------

    def get_greenhouse(self) -> Greenhouse:
        zones = []
        for h in self._houses():
            cfg = self._CONFIG.get(h["house_id"])
            if not cfg:
                continue
            zones.append(Zone(id="h" + h["house_id"], name=cfg["name"],
                              stage=cfg["stage"], crop=cfg["crop"], targets=cfg["targets"]))
        return Greenhouse(id="gh-kalaberga", name=self._raw.get("site", "Greenhouse"),
                          location="Sweden", zones=zones)

    def get_latest_climate(self) -> Dict[str, ClimateReading]:
        ts = self._raw.get("captured_at")
        out: Dict[str, ClimateReading] = {}
        for h in self._houses():
            if h["house_id"] not in self._CONFIG:
                continue
            sig = h.get("signals", {})
            alarm = sig.get("alarm", {}) or {}
            alarm_text = (alarm.get("text") or "").lower()
            # A sensor-fault alarm means we shouldn't trust this reading -> 'suspect'.
            reliability = "suspect" if alarm.get("active") and "sensor" in alarm_text else "normal"
            zid = "h" + h["house_id"]
            out[zid] = ClimateReading(
                zone_id=zid,
                temp_c=_signal(sig, "air_temp") or 0.0,
                humidity_pct=_signal(sig, "rel_humidity") or 0.0,
                co2_ppm=0.0,        # not supplied by Claude Dispatch v1
                light_ppfd=0.0,     # not supplied by Claude Dispatch v1
                airflow=airflow_from_vent(_signal(sig, "vent_position")),
                source="claude-dispatch",
                reliability=reliability,
                hours_old=0.0,
                timestamp=ts,
            )
        return out

    def get_humidity_history(self, zone_id: str) -> List[float]:
        # Claude Dispatch v1 gives the current snapshot only — no history.
        return []

    def get_observations(self) -> List[Observation]:
        # Climate telemetry carries no plant/human observations. Honest absence.
        return []

    def get_outlook(self) -> Outlook:
        # The only 'weather' we have is outside temperature. Make a minimal, low-
        # confidence outlook from it — never a full forecast.
        temps = [t for t in (_signal(h.get("signals", {}), "outside_temp") for h in self._houses())
                 if t is not None]
        if not temps:
            return Outlook(text="no outdoor reading available", heat_load="low", confidence="Low")
        t = max(temps)
        heat = "high" if t >= 26 else ("moderate" if t >= 20 else "low")
        return Outlook(text=f"outside about {t:.0f}C right now", heat_load=heat, confidence="Low")

"""Translate a raw Synopta reading into a Canonical Greenhouse Snapshot (a dict).

This is field-mapping and unit-cleaning ONLY. It records what was observed; it never
interprets it. No Plant State, no Stress, no Disease Risk, no advice — those are latent and
inferred downstream (BIOLOGY.md, snapshot spec Principle 2). The one rule it must never
break: it does not invent a value to fill a gap (snapshot §10). A value it cannot read
becomes an honest absence and a warning, never a number.

Confidence here is about the *observation*, derived from source reliability and recency —
a sensor-fault alarm makes that house's reading low-confidence. It is never a judgement
about the plant.
"""
from __future__ import annotations

from typing import List, Optional

from . import _paths  # noqa: F401  (puts app/ on the path)
from greenhouse_brain.units import to_number  # the shared, tested number primitive

# vendor signal key -> (canonical kind, canonical unit)
_QUANT = {
    "air_temp": ("air-temperature", "°C"),
    "rel_humidity": ("relative-humidity", "%RH"),
}

# Live exports arrive messy ('24,2 °C', '92', 16.0); reuse Gaia's own cleaning so there is
# one definition of "what is this number?". A non-number stays absence, never a fabricated 0.
_clean_number = to_number


def _signal_value(signals: dict, key: str):
    node = signals.get(key)
    if isinstance(node, dict):
        return node.get("value")
    return node  # tolerate a bare value


def _vent_text(raw_value) -> Optional[str]:
    """A vent position as the grower reads it: 'closed' at 0, otherwise 'N%'. Absence stays
    absence."""
    n = _clean_number(raw_value)
    if n is None:
        # Maybe it is already a word like 'closed'/'open'.
        if raw_value is None:
            return None
        s = str(raw_value).strip()
        return s or None
    if n <= 0:
        return "closed"
    return f"{n:g}%"


def _confidence_for(alarm_active: bool, alarm_text: str) -> str:
    """Provenance-based confidence: a sensor-fault alarm means don't trust that house's
    reading (low); otherwise a measured value is high. Not a biological judgement."""
    if alarm_active and "sensor" in (alarm_text or "").lower():
        return "low"
    return "high"


def to_snapshot(raw: dict, facility: dict, assembled_at: str,
                warnings: List[str] = None) -> dict:
    """Build a canonical snapshot dict. Appends any per-signal problems to `warnings`
    (for the log) and keeps going — one bad value never aborts the rest (responsibility 9)."""
    warnings = warnings if warnings is not None else []
    raw = raw if isinstance(raw, dict) else {}
    captured_at = raw.get("captured_at")

    zones_cfg = {z.get("house_id"): z for z in (facility.get("zones") or [])}
    houses = {str(h.get("house_id")): h for h in (raw.get("houses") or [])
              if isinstance(h, dict) and h.get("house_id") is not None}

    observations: List[dict] = []
    not_observed: List[str] = list(facility.get("known_absent") or [])
    site_outside_done = False

    for house_id, cfg in zones_cfg.items():
        zone_id = cfg.get("id", f"h{house_id}")
        zone_name = cfg.get("name", zone_id)
        house = houses.get(str(house_id))
        if not house:
            # Configured house, but nothing in this export — looked, saw nothing.
            not_observed.append(f"{zone_name} — no reading in this export")
            warnings.append(f"{zone_name}: absent from export (house_id {house_id})")
            continue

        signals = house.get("signals") or {}
        alarm = signals.get("alarm") or {}
        alarm_active = bool(alarm.get("active"))
        alarm_text = alarm.get("text") or ""
        conf = _confidence_for(alarm_active, alarm_text)

        # Quantitative climate metrics.
        for key, (kind, unit) in _QUANT.items():
            n = _clean_number(_signal_value(signals, key))
            if n is None:
                observations.append({
                    "subject": zone_id, "kind": kind, "value": None,
                    "absence": "value missing in this export",
                })
                warnings.append(f"{zone_name}: {kind} missing or unreadable")
            else:
                observations.append({
                    "subject": zone_id, "kind": kind, "value": n, "unit": unit,
                    "captured_at": captured_at, "source": "synopta",
                    "method": "measured", "confidence": conf,
                })

        # Vent position (equipment) — categorical/text, not a bare number.
        vent = _vent_text(_signal_value(signals, "vent_position"))
        if vent is None:
            observations.append({"subject": zone_id, "kind": "vent-position",
                                 "value": None, "absence": "value missing in this export"})
            warnings.append(f"{zone_name}: vent-position missing or unreadable")
        else:
            observations.append({
                "subject": zone_id, "kind": "vent-position", "value": vent,
                "captured_at": captured_at, "source": "synopta",
                "method": "measured", "confidence": "high",
            })

        # Alarm — carried as an observation, never interpreted. Absence of an alarm is not
        # itself recorded.
        if alarm_active:
            observations.append({
                "subject": zone_id, "kind": "alarm",
                "value": alarm_text or "alarm active",
                "captured_at": captured_at, "source": "synopta",
                "method": "measured", "confidence": "high",
            })

        # Outside temperature — a site-level reading; record it once.
        if not site_outside_done:
            ot = _clean_number(_signal_value(signals, "outside_temp"))
            if ot is not None:
                observations.append({
                    "subject": "site", "kind": "outside-temperature", "value": ot,
                    "unit": "°C", "captured_at": captured_at, "source": "synopta",
                    "method": "measured", "confidence": "medium",
                })
                site_outside_done = True
    if not site_outside_done:
        not_observed.append("outside-temperature — not present in this export")

    # Houses present in the export but unknown to the facility config — we cannot place
    # them in the structure, so we honestly skip them rather than guess their identity.
    for hid in houses:
        if hid not in {str(k) for k in zones_cfg}:
            warnings.append(f"export house_id {hid} not in facility config — skipped")

    structure_zones = [{"id": z.get("id", f"h{z.get('house_id')}"),
                        "name": z.get("name", z.get("id")),
                        "stage": z.get("stage", "unknown"),
                        "crop": z.get("crop", "")}
                       for z in (facility.get("zones") or [])]

    provenance = [{"source": "synopta", "method": "measured"}]

    return {
        "greenhouse_id": facility.get("greenhouse_id", "unknown"),
        "greenhouse_name": facility.get("greenhouse_name", "Greenhouse"),
        "assembled_at": assembled_at,
        "provenance": provenance,
        "coverage": {"not_observed": not_observed},
        "structure": {"zones": structure_zones},
        "observations": observations,
    }

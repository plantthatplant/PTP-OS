"""What changed since yesterday — the first thing a head grower wants to know.

A small, transparent comparison of this morning's key signals and concerns against
yesterday's. No engine, no new data: it reads the climate the provider already returns
and the concerns the analysis already produced, stores them, and diffs them next morning.
"""
from __future__ import annotations

from typing import Dict, List, Optional


def signals(latest_climate: dict, analysis) -> dict:
    """The handful of things worth watching morning to morning."""
    zones = {zid: {"temp": round(r.temp_c, 1), "hum": round(r.humidity_pct, 1), "airflow": r.airflow}
             for zid, r in latest_climate.items()}
    concerns = sorted(f"{c.zone_name}|{c.kind}|{c.title}" for c in analysis.concerns)
    return {"zones": zones, "concerns": concerns}


def diff(prev: Optional[dict], curr: dict, zone_names: Dict[str, str]) -> Optional[List[str]]:
    """Return the notable overnight changes, or None if there's nothing to compare to."""
    if not prev:
        return None
    lines: List[str] = []

    for zid, cz in curr.get("zones", {}).items():
        pz = prev.get("zones", {}).get(zid)
        if not pz:
            continue
        name = zone_names.get(zid, zid)
        dh = cz["hum"] - pz["hum"]
        if abs(dh) >= 3:
            lines.append(f"{name}: humidity {pz['hum']:.0f}% → {cz['hum']:.0f}% "
                         f"({'+' if dh > 0 else ''}{dh:.0f})")
        dt = cz["temp"] - pz["temp"]
        if abs(dt) >= 1.5:
            lines.append(f"{name}: temperature {pz['temp']:.0f}°C → {cz['temp']:.0f}°C")
        if cz["airflow"] != pz["airflow"]:
            lines.append(f"{name}: airflow {pz['airflow']} → {cz['airflow']}")

    prev_c = {c.split("|")[0] + "|" + c.split("|")[1]: c for c in prev.get("concerns", [])}
    curr_c = {c.split("|")[0] + "|" + c.split("|")[1]: c for c in curr.get("concerns", [])}
    for key in sorted(set(curr_c) - set(prev_c)):
        zn, kind = key.split("|")
        lines.append(f"NEW concern — {kind} in {zn}")
    for key in sorted(set(prev_c) - set(curr_c)):
        zn, kind = key.split("|")
        lines.append(f"cleared — {kind} in {zn} is no longer flagged")

    return lines

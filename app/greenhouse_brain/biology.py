"""Derived biological signals.

Conditions are levers; biology is the meaning. These small functions turn raw
climate numbers into the quantities a grower actually reasons about — chiefly
VPD (how hard the air pulls water from the plant) and dew point (when the canopy
will wet). They are deliberately transparent: every value can be explained.
"""
from __future__ import annotations

import math


def saturation_vapour_pressure_kpa(temp_c: float) -> float:
    """Tetens equation — saturation vapour pressure of air at temp_c, in kPa."""
    return 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))


def vpd_kpa(temp_c: float, humidity_pct: float) -> float:
    """Vapour Pressure Deficit. Low VPD (very humid) -> sluggish transpiration,
    soft growth, condensation/disease risk. High VPD (very dry) -> stomata close,
    growth stalls. Growers steer the band between."""
    svp = saturation_vapour_pressure_kpa(temp_c)
    return round(svp * (1.0 - humidity_pct / 100.0), 2)


def dew_point_c(temp_c: float, humidity_pct: float) -> float:
    """Temperature at which the air's moisture condenses. When surfaces near the
    dew point, the canopy wets — the precondition for many leaf diseases."""
    humidity_pct = max(1.0, min(100.0, humidity_pct))
    alpha = math.log(humidity_pct / 100.0) + (17.27 * temp_c) / (temp_c + 237.3)
    return round((237.3 * alpha) / (17.27 - alpha), 1)

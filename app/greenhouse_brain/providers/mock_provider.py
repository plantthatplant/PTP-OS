"""MockGreenhouseProvider — realistic, hand-built greenhouse reality for Sprint 1.

This is the 'FakeGreenhouseProvider' the backlog calls for (S1-05). It lets us
validate the whole reasoning flow before any live feed exists. The scenario is the
worked morning from specs/first-useful-decision.md, so the brain's answer can be
checked against the reasoning we already wrote down.

EVERYTHING here is invented. It is the first and most important shortcut, and is
exactly what Claude Dispatch (then Synopta) plus real plant observations replace.
"""
from __future__ import annotations

from typing import Dict, List

from typing import List

from ..domain import (
    Greenhouse, Zone, ClimateTargets, ClimateReading, Observation, Outlook, Change,
)
from .base import GreenhouseProvider


class MockGreenhouseProvider(GreenhouseProvider):
    name = "mock"
    data_source = "mock data"

    def get_greenhouse(self) -> Greenhouse:
        return Greenhouse(
            id="gh-kalaberga",
            name="Kalaberga",
            location="Sweden",
            zones=[
                Zone(
                    id="h1", name="House 1 (propagation)", stage="propagation",
                    crop="mixed aroid cuttings",
                    targets=ClimateTargets(temp_c=(22, 26), humidity_pct=(70, 85),
                                           note="humid, but avoid prolonged leaf wetness"),
                ),
                Zone(
                    id="h2", name="House 2 (growing on)", stage="vegetative",
                    crop="young foliage plants",
                    targets=ClimateTargets(temp_c=(20, 24), humidity_pct=(60, 75)),
                ),
                Zone(
                    id="h3", name="House 3 (finishing)", stage="finishing",
                    crop="finishing batch — order #1043",
                    targets=ClimateTargets(temp_c=(18, 22), humidity_pct=(55, 70),
                                           note="cooler/drier to tone before dispatch"),
                ),
            ],
        )

    def get_latest_climate(self) -> Dict[str, ClimateReading]:
        return {
            # House 1: too humid, air stagnant — a disease setup in the most fragile stock.
            "h1": ClimateReading("h1", temp_c=24.2, humidity_pct=92, co2_ppm=480,
                                 light_ppfd=90, airflow="low", hours_old=0.3),
            # House 2: reads oddly cold while the crop looks fine -> suspect sensor.
            "h2": ClimateReading("h2", temp_c=16.0, humidity_pct=66, co2_ppm=450,
                                 light_ppfd=120, airflow="normal",
                                 reliability="suspect", hours_old=0.4),
            # House 3: comfortable; the issue here is the crop is still soft (an observation).
            "h3": ClimateReading("h3", temp_c=21.0, humidity_pct=64, co2_ppm=440,
                                 light_ppfd=110, airflow="normal", hours_old=0.3),
        }

    def get_humidity_history(self, zone_id: str) -> List[float]:
        # Same-time-of-day humidity over the last few mornings (oldest first).
        return {
            "h1": [83, 86, 92],   # rising AND now over target -> a concern
            "h2": [62, 64, 66],   # creeping up but still in range -> a curiosity
            "h3": [63, 64, 64],
        }.get(zone_id, [])

    def get_observations(self) -> List[Observation]:
        return [
            Observation("h1", "leaf-wetness",
                        "condensation still on the bench-B canopy after sunrise"),
            Observation("h1", "stage-note",
                        "bench A holds 2-day-old unrooted cuttings (no roots yet)"),
            Observation("h1", "transient",
                        "overnight temperature dipped to ~19C and recovered by dawn; plants turgid"),
            Observation("h1", "dev-note",
                        "bench B has run a few days behind bench A for two batches now, under the same conditions"),
            Observation("h2", "sensor-anomaly",
                        "H2 reads well below the other houses while the plants look turgid and normal"),
            Observation("h2", "mother-stock",
                        "the House 2 mother plants are vigorous and well-fed — prime for taking cuttings"),
            Observation("h3", "tone",
                        "finishing batch still slightly soft; cool nights available for toning"),
            Observation("h3", "order",
                        "reserved for dispatch in 4 days (order #1043)"),
        ]

    def get_outlook(self) -> Outlook:
        return Outlook(text="clear and bright, a hot afternoon expected",
                       heat_load="high", confidence="Medium")

    def get_recent_changes(self) -> List[Change]:
        return [
            Change("h3",
                   text="yesterday we reduced irrigation frequency in House 3 to start toning",
                   question="did it firm the batch up without tipping it into water stress?"),
        ]

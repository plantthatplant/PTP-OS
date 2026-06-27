"""Decision Engine — reason over context, produce candidates and rank them.

This is where cultivation judgement lives. A small set of TRANSPARENT heuristics
(the Sprint-1 stand-in for a real Decision Library) reads the assembled context and
emits fully-characterised Candidates — concerns to address, opportunities to seize,
and the odd thing to hold. They are ranked for long-term plant health, never for
speed (the method from specs/first-useful-decision.md). No AI, no vendor types
(ADR-001, ADR-003).
"""
from __future__ import annotations

from typing import List, Optional

from .context_engine import GreenhouseContext, ZoneContext
from .domain import Candidate


# --- ranking scales (health-first; effort is NOT a ranking input) ------------

_VALUE = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
_WINDOW = {"Now": 4, "Hours": 3, "Today": 2, "Days": 1}
_CONF = {"High": 3, "Medium": 2, "Low": 1}
# cannot-wait (protect/prevent) outrank inspect, then progress, then maintain,
# then opportunity (value, not urgency). 'hold' never ranks.
_TIER = {"protect": 0, "prevent": 0, "inspect": 1, "progress": 2,
         "maintain": 3, "opportunity": 4, "hold": 9}

CAVEATS = [
    "Built on MOCK greenhouse data — no live Claude Dispatch / Synopta feed yet.",
    "Plant condition is INFERRED from climate plus a few human notes — no direct plant observations.",
    "The afternoon outlook is a placeholder, not a real weather feed.",
    "Trends and follow-ups use mock history; there is no Memory Engine yet.",
]


def _sort_key(c: Candidate):
    return (_TIER[c.kind], -_WINDOW[c.window], -_VALUE[c.value], -_CONF[c.confidence])


class DecisionEngine:

    def generate_candidates(self, ctx: GreenhouseContext) -> List[Candidate]:
        out: List[Candidate] = []
        for zc in ctx.zones:
            out += self._rules_for_zone(zc, ctx)
        return out

    def rank(self, candidates: List[Candidate]) -> List[Candidate]:
        """Actionable candidates, health-first. 'hold' is dropped (chosen non-action)."""
        return sorted([c for c in candidates if c.kind != "hold"], key=_sort_key)

    # --- the rules (transparent stand-in for a Decision Library) -------------

    def _rules_for_zone(self, zc: ZoneContext, ctx: GreenhouseContext) -> List[Candidate]:
        out: List[Candidate] = []
        z = zc.zone
        obs_types = {o.type for o in zc.observations}
        vulnerable = z.stage in ("propagation",)

        # 1) PREVENT — disease setup: humid + stagnant + (lingering leaf wetness).
        if zc.humidity_excess > 0 and zc.reading.airflow == "low":
            wet = "leaf-wetness" in obs_types
            rising = zc.humidity_trend == "rising"
            out.append(Candidate(
                zone_id=z.id, zone_name=z.name, kind="prevent",
                title="Rising disease risk (humid, stagnant, wet canopy)",
                action=("increase air movement now and ease humidity as the light climbs, "
                        "so the canopy dries and leaf wetness is broken"),
                why=("a wet, still, warm canopy on young tissue is how propagation is lost — "
                     "the classic Botrytis / damping-off setup"),
                objective="prevent disease (protect plant health) — a small cost now avoids a large, unrecoverable loss",
                expected_benefit="infection risk falls sharply within the hour",
                if_ignored="Botrytis / damping-off can take a propagation bench in a day or two; losses are unrecoverable",
                value="Critical" if vulnerable else "High",
                window="Now",
                confidence="High" if (wet and rising) else "Medium",
                effort="Low",
                evidence=[
                    f"humidity {zc.reading.humidity_pct:.0f}% vs target <= {z.targets.humidity_pct[1]:.0f}%",
                    f"air movement {zc.reading.airflow}; VPD {zc.vpd} kPa (low)",
                ] + (["condensation on the canopy after sunrise"] if wet else [])
                  + (["humidity rising three mornings running"] if rising else []),
            ))

        # 2) PROTECT — rootless cuttings facing a hot, bright afternoon.
        if vulnerable and ctx.outlook_heat_load == "high":
            out.append(Candidate(
                zone_id=z.id, zone_name=z.name, kind="protect",
                title="Unrooted cuttings exposed to the afternoon heat",
                action="set shade and misting for the unrooted bench ahead of the midday peak",
                why=("cuttings with no roots cannot replace the water they lose; a hot bright "
                     "afternoon can push them past recovery"),
                objective="protect the most vulnerable stock (plant health) — anticipate, don't react",
                expected_benefit="cuttings ride the peak turgid and keep forming roots",
                if_ignored="irreversible loss of the most fragile stock by mid-afternoon",
                value="Critical", window="Hours",
                confidence=ctx.outlook_confidence,  # rests on the (mock) forecast
                effort="Low",
                evidence=[f"outlook: {ctx.outlook_text}", "bench A holds 2-day unrooted cuttings"],
            ))

        # 3) INSPECT — a reading the crop contradicts; resolve before acting.
        if zc.reading.reliability == "suspect" or "sensor-anomaly" in obs_types:
            out.append(Candidate(
                zone_id=z.id, zone_name=z.name, kind="inspect",
                title="A climate reading the plants seem to contradict",
                action="walk the zone and check the sensor before trusting the number or acting on it",
                why="the plant is the ground truth; the reading disagrees with how the crop looks",
                objective="resolve high-stakes uncertainty before acting (avoid a wrong, costly move)",
                expected_benefit="either a corrected sensor or a real issue found — truth restored",
                if_ignored="acting on a false reading wastes energy and can harm a healthy crop",
                value="Medium", window="Today", confidence="Low", effort="Low",
                evidence=[f"{z.name} reads {zc.reading.temp_c:.0f}C, out of step with the other houses",
                          "plants reported turgid and normal"],
            ))

        # 4) PROGRESS — toning a finishing batch before a near dispatch date.
        if z.stage == "finishing" and "tone" in obs_types and "order" in obs_types:
            out.append(Candidate(
                zone_id=z.id, zone_name=z.name, kind="progress",
                title="Toning window before dispatch is open",
                action="begin a cooler, drier, well-aired regime to tone the finishing batch",
                why="a batch that ships in days must be hardened so it travels and lasts in the customer's hands",
                objective="build quality and shelf life (quality, on time) — the window is closing",
                expected_benefit="a firmer, more resilient plant that survives transport and the shelf",
                if_ignored="a soft batch ships, looks fine leaving, and fails at the customer",
                value="High", window="Days", confidence="Medium", effort="Medium",
                evidence=["finishing batch still slightly soft", "reserved for dispatch in 4 days",
                          "cool nights available"],
            ))

        # 5) OPPORTUNITY — realise potential while the window is good (not a problem).
        if "mother-stock" in obs_types:
            out.append(Candidate(
                zone_id=z.id, zone_name=z.name, kind="opportunity",
                title="Mother stock is at its best — a window to propagate",
                action="take cuttings from the vigorous mother plants while they are strong",
                why="cuttings taken from vigorous, well-fed mother stock root faster and start stronger",
                objective="realise propagation potential while the stock is at its peak (growth potential)",
                expected_benefit="a stronger, more uniform next generation of cuttings",
                if_ignored="no harm — just a good propagation window left unused",
                value="Medium", window="Days", confidence="Medium", effort="Medium",
                evidence=["mother plants vigorous and well-fed"],
            ))

        # 6) HOLD — a transient that already recovered: do nothing, on purpose.
        if "transient" in obs_types:
            out.append(Candidate(
                zone_id=z.id, zone_name=z.name, kind="hold",
                title="Overnight excursion already recovered",
                action="do nothing — hold steady and re-observe",
                why="the dip corrected by dawn and the plants are turgid; recovery is the diagnostic",
                objective="avoid intervention whiplash — patience protects the plant",
                expected_benefit="no action needed",
                if_ignored="n/a",
                value="Low", window="Days", confidence="High", effort="Low",
                evidence=["overnight temperature dip recovered by sunrise; plants turgid"],
            ))
        return out

    # --- synthesis helpers ---------------------------------------------------

    def overall_confidence(self, rec: Optional[Candidate], ctx: GreenhouseContext):
        if rec is None:
            return "Low", "No clear signal this morning — too little to go on."
        if rec.confidence == "High":
            return ("Medium-high",
                    "The climate signals are clear and corroborated; but plant condition is "
                    "inferred from climate, not yet directly observed.")
        return ("Medium",
                "The reasoning is sound on the evidence available, though some rests on a "
                "placeholder outlook and on climate rather than direct plant observation.")

    def morning_summary(self, ctx: GreenhouseContext, concern: Optional[Candidate],
                        opportunities: List[Candidate], curiosities) -> str:
        if concern is not None:
            head = (f"{ctx.greenhouse.name} is mostly settled this morning, but "
                    f"{concern.zone_name} needs attention before the day warms")
        else:
            head = f"{ctx.greenhouse.name} looks settled and on track this morning"
        extras = []
        if opportunities:
            extras.append(f"{len(opportunities)} opportunity" + ("s" if len(opportunities) != 1 else ""))
        if curiosities:
            extras.append(f"{len(curiosities)} curiosit" + ("ies" if len(curiosities) != 1 else "y"))
        tail = (" I've also noted " + " and ".join(extras) + ".") if extras else ""
        return head + "." + tail

"""Curiosity Engine — notice what deserves attention but is not yet a recommendation.

A curiosity is the seed of learning: a pattern, an oddity, or a deliberate change
whose effect we'd like to confirm. Curiosities never alarm. They invite a look, and
they are how the Brain stays interested in the world rather than only firefighting it
(see docs/decision-philosophy.md 'value information', docs/cultivation-intelligence-model.md
'pattern recognition', and RFC-001's learning loop).

These are transparent heuristics, like the decision rules — a Sprint-1 stand-in for a
real curiosity/learning capability.
"""
from __future__ import annotations

from typing import List

from .context_engine import GreenhouseContext
from .domain import Curiosity


class CuriosityEngine:
    def generate(self, ctx: GreenhouseContext, provider) -> List[Curiosity]:
        out: List[Curiosity] = []
        names = {zc.zone.id: zc.zone.name for zc in ctx.zones}

        for zc in ctx.zones:
            # 1) PATTERN — a within-range drift. Not a problem yet; worth understanding.
            if zc.humidity_trend == "rising" and zc.humidity_excess == 0:
                out.append(Curiosity(
                    subject=zc.zone.name, kind="pattern",
                    observation=(f"humidity in {zc.zone.name} has crept up a little each morning "
                                 "this week, though it is still comfortably in range"),
                    why_it_matters=("a steady drift, even within range, is sometimes the early shape "
                                    "of a problem and sometimes just the season changing — better to "
                                    "understand it before it matters"),
                    worth_a_look="watch it a few more mornings; glance at overnight ventilation and the outside weather",
                ))

            # 2) ANOMALY/PATTERN — a consistent difference under the same conditions.
            for o in zc.observations:
                if o.type == "dev-note":
                    out.append(Curiosity(
                        subject=zc.zone.name, kind="pattern",
                        observation=o.text,
                        why_it_matters=("a consistent difference under the same conditions usually has "
                                        "a cause worth finding — substrate, light, position, or the cuttings themselves"),
                        worth_a_look="compare the two benches side by side; note any difference in medium, placement, or light",
                    ))

        # 3) EXPERIMENT FOLLOW-UP — we changed something; did it do what we hoped?
        for ch in provider.get_recent_changes():
            out.append(Curiosity(
                subject=names.get(ch.zone_id, ch.zone_id), kind="experiment-followup",
                observation=ch.text,
                why_it_matters=("we made a deliberate change, so confirming its effect is exactly how "
                                "we turn a guess into knowledge"),
                worth_a_look=ch.question,
            ))
        return out

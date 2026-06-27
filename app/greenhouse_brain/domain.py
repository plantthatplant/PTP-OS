"""Domain model (the slice Sprint 1 needs).

These are the shared, provider- and model-agnostic concepts the whole pipeline
speaks in — the code echo of `domain/`. Nothing here knows where data came from
(Synopta, Claude Dispatch, or mock) or whether any AI is involved.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


# --- Reality, as supplied by a provider -------------------------------------

@dataclass
class ClimateTargets:
    """What 'good' looks like for this zone's crop and stage (Knowledge)."""
    temp_c: Tuple[float, float]
    humidity_pct: Tuple[float, float]
    note: str = ""


@dataclass
class Zone:
    id: str
    name: str
    stage: str          # propagation | vegetative | finishing
    crop: str
    targets: ClimateTargets


@dataclass
class ClimateReading:
    zone_id: str
    temp_c: float
    humidity_pct: float
    co2_ppm: float
    light_ppfd: float
    airflow: str            # low | normal | good
    source: str = "mock-sensor"
    reliability: str = "normal"   # normal | suspect
    hours_old: float = 0.0
    timestamp: Optional[str] = None   # absolute capture time, if the provider supplies one


@dataclass
class Observation:
    """A recorded fact about reality. Human notes rank equal to sensors."""
    zone_id: str
    type: str               # leaf-wetness | sensor-anomaly | tone | order | stage-note | transient
    text: str
    source: str = "grower"  # grower | sensor | camera


@dataclass
class Outlook:
    """A placeholder day-ahead outlook (a Sprint-1 stand-in for a Weather provider)."""
    text: str
    heat_load: str          # low | moderate | high
    confidence: str         # Low | Medium | High


@dataclass
class Change:
    """A deliberate recent change worth following up — the seed of a learning loop."""
    zone_id: str
    text: str               # what was changed
    question: str           # what we'd like to know about its effect


@dataclass
class Greenhouse:
    id: str
    name: str
    location: str
    zones: List[Zone]


# --- What the brain produces -------------------------------------------------

@dataclass
class Candidate:
    """One thing the grower could do, fully characterised (see specs/first-useful-decision.md)."""
    zone_id: str
    zone_name: str
    kind: str               # protect | prevent | inspect | progress | maintain | hold
    title: str
    action: str
    why: str
    objective: str
    expected_benefit: str
    if_ignored: str
    value: str              # Critical | High | Medium | Low
    window: str             # Now | Hours | Today | Days
    confidence: str         # High | Medium | Low
    effort: str             # Low | Medium | High
    evidence: List[str] = field(default_factory=list)


@dataclass
class Curiosity:
    """Something not yet a recommendation — an observation that deserves attention.

    Curiosities never alarm. They encourage investigation and become future learning.
    """
    subject: str            # the zone or area it concerns
    kind: str               # pattern | anomaly | experiment-followup
    observation: str        # what was noticed (the thing we're curious about)
    why_it_matters: str     # why it's worth understanding (gently)
    worth_a_look: str       # a low-key suggestion for how to investigate


@dataclass
class MorningAnalysis:
    """What the Brain worked out before anyone arrived. Computed once each morning,
    stored, and served when the grower asks 'How is the greenhouse today?'."""
    prepared_at: str                 # e.g. "05:50"
    greenhouse_name: str
    summary: str
    concerns: List[Candidate]        # risks, ranked (prevent / protect / inspect)
    opportunities: List[Candidate]   # ways to realise potential (not problems)
    priorities: List[Candidate]      # today's ranked do-list (top few)
    curiosities: List[Curiosity]     # things to wonder about and watch
    confidence_level: str
    confidence_rationale: str
    data_source: str
    caveats: List[str] = field(default_factory=list)

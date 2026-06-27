"""A tiny store for the latest Morning Analysis and the raw feedback log.

So the morning's work survives between commands: `morning.py` computes and saves it,
and `ask.py` serves it without re-analysing. This is a deliberately minimal local
cache — NOT the Memory Engine. It keeps only the most recent analysis and learns
nothing. The real Memory Engine (history, outcomes, calibration) replaces it later.

It also appends grower feedback to a plain, append-only log (`data/feedback.jsonl`).
That log is *collected, never analysed* here — capturing real-world validation is the
whole point; making sense of it comes in a later sprint.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict
from typing import Optional

from .domain import MorningAnalysis, Candidate, Curiosity

_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_STATE_DIR = os.path.join(_APP_DIR, ".state")          # transient cache
_STATE_FILE = os.path.join(_STATE_DIR, "morning-analysis.json")
_DATA_DIR = os.path.join(_APP_DIR, "data")             # kept data
_FEEDBACK_FILE = os.path.join(_DATA_DIR, "feedback.jsonl")


def save(analysis: MorningAnalysis) -> None:
    os.makedirs(_STATE_DIR, exist_ok=True)
    with open(_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(asdict(analysis), f, indent=2)


def load() -> Optional[MorningAnalysis]:
    if not os.path.exists(_STATE_FILE):
        return None
    with open(_STATE_FILE, "r", encoding="utf-8") as f:
        d = json.load(f)
    return MorningAnalysis(
        prepared_at=d["prepared_at"],
        greenhouse_name=d["greenhouse_name"],
        summary=d["summary"],
        concerns=[Candidate(**c) for c in d["concerns"]],
        opportunities=[Candidate(**c) for c in d["opportunities"]],
        priorities=[Candidate(**c) for c in d["priorities"]],
        curiosities=[Curiosity(**c) for c in d["curiosities"]],
        confidence_level=d["confidence_level"],
        confidence_rationale=d["confidence_rationale"],
        data_source=d["data_source"],
        caveats=d.get("caveats", []),
    )


def append_feedback(record: dict) -> str:
    """Append one feedback record to the log. Capture only — nothing is read back
    or analysed here. Returns the log path."""
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_FEEDBACK_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return _FEEDBACK_FILE


# --- the recommendation lifecycle (Sprint 3) --------------------------------
# A minimal local persistence for the learning loop — NOT the Memory Engine, but the
# place experiments live (open) and memories accumulate (closed, append-only).

_EXPERIMENTS_FILE = os.path.join(_DATA_DIR, "experiments-open.json")
_MEMORIES_FILE = os.path.join(_DATA_DIR, "memories.jsonl")
_QUESTIONS_FILE = os.path.join(_DATA_DIR, "questions-today.json")
_ANSWERS_FILE = os.path.join(_DATA_DIR, "answers.jsonl")


def append_answer(record: dict) -> None:
    """Store a walk answer as evidence (append-only). Captured, not yet analysed."""
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_ANSWERS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_answers():
    if not os.path.exists(_ANSWERS_FILE):
        return []
    out = []
    with open(_ANSWERS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


# --- Field Companion interactions (Sprint 4) --------------------------------
# Every interaction the Companion has with the grower (asked or silently considered) is
# preserved here as permanent evidence — append-only, captured not analysed. The *worthwhile*
# signal still flows through append_question_eval() so the existing learning loop applies.

_INTERACTIONS_FILE = os.path.join(_DATA_DIR, "interactions.jsonl")


def append_interaction(record: dict) -> str:
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_INTERACTIONS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return _INTERACTIONS_FILE


def load_interactions():
    if not os.path.exists(_INTERACTIONS_FILE):
        return []
    out = []
    with open(_INTERACTIONS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


_TODAY_SNAPSHOT_FILE = os.path.join(_DATA_DIR, "today-snapshot.json")


def save_today_snapshot(meta: dict) -> None:
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_TODAY_SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)


def load_today_snapshot():
    if not os.path.exists(_TODAY_SNAPSHOT_FILE):
        return None
    with open(_TODAY_SNAPSHOT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


_YESTERDAY_FILE = os.path.join(_DATA_DIR, "yesterday-signals.json")


def save_yesterday(signals: dict) -> None:
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_YESTERDAY_FILE, "w", encoding="utf-8") as f:
        json.dump(signals, f, indent=2, ensure_ascii=False)


def load_yesterday():
    if not os.path.exists(_YESTERDAY_FILE):
        return None
    with open(_YESTERDAY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_open_experiments(experiments) -> None:
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_EXPERIMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump([asdict(e) for e in experiments], f, indent=2, ensure_ascii=False)


def load_open_experiments():
    from .lifecycle import Experiment
    if not os.path.exists(_EXPERIMENTS_FILE):
        return []
    with open(_EXPERIMENTS_FILE, "r", encoding="utf-8") as f:
        return [Experiment(**d) for d in json.load(f)]


def append_memory(experiment) -> None:
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_MEMORIES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(experiment), ensure_ascii=False) + "\n")


def load_memories():
    if not os.path.exists(_MEMORIES_FILE):
        return []
    out = []
    with open(_MEMORIES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def save_questions(questions) -> None:
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump([asdict(q) for q in questions], f, indent=2, ensure_ascii=False)


def load_questions():
    from .knowledge_gap import Question
    if not os.path.exists(_QUESTIONS_FILE):
        return []
    with open(_QUESTIONS_FILE, "r", encoding="utf-8") as f:
        return [Question(**d) for d in json.load(f)]


_QEVAL_FILE = os.path.join(_DATA_DIR, "question-evaluations.jsonl")


def append_question_eval(record: dict) -> None:
    """Permanent, append-only log of whether a question was worth asking."""
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_QEVAL_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_question_evals():
    if not os.path.exists(_QEVAL_FILE):
        return []
    out = []
    with open(_QEVAL_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def prior_worth_by_kind() -> dict:
    """Learned multiplier per decision-kind: how often that kind of question has been
    worth asking. Default 1.0; a kind that's never worthwhile drifts toward 0.5, one that
    always is toward 1.5 — so low-value questions stop clearing the bar over time."""
    tally = {}
    for e in load_question_evals():
        k = e.get("decision_kind", "?")
        t = tally.setdefault(k, [0, 0])
        t[0] += 1
        if e.get("worthwhile"):
            t[1] += 1
    return {k: round(0.5 + (w / n), 2) for k, (n, w) in tally.items() if n}

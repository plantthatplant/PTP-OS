"""GaiaService — the gateway facade. Composes the Brain once; returns Gaia's understanding.

This consolidates the morning/evening/companion orchestration that was duplicated across
gaia.py, companion/daily.py, and the demos (see docs/gaia-api-audit.md). It is the only place
that imports store (Memory), knowledge_gap, lifecycle, fusion, providers, and observers.

It is stateless per call (state lives in the snapshot + the store, not in the service) and it
returns plain dicts of *understanding* — no file paths, no vendor names, no observer identity.
It adds no reasoning; the engines still reason exactly once.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from . import _paths

from greenhouse_brain.snapshot_importer import import_snapshot
from greenhouse_brain.providers.snapshot_provider import SnapshotProvider
from greenhouse_brain.morning_analysis import MorningAnalysisEngine
from greenhouse_brain import knowledge_gap, store, fusion
from greenhouse_brain.lifecycle import experiment_from_candidate, reinforce, apply_outcome
from collector.observers import plan_vs_reality
from . import health as _health

_LATEST = os.path.join(_paths.REPO_ROOT, "data", "inbox", "latest.json")
_PLAN = os.path.join(_paths.REPO_ROOT, "data", "inbox", "plan-latest.json")
_SAMPLE = os.path.join(_paths.APP_DIR, "sample_snapshot.json")
_OBS_LOG = os.path.join(_paths.APP_DIR, "data", "observations.jsonl")


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _short(name):
    import re
    return re.sub(r"\s*\(.*?\)\s*", "", name or "").strip() or (name or "")


class GaiaService:
    def __init__(self, snapshot_path=None, plan_path=None):
        self.snapshot_path = snapshot_path
        self.plan_path = plan_path or _PLAN

    # --- internal composition (the one orchestration) -----------------------
    def _snapshot(self):
        # Resilience: prefer the configured snapshot, then the published latest, then the bundled
        # sample — so a missing or not-yet-collected snapshot never takes Gaia down.
        for path in (self.snapshot_path, _LATEST, _SAMPLE):
            if path and os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        return import_snapshot(json.load(f))
                except (OSError, json.JSONDecodeError):
                    continue
        with open(_SAMPLE, "r", encoding="utf-8") as f:   # last resort, always present
            return import_snapshot(json.load(f))

    def _plan_obs(self):
        try:
            with open(self.plan_path, "r", encoding="utf-8") as f:
                return json.load(f).get("observations", [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _compose(self):
        snap = self._snapshot()
        date = (snap.assembled_at or "today")[:10]
        provider = SnapshotProvider(snap)
        analysis = MorningAnalysisEngine().run(provider)
        # keep the day's experiments + questions in the store (the existing memory), so answers
        # can be routed later — same as the CLI, now in one place.
        open_exps = store.load_open_experiments()
        existing = {e.id for e in open_exps}
        for c in list(analysis.priorities) + list(analysis.opportunities):
            e = experiment_from_candidate(c, date)
            if e.id not in existing:
                open_exps.append(e); existing.add(e.id)
        store.save_open_experiments(open_exps)
        questions, _ = knowledge_gap.generate(analysis, [], snap.assembled_at, date,
                                              store.prior_worth_by_kind())
        store.save_questions(questions)
        plan_obs = self._plan_obs()
        reality = [{"subject": o.subject, "kind": o.kind, "value": o.value} for o in snap.present()]
        gaps = plan_vs_reality.compare(plan_obs, reality, now_iso=snap.assembled_at)
        brief = fusion.synthesize(analysis, coverage=snap.coverage(),
                                  reality=snap.reality_confidence(), plan_obs=plan_obs,
                                  plan_gaps=gaps, memories=store.load_memories(),
                                  changes=None, questions=questions)
        _health.STATE.record_analysis()
        return snap, provider, analysis, questions, gaps, brief

    # --- public surface (one method per endpoint) ---------------------------
    def morning(self) -> dict:
        snap, _, analysis, questions, gaps, brief = self._compose()
        return {
            "greenhouse": _short(analysis.greenhouse_name),
            "brief": brief.narrative,
            "priority": brief.one_priority,
            "first_recommendation": brief.one_recommendation,
            "confidence": brief.confidence,
            "ask_today": brief.ask_today,
            "observe_today": brief.observe_today,
            "learned_yesterday": brief.learned_yesterday,
            "knowledge_gaps": [self._q(q) for q in questions[:3]]
                              + [{"text": g["text"], "kind": "plan-vs-reality"} for g in gaps[:2]],
        }

    def houses(self) -> list:
        snap, provider, analysis, *_ = self._compose()
        climate = provider.get_latest_climate()
        concern_by_zone = {c.zone_id: c for c in analysis.concerns}
        out = []
        for z in snap.zones:
            r = climate.get(z.id)
            c = concern_by_zone.get(z.id)
            out.append({
                "id": z.id, "name": _short(z.name), "stage": z.stage, "crop": z.crop,
                "climate": ({"air_temperature_c": r.temp_c, "humidity_pct": r.humidity_pct,
                             "airflow": r.airflow, "reliable": r.reliability != "suspect"} if r else None),
                "status": (c.title if c else "settled"),
                "needs_attention": bool(c)})
        return out

    def house(self, house_id) -> dict:
        return next((h for h in self.houses() if h["id"] == house_id), None)

    def memory(self, limit=20) -> list:
        mems = store.load_memories()[-limit:]
        return [{"date": m.get("closed_on"), "zone": _short(m.get("zone", "")),
                 "lesson": m.get("lesson"), "outcome": m.get("outcome"),
                 "confidence": m.get("confidence_after")} for m in mems if m.get("lesson")]

    def memory_search(self, q) -> list:
        ql = (q or "").lower()
        return [m for m in self.memory(limit=1000)
                if ql in (str(m.get("lesson", "")) + " " + str(m.get("zone", ""))).lower()]

    def knowledge_gaps(self) -> list:
        _, _, _, questions, gaps, _ = self._compose()
        return [self._q(q) for q in questions] + [
            {"text": g["text"], "kind": "plan-vs-reality", "subject": g.get("subject")} for g in gaps]

    def learning(self) -> dict:
        mems = store.load_memories()
        closed = [m for m in mems if m.get("status") == "closed"]
        held = [m for m in closed if m.get("outcome") == "improved"]
        return {
            "experiments_open": len(store.load_open_experiments()),
            "experiments_closed": len(closed),
            "lessons": [m.get("lesson") for m in closed if m.get("lesson")][-10:],
            "calibration": {"closed": len(closed), "predictions_held": len(held),
                            "hold_rate": round(len(held) / len(closed), 2) if closed else None},
        }

    def questions(self) -> list:
        _, _, _, questions, _, _ = self._compose()
        return [self._q(q) for q in questions]

    def answer_question(self, qid, answer) -> dict:
        questions = store.load_questions()
        q = next((x for x in questions if x.id == qid), None)
        if q is None:
            return {"error": "unknown question id"}
        open_exps = store.load_open_experiments()
        by_id = {e.id: e for e in open_exps}
        date = next((e.opened_on for e in open_exps), (datetime.now().date().isoformat()))
        al = (answer or "").lower()
        informative = not any(w in al for w in ("not sure", "dunno", "don't know"))
        negated = any(w in al for w in ("no ", "not ", "n't", " dry", "none", "clear", "fine"))
        result = {"question_id": qid, "informative": informative}
        if q.kind == "close" and q.experiment_id in by_id:
            e = by_id[q.experiment_id]
            outcome = ("improved" if any(w in al for w in ("better", "help", "improv"))
                       else "worse" if "worse" in al else "unchanged" if "same" in al else "unknown")
            apply_outcome(e, "done" if "skip" not in al else "skipped", outcome, answer, date)
            store.append_memory(e)
            store.save_open_experiments([x for x in open_exps if x.id != e.id])
            result.update(confidence_before=e.confidence_before, confidence_after=e.confidence_after,
                          worthwhile=outcome != "unknown")
        else:
            exp = by_id.get(f"exp-{date}-{q.decision_id}-{q.decision_kind}")
            before = getattr(exp, "confidence_before", None)
            after = before
            if exp is not None and informative:
                before, after = reinforce(exp, agrees=not negated, note=answer)
                store.save_open_experiments(open_exps)
            store.append_answer({"question": q.text, "answer": answer, "kind": q.kind,
                                 "subject": q.subject, "captured_on": date})
            worthwhile = informative and (q.voi >= 0.30 or negated)
            store.append_question_eval({"question_id": qid, "decision_kind": q.decision_kind,
                                        "voi": q.voi, "answer": answer, "changed_decision": negated,
                                        "confidence_increase": informative, "worthwhile": worthwhile,
                                        "captured_on": date})
            result.update(confidence_before=before, confidence_after=after, worthwhile=worthwhile)
        return result

    def voice_note(self, text, subject="site") -> dict:
        """The API converts a voice note into a Canonical Observation. Clients never interpret."""
        obs = {"subject": subject or "site", "kind": "note", "value": text,
               "captured_at": _now(), "source": "grower (voice)", "method": "observed-by-human",
               "confidence": "medium", "verbatim": text}
        store.append_answer({"question": "(voice note)", "answer": text, "kind": "note",
                             "subject": subject or "site", "captured_on": _now()[:10]})
        return {"accepted": True, "observation": obs}

    def post_observation(self, payload) -> dict:
        """Accept Canonical Observation(s) only. Validate the envelope; never reason on them."""
        items = payload if isinstance(payload, list) else [payload]
        accepted, rejected = [], []
        for o in items:
            ok = isinstance(o, dict) and o.get("subject") and o.get("kind") and (
                o.get("value") is not None or o.get("absence"))
            (accepted if ok else rejected).append(o)
        if accepted:
            os.makedirs(os.path.dirname(_OBS_LOG), exist_ok=True)
            with open(_OBS_LOG, "a", encoding="utf-8") as f:
                for o in accepted:
                    o.setdefault("captured_at", _now())
                    f.write(json.dumps(o, ensure_ascii=False) + "\n")
        return {"accepted": len(accepted), "rejected": len(rejected)}

    def observations(self, limit=50) -> list:
        """Observation history — posted Canonical Observations + captured voice notes, newest
        first. Read-only view of what has been observed; no reasoning."""
        items = []
        if os.path.exists(_OBS_LOG):
            with open(_OBS_LOG, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        items.append(json.loads(line))
        for a in store.load_answers():
            if a.get("kind") == "note":
                items.append({"subject": a.get("subject", "site"), "kind": "note",
                              "value": a.get("answer"), "captured_at": a.get("captured_on"),
                              "source": "grower (voice)", "method": "observed-by-human",
                              "confidence": "medium"})
        items.sort(key=lambda o: str(o.get("captured_at") or ""), reverse=True)
        return [{"subject": o.get("subject"), "kind": o.get("kind"), "value": o.get("value"),
                 "captured_at": o.get("captured_at"), "method": o.get("method"),
                 "confidence": o.get("confidence")} for o in items[:limit]]

    def companion(self) -> dict:
        """The Even G2 surface: exactly one message + urgency + confidence + ack state."""
        _, _, analysis, questions, gaps, brief = self._compose()
        critical = next((c for c in analysis.concerns if c.value == "Critical"), None)
        if critical:
            return {"message": f"{_short(critical.zone_name)}: {critical.title}",
                    "urgency": "warn", "confidence": brief.confidence,
                    "acknowledged": False, "question_id": None}
        if questions:
            q = max(questions, key=lambda x: x.voi)
            return {"message": brief.ask_today, "urgency": "ask", "confidence": brief.confidence,
                    "acknowledged": False, "question_id": q.id}
        return {"message": brief.headline, "urgency": "info", "confidence": brief.confidence,
                "acknowledged": True, "question_id": None}

    def health(self) -> dict:
        """Production liveness — overall + per-component status, last snapshot/analysis, uptime."""
        st = _health.STATE
        # last snapshot freshness
        snap_path = self.snapshot_path or (_LATEST if os.path.exists(_LATEST) else _SAMPLE)
        snap_at, snap_age_min = None, None
        try:
            with open(snap_path, "r", encoding="utf-8") as f:
                snap_at = json.load(f).get("assembled_at")
            snap_age_min = int((datetime.now(timezone.utc).timestamp()
                                - os.path.getmtime(snap_path)) / 60)
        except (OSError, json.JSONDecodeError):
            pass
        try:
            mem_ok = isinstance(store.load_memories(), list)
            learn = self.learning()
            learn_ok = True
        except Exception:
            mem_ok = learn_ok = False
            learn = {}
        collector = st.last_collection or {"status": "not-run-yet"}
        snapshot_present = snap_at is not None
        stale = snap_age_min is not None and snap_age_min > 24 * 60
        overall = "ok"
        if not snapshot_present or not mem_ok or not learn_ok:
            overall = "degraded"
        if collector.get("status") in ("source-failed",) and not snapshot_present:
            overall = "down"
        return {
            "status": overall,
            "version": st.version,
            "uptime_seconds": st.uptime_seconds(),
            "api": "ok",
            "brain": "ok",
            "memory": "ok" if mem_ok else "error",
            "learning": "ok" if learn_ok else "error",
            "collector": collector.get("status", "unknown"),
            "last_snapshot": {"assembled_at": snap_at, "age_minutes": snap_age_min,
                              "stale": bool(stale)},
            "last_successful_analysis": st.last_analysis_at,
            "experiments": {"open": learn.get("experiments_open"),
                            "closed": learn.get("experiments_closed")},
        }

    def evening(self) -> dict:
        learning = self.learning()
        return {"reviewed": True, "lessons_today": learning["lessons"][-3:],
                "calibration": learning["calibration"],
                "open_experiments": learning["experiments_open"]}

    # --- helpers ------------------------------------------------------------
    @staticmethod
    def _q(q) -> dict:
        return {"id": q.id, "text": q.text, "subject": _short(q.subject),
                "why": q.biological_reason, "value": round(getattr(q, "voi", 0), 3),
                "kind": q.kind}

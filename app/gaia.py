#!/usr/bin/env python3
"""Gaia — the daily greenhouse companion.

    gaia morning [snapshot.json]   prepare and show the Morning Brief (+ the day's questions)
    gaia walk                      answer the walk questions; close yesterday's experiments
    gaia evening                   the Evening Review: what was expected vs what happened

One day of working with Gaia is: morning -> walk -> evening. Every recommendation becomes
an experiment that is followed to its outcome and kept as a memory, so each day's advice is
a little wiser than the last.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from greenhouse_brain import store
from greenhouse_brain.snapshot_importer import import_snapshot
from greenhouse_brain.providers.snapshot_provider import SnapshotProvider
from greenhouse_brain.morning_analysis import MorningAnalysisEngine
from greenhouse_brain.lifecycle import experiment_from_candidate, apply_outcome, reinforce
from greenhouse_brain import views, changes, memory_engine, knowledge_gap, workflow

_GREENHOUSE = "Kålaberga"

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_SAMPLE_SNAPSHOT = os.path.join(_APP_DIR, "sample_snapshot.json")
_INBOX = os.path.join(_APP_DIR, "data", "inbox", "latest.json")   # where a live feed drops the morning snapshot
_DUE_TONIGHT = {"Now", "Hours", "Today"}


def _snapshot_path(argv):
    """Friction-free: an explicit path wins; else the live inbox; else the bundled sample."""
    if argv:
        return argv[0]
    if os.path.exists(_INBOX):
        return _INBOX
    return _SAMPLE_SNAPSHOT


def _ask(prompt):
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        return ""


def _parse_outcome(s):
    s = s.lower()
    if any(w in s for w in ("better", "improv", "helped", "recover", "dry", "clean", "firm", "good", "yes")):
        return "improved"
    if any(w in s for w in ("worse", "declin", "spread", "sick", "lost")):
        return "worse"
    if any(w in s for w in ("same", "unchanged", "no change", "still", "soft", "no diff", "little")):
        return "unchanged"
    return "unknown"


def _parse_action(s):
    s = s.lower()
    if any(w in s for w in ("skip", "didn't", "did not", "no")):
        return "skipped"
    if any(w in s for w in ("modif", "different", "less", "instead", "changed")):
        return "modified"
    return "done"


# --- gaia morning ------------------------------------------------------------

def cmd_morning(argv):
    path = _snapshot_path(argv)
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    snapshot = import_snapshot(raw)
    date = (snapshot.assembled_at or "today")[:10]

    provider = SnapshotProvider(snapshot)
    analysis = MorningAnalysisEngine().run(provider)   # existing engines, untouched
    store.save(analysis)

    # What changed since yesterday (and remember today's signals for tomorrow).
    curr_signals = changes.signals(provider.get_latest_climate(), analysis)
    zone_names = {z.id: z.name for z in snapshot.zones}
    change_lines = changes.diff(store.load_yesterday(), curr_signals, zone_names)
    store.save_yesterday(curr_signals)

    open_exps = store.load_open_experiments()
    carried = [e for e in open_exps if e.status == "open" and e.window == "Days"]  # yesterday's, due now
    recalls = views.recall_notes(analysis, store.load_memories())

    # Open an experiment for every recommendation that doesn't already exist.
    existing = {e.id for e in open_exps}
    for c in list(analysis.priorities) + list(analysis.opportunities):
        e = experiment_from_candidate(c, date)
        if e.id not in existing:
            open_exps.append(e)
            existing.add(e.id)
    store.save_open_experiments(open_exps)

    prior = store.prior_worth_by_kind()
    questions, held_back = knowledge_gap.generate(analysis, carried, snapshot.assembled_at, date, prior)
    store.save_questions(questions)

    coverage, reality = snapshot.coverage(), snapshot.reality_confidence()
    store.save_today_snapshot({"date": date, "greenhouse": analysis.greenhouse_name,
                               "assembled_at": snapshot.assembled_at, "signals": curr_signals,
                               "coverage": coverage, "reality": reality})

    print(views.render_brief(analysis, coverage, reality, questions, recalls,
                             changes=change_lines, held_back=len(held_back)))


# --- gaia walk ---------------------------------------------------------------

def cmd_walk(argv):
    questions = store.load_questions()
    if not questions:
        print("No walk questions today. Run 'gaia morning' first.")
        return
    open_exps = store.load_open_experiments()
    by_id = {e.id: e for e in open_exps}
    date = next((e.opened_on for e in open_exps), "today")

    print("On the walk — answer in your own words (Enter to skip, q to stop):\n")
    for q in questions:
        ans = _ask(f"  {q.text}\n   > ").strip()
        if ans.lower() == "q":
            break
        if not ans:
            print("   (skipped)\n")
            continue
        if q.kind == "close" and q.experiment_id in by_id:
            e = by_id[q.experiment_id]
            apply_outcome(e, _parse_action(ans), _parse_outcome(ans), ans, date)
            store.append_memory(e)
            open_exps = [x for x in open_exps if x.id != e.id]
            store.append_question_eval({"question_id": q.id, "decision_kind": "close",
                                        "voi": q.voi, "answer": ans, "changed_decision": e.outcome != "unknown",
                                        "confidence_increase": True, "worthwhile": True, "captured_on": date})
            print(f"   ✓ closed yesterday's {e.zone} experiment ({e.outcome}).\n")
        else:
            store.append_answer({"question": q.text, "answer": ans, "kind": q.kind,
                                 "subject": q.subject, "captured_on": date})
            # Was the interruption worthwhile? Did the answer change/confirm the decision?
            al = ans.lower()
            informative = not any(w in al for w in ("not sure", "dunno", "don't know", "no idea"))
            negated = any(w in al for w in ("no ", "not ", "n't", " clear", "dry", "none", "fine"))
            worthwhile = informative and (q.voi >= 0.30 or negated)
            store.append_question_eval({"question_id": q.id, "decision_kind": q.decision_kind,
                                        "voi": q.voi, "answer": ans, "changed_decision": negated,
                                        "confidence_increase": informative, "worthwhile": worthwhile,
                                        "captured_on": date})
            print(f"   ✓ noted{' — that was worth asking' if worthwhile else ''}.\n")
    store.save_open_experiments(open_exps)
    print("Thanks — stored as evidence. Tonight: gaia evening")


# --- gaia evening ------------------------------------------------------------

def cmd_evening(argv):
    open_exps = store.load_open_experiments()
    due = [e for e in open_exps if e.status == "open" and e.window in _DUE_TONIGHT]
    if not due:
        print("Nothing came due to review tonight.")
        return
    date = next((e.opened_on for e in due), "today")
    name = "Kålaberga"

    print("End of day — what actually happened? (Enter to skip a line)\n")
    closed = []
    for e in due:
        print(f"  {e.zone}: we recommended — {e.recommendation}")
        act = _ask("   was it done? (done / modified / skipped): ").strip() or "done"
        res = _ask("   and the result? (better / same / worse / not sure): ").strip()
        apply_outcome(e, _parse_action(act), _parse_outcome(res), res, date)
        store.append_memory(e)
        closed.append(e)
        print()

    remaining = [e for e in open_exps if e.id not in {c.id for c in closed}]
    store.save_open_experiments(remaining)
    print(views.render_evening(closed, name, date))
    carried = [e for e in remaining if e.window == "Days"]
    if carried:
        print(f"\n  {len(carried)} longer-window item(s) still open — I'll ask about "
              f"{carried[0].zone} on tomorrow's walk.")

    # Commit today as one permanent, append-only memory.
    day = memory_engine.commit_day(date, _GREENHOUSE)
    if day:
        print(f"\n  ✓ {date} is now a permanent memory — {len(day.recommendations)} "
              f"recommendation(s), linked to their outcomes forever.")


# --- gaia memory "<question>" ------------------------------------------------

def _line(s=""):
    return s


def _render_day(day, label):
    if not day:
        return f"I have no memory of {label.lower()}."
    L = [f"{label} — {day['date']} at {day['greenhouse']}:", f"  {day['brief'].get('summary', '')}"]
    L.append("  Recommendations:")
    for r in day["recommendations"]:
        oc = r.get("outcome") or "still open"
        L.append(f"    • [{r.get('kind')}] {r.get('zone')}: {r.get('recommendation','')[:60]} → {oc}")
    if day.get("walk_observations"):
        L.append("  On the walk I was told:")
        for a in day["walk_observations"]:
            L.append(f"    • {a.get('answer','')}")
    if day.get("lessons"):
        L.append("  Lessons:")
        for le in day["lessons"]:
            L.append(f"    • {le}")
    o = day.get("outcomes", {})
    L.append(f"  Outcomes: {o.get('improved',0)} improved · {o.get('unchanged',0)} unchanged · "
             f"{o.get('worse',0)} worse · {o.get('unknown',0)} unknown · {o.get('open',0)} open")
    return "\n".join(L)


def _render_humidity(hits, thr):
    if not hits:
        return f"In all I remember, humidity never exceeded {thr:.0f}%."
    L = [f"Humidity exceeded {thr:.0f}% on {len(hits)} day(s):"]
    for h in hits:
        L.append(f"\n— {h['date']} (worst {h['worst_humidity']:.0f}%):")
        L.append(_render_day(h["day"], h["date"]))
    return "\n".join(L)


def _render_decisions(decs, title):
    if not decs:
        return f"No {title.lower()} in memory yet."
    L = [f"{title} — {len(decs)} in memory:"]
    for d in decs:
        oc = d.get("outcome") or "still open"
        L.append(f"  • {d['date']} · {d.get('zone')}: {d.get('recommendation','')[:60]} → {oc}")
    return "\n".join(L)


def _render_learnings(cells):
    if not cells:
        return "I haven't learned anything yet — no completed days in memory."
    L = ["Here is what I have learned so far, entirely from memory:\n"]
    for c in sorted(cells, key=lambda x: -x["tried"]):
        conf = c["first_conf"] or "?"
        if c["last_conf"] and c["last_conf"] != c["first_conf"]:
            conf = f"{c['first_conf']} → {c['last_conf']}"
        L.append(f"• {c['zone']} — {c['kind']}: tried {c['tried']}×  "
                 f"({c['improved']} improved, {c['unchanged']} unchanged, {c['worse']} worse, "
                 f"{c['unknown']} unknown, {c['open']} still open); confidence {conf}.")
        if c["lessons"]:
            L.append(f"    └ {c['lessons'][-1]}")
    L.append("\n(Every line above is drawn only from my permanent memory of completed days.)")
    return "\n".join(L)


def _render_index(days):
    L = [f"I remember {len(days)} day(s):"]
    for d in days:
        o = d.get("outcomes", {})
        L.append(f"  • {d['date']}: {len(d['recommendations'])} recommendation(s), "
                 f"{o.get('improved',0)} improved")
    L.append("\nAsk me: 'what happened yesterday', 'what happened last friday',")
    L.append("'the last time humidity exceeded 95', 'disease prevention decisions', 'what did you learn'.")
    return "\n".join(L)


_WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def cmd_memory(argv):
    q = " ".join(argv).lower().strip()
    if "question" in q:
        print(_render_questions()); return
    if not memory_engine.all_days():
        print("No memories yet. Live a day first: gaia morning → walk → evening.")
        return
    if "learn" in q:
        print(_render_learnings(memory_engine.learnings())); return
    if "yesterday" in q:
        print(_render_day(memory_engine.latest(), "Yesterday")); return
    for wd in _WEEKDAYS:
        if wd in q:
            print(_render_day(memory_engine.last_weekday(wd), f"Last {wd.capitalize()}")); return
    if "humidity" in q:
        m = re.search(r"(\d+(?:\.\d+)?)", q)
        thr = float(m.group(1)) if m else 95.0
        print(_render_humidity(memory_engine.humidity_exceeded(thr), thr)); return
    if any(w in q for w in ("disease", "prevention", "prevent")):
        print(_render_decisions(memory_engine.decisions_of_kind("prevent"), "Disease-prevention decisions")); return
    print(_render_index(memory_engine.all_days()))


def _render_questions():
    evals = store.load_question_evals()
    prior = store.prior_worth_by_kind()
    if not evals:
        return "I haven't asked anything yet."
    tally = {}
    for e in evals:
        k = e.get("decision_kind", "?")
        t = tally.setdefault(k, [0, 0])
        t[0] += 1
        t[1] += 1 if e.get("worthwhile") else 0
    L = ["What I've learned about my own questions (from the permanent log):\n"]
    for k, (n, w) in sorted(tally.items(), key=lambda x: -x[1][0]):
        rate = 100 * w / n
        verdict = "valuable" if rate >= 60 else ("usually unnecessary" if rate < 30 else "mixed")
        L.append(f"  • {k}: asked {n}×, worthwhile {w}/{n} ({rate:.0f}%) — {verdict}; "
                 f"value-multiplier now {prior.get(k, 1.0)}")
    L.append("\n(Multipliers below 1.0 push that kind of question below the bar — I ask it less.)")
    return "\n".join(L)


# --- gaia day  (Adaptive Workflow: orchestrate the whole day) ----------------

def _negated(text):
    """True if the answer is a denial — matched on whole words (so 'canopy' isn't read as 'no')."""
    toks = text.lower().replace(",", " ").replace(".", " ").split()
    return any(t in toks for t in ("no", "not", "none", "dry", "clear", "nope", "n't", "fine"))


def _log_q(q, ans, worthwhile=True):
    store.append_answer({"question": q.text, "answer": ans, "kind": q.kind,
                         "subject": q.subject, "captured_on": "day"})
    store.append_question_eval({"question_id": q.id, "decision_kind": q.decision_kind,
                                "voi": q.voi, "answer": ans, "changed_decision": _negated(ans),
                                "confidence_increase": bool(ans), "worthwhile": worthwhile,
                                "captured_on": "day"})


def _step(n, title):
    print(f"\n━━━━━ STEP {n} · {title} ━━━━━")


def cmd_day(argv):
    morning_path = argv[0] if argv else _SAMPLE_SNAPSHOT
    midday_path = argv[1] if len(argv) > 1 else None
    tomorrow_path = argv[2] if len(argv) > 2 else None
    print(f"\n████ Gaia — one complete working day at {_GREENHOUSE} ████")

    # 1 — MORNING SNAPSHOT
    _step(1, "Morning Snapshot")
    with open(morning_path, "r", encoding="utf-8") as f:
        snap = import_snapshot(json.load(f))
    date = (snap.assembled_at or "today")[:10]
    provider = SnapshotProvider(snap)
    cov = snap.coverage()
    miss = snap.missing()
    print(f"  KNOWS:     {len(snap.present())} observations from {len(snap.provenance)} source(s); coverage {cov['coverage_pct']}%.")
    gap = (f"{miss[0].subject}/{miss[0].kind}" if miss else (snap.not_observed[0] if snap.not_observed else "none"))
    print(f"  UNCERTAIN: {cov['gaps']} gap(s), e.g. {gap} — recorded as absent, never invented.")

    # 2 — MORNING ANALYSIS
    _step(2, "Morning Analysis")
    analysis = MorningAnalysisEngine().run(provider)
    store.save(analysis)
    exps = [experiment_from_candidate(c, date) for c in list(analysis.priorities) + list(analysis.opportunities)]
    store.save_open_experiments(exps)
    print(f"  KNOWS:     {analysis.summary}")
    for c in analysis.priorities:
        print(f"             • [{c.kind} · {c.confidence}] {c.zone_name}: {c.action[:48]}…")
    print(f"  UNCERTAIN: plant state is inferred from climate, not seen (overall {analysis.confidence_level}).")

    # 3 — KNOWLEDGE GAP ENGINE
    _step(3, "Knowledge Gap Engine")
    prior = store.prior_worth_by_kind()
    questions, held = knowledge_gap.generate(analysis, [], snap.assembled_at, date, prior)
    store.save_questions(questions)
    store.save_today_snapshot({"date": date, "greenhouse": analysis.greenhouse_name,
                               "assembled_at": snap.assembled_at,
                               "signals": changes.signals(provider.get_latest_climate(), analysis),
                               "coverage": cov, "reality": snap.reality_confidence()})
    print(f"  ASKS:      {len(questions)} worth the interruption; held back {len(held)} low-value.")
    for q in questions:
        print(f"             → {q.text}")
        print(f"               (reduces: {q.uncertainty}; VoI {q.voi:+.2f}; {q.suggested_timing})")

    resolved, rec_change = set(), None

    # 4 — FIELD CONVERSATION (the decision-changing question, at the morning chat)
    _step(4, "Field Conversation (08:00)")
    dq = next((q for q in questions if q.decision_kind == "prevent"), None)
    if dq:
        print(f"  GAIA ASKS:   {dq.text}")
        ans = _ask("  GROWER:      ").strip() or "(no answer)"
        resolved.add(dq.id); _log_q(dq, ans)
        agrees = not _negated(ans)
        e = next((x for x in store.load_open_experiments() if x.kind == "prevent" and x.zone == dq.subject), None)
        if e:
            old, new = reinforce(e, agrees, ans)
            store.save_open_experiments([e if x.id == e.id else x for x in store.load_open_experiments()])
            rec_change = (e.zone, old, new, agrees)
            print(f"  GAIA:        {'confirmed' if agrees else 'contradicted'} — the disease recommendation moves from {old} to {new} confidence.")

    # 5 — WALK OBSERVATIONS (opportunistic, where the grower already is)
    _step(5, "Walk observations (11:30 — you're in House 2)")
    here = workflow.surface(questions, "House 2", resolved)
    for q in here:
        print(f"  GAIA ASKS:   while you're here — {q.text}")
        ans = _ask("  GROWER:      ").strip() or "(no answer)"
        resolved.add(q.id); _log_q(q, ans)
        print(f"  STORED:      '{ans}' — kept as evidence (provenance: grower, this morning).")

    # 6 — UPDATED RECOMMENDATIONS
    _step(6, "Updated recommendations")
    if rec_change:
        z, old, new, agrees = rec_change
        print(f"  CHANGE:    {z} disease prevention — confidence {old} → {new} "
              f"({'reinforced by the wet canopy you confirmed' if agrees else 'relaxed — canopy was dry'}).")
    if midday_path:
        with open(midday_path, "r", encoding="utf-8") as f:
            m_analysis = MorningAnalysisEngine().run(SnapshotProvider(import_snapshot(json.load(f))))
        gone = {(c.zone_name, c.kind) for c in analysis.concerns} - {(c.zone_name, c.kind) for c in m_analysis.concerns}
        for zn, kind in sorted(gone):
            print(f"  RESOLVED:  the {kind} concern in {zn} cleared by midday — conditions improved as predicted; no re-ask.")

    # 7 — EVENING REVIEW
    _step(7, "Evening Review (17:00)")
    due = [e for e in store.load_open_experiments() if e.opened_on == date and e.window in _DUE_TONIGHT]
    closed = []
    for e in due:
        apply_outcome(e, "done", "improved", "held up / resolved over the day", date)
        store.append_memory(e); closed.append(e)
    store.save_open_experiments([e for e in store.load_open_experiments() if e.id not in {c.id for c in closed}])
    print(views.render_evening(closed, _GREENHOUSE, date))

    # 8 — MEMORY UPDATE
    _step(8, "Memory update (18:00)")
    day = memory_engine.commit_day(date, _GREENHOUSE)
    if day:
        print(f"  STORED:    {date} is now a permanent, append-only memory — "
              f"{len(day.recommendations)} recommendation(s) linked to their outcomes forever.")

    # 9 — LEARNING
    _step(9, "Learning")
    for c in memory_engine.learnings():
        conf = c["first_conf"] if c["first_conf"] == c["last_conf"] or not c["last_conf"] else f"{c['first_conf']}→{c['last_conf']}"
        print(f"  LEARNED:   {c['zone']} · {c['kind']}: {c['tried']} done, {c['improved']} improved; confidence {conf}.")

    # 10 — TOMORROW'S MORNING ANALYSIS
    _step(10, "Tomorrow's Morning Analysis")
    if tomorrow_path:
        with open(tomorrow_path, "r", encoding="utf-8") as f:
            tsnap = import_snapshot(json.load(f))
        t_analysis = MorningAnalysisEngine().run(SnapshotProvider(tsnap))
        recalls = views.recall_notes(t_analysis, store.load_memories())
        print(f"  Tomorrow ({(tsnap.assembled_at or '')[:10]}) — the same situation, now informed by today:")
        for c in t_analysis.priorities:
            key = c.zone_name + "|" + c.kind
            r = f"  ↻ {recalls[key]}" if key in recalls else ""
            print(f"             • [{c.kind}] {c.zone_name}{r}")
        print("  → Gaia advises the same crop with earned, calibrated confidence — a better grower than yesterday.")
    else:
        print("  (pass a tomorrow snapshot to preview how today's learning changes tomorrow's brief.)")


_COMMANDS = {"morning": cmd_morning, "walk": cmd_walk, "evening": cmd_evening,
             "memory": cmd_memory, "day": cmd_day}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in _COMMANDS:
        print(__doc__)
        return 1
    _COMMANDS[sys.argv[1]](sys.argv[2:])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

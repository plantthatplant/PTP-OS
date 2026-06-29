"""GoogleDriveObserver — the Business Knowledge Observer.

It reads the greenhouse's planning spreadsheets (crop/production plans, bench allocation,
profitability) and reports them as **Canonical Observations of intention** — what was *supposed*
to happen — distinct from what Synopta and the grower observe is *actually* happening.

Hard rules (Observer Network):
  * It performs NO biological reasoning. It parses and reports; nothing more.
  * The spreadsheets are NOT the truth — they are intention. Reality always has priority.
  * Every observation preserves provenance (which file), timestamp (the plan's last-modified),
    method (`imported`), and confidence (a plan is medium-confidence by nature, lower if stale).
  * Missing/unreadable tables become honest absence, never invented values.

Today it reads spreadsheet files from disk (kept in sync by Google Drive's desktop client or a
download). The live Drive API is a transport detail behind this same observer — the observations
it produces do not change.
"""
from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .. import xlsx_read

# Vendor-neutral zone ids for Kålaberga's houses (the names as they appear in the plan).
_ZONE_MAP = {
    "hus 1": "h1", "hus 2": "h2", "hus 3": "h3",
    "mellanbygge": "mellanbygge", "plasthusen": "plast",
    "venlo golv": "venlo-golv", "venlo": "venlo",
}


def _zone_id(name: str) -> str:
    key = str(name or "").strip().lower()
    return _ZONE_MAP.get(key, key.replace(" ", "-") or "site")


def _zone_from_bordid(bord: str) -> str:
    m = str(bord or "").strip().upper()
    if m.startswith("H1"):
        return "h1"
    if m.startswith("H2"):
        return "h2"
    if m.startswith("H3"):
        return "h3"
    return "site"


def _obs(subject, kind, value, captured_at, source, *, unit=None, confidence="medium",
         notes=None, absence=None) -> dict:
    o = {"subject": subject, "kind": kind, "value": value, "captured_at": captured_at,
         "source": source, "method": "imported", "confidence": confidence}
    if unit:
        o["unit"] = unit
    if notes:
        o["notes"] = notes
    if absence:
        o["value"] = None
        o["absence"] = absence
    return o


def _find_header_row(rows, label, col=None) -> Optional[int]:
    """Index of the first row containing `label` (in column `col` if given, else any column)."""
    for i, r in enumerate(rows):
        if col is not None:
            if str(r.get(col, "")).strip().lower() == label.lower():
                return i
        elif any(str(v).strip().lower() == label.lower() for k, v in r.items() if k != "_r"):
            return i
    return None


# --- table parsers (pure; each returns a list of Canonical Observation dicts) ----

def parse_occupancy(rows, source, captured_at) -> List[dict]:
    """The 'BELÄGGNING PER VÄXTHUS' table → per-zone bench allocation (intention)."""
    h = _find_header_row(rows, "Växthus", col="B")
    if h is None:
        return []
    out: List[dict] = []
    for r in rows[h + 1:]:
        name = r.get("B")
        if not name or str(name).strip().upper() == "TOTAL":
            break
        zid = _zone_id(name)
        cap, active, delayed = r.get("C"), r.get("D"), r.get("F")
        occ = r.get("H")
        if isinstance(occ, (int, float)):
            pct = round(occ * 100, 1) if occ <= 1 else round(float(occ), 1)
            out.append(_obs(zid, "expected-occupancy", pct, captured_at, source, unit="%",
                            notes=f"plan: {name}"))
        if isinstance(active, (int, float)):
            out.append(_obs(zid, "planned-benches-active", active, captured_at, source,
                            notes=f"of {cap} benches" if cap else None))
        if isinstance(delayed, (int, float)) and delayed > 0:
            out.append(_obs(zid, "benches-delayed", delayed, captured_at, source,
                            confidence="medium", notes="plan flags delayed benches"))
    return out


def parse_deliveries(rows, source, captured_at, limit=12) -> List[dict]:
    """The 'KOMMANDE LEVERANSER' table → expected harvest/shipment per bench."""
    h = _find_header_row(rows, "Kultur", col="D")
    if h is None:
        return []
    out: List[dict] = []
    for r in rows[h + 1:]:
        crop = r.get("D")
        if not crop:
            continue
        bord, count = r.get("C"), r.get("I")
        due = xlsx_read.excel_date(r.get("K"))
        status = r.get("N")
        zid = _zone_from_bordid(bord)
        value = f"{int(count)} × {crop}" if isinstance(count, (int, float)) else str(crop)
        notes = "  ".join(x for x in [f"bench {bord}" if bord else "",
                                      f"due {due}" if due else "",
                                      f"status {status}" if status else ""] if x)
        out.append(_obs(zid, "expected-harvest", value, captured_at, source, notes=notes))
        if due:
            out.append(_obs(zid, "expected-harvest-date", due, captured_at, source,
                            notes=f"bench {bord}, {crop}" if bord else str(crop)))
        if len(out) >= limit * 2:
            break
    return out


def parse_financials(rows, source, captured_at) -> List[dict]:
    """'INDATA – BOKSLUT' → site-level expected revenue and labour (assumptions)."""
    out: List[dict] = []

    def find_value(label_substring):
        for r in rows:
            a = str(r.get("A", ""))
            if label_substring.lower() in a.lower():
                return r.get("B")
        return None

    revenue = find_value("SUMMA OMSÄTTNING")
    if isinstance(revenue, (int, float)):
        out.append(_obs("site", "expected-revenue", round(float(revenue)), captured_at, source,
                        unit="kr", notes="annual, from the profitability plan"))
    fte = find_value("Antal anställda")
    if isinstance(fte, (int, float)):
        out.append(_obs("site", "expected-labour", fte, captured_at, source, unit="FTE"))
    area = find_value("Odlingsyta")
    if isinstance(area, (int, float)):
        out.append(_obs("site", "planned-growing-area", area, captured_at, source, unit="m²"))
    return out


def parse_profitability(rows, source, captured_at, limit=20) -> List[dict]:
    """'PORTFOLJMATRIS' classification table → per-crop expected profitability (intention)."""
    h = None
    for i, r in enumerate(rows):
        if str(r.get("A", "")).strip().lower() == "kultur" and \
                any("klassificering" in str(v).lower() for v in r.values()):
            h = i
            break
    if h is None:
        return []
    out: List[dict] = []
    for r in rows[h + 1:]:
        crop = r.get("A")
        if not crop:
            break
        margin, volume, contrib = r.get("C"), r.get("D"), r.get("E")
        klass, action = r.get("F"), r.get("G")
        if not klass:
            continue
        notes = "  ".join(x for x in [
            f"margin {round(margin * 100)}%" if isinstance(margin, (int, float)) else "",
            f"volume {int(volume)}" if isinstance(volume, (int, float)) else "",
            f"contribution {round(contrib)} tkr" if isinstance(contrib, (int, float)) else "",
            f"action: {action}" if action else ""] if x)
        out.append(_obs(f"crop:{str(crop).strip()}", "expected-profitability", klass,
                        captured_at, source, notes=notes))
        if len(out) >= limit:
            break
    return out


def _captured_at(path: str) -> str:
    try:
        ts = os.path.getmtime(path)
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(timespec="seconds")
    except OSError:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --- bench-overview sheets ("Översikt bord …") --------------------------------------------------
# Single-sheet (Blad1) SPATIAL layouts: row 1 names the house; the cells map benches to their
# planned contents. They carry intention — *which crops are planned in each house* — but no
# structured table, so the dashboard/portfolio parsers above find nothing. We extract distinct
# planned crops conservatively: skip the house header, bench descriptors ("15 rännebord",
# "13 ebb och flod", "9 plåtbord"), bare numbers, and size fragments ("6-pack"). Honest absence
# holds: a cell we can't recognise is simply not turned into an observation (never invented).

_BENCH_WORDS = ("rännebord", "ränne", "ebb och flod", "plåtbord", "plåt", "plasthus", "bord")
_SIZE_RE = re.compile(r"^\d+\s*-?\s*pack$", re.IGNORECASE)
_NUM_RE = re.compile(r"^\d+([.,]\d+)?$")


def _overview_house(header: str, filename: str) -> str:
    """Map an overview sheet to a vendor-neutral zone id from its row-1 header, then its filename."""
    for text in (header or "", filename or ""):
        low = text.strip().lower()
        for key in sorted(_ZONE_MAP, key=len, reverse=True):   # longest first: 'venlo golv' before 'venlo'
            if key in low:
                return _ZONE_MAP[key]
        if "golv" in low and "venlo" in low:
            return "venlo-golv"
        if "plasthus" in low:
            return "plast"
        if "venlo" in low:
            return "venlo"
        if "mellanbygge" in low:
            return "mellanbygge"
    return "site"


def _is_bench_descriptor(text: str) -> bool:
    t = text.strip().lower()
    if _NUM_RE.match(t):                                       # a bare number is layout, not a crop
        return True
    if t[:1].isdigit() and any(w in t for w in _BENCH_WORDS):  # "15 rännebord", "13 ebb och flod"
        return True
    return bool(_SIZE_RE.match(t))                             # "6-pack" size fragment


def parse_bench_overview(rows, source, captured_at, filename=None) -> List[dict]:
    """Distinct planned crops per house from a bench-overview ('Översikt bord …') sheet.

    Each distinct crop name becomes a Canonical Observation: subject=<house>, kind=planned-crop,
    value=<crop>, method=imported (intention, medium confidence). Returns [] for an empty sheet."""
    if not rows:
        return []
    header = ""
    for k, v in rows[0].items():
        if k != "_r" and str(v).strip():
            header = str(v).strip()
            break
    house = _overview_house(header, filename or "")
    seen, out = set(), []
    for r in rows:
        for k, v in r.items():
            if k == "_r":
                continue
            cell = str(v).strip()
            if not cell or cell.lower() == header.lower() or _is_bench_descriptor(cell):
                continue
            key = cell.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(_obs(house, "planned-crop", cell, captured_at, source))
    return out


def _pick_sheet(path, *substrings):
    for name in xlsx_read.sheet_names(path):
        low = name.lower()
        if any(s in low for s in substrings):
            return name
    return None


def observe_files(paths: List[str]) -> List[dict]:
    """Read each spreadsheet and return all Canonical Observations of intention it yields.
    Unknown/unreadable files are skipped (logged by the caller), never invented."""
    observations: List[dict] = []
    for path in paths:
        if not os.path.exists(path):
            continue
        source = f"google-drive:{os.path.basename(path)}"
        captured = _captured_at(path)
        try:
            names = xlsx_read.sheet_names(path)
        except Exception:
            continue
        dash = _pick_sheet(path, "dashboard")
        if dash:
            rows = xlsx_read.read_sheet(path, dash)
            observations += parse_occupancy(rows, source, captured)
            observations += parse_deliveries(rows, source, captured)
        indata = _pick_sheet(path, "indata", "bokslut")
        if indata:
            observations += parse_financials(xlsx_read.read_sheet(path, indata), source, captured)
        portfolio = _pick_sheet(path, "portfolj", "portfolio")
        if portfolio:
            observations += parse_profitability(xlsx_read.read_sheet(path, portfolio), source, captured)
        # Bench-overview workbooks ("Översikt bord …") carry no structured table — extract the
        # planned crops per house from their spatial layout instead of yielding nothing.
        if "versikt" in os.path.basename(path).lower() and not (dash or indata or portfolio):
            if names:
                observations += parse_bench_overview(
                    xlsx_read.read_sheet(path, names[0]), source, captured, os.path.basename(path))
    return observations


class GoogleDriveObserver:
    """The Business Knowledge Observer. Configure it with the spreadsheet paths (a folder kept in
    sync by Google Drive, or explicit files). `observe()` returns Canonical Observations."""

    name = "google-drive"

    def __init__(self, paths: List[str]):
        self.paths = list(paths)

    def observe(self) -> List[dict]:
        return observe_files(self.paths)

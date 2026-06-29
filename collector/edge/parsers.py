"""Parse a real Synopta export FILE into the raw, vendor-shaped reading dict the existing
translator already understands.

This is the *format* seam. Whatever shape Ridder's scheduled export takes — semicolon CSV with
European comma decimals, tab-separated, an Excel workbook, or (later) JSON — every parser emits
the **same** intermediate dict:

    {
      "captured_at": "2026-06-29T05:48:00+00:00",   # the reading's own time (best available)
      "site": "Kalaberga",
      "_source_file": "export_20260629_0548.csv",
      "houses": [
        {"house_id": "1", "label": "Hus 1", "signals": {
            "air_temp":      {"value": "24,2"},        # left messy on purpose — translate cleans it
            "rel_humidity":  {"value": "92"},
            "vent_position": {"value": "0"},
            "outside_temp":  {"value": "11.0"},
            "alarm":         {"active": false, "text": null}
        }},
        ...
      ]
    }

That dict is exactly what `collector/translate.py:to_snapshot` consumes today, so nothing above
this module changes when the real export format is confirmed — only the column alias map (below)
or, at most, this file.

**This is translation, not interpretation.** It maps columns to signal keys and structures rows
into houses. It does NOT clean numbers (translate's tested `to_number` does that downstream), does
NOT decide confidence, and NEVER invents a value: an empty cell becomes an absent signal, which
becomes honest absence in the snapshot — never a fabricated 0.
"""
from __future__ import annotations

import csv
import io
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from .. import xlsx_read


class ParseError(Exception):
    """The file could not be turned into a reading at all (corrupt, empty, wrong shape, or no
    recognisable house column). A *content* problem, distinct from a transient IO error — the
    watcher moves such a file to FAILED rather than retrying it forever."""


# ──────────────────────────────────────────────────────────────────────────────
# Column → signal alias map.
#
# Case/space/underscore-insensitive. Multilingual (Synopta/Ridder ship Swedish, Dutch and
# English headers depending on site language). This is the single place to add a real column
# name when Ridder's export is confirmed — add the header on the left, keep the canonical key
# on the right. Order of columns in the file does not matter; unknown columns are ignored.
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_COLUMN_ALIASES: Dict[str, str] = {
    # house / compartment identity
    "house": "house_id", "houseid": "house_id", "house_id": "house_id", "houseno": "house_id",
    "hus": "house_id", "kas": "house_id", "afdeling": "house_id", "compartment": "house_id",
    "kompartiment": "house_id", "section": "house_id", "zone": "house_id", "id": "house_id",
    # human label (optional)
    "label": "label", "name": "label", "housename": "label", "husnamn": "label",
    "naam": "label", "description": "label",
    # timestamp (row level)
    "timestamp": "captured_at", "time": "captured_at", "datetime": "captured_at",
    "date": "captured_at", "tijd": "captured_at", "tid": "captured_at",
    "datum": "captured_at", "loggedat": "captured_at", "capturedat": "captured_at",
    "logtime": "captured_at", "tidpunkt": "captured_at", "tidstampel": "captured_at",
    "datumtid": "captured_at", "tijdstip": "captured_at", "registreringstid": "captured_at",
    # air temperature
    "airtemp": "air_temp", "airtemperature": "air_temp", "temperature": "air_temp",
    "temp": "air_temp", "luchttemperatuur": "air_temp", "kastemperatuur": "air_temp",
    "lufttemperatur": "air_temp", "tempair": "air_temp", "greenhousetemp": "air_temp",
    "kastemp": "air_temp",
    # relative humidity
    "relhumidity": "rel_humidity", "relativehumidity": "rel_humidity", "humidity": "rel_humidity",
    "rh": "rel_humidity", "rv": "rel_humidity", "luchtvochtigheid": "rel_humidity",
    "luftfuktighet": "rel_humidity", "vochtigheid": "rel_humidity",
    # vent / window position
    "vent": "vent_position", "ventposition": "vent_position", "ventilation": "vent_position",
    "raam": "vent_position", "raamstand": "vent_position", "window": "vent_position",
    "windowposition": "vent_position", "lucht": "vent_position", "luchtstand": "vent_position",
    "ventilationposition": "vent_position", "fonster": "vent_position",
    # outside / outdoor temperature
    "outsidetemp": "outside_temp", "outdoortemp": "outside_temp", "outsidetemperature": "outside_temp",
    "buitentemperatuur": "outside_temp", "utetemperatur": "outside_temp",
    "externaltemp": "outside_temp", "weathertemp": "outside_temp", "outtemp": "outside_temp",
    # alarm active flag  (en / sv 'larm','störning' / nl 'storing')
    "alarm": "alarm_active", "alarmactive": "alarm_active", "fault": "alarm_active",
    "storing": "alarm_active", "storning": "alarm_active", "alarmstatus": "alarm_active",
    "larm": "alarm_active", "larmaktiv": "alarm_active", "alarmaktiv": "alarm_active",
    # alarm text
    "alarmtext": "alarm_text", "alarmmessage": "alarm_text", "message": "alarm_text",
    "storingstekst": "alarm_text", "storningstext": "alarm_text", "faulttext": "alarm_text",
    "larmtext": "alarm_text", "larmmeddelande": "alarm_text",
}

_QUANT_SIGNALS = ("air_temp", "rel_humidity", "vent_position", "outside_temp")

_TRUE_TOKENS = {"1", "true", "yes", "y", "on", "active", "alarm", "ja", "aktiv", "actief"}
_FALSE_TOKENS = {"0", "false", "no", "n", "off", "ok", "normal", "nej", "-", "", "none", "geen"}


import re as _re

# Unit tokens that may trail a header with no parentheses ("Air Temp C"); stripped only as a
# fallback when the full token isn't recognised, so a real alias is never mangled.
_UNIT_SUFFIXES = ("celsius", "degc", "deg", "percent", "pct", "ppm", "c")
_PAREN_GROUP = _re.compile(r"[\(\[\{].*?[\)\]\}]")


def _norm_header(h: str) -> str:
    """'Air Temp (°C)' / 'RH (%)' / 'air_temp' / 'AIR-TEMP' all collapse to the same lookup key.
    A unit in parentheses/brackets is dropped first so it cannot bleed into the token."""
    base = _PAREN_GROUP.sub(" ", (h or "").lower())
    return "".join(ch for ch in base if ch.isalnum())


def _lookup_alias(norm: str, alias: Dict[str, str]) -> Optional[str]:
    """Resolve a normalised header to a canonical key, with a fallback that strips a trailing
    unit token ('airtempc' → 'airtemp') only if the bare form is itself a known alias."""
    if norm in alias:
        return alias[norm]
    for suffix in _UNIT_SUFFIXES:
        if norm.endswith(suffix) and len(norm) - len(suffix) >= 3:
            base = norm[: -len(suffix)]
            if base in alias:
                return alias[base]
    return None


def _resolve_aliases(headers: List[str], overrides: Optional[Dict[str, str]]) -> Dict[int, str]:
    """Map each column index to a canonical key (house_id / captured_at / air_temp / …).
    Columns we do not recognise are simply left out — unexpected columns never break a parse."""
    alias = dict(DEFAULT_COLUMN_ALIASES)
    if overrides:
        for k, v in overrides.items():
            alias[_norm_header(k)] = v
    resolved: Dict[int, str] = {}
    for i, h in enumerate(headers):
        key = _lookup_alias(_norm_header(h), alias)
        if key and i not in resolved:
            resolved[i] = key
    return resolved


def parse_timestamp(value, default_tz: str = "UTC") -> Optional[str]:
    """Parse a wide range of export timestamps into a timezone-aware ISO-8601 string.

    Robust across daylight-saving transitions: anything that already carries an offset/zone is
    converted to UTC; a naive local time is interpreted in `default_tz` (falling back to UTC if
    that zone is unavailable). Returns None for a genuinely unparseable / empty value — never a
    guessed 'now'."""
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        s = str(value).strip()
        if not s:
            return None
        dt = _parse_dt_string(s)
        if dt is None:
            return None
    if dt.tzinfo is None:
        tz = _zone(default_tz)
        try:
            dt = dt.replace(tzinfo=tz)
        except Exception:
            dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def _zone(name: str):
    if not name or name.upper() == "UTC":
        return timezone.utc
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(name)
    except Exception:
        return timezone.utc


_DT_FORMATS = (
    "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M",
    "%Y-%m-%d", "%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M", "%d-%m-%Y",
    "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y",
    "%m/%d/%Y %H:%M:%S", "%Y/%m/%d %H:%M:%S",
)


def _parse_dt_string(s: str) -> Optional[datetime]:
    raw = s.replace("Z", "+00:00") if s.endswith("Z") else s
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        pass
    for fmt in _DT_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def _parse_alarm_active(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    token = str(value).strip().lower()
    if token in _TRUE_TOKENS:
        return True
    if token in _FALSE_TOKENS:
        return False
    # Unknown non-empty text in an alarm column: treat as an active alarm carrying that text,
    # rather than silently dropping a possible fault. (The text itself is preserved separately.)
    return bool(token)


# ──────────────────────────────────────────────────────────────────────────────
# Record → raw dict assembly (shared by every format)
# ──────────────────────────────────────────────────────────────────────────────
def _records_to_raw(records: List[Dict[str, object]], *, site: Optional[str],
                    source_file: Optional[str], default_tz: str,
                    fallback_ts: Optional[str] = None) -> dict:
    """Group flat per-row records (already keyed by canonical signal name) into houses.

    Multiple rows for one house (a time series) collapse to the most recent row. The file's
    `captured_at` is the latest row timestamp seen, or — when the export carries no timestamp
    column at all — the file's own production time (`fallback_ts`). That fallback is honest
    provenance (when the export was made), not a fabricated reading value. A record with no
    house id is skipped (we cannot place an anonymous reading without guessing where it belongs)."""
    by_house: Dict[str, Dict[str, object]] = {}
    house_ts: Dict[str, Optional[str]] = {}
    latest_overall: Optional[str] = None

    for rec in records:
        hid = rec.get("house_id")
        if hid is None or str(hid).strip() == "":
            continue
        hid = str(hid).strip()
        row_ts = parse_timestamp(rec.get("captured_at"), default_tz) if rec.get("captured_at") else None
        # Keep the most recent row per house. Rows without timestamps keep last-seen order.
        if hid in by_house and row_ts and house_ts.get(hid) and row_ts < house_ts[hid]:
            continue
        signals: Dict[str, object] = {}
        for key in _QUANT_SIGNALS:
            if key in rec and rec[key] not in (None, ""):
                signals[key] = {"value": rec[key]}
        if "alarm_active" in rec or "alarm_text" in rec:
            active = _parse_alarm_active(rec.get("alarm_active")) if "alarm_active" in rec else False
            text = rec.get("alarm_text")
            text = str(text) if text not in (None, "") else None
            if text and "alarm_active" not in rec:
                active = True
            signals["alarm"] = {"active": active, "text": text}
        house = {"house_id": hid, "signals": signals}
        if rec.get("label") not in (None, ""):
            house["label"] = str(rec["label"])
        by_house[hid] = house
        house_ts[hid] = row_ts or house_ts.get(hid)
        if row_ts and (latest_overall is None or row_ts > latest_overall):
            latest_overall = row_ts

    if not by_house:
        raise ParseError("no rows with a recognisable house/compartment id were found")

    raw: dict = {"houses": list(by_house.values())}
    captured = latest_overall or fallback_ts
    if captured:
        raw["captured_at"] = captured
    if site:
        raw["site"] = site
    if source_file:
        raw["_source_file"] = source_file
    return raw


# ──────────────────────────────────────────────────────────────────────────────
# Encoding-tolerant text loading
# ──────────────────────────────────────────────────────────────────────────────
def _read_text(path: str) -> str:
    """Read a delimited text export tolerant of the encodings live exports actually arrive in:
    UTF-8 with or without BOM first, then Windows-1252 / Latin-1 (common from European Windows
    tools). Never raises on encoding — the last fallback decodes every byte."""
    with open(path, "rb") as f:
        data = f.read()
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1", errors="replace")


def _sniff_delimiter(sample: str, prefer_tab: bool) -> str:
    if prefer_tab:
        return "\t"
    try:
        return csv.Sniffer().sniff(sample, delimiters=";,\t|").delimiter
    except csv.Error:
        # European exports favour ';' (so comma decimals stay intact); fall back sensibly.
        if ";" in sample:
            return ";"
        if "\t" in sample:
            return "\t"
        return ","


def _mtime_iso(path: str) -> Optional[str]:
    """The file's last-modified time as a UTC ISO string — the export's production time, used as
    the captured_at of last resort when the export carries no timestamp of its own."""
    try:
        return datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc).isoformat()
    except OSError:
        return None


def _parse_delimited(path: str, *, prefer_tab: bool, overrides, default_tz: str) -> dict:
    text = _read_text(path)
    if not text.strip():
        raise ParseError(f"file is empty: {os.path.basename(path)}")
    sample = text[:4096]
    delim = _sniff_delimiter(sample, prefer_tab)
    reader = csv.reader(io.StringIO(text), delimiter=delim)
    rows = [r for r in reader if any((c or "").strip() for c in r)]  # drop blank lines
    if len(rows) < 2:
        raise ParseError("file has no data rows under its header")
    headers = [h.strip() for h in rows[0]]
    resolved = _resolve_aliases(headers, overrides)
    if "house_id" not in resolved.values():
        raise ParseError(
            "no house/compartment column recognised in header: " + ", ".join(headers[:12]))
    records: List[Dict[str, object]] = []
    for raw_row in rows[1:]:
        rec: Dict[str, object] = {}
        for idx, key in resolved.items():
            if idx < len(raw_row):
                val = raw_row[idx].strip()
                if val != "":
                    rec[key] = val
        if rec:
            records.append(rec)
    return _records_to_raw(records, site=None, source_file=os.path.basename(path),
                           default_tz=default_tz, fallback_ts=_mtime_iso(path))


def _parse_xlsx(path: str, *, overrides, default_tz: str) -> dict:
    """Read the first worksheet as a table. Reuses the project's dependency-free xlsx reader."""
    try:
        names = xlsx_read.sheet_names(path)
    except Exception as e:  # zipfile / xml errors on a corrupt workbook
        raise ParseError(f"not a readable .xlsx workbook: {e}") from e
    if not names:
        raise ParseError("workbook has no sheets")
    rows = xlsx_read.read_sheet(path, names[0])
    if len(rows) < 2:
        raise ParseError("worksheet has no data rows under its header")
    # rows are dicts keyed by column letter ('A','B',...) with a '_r' row number. Build an
    # ordered header list from the first row, then map subsequent rows positionally.
    header_row = rows[0]
    letters = sorted((k for k in header_row if k != "_r"), key=_col_index)
    headers = [str(header_row[l]).strip() for l in letters]
    resolved = _resolve_aliases(headers, overrides)
    if "house_id" not in resolved.values():
        raise ParseError("no house/compartment column recognised in worksheet header")
    letter_to_key = {letters[i]: key for i, key in resolved.items() if i < len(letters)}
    records: List[Dict[str, object]] = []
    for row in rows[1:]:
        rec: Dict[str, object] = {}
        for letter, key in letter_to_key.items():
            if letter in row and row[letter] not in (None, ""):
                rec[key] = row[letter]
        if rec:
            records.append(rec)
    return _records_to_raw(records, site=None, source_file=os.path.basename(path),
                           default_tz=default_tz, fallback_ts=_mtime_iso(path))


def _col_index(letter: str) -> int:
    n = 0
    for ch in letter:
        n = n * 26 + (ord(ch) - ord("A") + 1)
    return n


def _parse_json(path: str, *, overrides, default_tz: str) -> dict:
    """JSON arrives in one of two shapes:
      1. the established vendor shape ({captured_at, site, houses:[{signals}]}) — passed through
         unchanged, so the existing fixture format keeps working;
      2. a flat array of row records (or {rows:[...]}/{data:[...]}) — mapped via the alias map,
         exactly like a CSV would be.
    """
    try:
        data = json.loads(_read_text(path))
    except json.JSONDecodeError as e:
        raise ParseError(f"file is not valid JSON: {e}") from e

    if isinstance(data, dict) and isinstance(data.get("houses"), list):
        data.setdefault("_source_file", os.path.basename(path))  # provenance, never invents data
        return data

    rows = None
    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict):
        for key in ("rows", "data", "records", "readings"):
            if isinstance(data.get(key), list):
                rows = data[key]
                break
    if rows is None:
        raise ParseError("JSON is neither the vendor 'houses' shape nor an array of row records")

    records: List[Dict[str, object]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        resolved = _resolve_aliases(list(row.keys()), overrides)
        idx_keys = list(row.keys())
        rec: Dict[str, object] = {}
        for idx, key in resolved.items():
            val = row[idx_keys[idx]]
            if val not in (None, ""):
                rec[key] = val
        if rec:
            records.append(rec)
    site = data.get("site") if isinstance(data, dict) else None
    return _records_to_raw(records, site=site, source_file=os.path.basename(path),
                           default_tz=default_tz, fallback_ts=_mtime_iso(path))


# ──────────────────────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────────────────────
_PARSERS = {
    ".csv": lambda p, o, tz: _parse_delimited(p, prefer_tab=False, overrides=o, default_tz=tz),
    ".tsv": lambda p, o, tz: _parse_delimited(p, prefer_tab=True, overrides=o, default_tz=tz),
    ".txt": lambda p, o, tz: _parse_delimited(p, prefer_tab=False, overrides=o, default_tz=tz),
    ".xlsx": lambda p, o, tz: _parse_xlsx(p, overrides=o, default_tz=tz),
    ".json": lambda p, o, tz: _parse_json(p, overrides=o, default_tz=tz),
}


def supported_extensions() -> Tuple[str, ...]:
    return tuple(_PARSERS.keys())


def parse_export(path: str, column_map: Optional[Dict[str, str]] = None,
                 default_tz: str = "UTC") -> dict:
    """Parse one export file into the raw vendor dict. Raises ParseError on any content problem.

    The format is chosen by extension; the same alias map and timestamp handling apply across
    all of them, so the canonical output is identical no matter which format Ridder ships."""
    ext = os.path.splitext(path)[1].lower()
    parser = _PARSERS.get(ext)
    if parser is None:
        raise ParseError(f"unsupported export format '{ext}' for {os.path.basename(path)}")
    return parser(path, column_map, default_tz)

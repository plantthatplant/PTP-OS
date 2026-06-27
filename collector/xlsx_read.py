"""A tiny, dependency-free .xlsx reader (standard library only).

An .xlsx is a zip of XML. The Collector and the Business Knowledge Observer need to read planning
spreadsheets without adding a third-party dependency (the project stays install-free), so this
extracts just what we need: sheet names and cell values (resolving shared strings). It does not
evaluate formulas — it reads the last cached value Excel/Sheets stored, which is what we want.

Numbers come back as float/int, text as str, empty cells are absent. Excel date *serials* are
left as numbers; call excel_date() to convert the ones you know are dates.
"""
from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from typing import Dict, List, Optional

_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def _shared_strings(z) -> List[str]:
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.iter(f"{_NS}t")) for si in root.findall(f"{_NS}si")]


def _sheet_targets(z) -> List[tuple]:
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid_to_target = {r.get("Id"): r.get("Target") for r in rels}
    out = []
    for s in wb.find(f"{_NS}sheets"):
        target = rid_to_target.get(s.get(f"{_RNS}id"), "")
        if not target.startswith("xl/"):
            target = "xl/" + target.lstrip("/")
        out.append((s.get("name"), target))
    return out


def _num(text):
    try:
        f = float(text)
        return int(f) if f.is_integer() else f
    except (TypeError, ValueError):
        return text


def _col(ref: str) -> str:
    return re.match(r"[A-Z]+", ref).group(0)


def read_sheet(path: str, sheet_name: str) -> List[Dict[str, object]]:
    """Return a sheet as a list of row dicts keyed by column letter:
    [{'B': 'Hus 1', 'C': 41, ...}, ...]  (only non-empty cells; rows in order)."""
    z = zipfile.ZipFile(path)
    try:
        ss = _shared_strings(z)
        target = dict(_sheet_targets(z)).get(sheet_name)
        if not target:
            return []
        root = ET.fromstring(z.read(target))
        rows = []
        for row in root.iter(f"{_NS}row"):
            cells: Dict[str, object] = {"_r": int(row.get("r"))}
            for c in row.findall(f"{_NS}c"):
                t = c.get("t")
                v = c.find(f"{_NS}v")
                if t == "s" and v is not None:
                    try:
                        val = ss[int(v.text)]
                    except (ValueError, IndexError):
                        val = v.text
                elif v is not None:
                    val = _num(v.text)
                else:
                    isv = c.find(f"{_NS}is")
                    val = "".join(t.text or "" for t in isv.iter(f"{_NS}t")) if isv is not None else None
                if val not in (None, ""):
                    cells[_col(c.get("r"))] = val
            if len(cells) > 1:
                rows.append(cells)
        return rows
    finally:
        z.close()


def sheet_names(path: str) -> List[str]:
    z = zipfile.ZipFile(path)
    try:
        return [n for n, _ in _sheet_targets(z)]
    finally:
        z.close()


def excel_date(serial) -> Optional[str]:
    """Excel/Sheets date serial → ISO 'YYYY-MM-DD'. Epoch is 1899-12-30 (the 1900 system)."""
    try:
        n = int(float(serial))
    except (TypeError, ValueError):
        return None
    if n <= 0:
        return None
    return (date(1899, 12, 30) + timedelta(days=n)).isoformat()

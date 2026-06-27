"""Drive live-read seam — keep the plan files current, then let the observer read them.

The GoogleDriveObserver reads .xlsx files from a folder. This seam keeps that folder in sync
with the live Google Drive documents. It is deliberately transport-agnostic: a `downloader`
callable does the actual fetch, so the *same* code works whether the downloader is

  * a production **service account** (Google Drive API export to xlsx), or
  * this session's **Drive connector** (Claude exports the sheet), or
  * the Google Drive desktop client (in which case no downloader is needed).

The observations the observer produces do not depend on which of these is used — only the file
on disk does. (Liveness confirmed in this environment: both sheets are reachable via the Drive
connector, owner hello@plantthatplant.com.)

This module performs no biology and no parsing — it only fetches bytes and writes a file.
"""
from __future__ import annotations

import os
from typing import Callable, Dict, List

# fileId -> a friendly local filename (so the observer's sheet-name heuristics still match)
KALABERGA_SHEETS: Dict[str, str] = {
    "1S9bc4p13618Daornv4m0-OZ0W94McSvo8pwfqjR7vuc": "Odlingsplan.xlsx",
    "1ILokJiDY8wLxkU9k_GxsoradXnzEngJ7qmk_nSm2Gj8": "Lonsamhetsanalys.xlsx",
}

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def sync_to_folder(file_map: Dict[str, str], downloader: Callable[[str], bytes],
                   out_dir: str) -> List[str]:
    """Export each Drive file to `out_dir` using `downloader(file_id) -> xlsx bytes`.
    Returns the local paths written. Skips a file (does not invent one) if the download fails."""
    os.makedirs(out_dir, exist_ok=True)
    written: List[str] = []
    for file_id, filename in file_map.items():
        try:
            data = downloader(file_id)
        except Exception:
            continue
        if not data:
            continue
        path = os.path.join(out_dir, filename)
        with open(path, "wb") as f:
            f.write(data)
        written.append(path)
    return written


class DriveExportSource:
    """Sync the live Drive plan files into a folder, then hand the paths to the observer.

        paths = DriveExportSource(KALABERGA_SHEETS, downloader, 'data/drive').sync()
        observations = GoogleDriveObserver(paths).observe()
    """

    def __init__(self, file_map: Dict[str, str], downloader: Callable[[str], bytes], out_dir: str):
        self.file_map = file_map
        self.downloader = downloader
        self.out_dir = out_dir

    def sync(self) -> List[str]:
        return sync_to_folder(self.file_map, self.downloader, self.out_dir)

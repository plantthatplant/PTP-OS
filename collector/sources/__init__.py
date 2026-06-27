"""Sources — the ONLY place Synopta's vendor reality enters the Collector.

Every source returns the same thing: a raw, vendor-shaped reading dict (or raises
SourceError). Everything downstream (translate, validate, diff, write) is identical no
matter which source produced it — exactly so the live-source decision (API vs scheduled
Export) changes one class and nothing else. This mirrors the Brain's transport seam
(app/greenhouse_brain/providers/transport.py).

Selection is a composition-time choice (a CLI flag / config), never a business-logic one.
"""
from .base import SynoptaSource, SourceError
from .fixture_source import FixtureSource
from .drop_folder_source import DropFolderSource

__all__ = ["SynoptaSource", "SourceError", "FixtureSource", "DropFolderSource",
           "make_source"]


def make_source(name: str = "fixture", path: str = None) -> SynoptaSource:
    """Pick a source by name. ('api' will be added here later — same interface,
    nothing else changes.)"""
    name = (name or "fixture").lower()
    if name in ("drop-folder", "drop_folder", "folder", "export"):
        return DropFolderSource(path)
    return FixtureSource(path) if path else FixtureSource()

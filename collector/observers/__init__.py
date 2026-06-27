"""Observers — components that produce Canonical Observations from a source of truth.

Per the Observer Network (rfc/RFC-004-observer-network.md), an observer holds no biological
reasoning; it only observes and reports. The Business Knowledge Observer (GoogleDriveObserver)
is the first non-greenhouse observer: it reports what was *intended* (plans), distinct from what
is *happening* (Synopta, humans, cameras). Reality always has priority over plans.
"""
from .google_drive_observer import GoogleDriveObserver, observe_files

__all__ = ["GoogleDriveObserver", "observe_files"]

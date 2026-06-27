"""Gaia API — the single public gateway to the Brain.

Every client (Lovable, Even G2, mobile, desktop, DJI, future robots) talks to Gaia ONLY through
this layer. Nothing here adds reasoning; it composes the existing engines once (GaiaService) and
exposes Gaia's *understanding* — never storage, vendors, or observer identity. See docs/gaia-api.md.
"""
from .service import GaiaService

__all__ = ["GaiaService"]

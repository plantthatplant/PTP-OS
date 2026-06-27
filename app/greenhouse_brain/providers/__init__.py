"""Provider Layer — every external system enters here, returning domain types only.

Which provider is used is a *composition-time* choice (env var PTP_PROVIDER), never a
business-logic one — exactly so the Brain cannot tell mock from Claude Dispatch from
(future) Synopta.
"""
import os

from .base import GreenhouseProvider
from .mock_provider import MockGreenhouseProvider
from .claude_dispatch_provider import ClaudeDispatchProvider

__all__ = ["GreenhouseProvider", "MockGreenhouseProvider", "ClaudeDispatchProvider",
           "make_provider"]


def make_provider(name: str = None) -> GreenhouseProvider:
    name = (name or os.environ.get("PTP_PROVIDER", "mock")).lower()
    if name in ("claude-dispatch", "claude_dispatch", "dispatch"):
        # Live transport if a URL is configured; otherwise the captured fixture.
        # Either way the translation — and everything above it — is identical.
        url = os.environ.get("PTP_DISPATCH_URL")
        if url:
            from .transport import HttpDispatchTransport
            key = os.environ.get("PTP_DISPATCH_KEY")
            return ClaudeDispatchProvider(transport=HttpDispatchTransport(url, api_key=key))
        return ClaudeDispatchProvider()
    # ("synopta" will be added here later — same interface, nothing else changes.)
    return MockGreenhouseProvider()

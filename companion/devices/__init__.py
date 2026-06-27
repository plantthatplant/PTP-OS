"""Device adapters — translate device-independent primitives into a specific device.

Each adapter implements CompanionDisplay. Adding a device (Android, AR, voice, robot) is a new
module here and nothing else. Gaia never imports any of these.
"""
from .even_g2 import EvenG2Display
from .console import ConsoleDisplay
from .phone import PhoneDisplay

__all__ = ["EvenG2Display", "ConsoleDisplay", "PhoneDisplay"]

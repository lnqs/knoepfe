"""OBS Studio integration widgets for knoepfe.

This plugin provides widgets for controlling OBS Studio via WebSocket connection.
"""

# Import widget modules to ensure they're loaded for discovery
from . import current_scene, recording, streaming, switch_scene  # noqa: F401

__version__ = "0.1.0"

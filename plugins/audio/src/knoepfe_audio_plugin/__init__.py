"""Audio plugin for knoepfe.

This __init__ file ensures all widget modules are imported,
making them discoverable by the PluginManager.
"""

# Import all widget modules to ensure they're loaded
from . import mic_mute

# The plugin itself
from .plugin import AudioPlugin

__version__ = "0.1.0"
__all__ = ["AudioPlugin"]

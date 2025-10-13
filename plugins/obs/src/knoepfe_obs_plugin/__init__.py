"""OBS Studio integration widgets for knoepfe.

This plugin provides widgets for controlling OBS Studio via WebSocket connection.
"""

from typing import Type

from knoepfe.plugins import PluginDescriptor
from knoepfe.widgets import Widget

from .config import OBSPluginConfig
from .plugin import OBSPlugin
from .widgets.current_scene import CurrentScene
from .widgets.recording import Recording
from .widgets.streaming import Streaming
from .widgets.switch_scene import SwitchScene

__version__ = "0.1.0"


class OBSPluginDescriptor(PluginDescriptor[OBSPluginConfig, OBSPlugin]):
    """OBS Studio integration widgets for knoepfe."""

    @classmethod
    def widgets(cls) -> list[Type[Widget]]:
        """Widgets provided by this plugin."""
        return [Recording, Streaming, CurrentScene, SwitchScene]

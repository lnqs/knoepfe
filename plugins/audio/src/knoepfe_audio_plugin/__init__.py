"""Audio plugin for knoepfe."""

from typing import Type

from knoepfe.plugins import PluginDescriptor
from knoepfe.widgets import Widget

from .config import AudioPluginConfig
from .mic_mute import MicMute
from .plugin import AudioPlugin

__version__ = "0.1.0"


class AudioPluginDescriptor(PluginDescriptor[AudioPluginConfig, AudioPlugin]):
    """Audio control widgets for knoepfe."""

    @classmethod
    def widgets(cls) -> list[Type[Widget]]:
        """Widgets provided by this plugin."""
        return [MicMute]

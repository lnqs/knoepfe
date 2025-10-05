"""Audio plugin for knoepfe."""

from typing import Type

from knoepfe.plugins import Plugin
from knoepfe.widgets import Widget

from .config import AudioPluginConfig
from .context import AudioPluginContext
from .mic_mute import MicMute

__version__ = "0.1.0"


class AudioPlugin(Plugin[AudioPluginConfig, AudioPluginContext]):
    """Audio control plugin for knoepfe."""

    description = "Audio control widgets for knoepfe"

    @classmethod
    def widgets(cls) -> list[Type[Widget]]:
        """Widgets provided by this plugin."""
        return [MicMute]

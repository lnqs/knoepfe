"""Audio control plugin for knoepfe."""

from typing import Any, Type

from knoepfe.plugin import Plugin
from knoepfe.widgets.base import Widget
from schema import Optional, Schema

from .mic_mute import MicMute

# Import state and widgets at module level
from .state import AudioPluginState


class AudioPlugin(Plugin):
    """Audio control plugin for knoepfe."""

    def create_state(self, config: dict[str, Any]) -> AudioPluginState:
        """Create audio-specific plugin state."""
        return AudioPluginState(config)

    @property
    def widgets(self) -> list[Type[Widget]]:
        """Widgets provided by this plugin."""
        return [MicMute]

    @property
    def config_schema(self) -> Schema:
        return Schema(
            {
                Optional("default_source"): str,
            }
        )

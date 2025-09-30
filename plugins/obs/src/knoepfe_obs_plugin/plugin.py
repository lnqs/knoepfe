"""OBS Studio integration plugin for knoepfe."""

from typing import Any, Type

from knoepfe.plugin import Plugin
from knoepfe.widgets.base import Widget
from schema import Optional, Schema

from .current_scene import CurrentScene
from .recording import Recording
from .state import OBSPluginState
from .streaming import Streaming
from .switch_scene import SwitchScene


class OBSPlugin(Plugin):
    """OBS Studio integration plugin for knoepfe."""

    def create_state(self, config: dict[str, Any]) -> OBSPluginState:
        """Create OBS-specific plugin state."""
        return OBSPluginState(config)

    @property
    def widgets(self) -> list[Type[Widget]]:
        """Widgets provided by this plugin."""
        return [Recording, Streaming, CurrentScene, SwitchScene]

    @property
    def config_schema(self) -> Schema:
        return Schema(
            {
                Optional("host", default="localhost"): str,
                Optional("port", default=4455): int,
                Optional("password"): str,
            }
        )

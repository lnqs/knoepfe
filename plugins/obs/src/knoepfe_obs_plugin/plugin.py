"""OBS Studio integration plugin for knoepfe."""

from typing import Type

from knoepfe.plugin import Plugin
from knoepfe.widgets.base import Widget
from schema import Optional, Schema

from knoepfe_obs_plugin.current_scene import CurrentScene
from knoepfe_obs_plugin.recording import Recording
from knoepfe_obs_plugin.streaming import Streaming
from knoepfe_obs_plugin.switch_scene import SwitchScene


class OBSPlugin(Plugin):
    """OBS Studio integration plugin for knoepfe."""

    name = "obs"

    @property
    def widgets(self) -> list[Type[Widget]]:
        return [
            Recording,
            Streaming,
            CurrentScene,
            SwitchScene,
        ]

    @property
    def config_schema(self) -> Schema | None:
        return Schema(
            {
                Optional("host", default="localhost"): str,
                Optional("port", default=4455): int,
                Optional("password"): str,
            }
        )

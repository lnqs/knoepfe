"""Audio control plugin for knoepfe."""

from typing import Type

from knoepfe.plugin import Plugin
from knoepfe.widgets.base import Widget
from schema import Optional, Schema

from knoepfe_audio_plugin.mic_mute import MicMute


class AudioPlugin(Plugin):
    """Audio control plugin for knoepfe."""

    name = "audio"

    @property
    def widgets(self) -> list[Type[Widget]]:
        return [MicMute]

    @property
    def config_schema(self) -> Schema | None:
        return Schema(
            {
                Optional("default_source"): str,
            }
        )

"""Audio control plugin for knoepfe."""

from knoepfe.config.plugin import PluginConfig
from pydantic import Field


class AudioPluginConfig(PluginConfig):
    """Configuration for audio plugin."""

    default_source: str | None = Field(default=None, description="Default audio source name")

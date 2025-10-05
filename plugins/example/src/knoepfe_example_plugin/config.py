"""Configuration for example plugin."""

from knoepfe.config.plugin import PluginConfig
from pydantic import Field


class ExamplePluginConfig(PluginConfig):
    """Configuration for example plugin."""

    default_message: str = Field(default="Example", description="Default message to display")

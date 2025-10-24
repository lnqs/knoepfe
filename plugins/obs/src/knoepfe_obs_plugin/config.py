"""Configuration for OBS plugin."""

from knoepfe.config.plugin import PluginConfig
from pydantic import Field


class OBSPluginConfig(PluginConfig):
    """Configuration for OBS plugin."""

    host: str = Field(default="localhost", description="OBS WebSocket host")
    port: int = Field(default=4455, ge=1, le=65535, description="OBS WebSocket port")
    password: str | None = Field(default=None, description="OBS WebSocket password")

    disconnected_color: str = Field(default="#202020", description="Icon color when OBS is disconnected")

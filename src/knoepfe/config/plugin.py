"""Base configuration class for plugins."""

from pydantic import Field

from knoepfe.config.base import BaseConfig


class PluginConfig(BaseConfig):
    """Base class for plugin configurations.

    All plugin-specific configuration classes should inherit from this.
    """

    enabled: bool = Field(default=True, description="Whether plugin is enabled")


class EmptyPluginConfig(PluginConfig):
    """Empty configuration for plugins that don't need additional config fields."""

    pass

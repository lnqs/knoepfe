"""Configuration system for knoepfe using Pydantic models and Python DSL."""

from knoepfe.config.base import BaseConfig
from knoepfe.config.loader import ConfigError, create_decks, create_widget, load_config
from knoepfe.config.models import DeckConfig, DeviceConfig, GlobalConfig, WidgetSpec
from knoepfe.config.plugin import PluginConfig
from knoepfe.config.widget import WidgetConfig

__all__ = [
    "BaseConfig",
    "ConfigError",
    "DeckConfig",
    "DeviceConfig",
    "GlobalConfig",
    "PluginConfig",
    "WidgetConfig",
    "WidgetSpec",
    "create_decks",
    "create_widget",
    "load_config",
]

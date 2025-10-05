"""Plugin system for knoepfe."""

from knoepfe.plugins.context import PluginContext
from knoepfe.plugins.manager import PluginInfo, PluginManager, WidgetInfo
from knoepfe.plugins.plugin import Plugin

__all__ = [
    "Plugin",
    "PluginContext",
    "PluginManager",
    "PluginInfo",
    "WidgetInfo",
]

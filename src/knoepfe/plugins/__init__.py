"""Plugin system for knoepfe."""

from knoepfe.plugins.descriptor import PluginDescriptor
from knoepfe.plugins.manager import PluginInfo, PluginManager, WidgetInfo
from knoepfe.plugins.plugin import Plugin

__all__ = [
    "Plugin",
    "PluginDescriptor",
    "PluginManager",
    "PluginInfo",
    "WidgetInfo",
]

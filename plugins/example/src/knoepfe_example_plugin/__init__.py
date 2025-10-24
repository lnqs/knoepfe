"""Knoepfe Example Plugin

A minimal example plugin demonstrating how to create widgets for knoepfe.
"""

from typing import Type

from knoepfe.plugins import PluginDescriptor
from knoepfe.widgets import Widget

from .config import ExamplePluginConfig
from .plugin import ExamplePlugin
from .widgets import ExampleWidget

__version__ = "0.1.0"


class ExamplePluginDescriptor(PluginDescriptor[ExamplePluginConfig, ExamplePlugin]):
    """Example plugin demonstrating knoepfe widget development."""

    @classmethod
    def widgets(cls) -> list[Type[Widget]]:
        """Widgets provided by this plugin."""
        return [ExampleWidget]

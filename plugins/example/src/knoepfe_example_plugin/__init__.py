"""Knoepfe Example Plugin

A minimal example plugin demonstrating how to create widgets for knoepfe.
"""

from typing import Type

from knoepfe.plugins import Plugin
from knoepfe.widgets import Widget

from .config import ExamplePluginConfig
from .context import ExamplePluginContext
from .example_widget import ExampleWidget

__version__ = "0.1.0"


class ExamplePlugin(Plugin[ExamplePluginConfig, ExamplePluginContext]):
    """Example plugin demonstrating knoepfe plugin development."""

    description = "Example plugin demonstrating knoepfe widget development"

    @classmethod
    def widgets(cls) -> list[Type[Widget]]:
        """Widgets provided by this plugin."""
        return [ExampleWidget]

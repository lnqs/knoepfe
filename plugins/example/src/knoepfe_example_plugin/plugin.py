"""Example plugin for knoepfe."""

from typing import Any, Type

from knoepfe.plugin import Plugin
from knoepfe.widgets.base import Widget
from schema import Optional, Schema

from .example_widget import ExampleWidget

# Import state and widgets at module level
from .state import ExamplePluginState


class ExamplePlugin(Plugin):
    """Example plugin demonstrating knoepfe plugin development."""

    def create_state(self, config: dict[str, Any]) -> ExamplePluginState:
        """Create example-specific plugin state."""
        return ExamplePluginState(config)

    @property
    def widgets(self) -> list[Type[Widget]]:
        """Widgets provided by this plugin."""
        return [ExampleWidget]

    @property
    def config_schema(self) -> Schema:
        return Schema(
            {
                Optional("default_message", default="Example"): str,
            }
        )

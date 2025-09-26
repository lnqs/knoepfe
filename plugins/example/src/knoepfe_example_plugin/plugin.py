"""Example plugin for knoepfe."""

from typing import Type

from knoepfe.plugin import Plugin
from knoepfe.widgets.base import Widget
from schema import Optional, Schema

from knoepfe_example_plugin.example_widget import ExampleWidget


class ExamplePlugin(Plugin):
    """Example plugin demonstrating knoepfe plugin development."""

    name = "example"

    @property
    def widgets(self) -> list[Type[Widget]]:
        return [ExampleWidget]

    @property
    def config_schema(self) -> Schema | None:
        return Schema(
            {
                Optional("default_message", default="Example"): str,
            }
        )

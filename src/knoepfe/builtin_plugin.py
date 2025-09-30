"""Built-in widgets plugin."""

from typing import Type

from knoepfe.plugin import Plugin
from knoepfe.widgets.base import Widget

# Import built-in widgets at module level
from knoepfe.widgets.clock import Clock
from knoepfe.widgets.text import Text
from knoepfe.widgets.timer import Timer


class BuiltinPlugin(Plugin):
    """Plugin providing built-in widgets."""

    @property
    def widgets(self) -> list[Type[Widget]]:
        """Return built-in widgets."""
        return [Clock, Text, Timer]

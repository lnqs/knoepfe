"""Built-in widgets plugin descriptor."""

from typing import Type

from ..config.plugin import EmptyPluginConfig
from ..widgets.builtin.clock import Clock
from ..widgets.builtin.text import Text
from ..widgets.builtin.timer import Timer
from ..widgets.widget import Widget
from .descriptor import PluginDescriptor
from .plugin import Plugin


class BuiltinPluginDescriptor(PluginDescriptor[EmptyPluginConfig, Plugin]):
    """Plugin descriptor providing built-in widgets."""

    @classmethod
    def widgets(cls) -> list[Type[Widget]]:
        """Return built-in widgets."""
        return [Clock, Text, Timer]

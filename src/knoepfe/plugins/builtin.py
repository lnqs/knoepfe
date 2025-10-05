"""Built-in widgets plugin."""

from typing import Type

from ..config.plugin import EmptyPluginConfig
from ..widgets.base import Widget
from ..widgets.builtin.clock import Clock
from ..widgets.builtin.text import Text
from ..widgets.builtin.timer import Timer
from .context import PluginContext
from .plugin import Plugin


class BuiltinPlugin(Plugin[EmptyPluginConfig, PluginContext]):
    """Plugin providing built-in widgets."""

    @classmethod
    def widgets(cls) -> list[Type[Widget]]:
        """Return built-in widgets."""
        return [Clock, Text, Timer]

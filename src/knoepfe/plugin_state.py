"""Base class for plugin state containers."""

from typing import Any


class PluginState:
    """Base class for plugin state containers.

    This class holds shared state that can be accessed by all widgets
    belonging to a plugin. Plugins can subclass this to add custom state.
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize plugin state with configuration.

        Args:
            config: Plugin-specific configuration dictionary
        """
        self.config = config

"""Base class for plugin context containers."""

from ..config.plugin import PluginConfig


class PluginContext:
    """Base class for plugin context containers.

    This class holds shared context that can be accessed by all widgets
    belonging to a plugin. Plugins can subclass this to add custom context
    and implement cleanup logic in the shutdown method.
    """

    def __init__(self, config: PluginConfig):
        """Initialize plugin context with configuration.

        Args:
            config: Typed plugin configuration object
        """
        self.config = config

    def shutdown(self) -> None:
        """Called when the plugin is being unloaded.

        Override this method to clean up any resources, close connections,
        stop background tasks, etc.
        """
        pass

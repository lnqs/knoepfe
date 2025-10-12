"""Base class for plugin instances."""

from typing import TYPE_CHECKING

from ..config.plugin import PluginConfig
from ..utils.task_manager import TaskManager

if TYPE_CHECKING:
    from ..widgets.base import Widget


class Plugin:
    """Base class for plugin instances.

    This class holds shared state and resources that can be accessed by all widgets
    belonging to a plugin. Plugin instances can be subclassed to add custom state
    and implement cleanup logic in the shutdown method.

    The plugin provides a TaskManager for managing plugin-wide background tasks
    that are shared across all widgets of the plugin.

    Lifecycle Hooks:
        Subclasses can override on_widget_activate() and on_widget_deactivate()
        to be notified when widgets using this plugin are activated or deactivated.
        This enables lazy initialization of resources and proper cleanup.
    """

    def __init__(self, config: PluginConfig):
        """Initialize plugin instance with configuration.

        Args:
            config: Typed plugin configuration object
        """
        self.config = config
        self.tasks = TaskManager()

    async def on_widget_activate(self, widget: "Widget") -> None:
        """Called when a widget using this plugin is activated.

        This is called BEFORE the widget's activate() method.
        Use this to initialize shared resources lazily when the first
        widget is activated.

        Args:
            widget: The widget instance being activated
        """
        pass

    async def on_widget_deactivate(self, widget: "Widget") -> None:
        """Called when a widget using this plugin is deactivated.

        This is called AFTER the widget's deactivate() method.
        Use this to clean up shared resources when the last widget
        is deactivated.

        Args:
            widget: The widget instance being deactivated
        """
        pass

    def shutdown(self) -> None:
        """Called when the plugin is being unloaded.

        Override this method to clean up any resources, close connections,
        stop background tasks, etc. Tasks are automatically cleaned up.
        """
        self.tasks.cleanup()

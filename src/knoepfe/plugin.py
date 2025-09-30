"""Plugin system for knoepfe."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Type

from schema import Schema

from knoepfe.plugin_state import PluginState

if TYPE_CHECKING:
    from knoepfe.widgets.base import Widget


class Plugin(ABC):
    """Base class for all knoepfe plugins.

    The Plugin creates and manages a PluginState instance that is shared
    with all widgets belonging to this plugin. This breaks circular imports
    while allowing widgets to access shared plugin state.
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize plugin with configuration.

        Args:
            config: Plugin-specific configuration dictionary
        """
        self.config = config
        self.state = self.create_state(config)

    def create_state(self, config: dict[str, Any]) -> PluginState:
        """Create the plugin state container.

        Override this method to return a custom PluginState subclass.

        Args:
            config: Plugin configuration dictionary

        Returns:
            PluginState instance for this plugin
        """
        return PluginState(config)

    @property
    @abstractmethod
    def widgets(self) -> list[Type["Widget"]]:
        """Return list of widget classes provided by this plugin.

        This property must be implemented by subclasses to declare
        which widgets they provide.

        Returns:
            List of widget classes
        """
        pass

    @property
    def config_schema(self) -> Schema:
        """Return configuration schema for this plugin.

        Returns:
            Schema object for validating plugin configuration. Must always return a Schema,
            even if empty.
        """
        return Schema({})

    def shutdown(self) -> None:
        """Called when plugin is being unloaded.

        Use this method to clean up any resources, close connections, etc.
        """
        return

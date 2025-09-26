"""Plugin system for knoepfe."""

from abc import ABC, abstractmethod
from typing import Any, Type

from schema import Schema

from knoepfe.widgets.base import Widget


class Plugin(ABC):
    """Base class for all knoepfe plugins."""

    # Abstract class attributes - subclasses must define these
    name: str

    def __init__(self, config: dict[str, Any]):
        """Initialize plugin with configuration.

        Args:
            config: Plugin-specific configuration dictionary
        """
        self.config = config

    @property
    @abstractmethod
    def widgets(self) -> list[Type[Widget]]:
        """Return list of widget classes provided by this plugin.

        Returns:
            List of Widget classes that this plugin provides
        """
        pass

    @property
    def config_schema(self) -> Schema | None:
        """Return configuration schema for this plugin.

        Returns:
            Schema object for validating plugin configuration, or None if no config needed
        """
        return None

    def shutdown(self) -> None:
        """Called when plugin is being unloaded.

        Use this method to clean up any resources, close connections, etc.
        """
        return None

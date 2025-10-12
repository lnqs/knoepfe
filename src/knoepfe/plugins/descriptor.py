"""Plugin descriptor system for knoepfe."""

from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

from ..config.plugin import PluginConfig
from ..utils.type_utils import extract_generic_arg
from ..widgets.base import Widget
from .plugin import Plugin

TPluginConfig = TypeVar("TPluginConfig", bound=PluginConfig)
TPlugin = TypeVar("TPlugin", bound=Plugin)


class PluginDescriptor(ABC, Generic[TPluginConfig, TPlugin]):
    """Base class for all knoepfe plugin descriptors.

    Plugin descriptors are pure type containers that declare their configuration schema,
    plugin type, and provided widgets. Descriptors are never instantiated - the
    PluginManager uses them only to extract type information and widget lists.

    Type Parameters:
        TPluginConfig: The plugin's configuration type (subclass of PluginConfig)
        TPlugin: The plugin instance type (subclass of Plugin)

    Example:
        class AudioPluginDescriptor(PluginDescriptor[AudioPluginConfig, AudioPlugin]):
            description = "Audio control plugin for knoepfe"

            @classmethod
            def widgets(cls) -> list[Type[Widget]]:
                return [MicMute, VolumeControl]
    """

    description: str | None = None

    @classmethod
    def get_config_type(cls) -> Type[PluginConfig]:
        """Extract the config type from the first generic parameter.

        Returns:
            The PluginConfig subclass specified as the first type parameter

        Raises:
            TypeError: If the descriptor doesn't specify a valid PluginConfig type
        """
        return extract_generic_arg(cls, PluginConfig, 0)

    @classmethod
    def get_plugin_type(cls) -> Type["Plugin"]:
        """Extract the plugin type from the second generic parameter.

        Returns:
            The Plugin subclass specified as the second type parameter

        Raises:
            TypeError: If the descriptor doesn't specify a valid Plugin type
        """
        return extract_generic_arg(cls, Plugin, 1)

    @classmethod
    @abstractmethod
    def widgets(cls) -> list[Type["Widget"]]:
        """Return list of widget classes provided by this plugin descriptor.

        This method must be implemented by subclasses to declare
        which widgets they provide.

        Returns:
            List of widget classes
        """
        pass

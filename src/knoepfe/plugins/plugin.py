"""Plugin system for knoepfe."""

from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

from ..config.plugin import PluginConfig
from ..utils.type_utils import extract_generic_arg
from ..widgets.base import Widget
from .context import PluginContext

TConfig = TypeVar("TConfig", bound=PluginConfig)
TContext = TypeVar("TContext", bound=PluginContext)


class Plugin(ABC, Generic[TConfig, TContext]):
    """Base class for all knoepfe plugins.

    Plugins are pure type containers that declare their configuration schema,
    context type, and provided widgets. Plugins are never instantiated - the
    PluginManager uses them only to extract type information and widget lists.

    Type Parameters:
        TConfig: The plugin's configuration type (subclass of PluginConfig)
        TState: The plugin's context type (subclass of PluginContext)

    Example:
        class AudioPlugin(Plugin[AudioPluginConfig, AudioPluginContext]):
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
            TypeError: If the plugin doesn't specify a valid PluginConfig type
        """
        return extract_generic_arg(cls, PluginConfig, 0)

    @classmethod
    def get_context_type(cls) -> Type[PluginContext]:
        """Extract the context type from the second generic parameter.

        Returns:
            The PluginContext subclass specified as the second type parameter

        Raises:
            TypeError: If the plugin doesn't specify a valid PluginContext type
        """
        return extract_generic_arg(cls, PluginContext, 1)

    @classmethod
    @abstractmethod
    def widgets(cls) -> list[Type["Widget"]]:
        """Return list of widget classes provided by this plugin.

        This method must be implemented by subclasses to declare
        which widgets they provide.

        Returns:
            List of widget classes
        """
        pass

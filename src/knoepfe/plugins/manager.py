import inspect
import logging
from dataclasses import dataclass, field
from importlib.metadata import entry_points
from typing import Type

from ..config.plugin import PluginConfig
from ..config.widget import WidgetConfig
from ..widgets.base import Widget
from .descriptor import PluginDescriptor
from .plugin import Plugin

logger = logging.getLogger(__name__)


@dataclass
class PluginInfo:
    """Information about a loaded plugin descriptor and its instance."""

    name: str
    descriptor_class: Type[PluginDescriptor]
    config: PluginConfig
    plugin: Plugin
    version: str
    description: str | None
    widgets: list["WidgetInfo"] = field(default_factory=list)


@dataclass
class WidgetInfo:
    """Information about a discovered widget."""

    name: str
    description: str | None
    widget_class: Type[Widget]
    config_type: Type[WidgetConfig]
    plugin_info: PluginInfo


class PluginManager:
    """Manages plugin lifecycle and widget discovery.

    The PluginManager is responsible for:
    - Loading plugin descriptor classes from entry points
    - Instantiating plugin configs and plugin instances based on descriptor type parameters
    - Registering widgets provided by plugin descriptors
    - Providing access to plugin instances for widgets
    """

    def __init__(self, plugin_configs: dict[str, dict] | None = None):
        """Initialize the plugin manager.

        Args:
            plugin_configs: Optional dictionary mapping plugin names to their configuration dicts
        """
        self._plugins: dict[str, PluginInfo] = {}
        self._widgets: dict[str, WidgetInfo] = {}
        self._plugin_configs: dict[str, dict] = plugin_configs or {}
        self._load_plugins()

    def _load_plugins(self):
        """Load all registered plugin descriptors via entry points."""
        for ep in entry_points(group="knoepfe.plugins"):
            try:
                plugin_name = ep.name
                dist_name = ep.dist.name if ep.dist else plugin_name

                logger.debug(f"Loading plugin '{plugin_name}' from {dist_name}")

                # Load the plugin descriptor class (not instantiated!)
                descriptor_class = ep.load()

                # Validate that it's actually a PluginDescriptor subclass
                if not (inspect.isclass(descriptor_class) and issubclass(descriptor_class, PluginDescriptor)):
                    logger.error(
                        f"Entry point '{plugin_name}' does not point to a PluginDescriptor subclass: {descriptor_class}"
                    )
                    continue

                # Load the plugin with its metadata
                version = ep.dist.version if ep.dist else "unknown"
                # Get description from descriptor class attribute
                description = getattr(descriptor_class, "description", None)

                self._load_plugin(plugin_name, descriptor_class, version, description)

            except Exception:
                logger.exception(f"Failed to load plugin {ep.name}")

    def _load_plugin(
        self, plugin_name: str, descriptor_class: Type[PluginDescriptor], version: str, description: str | None
    ):
        """Load and register a plugin descriptor.

        Args:
            plugin_name: Name of the plugin
            descriptor_class: The plugin descriptor class to load
            version: Plugin version string
            description: Plugin description from descriptor class attribute
        """
        # Get plugin config dict from stored configs
        plugin_config_dict = self._plugin_configs.get(plugin_name, {})

        # Extract config and plugin types from the descriptor class
        config_type = descriptor_class.get_config_type()
        plugin_type = descriptor_class.get_plugin_type()

        # Instantiate config (validates automatically via Pydantic)
        plugin_config = config_type(**plugin_config_dict)

        # Check if plugin is enabled
        if not plugin_config.enabled:
            logger.info(f"Plugin '{plugin_name}' is disabled in config, skipping")
            return

        # Instantiate plugin with the config
        plugin_instance = plugin_type(plugin_config)

        # Create plugin info first (widgets will be added later)
        plugin_info = PluginInfo(
            name=plugin_name,
            descriptor_class=descriptor_class,
            config=plugin_config,
            plugin=plugin_instance,
            version=version,
            description=description,
        )

        # Store plugin info
        self._plugins[plugin_name] = plugin_info

        # Get widgets from the descriptor class (classmethod, no instance needed)
        widget_classes = descriptor_class.widgets()

        # Register widgets with reference to plugin info
        # This also populates plugin_info.widgets
        widget_infos = self._register_widgets(widget_classes, plugin_info)

        widget_names = ", ".join(w.name for w in widget_infos)
        logger.debug(f"Loaded {len(widget_infos)} widgets from plugin '{plugin_name}': {widget_names}")
        logger.debug(f"Successfully loaded plugin '{plugin_name}' v{plugin_info.version}")

    def _register_widgets(self, widget_classes: list[Type[Widget]], plugin_info: PluginInfo) -> list[WidgetInfo]:
        """Register widgets from a plugin.

        Args:
            widget_classes: List of widget classes to register
            plugin_info: Plugin info for the plugin providing the widgets

        Returns:
            List of successfully registered widget infos
        """
        widget_infos = []
        for widget_class in widget_classes:
            # Extract config type from widget class
            try:
                config_type = widget_class.get_config_type()
            except TypeError as e:
                logger.warning(f"Could not extract config type for widget '{widget_class.name}': {e}")
                continue

            widget_info = WidgetInfo(
                name=widget_class.name,
                description=widget_class.description,
                widget_class=widget_class,
                config_type=config_type,
                plugin_info=plugin_info,
            )

            if widget_info.name in self._widgets:
                logger.warning(f"Widget name '{widget_info.name}' already registered, skipping")
                continue

            self._widgets[widget_info.name] = widget_info
            widget_infos.append(widget_info)
            # Also add to plugin's widget list
            plugin_info.widgets.append(widget_info)
            logger.debug(f"Registered widget '{widget_info.name}' from plugin '{plugin_info.name}'")

        return widget_infos

    @property
    def widgets(self) -> dict[str, WidgetInfo]:
        """Get all registered widgets.

        Returns:
            Dictionary mapping widget names to WidgetInfo objects
        """
        return self._widgets

    @property
    def plugins(self) -> dict[str, PluginInfo]:
        """Get all registered plugins.

        Returns:
            Dictionary mapping plugin names to PluginInfo objects
        """
        return self._plugins

    def shutdown_all(self) -> None:
        """Shutdown all plugins by calling shutdown on their plugin instances."""
        for plugin_info in self._plugins.values():
            try:
                plugin_info.plugin.shutdown()
            except Exception:
                logger.exception(f"Error shutting down plugin {plugin_info.name}")

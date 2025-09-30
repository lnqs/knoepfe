import inspect
import logging
from dataclasses import dataclass
from importlib.metadata import entry_points
from typing import Type

from knoepfe.plugin import Plugin
from knoepfe.widgets.base import Widget

logger = logging.getLogger(__name__)


@dataclass
class PluginInfo:
    """Information about a loaded plugin."""

    name: str
    instance: Plugin
    version: str
    description: str


@dataclass
class WidgetInfo:
    """Information about a discovered widget."""

    name: str
    description: str | None
    widget_class: Type[Widget]
    plugin_name: str


class PluginNotFoundError(Exception):
    """Raised when a required plugin cannot be found or imported."""

    def __init__(self, plugin_name: str):
        self.plugin_name = plugin_name
        super().__init__(f"Plugin '{plugin_name}' not found.")


class WidgetNotFoundError(Exception):
    """Raised when a required widget cannot be found or imported."""

    def __init__(self, widget_name: str):
        self.widget_name = widget_name
        super().__init__(f"Widget '{widget_name}' not found. Use 'knoepfe list-widgets' to see available widgets.")


class PluginManager:
    """Manages plugin lifecycle and widget discovery."""

    def __init__(self):
        self._plugins: dict[str, PluginInfo] = {}
        self._widgets: dict[str, WidgetInfo] = {}
        self._plugin_configs: dict[str, dict] = {}
        self._load_plugins()

    def set_plugin_config(self, plugin_name: str, config: dict) -> None:
        """Set configuration for a plugin before it's loaded."""
        self._plugin_configs[plugin_name] = config

    def _load_plugins(self):
        """Load all registered plugins via entry points."""
        for ep in entry_points(group="knoepfe.plugins"):
            try:
                # Plugin name comes from entry point name
                plugin_name = ep.name
                dist_name = ep.dist.name if ep.dist else plugin_name

                logger.info(f"Loading plugin '{plugin_name}' from {dist_name}")

                # Load the plugin class
                plugin_class = ep.load()

                # Validate that it's actually a Plugin subclass
                if not (inspect.isclass(plugin_class) and issubclass(plugin_class, Plugin)):
                    logger.error(f"Entry point '{plugin_name}' does not point to a Plugin subclass: {plugin_class}")
                    continue

                # Instantiate plugin
                plugin_config = self._plugin_configs.get(plugin_name, {})

                # Create plugin instance first
                plugin_instance = plugin_class(plugin_config)

                # Validate plugin configuration
                schema = plugin_instance.config_schema
                schema.validate(plugin_config)

                # Get widgets from the plugin
                widget_classes = plugin_instance.widgets

                # Register widgets
                widget_infos = []
                for widget_class in widget_classes:
                    widget_info = WidgetInfo(
                        name=widget_class.name,
                        description=widget_class.description,
                        widget_class=widget_class,
                        plugin_name=plugin_name,
                    )

                    if widget_info.name in self._widgets:
                        logger.warning(f"Widget name '{widget_info.name}' already registered, skipping")
                        continue

                    self._widgets[widget_info.name] = widget_info
                    widget_infos.append(widget_info)
                    logger.debug(f"Registered widget '{widget_info.name}' from plugin '{plugin_name}'")

                widget_names = ", ".join(w.name for w in widget_infos)
                logger.info(f"Loaded {len(widget_infos)} widgets from plugin '{plugin_name}': {widget_names}")

                # Store plugin info
                plugin_info = PluginInfo(
                    name=plugin_name,
                    instance=plugin_instance,
                    version=ep.dist.version if ep.dist else "unknown",
                    description=(
                        ep.dist.metadata.get("Summary", "No description")
                        if ep.dist and ep.dist.metadata
                        else "No description"
                    ),
                )

                self._plugins[plugin_name] = plugin_info
                logger.info(f"Successfully loaded plugin '{plugin_name}' v{plugin_info.version}")

            except Exception:
                logger.exception(f"Failed to load plugin {ep.name}")

    def get_plugin_for_widget(self, widget_name: str) -> Plugin:
        """Get the plugin instance that provides a widget."""
        if widget_name not in self._widgets:
            raise WidgetNotFoundError(widget_name)

        plugin_name = self._widgets[widget_name].plugin_name
        return self.get_plugin(plugin_name)

    def get_plugin(self, name: str) -> Plugin:
        """Get plugin instance by name."""
        if name not in self._plugins:
            raise PluginNotFoundError(name)
        return self._plugins[name].instance

    def shutdown_all(self) -> None:
        """Shutdown all plugins."""
        for plugin_info in self._plugins.values():
            try:
                plugin_info.instance.shutdown()
            except Exception:
                logger.exception(f"Error shutting down plugin {plugin_info.name}")

    def get_widget(self, name: str) -> Type[Widget]:
        """Get widget class by name."""
        if name not in self._widgets:
            raise WidgetNotFoundError(name)
        return self._widgets[name].widget_class

    def list_widgets(self) -> list[str]:
        """List all available widget names."""
        return list(self._widgets.keys())

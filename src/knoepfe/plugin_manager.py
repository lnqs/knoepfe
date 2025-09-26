import logging
from dataclasses import dataclass
from importlib.metadata import entry_points
from typing import Type

from schema import Schema

from knoepfe.plugin import Plugin
from knoepfe.widgets.base import Widget

logger = logging.getLogger(__name__)


@dataclass
class PluginMetadata:
    """Metadata for a plugin extracted from package information."""

    version: str
    description: str


class PluginNotFoundError(Exception):
    """Raised when a required plugin cannot be found or imported."""

    def __init__(self, plugin_name: str):
        self.plugin_name = plugin_name

        super().__init__(f"Plugin '{plugin_name}' not found.")


class PluginManager:
    """Manages plugin lifecycle."""

    def __init__(self):
        self.plugins: dict[str, Plugin] = {}
        self._plugin_configs: dict[str, dict] = {}  # Store plugin configs
        self._plugin_metadata: dict[str, PluginMetadata] = {}
        self._load_plugins()

    def set_plugin_config(self, plugin_name: str, config: dict) -> None:
        """Set configuration for a plugin before it's loaded."""
        self._plugin_configs[plugin_name] = config

    def _load_plugins(self):
        """Load all registered plugins via entry points."""
        # Load plugins from entry points
        for ep in entry_points(group="knoepfe.plugins"):
            try:
                dist_name = ep.dist.name if ep.dist else ep.name
                logger.info(f"Loading plugin: {ep.name} from {dist_name}")

                plugin_class = ep.load()

                # Get config for this plugin (empty dict if none provided)
                plugin_config = self._plugin_configs.get(ep.name, {})

                # Instantiate plugin
                plugin = plugin_class(plugin_config)

                # Extract version and description from package metadata
                plugin_version = ep.dist.version if ep.dist else "unknown"
                plugin_description = (
                    ep.dist.metadata.get("Summary", "No description")
                    if ep.dist and ep.dist.metadata
                    else "No description"
                )

                self.register_plugin(plugin, plugin_version, plugin_description)
                logger.info(f"Successfully loaded plugin: {plugin.name} v{plugin_version}")

            except Exception:
                logger.exception(f"Failed to load plugin {ep.name}")

    def register_plugin(self, plugin: Plugin, version: str = "unknown", description: str = "No description") -> None:
        """Register a plugin and its widgets."""
        # Validate plugin name uniqueness
        if plugin.name in self.plugins:
            raise ValueError(f"Plugin name '{plugin.name}' already in use")

        # Validate plugin configuration if schema provided
        if plugin.config_schema:
            plugin.config_schema.validate(plugin.config)

        self.plugins[plugin.name] = plugin
        self._plugin_metadata[plugin.name] = PluginMetadata(version=version, description=description)

    def get_all_widgets(self) -> list[Type[Widget]]:
        """Get all widget classes from all loaded plugins."""
        widgets = []
        for plugin in self.plugins.values():
            widgets.extend(plugin.widgets)
        return widgets

    def get_plugin(self, name: str) -> Plugin:
        """Get plugin by name."""
        if name not in self.plugins:
            raise PluginNotFoundError(name)

        return self.plugins[name]

    def get_config_schema(self, plugin_name: str) -> Schema | None:
        """Get config schema by plugin name."""
        if plugin_name not in self.plugins:
            raise PluginNotFoundError(plugin_name)

        return self.plugins[plugin_name].config_schema

    def list_plugins(self) -> list[str]:
        """List all available plugin names."""
        return list(self.plugins.keys())

    def shutdown_all(self) -> None:
        """Shutdown all plugins."""
        for plugin in self.plugins.values():
            try:
                plugin.shutdown()
            except Exception:
                logger.exception(f"Error shutting down plugin {plugin.name}")

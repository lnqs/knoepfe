import logging
from importlib.metadata import entry_points
from typing import Type

from knoepfe.widgets.base import Widget

logger = logging.getLogger(__name__)


class WidgetNotFoundError(Exception):
    """Raised when a required widget cannot be found or imported."""

    def __init__(self, widget_name: str):
        self.widget_name = widget_name

        super().__init__(f"Widget '{widget_name}' not found. Use 'knoepfe list-widgets' to see available widgets.")


class PluginManager:
    def __init__(self):
        self._widget_plugins: dict[str, Type[Widget]] = {}
        self._load_plugins()

    def _load_plugins(self):
        """Load all registered widget plugins via entry points."""
        for ep in entry_points(group="knoepfe.widgets"):
            try:
                widget_class = ep.load()
                self._widget_plugins[ep.name] = widget_class
                logger.info(f"Loaded widget plugin: {ep.name} from {ep.dist}")
            except Exception as e:
                logger.error(f"Failed to load widget plugin {ep.name}: {e}")

    def get_widget(self, name: str) -> Type[Widget]:
        """Get widget class by name."""
        if name in self._widget_plugins:
            return self._widget_plugins[name]

        raise WidgetNotFoundError(name)

    def list_widgets(self) -> list[str]:
        """List all available widget names."""
        return list(self._widget_plugins.keys())


# Global plugin manager instance
plugin_manager = PluginManager()

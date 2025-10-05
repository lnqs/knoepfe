"""Custom exceptions for knoepfe."""


class PluginNotFoundError(Exception):
    """Raised when a required plugin cannot be found or imported."""

    def __init__(self, plugin_name: str):
        self.plugin_name = plugin_name
        super().__init__(f"Plugin '{plugin_name}' not found. Use 'knoepfe plugins list' to see available plugins.")


class WidgetNotFoundError(Exception):
    """Raised when a required widget cannot be found or imported."""

    def __init__(self, widget_name: str):
        self.widget_name = widget_name
        super().__init__(f"Widget '{widget_name}' not found. Use 'knoepfe widgets list' to see available widgets.")

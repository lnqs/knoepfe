"""Context container for example plugin."""

from knoepfe.plugins import PluginContext

from .config import ExamplePluginConfig


class ExamplePluginContext(PluginContext):
    """Context container for example plugin widgets."""

    def __init__(self, config: "ExamplePluginConfig"):
        super().__init__(config)
        # Initialize shared context - total clicks across all example widgets
        self.total_clicks = 0

    def increment_clicks(self) -> int:
        """Increment the total click count and return the new value."""
        self.total_clicks += 1
        return self.total_clicks

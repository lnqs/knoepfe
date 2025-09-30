"""State container for example plugin."""

from typing import Any

from knoepfe.plugin_state import PluginState


class ExamplePluginState(PluginState):
    """State container for example plugin widgets."""

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        # Initialize shared state - total clicks across all example widgets
        self.total_clicks = 0

    def increment_clicks(self) -> int:
        """Increment the total click count and return the new value."""
        self.total_clicks += 1
        return self.total_clicks

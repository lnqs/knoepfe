"""State container for audio plugin."""

from typing import Any

from knoepfe.plugin_state import PluginState


class AudioPluginState(PluginState):
    """State container for audio plugin widgets."""

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        # Plugin-specific state
        self.default_source = config.get("default_source")
        self.active_widgets: set[str] = set()
        self.mute_states: dict[str, bool] = {}

    def register_widget(self, widget_id: str) -> None:
        """Track active widgets."""
        self.active_widgets.add(widget_id)

    def unregister_widget(self, widget_id: str) -> None:
        """Remove widget from tracking."""
        self.active_widgets.discard(widget_id)

    def sync_mute_state(self, source: str, muted: bool) -> None:
        """Synchronize mute state across all widgets."""
        self.mute_states[source] = muted

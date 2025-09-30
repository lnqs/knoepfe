"""State container for OBS plugin."""

from typing import Any

from knoepfe.plugin_state import PluginState

from .connector import OBS


class OBSPluginState(PluginState):
    """State container for OBS plugin widgets."""

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        # Initialize shared OBS connector
        self.obs = OBS()

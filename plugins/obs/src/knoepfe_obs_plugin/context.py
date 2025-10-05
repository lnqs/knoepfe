"""Context container for OBS plugin."""

from knoepfe.plugins import PluginContext

from .config import OBSPluginConfig
from .connector import OBS


class OBSPluginContext(PluginContext):
    """Context container for OBS plugin widgets."""

    def __init__(self, config: OBSPluginConfig):
        super().__init__(config)
        self.obs = OBS(config)
        self.disconnected_color = config.disconnected_color

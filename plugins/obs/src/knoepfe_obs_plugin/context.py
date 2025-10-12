"""Context container for OBS plugin."""

import logging
from typing import TYPE_CHECKING

from knoepfe.plugins import PluginContext

from .config import OBSPluginConfig
from .connector import OBS

if TYPE_CHECKING:
    from knoepfe.widgets.base import Widget

logger = logging.getLogger(__name__)


class OBSPluginContext(PluginContext):
    """Context container for OBS plugin widgets.

    Provides shared state and resources for all OBS widgets, including
    a single OBS WebSocket connection that is shared across all widgets.

    The OBS connection is lazily initialized when the first widget
    is activated and remains connected for the lifetime of the plugin.
    """

    def __init__(self, config: OBSPluginConfig):
        super().__init__(config)
        self.obs = OBS(config, self.tasks)
        self.disconnected_color = config.disconnected_color

    async def on_widget_activate(self, widget: "Widget") -> None:
        """Connect to OBS when first widget activates.

        This is called BEFORE the widget's activate() method.
        The connection remains active for the lifetime of the plugin.
        """
        await super().on_widget_activate(widget)

        # Connect to OBS if not already connected
        if not self.obs.connected:
            logger.info("OBS plugin: First widget activated, connecting to OBS...")
            await self.obs.connect()
        else:
            logger.debug(f"OBS plugin: Widget {widget.name} activated (OBS already connected)")

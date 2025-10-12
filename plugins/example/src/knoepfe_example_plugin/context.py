"""Context container for example plugin."""

import logging
from typing import TYPE_CHECKING

from knoepfe.plugins import PluginContext

from .config import ExamplePluginConfig

if TYPE_CHECKING:
    from knoepfe.widgets.base import Widget

logger = logging.getLogger(__name__)


class ExamplePluginContext(PluginContext):
    """Context container for example plugin widgets.

    This example demonstrates the lifecycle hooks that plugins can use
    to be notified when widgets are activated or deactivated.
    """

    def __init__(self, config: "ExamplePluginConfig"):
        super().__init__(config)
        # Shared state
        self.active_widget_count = 0
        self.total_clicks = 0

    async def on_widget_activate(self, widget: "Widget") -> None:
        """Called when a widget using this context is activated.

        This is called BEFORE the widget's activate() method.
        Use this for lazy initialization of shared resources.
        """
        await super().on_widget_activate(widget)

        # Log when widgets are activated
        if self.active_widget_count == 1:
            # First widget activated - could initialize shared resources here
            logger.info(
                f"Example plugin: First widget activated ({widget.name}). "
                f"This is where you would initialize shared resources like connections."
            )
        else:
            logger.debug(
                f"Example plugin: Widget {widget.name} activated ({self.active_widget_count} total active widgets)"
            )

    async def on_widget_deactivate(self, widget: "Widget") -> None:
        """Called when a widget using this context is deactivated.

        This is called AFTER the widget's deactivate() method.
        Use this for cleanup when the last widget deactivates.
        """
        logger.debug(
            f"Example plugin: Widget {widget.name} deactivated "
            f"({self.active_widget_count - 1} remaining active widgets)"
        )

        self.active_widget_count -= 1
        await super().on_widget_deactivate(widget)

        if self.active_widget_count == 0:
            # Last widget deactivated - could clean up shared resources here
            logger.info(
                "Example plugin: Last widget deactivated. "
                "This is where you would clean up shared resources like connections."
            )

    def increment_clicks(self) -> int:
        """Increment the total click count and return the new value."""
        self.total_clicks += 1
        return self.total_clicks

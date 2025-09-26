"""Example Widget - A minimal widget demonstrating knoepfe plugin development."""

from typing import Any

from knoepfe.key import Key
from knoepfe.widgets.base import Widget
from schema import Optional, Schema


class ExampleWidget(Widget):
    """A minimal example widget that demonstrates the basic structure of a knoepfe widget.

    This widget displays a customizable message and changes appearance when clicked.
    It serves as a template for developing custom widgets.
    """

    name = "ExampleWidget"

    def __init__(self, widget_config: dict[str, Any], global_config: dict[str, Any]) -> None:
        """Initialize the ExampleWidget.

        Args:
            widget_config: Widget-specific configuration
            global_config: Global knoepfe configuration
        """
        super().__init__(widget_config, global_config)

        # Internal state to track clicks
        self._click_count = 0

    async def activate(self) -> None:
        """Called when the widget becomes active.

        Use this method to start background tasks, initialize resources, etc.
        """
        # Reset click count when widget becomes active
        self._click_count = 0

    async def deactivate(self) -> None:
        """Called when the widget becomes inactive.

        Use this method to clean up resources, stop background tasks, etc.
        """
        # Clean up any resources if needed
        pass

    async def update(self, key: Key) -> None:
        """Update the widget display.

        This method is called whenever the widget needs to be redrawn.

        Args:
            key: The Stream Deck key to render to
        """
        # Get the message from config, with a default
        message = self.config.get("message", "Example")

        # Create display text based on click count
        if self._click_count == 0:
            display_text = f"{message}\nClick me!"
        else:
            display_text = f"{message}\nClicked {self._click_count}x"

        # Use the key renderer to draw the widget
        with key.renderer() as renderer:
            # Draw the text
            renderer.text(display_text)

    async def on_key_down(self) -> None:
        """Handle key press events.

        This method is called when the Stream Deck key is pressed down.
        """
        # Increment click counter
        self._click_count += 1

        # Request an update to show the new state
        self.request_update()

    async def on_key_up(self) -> None:
        """Handle key release events.

        This method is called when the Stream Deck key is released.
        """
        # Optional: Handle key release if needed
        # For this example, we don't need to do anything on key up
        pass

    @classmethod
    def get_config_schema(cls) -> Schema:
        """Define the configuration schema for this widget.

        Returns:
            Schema object defining valid configuration parameters
        """
        schema = Schema(
            {
                Optional("message", default="Example"): str,
            }
        )
        return cls.add_defaults(schema)

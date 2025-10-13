"""Example Widget - A minimal widget demonstrating knoepfe plugin development."""

from knoepfe.config.widget import WidgetConfig
from knoepfe.core.key import Key
from knoepfe.widgets import Widget
from pydantic import Field

from .plugin import ExamplePlugin


class ExampleWidgetConfig(WidgetConfig):
    """Configuration for ExampleWidget."""

    message: str = Field(default="Example", description="Message to display")


class ExampleWidget(Widget[ExampleWidgetConfig, ExamplePlugin]):
    """Interactive example widget with click counter.

    This widget displays a customizable message and changes appearance when clicked.
    It serves as a template for developing custom widgets.
    """

    name = "ExampleWidget"

    def __init__(self, config: ExampleWidgetConfig, plugin: ExamplePlugin) -> None:
        """Initialize the ExampleWidget.

        Args:
            config: Widget-specific configuration
            plugin: Example plugin instance for sharing data between widgets and access to TaskManager
        """
        super().__init__(config, plugin)

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
        # Get the message from config
        message = self.config.message

        # Create display text based on click count
        if self._click_count == 0:
            display_text = f"{message}\nClick me!"
        else:
            display_text = f"{message}\nClicked {self._click_count}x"

        # Use the key renderer to draw the widget
        with key.renderer() as renderer:
            renderer.clear()
            # Draw the text
            renderer.text_wrapped(display_text)

    async def on_key_down(self) -> None:
        """Handle key press events.

        This method is called when the Stream Deck key is pressed down.
        """
        # Increment local click counter
        self._click_count += 1

        # Also increment the shared plugin counter
        total_clicks = self.plugin.increment_clicks()

        # Log the shared plugin state for demonstration
        print(f"Widget clicked {self._click_count} times, total across all widgets: {total_clicks}")

        # Request an update to show the new state
        self.request_update()

    async def on_key_up(self) -> None:
        """Handle key release events.

        This method is called when the Stream Deck key is released.
        """
        # Optional: Handle key release if needed
        # For this example, we don't need to do anything on key up
        pass

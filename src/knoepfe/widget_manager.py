import logging
from typing import Type

from knoepfe.widgets.base import Widget

logger = logging.getLogger(__name__)

"""Register built-in widgets directly."""
from knoepfe.widgets.clock import Clock
from knoepfe.widgets.text import Text
from knoepfe.widgets.timer import Timer

builtin_widgets = [Clock, Text, Timer]


class WidgetNotFoundError(Exception):
    """Raised when a required widget cannot be found or imported."""

    def __init__(self, widget_name: str):
        self.widget_name = widget_name

        super().__init__(f"Widget '{widget_name}' not found. Use 'knoepfe list-widgets' to see available widgets.")


class WidgetManager:
    """Manages widget registration and lookup."""

    def __init__(self):
        self.widgets: dict[str, Type[Widget]] = {}
        self._register_builtin_widgets()

    def _register_builtin_widgets(self):
        """Register built-in widgets directly."""
        for widget_class in builtin_widgets:
            widget_name = widget_class.name

            self.widgets[widget_name] = widget_class
            logger.info(f"Registered built-in widget: {widget_name}")

    def register_widget(self, widget_class: Type[Widget]) -> None:
        """Register a widget class."""
        # Widget must have a name attribute
        if not hasattr(widget_class, "name"):
            raise ValueError(f"Widget class '{widget_class.__name__}' must have a 'name' attribute")

        widget_name = widget_class.name

        if widget_name in self.widgets:
            raise ValueError(f"Widget name '{widget_name}' already in use")

        self.widgets[widget_name] = widget_class
        logger.info(f"Registered widget: {widget_name}")

    def get_widget(self, name: str) -> Type[Widget]:
        """Get widget class by name."""
        if name in self.widgets:
            return self.widgets[name]

        raise WidgetNotFoundError(name)

    def list_widgets(self) -> list[str]:
        """List all available widget names."""
        return list(self.widgets.keys())

    def has_widget(self, name: str) -> bool:
        """Check if a widget with the given name exists."""
        return name in self.widgets

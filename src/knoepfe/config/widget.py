"""Base configuration class for widgets."""

from pydantic import Field

from knoepfe.config.base import BaseConfig


class WidgetConfig(BaseConfig):
    """Base class for widget configurations.

    Widgets define their own fields by subclassing this class.
    """

    index: int | None = Field(default=None, description="Display position index (None = next available position)")
    switch_deck: str | None = Field(default=None, description="Deck to switch to when widget is pressed")
    font: str | None = Field(default=None, description="Font family and style (e.g., 'sans:style=Bold')")
    color: str = Field(default="white", description="Primary color for text/icons")


class EmptyConfig(WidgetConfig):
    """Empty configuration for widgets that don't need additional config fields."""

    pass

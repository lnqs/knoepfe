from pydantic import Field

from ...config.widget import WidgetConfig
from ...core.key import Key
from ...plugins.plugin import Plugin
from ..base import Widget


class TextConfig(WidgetConfig):
    """Configuration for Text widget."""

    text: str = Field(..., description="Text to display")


class Text(Widget[TextConfig, Plugin]):
    """Display static text."""

    name = "Text"

    def __init__(self, config: TextConfig, plugin: Plugin) -> None:
        super().__init__(config, plugin)

    async def update(self, key: Key) -> None:
        with key.renderer() as renderer:
            renderer.clear()
            renderer.text_wrapped(
                self.config.text,
                font=self.config.font,
                color=self.config.color,
            )

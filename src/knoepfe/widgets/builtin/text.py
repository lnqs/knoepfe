from pydantic import Field

from ...config.widget import WidgetConfig
from ...core.key import Key
from ...plugins.context import PluginContext
from ..base import Widget


class TextConfig(WidgetConfig):
    """Configuration for Text widget."""

    text: str = Field(..., description="Text to display")


class Text(Widget[TextConfig, PluginContext]):
    name = "Text"
    description = "Display static text"

    def __init__(self, config: TextConfig, context: PluginContext) -> None:
        super().__init__(config, context)

    async def update(self, key: Key) -> None:
        with key.renderer() as renderer:
            renderer.clear()
            renderer.text_wrapped(
                self.config.text,
                font=self.config.font,
                color=self.config.color,
            )

from pydantic import Field

from ...config.widget import WidgetConfig
from ...plugins.plugin import Plugin
from ...rendering import Renderer
from ..actions import UpdateResult
from ..base import Widget


class TextConfig(WidgetConfig):
    """Configuration for Text widget."""

    text: str = Field(..., description="Text to display")


class Text(Widget[TextConfig, Plugin]):
    """Display static text."""

    name = "Text"

    def __init__(self, config: TextConfig, plugin: Plugin) -> None:
        super().__init__(config, plugin)

    async def update(self, renderer: Renderer) -> UpdateResult:
        renderer.clear()
        renderer.text_multiline(
            self.config.text,
            font=self.config.font,
            color=self.config.color,
        )
        return UpdateResult.UPDATED

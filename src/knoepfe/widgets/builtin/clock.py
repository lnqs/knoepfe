from datetime import datetime

from pydantic import Field

from ...config.widget import WidgetConfig
from ...core.key import Key
from ...plugins.context import PluginContext
from ..base import Widget


class ClockConfig(WidgetConfig):
    """Configuration for Clock widget."""

    format: str = Field(default="%H:%M", description="Time format string")


class Clock(Widget[ClockConfig, PluginContext]):
    name = "Clock"
    description = "Display current time"

    def __init__(self, config: ClockConfig, context: PluginContext) -> None:
        super().__init__(config, context)
        self.last_time = ""

    async def activate(self) -> None:
        self.request_periodic_update(1.0)

    async def deactivate(self) -> None:
        self.last_time = ""

    async def update(self, key: Key) -> None:
        time = datetime.now().strftime(self.config.format)
        if time == self.last_time:
            return

        self.last_time = time

        with key.renderer() as renderer:
            renderer.clear()
            renderer.text(
                (48, 48),
                time,
                anchor="mm",
                font=self.config.font,
                color=self.config.color,
            )

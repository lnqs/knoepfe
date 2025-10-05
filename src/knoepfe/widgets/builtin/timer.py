import time
from datetime import timedelta

from pydantic import Field

from ...config.widget import WidgetConfig
from ...core.key import Key
from ...plugins.context import PluginContext
from ..base import Widget


class TimerConfig(WidgetConfig):
    """Configuration for Timer widget."""

    icon: str = Field(
        default="\ue425", description="Icon to display when timer is idle (unicode character or codepoint)"
    )
    running_color: str | None = Field(
        default=None, description="Text color when timer is running (defaults to base color)"
    )
    stopped_color: str = Field(default="red", description="Text color when timer is stopped")


class Timer(Widget[TimerConfig, PluginContext]):
    name = "Timer"
    description = "Start/stop timer with elapsed time display"

    def __init__(self, config: TimerConfig, context: PluginContext) -> None:
        super().__init__(config, context)
        self.start: float | None = None
        self.stop: float | None = None

    async def deactivate(self) -> None:
        self.stop_periodic_update()
        self.start = None
        self.stop = None
        self.release_wake_lock()

    async def update(self, key: Key) -> None:
        with key.renderer() as renderer:
            renderer.clear()
            if self.start and not self.stop:
                # Timer is running
                elapsed = f"{timedelta(seconds=time.monotonic() - self.start)}".rsplit(".", 1)[0]
                renderer.text(
                    (48, 48),
                    elapsed,
                    anchor="mm",
                    font=self.config.font,
                    color=self.config.running_color or self.config.color,
                )
            elif self.start and self.stop:
                # Timer is stopped
                elapsed = f"{timedelta(seconds=self.stop - self.start)}".rsplit(".", 1)[0]
                renderer.text(
                    (48, 48),
                    elapsed,
                    anchor="mm",
                    font=self.config.font,
                    color=self.config.stopped_color,
                )
            else:
                # Timer is idle
                renderer.icon(self.config.icon, size=86, color=self.config.color)

    async def triggered(self, long_press: bool = False) -> None:
        if not self.start:
            self.start = time.monotonic()
            self.request_periodic_update(1.0)
            self.request_update()
            self.acquire_wake_lock()
        elif self.start and not self.stop:
            self.stop = time.monotonic()
            self.stop_periodic_update()
            self.request_update()
            self.release_wake_lock()
        else:
            self.stop_periodic_update()
            self.start = None
            self.stop = None
            self.request_update()

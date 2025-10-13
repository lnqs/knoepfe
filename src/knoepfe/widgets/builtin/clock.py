from datetime import datetime

from pydantic import Field

from ...config.base import BaseConfig
from ...config.widget import WidgetConfig
from ...core.key import Key
from ...plugins.plugin import Plugin
from ..base import Widget


class ClockSegment(BaseConfig):
    """Configuration for a single clock segment."""

    format: str = Field(..., description="Time format string (Python strftime format)")
    x: int = Field(..., description="X position of segment")
    y: int = Field(..., description="Y position of segment")
    width: int = Field(..., description="Width of segment area")
    height: int = Field(..., description="Height of segment area")
    font: str | None = Field(default=None, description="Font for this segment (inherits from widget if None)")
    color: str | None = Field(default=None, description="Color for this segment (inherits from widget if None)")
    anchor: str = Field(default="mm", description="Text anchor point (e.g., 'mm' for middle-middle)")


class ClockConfig(WidgetConfig):
    """Configuration for Clock widget."""

    segments: list[ClockSegment] = Field(
        default_factory=lambda: [ClockSegment(format="%H:%M", x=0, y=0, width=96, height=96)],
        description="List of clock segments to render",
    )
    interval: float = Field(default=1.0, description="Update interval in seconds")


class Clock(Widget[ClockConfig, Plugin]):
    """Display current time with flexible segment-based layout."""

    name = "Clock"

    def __init__(self, config: ClockConfig, plugin: Plugin) -> None:
        super().__init__(config, plugin)
        self.last_time = ""

    async def activate(self) -> None:
        self.request_periodic_update(self.config.interval)

    async def deactivate(self) -> None:
        self.last_time = ""

    def _calculate_font_size(self, text: str, font: str | None, width: int, height: int, renderer) -> int:
        """Calculate the largest font size that fits within the given bounds."""
        # Binary search for optimal font size
        min_size, max_size = 8, 72
        best_size = min_size

        while min_size <= max_size:
            mid_size = (min_size + max_size) // 2
            text_width, text_height = renderer.measure_text(text, font=font, size=mid_size)

            if text_width <= width and text_height <= height:
                best_size = mid_size
                min_size = mid_size + 1
            else:
                max_size = mid_size - 1

        return best_size

    async def update(self, key: Key) -> None:
        now = datetime.now()

        # Generate current time string for all segments to check if update needed
        current_time = "".join(now.strftime(seg.format) for seg in self.config.segments)

        if current_time == self.last_time:
            return

        self.last_time = current_time

        with key.renderer() as renderer:
            renderer.clear()

            for segment in self.config.segments:
                # Get text for this segment
                text = now.strftime(segment.format)

                # Determine font and color (segment-specific or widget default)
                font = segment.font or self.config.font
                color = segment.color or self.config.color

                # Calculate optimal font size to fit within segment bounds
                font_size = self._calculate_font_size(text, font, segment.width, segment.height, renderer)

                # Calculate center position of segment
                center_x = segment.x + segment.width // 2
                center_y = segment.y + segment.height // 2

                # Render text at segment position
                renderer.text(
                    (center_x, center_y),
                    text,
                    font=font,
                    size=font_size,
                    color=color,
                    anchor=segment.anchor,
                )

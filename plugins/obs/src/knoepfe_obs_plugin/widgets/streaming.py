from asyncio import sleep

from knoepfe.config.widget import WidgetConfig
from knoepfe.rendering import Renderer
from knoepfe.widgets.actions import UpdateResult
from pydantic import Field

from ..plugin import OBSPlugin
from .base import OBSWidget


class StreamingConfig(WidgetConfig):
    """Configuration for Streaming widget."""

    streaming_icon: str = Field(
        default="󰄘",  # nf-md-cast
        description="Icon when streaming (unicode character or codepoint)",
    )
    stopped_icon: str = Field(
        default="󰄘",  # nf-md-cast
        description="Icon when stopped (unicode character or codepoint)",
    )
    loading_icon: str = Field(
        default="󰔟",  # nf-md-timer_sand
        description="Icon when loading (unicode character or codepoint)",
    )
    streaming_color: str = Field(default="red", description="Icon/text color when streaming")
    stopped_color: str | None = Field(default=None, description="Icon color when stopped (defaults to base color)")


class Streaming(OBSWidget[StreamingConfig]):
    """Start/stop OBS streaming with timecode display."""

    name = "OBSStreaming"

    relevant_events = [
        "ConnectionEstablished",
        "ConnectionLost",
        "StreamStateChanged",
    ]

    def __init__(self, config: StreamingConfig, plugin: OBSPlugin) -> None:
        super().__init__(config, plugin)
        self.streaming = False
        self.show_help = False
        self.show_loading = False

    async def update(self, renderer: Renderer) -> UpdateResult:
        if self.plugin.obs.streaming != self.streaming:
            if self.plugin.obs.streaming:
                self.request_periodic_update(1.0)
            else:
                self.stop_periodic_update()
            self.streaming = self.plugin.obs.streaming

        renderer.clear()
        if self.show_loading:
            self.show_loading = False
            renderer.icon(self.config.loading_icon, size=86)
        elif not self.plugin.obs.connected:
            renderer.icon(self.config.stopped_icon, size=86, color=self.plugin.disconnected_color)
        elif self.show_help:
            renderer.text_wrapped("long press\nto toggle", size=16)
        elif self.plugin.obs.streaming:
            timecode = (await self.plugin.obs.get_streaming_timecode() or "").rsplit(".", 1)[0]
            renderer.icon_and_text(
                self.config.streaming_icon,
                timecode,
                icon_size=64,
                text_size=16,
                icon_color=self.config.streaming_color,
                text_color=self.config.streaming_color,
            )
        else:
            renderer.icon(self.config.stopped_icon, size=86, color=self.config.stopped_color or self.config.color)

        return UpdateResult.UPDATED

    async def triggered(self, long_press: bool = False) -> None:
        if long_press:
            if not self.plugin.obs.connected:
                return

            if self.plugin.obs.streaming:
                await self.plugin.obs.stop_streaming()
            else:
                await self.plugin.obs.start_streaming()

            self.show_loading = True
            self.request_update()
        else:
            self.show_help = True
            self.request_update()
            await sleep(1.0)
            self.show_help = False
            self.request_update()

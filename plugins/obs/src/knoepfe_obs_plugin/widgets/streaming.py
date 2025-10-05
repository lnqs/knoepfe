from asyncio import sleep

from knoepfe.config.widget import WidgetConfig
from knoepfe.core.key import Key
from pydantic import Field

from ..context import OBSPluginContext
from .base import OBSWidget


class StreamingConfig(WidgetConfig):
    """Configuration for Streaming widget."""

    streaming_icon: str = Field(default="\ue0e2", description="Icon when streaming (unicode character or codepoint)")
    stopped_icon: str = Field(default="\ue0e3", description="Icon when stopped (unicode character or codepoint)")
    loading_icon: str = Field(default="\ue5d3", description="Icon when loading (unicode character or codepoint)")
    streaming_color: str = Field(default="red", description="Icon/text color when streaming")
    stopped_color: str | None = Field(default=None, description="Icon color when stopped (defaults to base color)")


class Streaming(OBSWidget[StreamingConfig]):
    name = "OBSStreaming"
    description = "Start/stop OBS streaming with timecode display"

    relevant_events = [
        "ConnectionEstablished",
        "ConnectionLost",
        "StreamStateChanged",
    ]

    def __init__(self, config: StreamingConfig, context: OBSPluginContext) -> None:
        super().__init__(config, context)
        self.streaming = False
        self.show_help = False
        self.show_loading = False

    async def update(self, key: Key) -> None:
        if self.context.obs.streaming != self.streaming:
            if self.context.obs.streaming:
                self.request_periodic_update(1.0)
            else:
                self.stop_periodic_update()
            self.streaming = self.context.obs.streaming

        with key.renderer() as renderer:
            renderer.clear()
            if self.show_loading:
                self.show_loading = False
                renderer.icon(self.config.loading_icon, size=86)
            elif not self.context.obs.connected:
                renderer.icon(self.config.stopped_icon, size=86, color=self.context.disconnected_color)
            elif self.show_help:
                renderer.text_wrapped("long press\nto toggle", size=16)
            elif self.context.obs.streaming:
                timecode = (await self.context.obs.get_streaming_timecode() or "").rsplit(".", 1)[0]
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

    async def triggered(self, long_press: bool = False) -> None:
        if long_press:
            if not self.context.obs.connected:
                return

            if self.context.obs.streaming:
                await self.context.obs.stop_streaming()
            else:
                await self.context.obs.start_streaming()

            self.show_loading = True
            self.request_update()
        else:
            self.show_help = True
            self.request_update()
            await sleep(1.0)
            self.show_help = False
            self.request_update()

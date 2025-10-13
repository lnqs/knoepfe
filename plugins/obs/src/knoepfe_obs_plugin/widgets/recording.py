from asyncio import sleep

from knoepfe.config.widget import WidgetConfig
from knoepfe.rendering import Renderer
from knoepfe.widgets.actions import UpdateResult
from pydantic import Field

from ..plugin import OBSPlugin
from .base import OBSWidget


class RecordingConfig(WidgetConfig):
    """Configuration for Recording widget."""

    recording_icon: str = Field(
        default="󰕧",  # nf-md-video
        description="Icon when recording (unicode character or codepoint)",
    )
    stopped_icon: str = Field(
        default="󰕨",  # nf-md-video_off
        description="Icon when stopped (unicode character or codepoint)",
    )
    loading_icon: str = Field(
        default="󰔟",  # nf-md-timer_sand
        description="Icon when loading (unicode character or codepoint)",
    )
    recording_color: str = Field(default="red", description="Icon/text color when recording")
    stopped_color: str | None = Field(default=None, description="Icon color when stopped (defaults to base color)")


class Recording(OBSWidget[RecordingConfig]):
    """Start/stop OBS recording with timecode display."""

    name = "OBSRecording"

    relevant_events = [
        "ConnectionEstablished",
        "ConnectionLost",
        "RecordStateChanged",
    ]

    def __init__(self, config: RecordingConfig, plugin: OBSPlugin) -> None:
        super().__init__(config, plugin)
        self.recording = False
        self.show_help = False
        self.show_loading = False

    async def update(self, renderer: Renderer) -> UpdateResult:
        if self.plugin.obs.recording != self.recording:
            if self.plugin.obs.recording:
                self.request_periodic_update(1.0)
            else:
                self.stop_periodic_update()
            self.recording = self.plugin.obs.recording

        renderer.clear()
        if self.show_loading:
            self.show_loading = False
            renderer.icon(self.config.loading_icon, size=86)
        elif not self.plugin.obs.connected:
            renderer.icon(self.config.stopped_icon, size=86, color=self.plugin.disconnected_color)
        elif self.show_help:
            renderer.text_wrapped("long press\nto toggle", size=16)
        elif self.plugin.obs.recording:
            timecode = (await self.plugin.obs.get_recording_timecode() or "").rsplit(".", 1)[0]
            renderer.icon_and_text(
                self.config.recording_icon,
                timecode,
                icon_size=64,
                text_size=16,
                icon_color=self.config.recording_color,
                text_color=self.config.recording_color,
            )
        else:
            renderer.icon(self.config.stopped_icon, size=86, color=self.config.stopped_color or self.config.color)

        return UpdateResult.UPDATED

    async def triggered(self, long_press: bool = False) -> None:
        if long_press:
            if not self.plugin.obs.connected:
                return

            if self.plugin.obs.recording:
                await self.plugin.obs.stop_recording()
            else:
                await self.plugin.obs.start_recording()

            self.show_loading = True
            self.request_update()
        else:
            self.show_help = True
            self.request_update()
            await sleep(1.0)
            self.show_help = False
            self.request_update()

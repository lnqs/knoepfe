from asyncio import sleep
from typing import Any

from knoepfe.key import Key
from schema import Schema

from .base import OBSWidget
from .state import OBSPluginState


class Recording(OBSWidget):
    name = "OBSRecording"

    relevant_events = [
        "ConnectionEstablished",
        "ConnectionLost",
        "RecordStateChanged",
    ]

    def __init__(self, widget_config: dict[str, Any], global_config: dict[str, Any], state: OBSPluginState) -> None:
        super().__init__(widget_config, global_config, state)
        self.recording = False
        self.show_help = False
        self.show_loading = False

    async def update(self, key: Key) -> None:
        if self.obs.recording != self.recording:
            if self.obs.recording:
                self.request_periodic_update(1.0)
            else:
                self.stop_periodic_update()
            self.recording = self.obs.recording

        with key.renderer() as renderer:
            renderer.clear()
            if self.show_loading:
                self.show_loading = False
                renderer.icon("\ue5d3", size=86)  # more_horiz (e5d3)
            elif not self.obs.connected:
                renderer.icon("\ue04c", size=86, color="#202020")  # videocam_off (e04c)
            elif self.show_help:
                renderer.text_wrapped("long press\nto toggle", size=16)
            elif self.obs.recording:
                timecode = (await self.obs.get_recording_timecode() or "").rsplit(".", 1)[0]
                renderer.icon_and_text(
                    "\ue04b",  # videocam (e04b)
                    timecode,
                    icon_size=64,
                    text_size=16,
                    icon_color="red",
                    text_color="red",
                )
            else:
                renderer.icon("\ue04c", size=86)  # videocam_off (e04c)

    async def triggered(self, long_press: bool = False) -> None:
        if long_press:
            if not self.obs.connected:
                return

            if self.obs.recording:
                await self.obs.stop_recording()
            else:
                await self.obs.start_recording()

            self.show_loading = True
            self.request_update()
        else:
            self.show_help = True
            self.request_update()
            await sleep(1.0)
            self.show_help = False
            self.request_update()

    @classmethod
    def get_config_schema(cls) -> Schema:
        schema = Schema({})
        return cls.add_defaults(schema)

from asyncio import sleep
from typing import Any

from knoepfe.key import Key
from schema import Schema

from .base import OBSWidget
from .state import OBSPluginState


class Streaming(OBSWidget):
    name = "OBSStreaming"

    relevant_events = [
        "ConnectionEstablished",
        "ConnectionLost",
        "StreamStateChanged",
    ]

    def __init__(self, widget_config: dict[str, Any], global_config: dict[str, Any], state: OBSPluginState) -> None:
        super().__init__(widget_config, global_config, state)
        self.streaming = False
        self.show_help = False
        self.show_loading = False

    async def update(self, key: Key) -> None:
        if self.obs.streaming != self.streaming:
            if self.obs.streaming:
                self.request_periodic_update(1.0)
            else:
                self.stop_periodic_update()
            self.streaming = self.obs.streaming

        with key.renderer() as renderer:
            renderer.clear()
            if self.show_loading:
                self.show_loading = False
                renderer.icon("\ue5d3", size=86)  # more_horiz (e5d3)
            elif not self.obs.connected:
                renderer.icon("\ue0e3", size=86, color="#202020")  # stop_screen_share (e0e3)
            elif self.show_help:
                renderer.text_wrapped("long press\nto toggle", size=16)
            elif self.obs.streaming:
                timecode = (await self.obs.get_streaming_timecode() or "").rsplit(".", 1)[0]
                renderer.icon_and_text(
                    "\ue0e2",  # screen_share (e0e2)
                    timecode,
                    icon_size=64,
                    text_size=16,
                    icon_color="red",
                    text_color="red",
                )
            else:
                renderer.icon("\ue0e3", size=86)  # stop_screen_share (e0e3)

    async def triggered(self, long_press: bool = False) -> None:
        if long_press:
            if not self.obs.connected:
                return

            if self.obs.streaming:
                await self.obs.stop_streaming()
            else:
                await self.obs.start_streaming()

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

from asyncio import sleep
from typing import Any, Dict

from schema import Schema

from knoepfe.key import Key
from knoepfe.widgets.obs.base import OBSWidget
from knoepfe.widgets.obs.connector import obs


class Recording(OBSWidget):
    relevant_events = [
        "ConnectionEstablished",
        "ConnectionLost",
        "RecordingStarted",
        "RecordingStopped",
        "StreamingStatus",
    ]

    def __init__(
        self, widget_config: Dict[str, Any], global_config: Dict[str, Any]
    ) -> None:
        super().__init__(widget_config, global_config)
        self.show_help = False
        self.show_loading = False

    async def update(self, key: Key) -> None:
        with key.renderer() as renderer:
            if self.show_loading:
                self.show_loading = False
                renderer.icon("more_horiz")
            elif not obs.connected:
                renderer.icon("videocam_off", color="#202020")
            elif self.show_help:
                renderer.text("long press\nto toggle", size=16)
            elif obs.recording:
                timecode = (obs.recording_timecode or "").rsplit(".", 1)[0]
                renderer.icon_and_text("videocam", timecode, color="red")
            else:
                renderer.icon("videocam_off")

    async def triggered(self, long_press: bool = False) -> None:
        if long_press:
            if obs.recording:
                await obs.stop_recording()
            else:
                await obs.start_recording()

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

from asyncio import sleep
from typing import Any, Dict

from schema import Schema

from deckconnect.key import Key
from deckconnect.widgets.obs.base import OBSWidget
from deckconnect.widgets.obs.connector import obs


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

    async def update(self, key: Key) -> None:
        with key.renderer() as renderer:
            if not obs.connected:
                renderer.icon("videocam_off", color="#202020")
            elif self.show_help:
                renderer.text("long press\nto toggle", size=16)
            elif obs.recording:
                assert obs.recording_timecode
                timecode = obs.recording_timecode.rsplit(".", 1)[0]
                renderer.icon_and_text("videocam", timecode, color="red")
            else:
                renderer.icon("videocam_off")

    async def triggered(self, long_press: bool = False) -> None:
        if long_press:
            if obs.recording:
                await obs.stop_recording()
            else:
                await obs.start_recording()
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

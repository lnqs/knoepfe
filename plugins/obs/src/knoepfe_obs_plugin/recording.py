from asyncio import sleep
from typing import Any

from knoepfe.key import Key
from schema import Schema

from knoepfe_obs_plugin.base import OBSWidget
from knoepfe_obs_plugin.connector import obs


class Recording(OBSWidget):
    relevant_events = [
        "ConnectionEstablished",
        "ConnectionLost",
        "RecordStateChanged",
    ]

    def __init__(self, widget_config: dict[str, Any], global_config: dict[str, Any]) -> None:
        super().__init__(widget_config, global_config)
        self.recording = False
        self.show_help = False
        self.show_loading = False

    async def update(self, key: Key) -> None:
        if obs.recording != self.recording:
            if obs.recording:
                self.request_periodic_update(1.0)
            else:
                self.stop_periodic_update()
            self.recording = obs.recording

        with key.renderer() as renderer:
            if self.show_loading:
                self.show_loading = False
                renderer.text("\ue5d3", font="Material Icons", size=86, anchor="mm")  # more_horiz (e5d3)
            elif not obs.connected:
                renderer.text(
                    "\ue04c", font="Material Icons", size=86, color="#202020", anchor="mm"
                )  # videocam_off (e04c)
            elif self.show_help:
                renderer.text("long press\nto toggle", size=16)
            elif obs.recording:
                timecode = (await obs.get_recording_timecode() or "").rsplit(".", 1)[0]
                renderer.text_at(
                    (48, 32), "\ue04b", font="Material Icons", size=64, color="red", anchor="mm"
                )  # videocam (e04b)
                renderer.text_at((48, 80), timecode, size=16, color="red", anchor="mt")
            else:
                renderer.text("\ue04c", font="Material Icons", size=86, anchor="mm")  # videocam_off (e04c)

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

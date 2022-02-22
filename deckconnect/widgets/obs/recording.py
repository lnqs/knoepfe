from asyncio import Task, get_event_loop, sleep
from typing import Any, Dict

from schema import Schema

from deckconnect.key import Key
from deckconnect.widgets.base import Widget
from deckconnect.widgets.obs.connector import obs


class Recording(Widget):
    def __init__(
        self, widget_config: Dict[str, Any], global_config: Dict[str, Any]
    ) -> None:
        super().__init__(widget_config, global_config)
        self.listening_task: Task[None] | None = None
        self.show_help = False

    async def activate(self) -> None:
        await obs.connect(self.global_config.get("deckconnect.widgets.obs.config", {}))

        if not self.listening_task:
            self.listening_task = get_event_loop().create_task(self.listener())

    async def deactivate(self) -> None:
        if self.listening_task:
            self.listening_task.cancel()
            self.listening_task = None

    async def listener(self) -> None:
        async for event in obs.listen():
            if event in [
                "ConnectionEstablished",
                "ConnectionLost",
                "RecordingStarted",
                "RecordingStopped",
                "StreamingStatus",
            ]:
                self.request_update()

    async def update(self, key: Key) -> None:
        with key.renderer() as renderer:
            if not obs.connected:
                renderer.icon(
                    "videocam_off", font_size=400, valign="top", color="#202020"
                )
                renderer.text(
                    "disconnected",
                    font_size=80,
                    y=-32,
                    valign="bottom",
                    color="#202020",
                )
            elif self.show_help:
                renderer.text("long press\nto toggle")
            elif obs.recording:
                assert obs.recording_timecode
                renderer.icon("videocam", font_size=400, valign="top", color="red")
                renderer.text(
                    obs.recording_timecode.rsplit(".", 1)[0],
                    font_size=80,
                    y=-32,
                    valign="bottom",
                    color="red",
                )
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

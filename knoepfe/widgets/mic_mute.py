from asyncio import Task, get_event_loop
from typing import Any, Dict

from pulsectl import PulseEventTypeEnum
from pulsectl_asyncio import PulseAsync
from schema import Optional, Schema

from knoepfe.key import Key
from knoepfe.log import error
from knoepfe.widgets.base import Widget


class MicMute(Widget):
    def __init__(
        self, widget_config: Dict[str, Any], global_config: Dict[str, Any]
    ) -> None:
        super().__init__(widget_config, global_config)
        self.pulse: None | PulseAsync = None
        self.event_listener: Task[None] | None = None

    async def activate(self) -> None:
        if not self.pulse:
            self.pulse = PulseAsync("MicMuteControl")
            await self.pulse.connect()
        if not self.event_listener:
            loop = get_event_loop()
            self.event_listener = loop.create_task(self.listen())

    async def deactivate(self) -> None:
        if self.event_listener:
            self.event_listener.cancel()
            self.event_listener = None
        if self.pulse:
            self.pulse.disconnect()
            self.pulse = None

    async def update(self, key: Key) -> None:
        source = await self.get_source()
        with key.renderer() as renderer:
            if source.mute:
                renderer.icon("mic_off")
            else:
                renderer.icon("mic", color="red")

    async def triggered(self, long_press: bool = False) -> None:
        assert self.pulse

        source = await self.get_source()
        await self.pulse.source_mute(source.index, mute=not source.mute)

    async def get_source(self) -> Any:
        assert self.pulse

        source = self.config.get("source")
        if not source:
            server_info = await self.pulse.server_info()
            source = server_info.default_source_name

        sources = await self.pulse.source_list()
        for s in sources:
            if s.name == source:
                return s

        error(f"Source {source} not found")

    async def listen(self) -> None:
        assert self.pulse

        async for event in self.pulse.subscribe_events("source"):
            if event.t == PulseEventTypeEnum.change:
                self.request_update()

    @classmethod
    def get_config_schema(cls) -> Schema:
        schema = Schema({Optional("source"): str})
        return cls.add_defaults(schema)

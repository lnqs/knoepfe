from asyncio import Task, get_event_loop
from typing import Generic, TypeVar

from knoepfe.config.widget import WidgetConfig
from knoepfe.widgets import Widget

from ..context import OBSPluginContext

TConfig = TypeVar("TConfig", bound=WidgetConfig)


class OBSWidget(Widget[TConfig, OBSPluginContext], Generic[TConfig]):
    """Base class for OBS widgets with typed configuration."""

    relevant_events: list[str] = []

    def __init__(self, config: TConfig, context: OBSPluginContext) -> None:
        super().__init__(config, context)
        self.listening_task: Task[None] | None = None

    async def activate(self) -> None:
        await self.context.obs.connect()

        if not self.listening_task:
            self.listening_task = get_event_loop().create_task(self.listener())

    async def deactivate(self) -> None:
        if self.listening_task:
            self.listening_task.cancel()
            self.listening_task = None

    async def listener(self) -> None:
        async for event in self.context.obs.listen():
            if event == "ConnectionEstablished":
                self.acquire_wake_lock()
            elif event == "ConnectionLost":
                self.release_wake_lock()

            if event in self.relevant_events:
                self.request_update()

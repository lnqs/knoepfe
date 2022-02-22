from asyncio import Task, get_event_loop
from typing import Any, Dict, List

from knoepfe.widgets.base import Widget
from knoepfe.widgets.obs.connector import obs


class OBSWidget(Widget):
    relevant_events: List[str] = []

    def __init__(
        self, widget_config: Dict[str, Any], global_config: Dict[str, Any]
    ) -> None:
        super().__init__(widget_config, global_config)
        self.listening_task: Task[None] | None = None

    async def activate(self) -> None:
        await obs.connect(self.global_config.get("knoepfe.widgets.obs.config", {}))

        if not self.listening_task:
            self.listening_task = get_event_loop().create_task(self.listener())

    async def deactivate(self) -> None:
        if self.listening_task:
            self.listening_task.cancel()
            self.listening_task = None

    async def listener(self) -> None:
        async for event in obs.listen():
            if event == "ConnectionEstablished":
                self.acquire_wake_lock()
            elif event == "ConnectionLost":
                self.release_wake_lock()

            if event in self.relevant_events:
                self.request_update()

from asyncio import Task, get_event_loop
from typing import Any

from knoepfe.widgets.base import Widget

# Import the state directly
from .state import OBSPluginState


class OBSWidget(Widget[OBSPluginState]):
    relevant_events: list[str] = []

    def __init__(self, widget_config: dict[str, Any], global_config: dict[str, Any], state: OBSPluginState) -> None:
        super().__init__(widget_config, global_config, state)
        self.listening_task: Task[None] | None = None

    @property
    def obs(self):
        """Get the shared OBS connector from state."""
        return self.state.obs

    async def activate(self) -> None:
        await self.obs.connect(self.global_config.get("obs", {}))

        if not self.listening_task:
            self.listening_task = get_event_loop().create_task(self.listener())

    async def deactivate(self) -> None:
        if self.listening_task:
            self.listening_task.cancel()
            self.listening_task = None

    async def listener(self) -> None:
        async for event in self.obs.listen():
            if event == "ConnectionEstablished":
                self.acquire_wake_lock()
            elif event == "ConnectionLost":
                self.release_wake_lock()

            if event in self.relevant_events:
                self.request_update()

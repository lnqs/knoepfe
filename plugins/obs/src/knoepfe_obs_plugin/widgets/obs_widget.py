from typing import Generic, TypeVar

from knoepfe.config.widget import WidgetConfig
from knoepfe.widgets import Widget

from ..plugin import OBSPlugin

TConfig = TypeVar("TConfig", bound=WidgetConfig)

# Task name constants
TASK_EVENT_LISTENER = "event_listener"


class OBSWidget(Widget[TConfig, OBSPlugin], Generic[TConfig]):
    """Base class for OBS widgets with typed configuration."""

    relevant_events: list[str] = []

    async def activate(self) -> None:
        """Start event listener.

        The OBS connection is managed by the plugin instance and is
        established when the first widget activates.
        """
        self.tasks.start_task(TASK_EVENT_LISTENER, self.listener())

    async def listener(self) -> None:
        async for event in self.plugin.obs.listen():
            if event == "ConnectionEstablished":
                self.acquire_wake_lock()
            elif event == "ConnectionLost":
                self.release_wake_lock()

            if event in self.relevant_events:
                self.request_update()

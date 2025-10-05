"""Base class for audio widgets with shared PulseAudio connection."""

from typing import Any, Generic, TypeVar

from knoepfe.config.widget import WidgetConfig
from knoepfe.widgets import Widget

from .context import AudioPluginContext

TConfig = TypeVar("TConfig", bound=WidgetConfig)

# Task name constants
TASK_EVENT_LISTENER = "event_listener"


class AudioWidget(Widget[TConfig, AudioPluginContext], Generic[TConfig]):
    """Base class for audio widgets with shared PulseAudio connection.

    Subclasses should define `relevant_events` with event types they care about.
    """

    relevant_events: list[str] = []

    @property
    def pulse(self):
        """Get the shared PulseAudio connector from context."""
        return self.context.pulse

    async def activate(self) -> None:
        """Connect to PulseAudio and start event listener."""
        await self.pulse.connect()
        self.tasks.start_task(TASK_EVENT_LISTENER, self.listener())

    async def listener(self) -> None:
        """Listen for PulseAudio events and request updates when relevant."""
        async for event in self.pulse.listen():
            event_type = event.get("type")

            if event_type == "ConnectionEstablished":
                self.acquire_wake_lock()
            elif event_type == "ConnectionLost":
                self.release_wake_lock()

            if event_type in self.relevant_events:
                self.request_update()

    async def get_source(self, source_name: str | None = None) -> Any:
        """Get a PulseAudio source with fallback logic.

        Priority: parameter > widget config > plugin config > system default
        """
        # Use explicit parameter if provided
        if not source_name:
            # Try widget config source
            if hasattr(self.config, "source"):
                source_name = self.config.source  # type: ignore

            # Fall back to plugin default
            if not source_name:
                source_name = self.context.default_source

        # Use system default if still no source specified
        if not source_name:
            return await self.pulse.get_default_source()

        return await self.pulse.get_source(source_name)

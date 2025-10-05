"""PulseAudio connector for managing shared connection across audio widgets."""

import logging
from asyncio import Condition
from typing import Any, AsyncIterator

from knoepfe.utils.task_manager import TaskManager
from pulsectl import PulseEventTypeEnum
from pulsectl_asyncio import PulseAsync

logger = logging.getLogger(__name__)

# Task name constants
TASK_EVENT_WATCHER = "pulse_event_watcher"


class PulseAudioConnector:
    """Manages a shared PulseAudio connection for all audio widgets.

    This connector maintains a single connection to PulseAudio and distributes
    events to all listening widgets. It handles automatic reconnection and
    provides a clean interface for audio operations.

    Attributes:
        tasks: TaskManager for managing background tasks.
        pulse: The PulseAsync connection instance.
        connected: Whether currently connected to PulseAudio.
        last_event: The most recent PulseAudio event received.
        event_condition: Condition variable for event notification.
    """

    def __init__(self, tasks: TaskManager) -> None:
        """Initialize the PulseAudio connector.

        Args:
            tasks: TaskManager from plugin context for managing background tasks.
        """
        self.tasks = tasks
        self.pulse: PulseAsync | None = None
        self._connected = False

        self.last_event: Any = None
        self.event_condition = Condition()

    async def connect(self) -> None:
        """Connect to PulseAudio if not already connected.

        This method is idempotent - calling it multiple times will only
        create one connection. Starts the event watcher task.
        """
        if self.tasks.is_running(TASK_EVENT_WATCHER):
            return

        if not self.pulse:
            self.pulse = PulseAsync("KnoepfeAudioPlugin")
            try:
                await self.pulse.connect()
                self._connected = True
                logger.debug("Connected to PulseAudio")
                await self._handle_event({"type": "ConnectionEstablished"})
            except Exception as e:
                logger.error(f"Failed to connect to PulseAudio: {e}")
                self._connected = False
                self.pulse = None
                return

        self.tasks.start_task(TASK_EVENT_WATCHER, self._watch_events())

    async def disconnect(self) -> None:
        """Disconnect from PulseAudio and clean up resources."""
        self.tasks.stop_task(TASK_EVENT_WATCHER)

        if self.pulse:
            self.pulse.disconnect()
            self.pulse = None
            self._connected = False
            logger.debug("Disconnected from PulseAudio")
            await self._handle_event({"type": "ConnectionLost"})

    @property
    def connected(self) -> bool:
        """Check if currently connected to PulseAudio."""
        return self._connected and self.pulse is not None

    async def listen(self) -> AsyncIterator[dict[str, Any]]:
        """Listen for PulseAudio events.

        Yields:
            Event dictionaries containing event type and data.
        """
        while True:
            async with self.event_condition:
                await self.event_condition.wait()
                assert self.last_event
                event = self.last_event
            yield event

    async def get_source(self, source_name: str) -> Any:
        """Get a PulseAudio source by name.

        Args:
            source_name: The name of the source to retrieve.

        Returns:
            The PulseAudio source object, or None if not found.

        Raises:
            RuntimeError: If not connected to PulseAudio.
        """
        if not self.pulse:
            raise RuntimeError("Not connected to PulseAudio")

        sources = await self.pulse.source_list()
        for source in sources:
            if source.name == source_name:
                return source

        logger.error(f"Source {source_name} not found")
        return None

    async def get_default_source(self) -> Any:
        """Get the system default PulseAudio source.

        Returns:
            The default source object.

        Raises:
            RuntimeError: If not connected to PulseAudio.
        """
        if not self.pulse:
            raise RuntimeError("Not connected to PulseAudio")

        server_info = await self.pulse.server_info()
        default_source_name = server_info.default_source_name  # pyright: ignore[reportAttributeAccessIssue]

        sources = await self.pulse.source_list()
        for source in sources:
            if source.name == default_source_name:
                return source

        logger.error(f"Default source {default_source_name} not found")
        return None

    async def source_mute(self, index: int, mute: bool) -> None:
        """Set the mute state of a source.

        Args:
            index: The index of the source to mute/unmute.
            mute: True to mute, False to unmute.

        Raises:
            RuntimeError: If not connected to PulseAudio.
        """
        if not self.pulse:
            raise RuntimeError("Not connected to PulseAudio")

        await self.pulse.source_mute(index, mute=mute)

    async def _watch_events(self) -> None:
        """Watch for PulseAudio events and distribute them to listeners.

        This runs as a background task and monitors the PulseAudio event stream.
        """
        if not self.pulse:
            return

        try:
            async for event in self.pulse.subscribe_events("source"):
                if event.t == PulseEventTypeEnum.change:  # pyright: ignore[reportAttributeAccessIssue]
                    await self._handle_event({"type": "SourceChanged", "data": event})
        except Exception as e:
            logger.error(f"Error in PulseAudio event watcher: {e}")
            self._connected = False
            await self._handle_event({"type": "ConnectionLost"})

    async def _handle_event(self, event: dict[str, Any]) -> None:
        """Handle a PulseAudio event and notify all listeners.

        Args:
            event: The event dictionary to handle.
        """
        logger.debug(f"PulseAudio event received: {event}")

        async with self.event_condition:
            self.last_event = event
            self.event_condition.notify_all()

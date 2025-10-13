from abc import ABC, abstractmethod
from asyncio import Event, sleep
from typing import TYPE_CHECKING, Generic, TypeVar

from ..config.widget import WidgetConfig
from ..rendering import Renderer
from ..utils.task_manager import TaskManager
from ..utils.type_utils import extract_generic_arg
from ..utils.wakelock import WakeLock
from .actions import SwitchDeckAction, UpdateResult, WidgetAction

if TYPE_CHECKING:
    from ..plugins.plugin import Plugin

TPlugin = TypeVar("TPlugin", bound="Plugin")
TConfig = TypeVar("TConfig", bound="WidgetConfig")

# Task name constants
TASK_PERIODIC_UPDATE = "periodic_update"
TASK_LONG_PRESS = "long_press"


class Widget(ABC, Generic[TConfig, TPlugin]):
    """Base widget class with strongly typed configuration.

    Widgets should specify their config type as the first generic parameter
    and their plugin instance type as the second generic parameter.
    """

    name: str

    def __init__(self, config: TConfig, plugin: TPlugin) -> None:
        """Initialize widget with typed configuration.

        Args:
            config: Validated widget configuration
            plugin: Plugin instance
        """
        self.config = config
        self.plugin = plugin

        # Runtime state
        self.update_requested_event: Event | None = None
        self.wake_lock: WakeLock | None = None
        self.holds_wait_lock = False
        self.needs_update = False

        # Task management
        self.tasks = TaskManager()

    @classmethod
    def get_config_type(cls) -> type:
        """Extract the config type from the generic parameter.

        Returns:
            The WidgetConfig subclass specified as the first type parameter

        Raises:
            TypeError: If the widget doesn't specify a valid WidgetConfig type
        """
        return extract_generic_arg(cls, WidgetConfig, 0)

    async def activate(self) -> None:  # pragma: no cover
        """Called when widget becomes active on the deck."""
        return

    async def deactivate(self) -> None:  # pragma: no cover
        """Called when widget is deactivated (e.g., deck switch)."""
        return

    @abstractmethod
    async def update(self, renderer: Renderer) -> UpdateResult:
        """Update the widget display using the provided renderer.

        Args:
            renderer: Renderer instance to draw the widget display

        Returns:
            UpdateResult.UPDATED if the widget drew to the canvas and it should be pushed to device
            UpdateResult.UNCHANGED if the widget didn't draw and the device should keep current display
        """
        pass

    async def pressed(self) -> None:
        """Called when key is pressed."""

        async def maybe_trigger_longpress() -> None:
            await sleep(1.0)
            await self.triggered(True)

        self.tasks.start_task("long_press", maybe_trigger_longpress())

    async def released(self) -> WidgetAction | None:
        """Called when key is released."""
        if self.tasks.is_running("long_press"):
            self.tasks.stop_task("long_press")
            action = await self.triggered(False)
            if action:
                return action

            if self.config.switch_deck:
                return SwitchDeckAction(self.config.switch_deck)

        return None

    async def triggered(self, long_press: bool = False) -> WidgetAction | None:
        return None

    def request_update(self) -> None:
        """Request an update for this widget.

        Sets the needs_update flag and signals the shared update event.
        This will cause the DeckManager to update this widget on the next cycle.
        """
        self.needs_update = True
        if self.update_requested_event:
            self.update_requested_event.set()

    def request_periodic_update(self, interval: float) -> None:
        """Request periodic updates at the specified interval.

        This is a convenience method that creates a background task to call
        request_update() at regular intervals. The task will be automatically
        cleaned up when the widget is deactivated.

        Args:
            interval: Time in seconds between updates
        """

        async def periodic_loop() -> None:
            while True:
                await sleep(interval)
                self.request_update()

        self.tasks.start_task("periodic_update", periodic_loop())

    def stop_periodic_update(self) -> None:
        """Stop periodic updates.

        This is a convenience method that stops the periodic update task.
        """
        self.tasks.stop_task("periodic_update")

    def acquire_wake_lock(self) -> None:
        if self.wake_lock and not self.holds_wait_lock:
            self.wake_lock.acquire()
            self.holds_wait_lock = True

    def release_wake_lock(self) -> None:
        if self.wake_lock and self.holds_wait_lock:
            self.wake_lock.release()
            self.holds_wait_lock = False

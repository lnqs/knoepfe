from abc import ABC, abstractmethod
from asyncio import Event, Task, get_event_loop, sleep
from typing import TYPE_CHECKING, Generic, TypeVar

from ..config.widget import WidgetConfig
from ..core.key import Key
from ..utils.type_utils import extract_generic_arg
from ..utils.wakelock import WakeLock
from .actions import SwitchDeckAction, WidgetAction

if TYPE_CHECKING:
    from ..plugins.context import PluginContext

TPluginContext = TypeVar("TPluginContext", bound="PluginContext")
TConfig = TypeVar("TConfig", bound=WidgetConfig)


class Widget(ABC, Generic[TConfig, TPluginContext]):
    """Base widget class with strongly typed configuration.

    Widgets should specify their config type as the first generic parameter
    and their plugin context type as the second generic parameter.
    """

    name: str
    description: str | None = None

    def __init__(self, config: TConfig, context: TPluginContext) -> None:
        """Initialize widget with typed configuration.

        Args:
            config: Validated widget configuration
            context: Plugin context container
        """
        self.config = config
        self.context = context

        # Runtime state
        self.update_requested_event: Event | None = None
        self.wake_lock: WakeLock | None = None
        self.holds_wait_lock = False
        self.needs_update = False
        self.periodic_update_task: Task[None] | None = None
        self.long_press_task: Task[None] | None = None

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
        return

    async def deactivate(self) -> None:  # pragma: no cover
        return

    @abstractmethod
    async def update(self, key: Key) -> None:
        """Update the widget display on the given key."""
        pass

    async def pressed(self) -> None:
        async def maybe_trigger_longpress() -> None:
            await sleep(1.0)
            self.long_press_task = None
            await self.triggered(True)

        self.long_press_task = get_event_loop().create_task(maybe_trigger_longpress())

    async def released(self) -> WidgetAction | None:
        if self.long_press_task:
            self.long_press_task.cancel()
            self.long_press_task = None
            action = await self.triggered(False)
            if action:
                return action

            if self.config.switch_deck:
                return SwitchDeckAction(self.config.switch_deck)

        return None

    async def triggered(self, long_press: bool = False) -> WidgetAction | None:
        return None

    def request_update(self) -> None:
        self.needs_update = True
        if self.update_requested_event:
            self.update_requested_event.set()

    def request_periodic_update(self, interval: float) -> None:
        if not self.periodic_update_task:
            loop = get_event_loop()
            self.periodic_update_task = loop.create_task(self.periodic_update_loop(interval))

    def stop_periodic_update(self) -> None:
        if self.periodic_update_task:
            self.periodic_update_task.cancel()
            self.periodic_update_task = None

    async def periodic_update_loop(self, interval: float) -> None:
        while True:
            await sleep(interval)
            self.request_update()

    def acquire_wake_lock(self) -> None:
        if self.wake_lock and not self.holds_wait_lock:
            self.wake_lock.acquire()
            self.holds_wait_lock = True

    def release_wake_lock(self) -> None:
        if self.wake_lock and self.holds_wait_lock:
            self.wake_lock.release()
            self.holds_wait_lock = False

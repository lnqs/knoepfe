from asyncio import Event, Task, get_event_loop, sleep
from typing import Any, Dict

from schema import Optional, Schema

from knoepfe.deck import SwitchDeckException
from knoepfe.key import Key
from knoepfe.wakelock import WakeLock


class Widget:
    def __init__(
        self, widget_config: Dict[str, Any], global_config: Dict[str, Any]
    ) -> None:
        self.config = widget_config
        self.global_config = global_config
        self.update_requested_event: Event | None = None
        self.wake_lock: WakeLock | None = None
        self.holds_wait_lock = False
        self.needs_update = False
        self.periodic_update_task: Task[None] | None = None
        self.long_press_task: Task[None] | None = None

    async def activate(self) -> None:  # pragma: no cover
        pass

    async def deactivate(self) -> None:  # pragma: no cover
        pass

    async def update(self, key: Key) -> None:  # pragma: no cover
        pass

    async def pressed(self) -> None:
        async def maybe_trigger_longpress() -> None:
            await sleep(1.0)
            self.long_press_task = None
            await self.triggered(True)

        self.long_press_task = get_event_loop().create_task(maybe_trigger_longpress())

    async def released(self) -> None:
        if self.long_press_task:
            self.long_press_task.cancel()
            self.long_press_task = None
            await self.triggered(False)

            if "switch_deck" in self.config:
                raise SwitchDeckException(self.config["switch_deck"])

    async def triggered(self, long_press: bool = False) -> None:
        pass

    def request_update(self) -> None:
        self.needs_update = True
        if self.update_requested_event:
            self.update_requested_event.set()

    def request_periodic_update(self, interval: float) -> None:
        if not self.periodic_update_task:
            loop = get_event_loop()
            self.periodic_update_task = loop.create_task(
                self.periodic_update_loop(interval)
            )

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

    @classmethod
    def get_config_schema(cls) -> Schema:
        return cls.add_defaults(Schema({}))

    @classmethod
    def add_defaults(cls, schema: Schema) -> Schema:
        schema.schema.update({Optional("switch_deck"): str})
        return schema

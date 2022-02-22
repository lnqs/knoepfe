import time
from datetime import timedelta
from typing import Any, Dict

from schema import Schema

from knoepfe.key import Key
from knoepfe.widgets.base import Widget


class Timer(Widget):
    def __init__(
        self, widget_config: Dict[str, Any], global_config: Dict[str, Any]
    ) -> None:
        super().__init__(widget_config, global_config)
        self.start: float | None = None
        self.stop: float | None = None

    async def deactivate(self) -> None:
        self.stop_periodic_update()
        self.start = None
        self.stop = None
        self.release_wake_lock()

    async def update(self, key: Key) -> None:
        with key.renderer() as renderer:
            if self.start and not self.stop:
                renderer.text(
                    f"{timedelta(seconds=time.monotonic() - self.start)}".rsplit(
                        ".", 1
                    )[0],
                )
            elif self.start and self.stop:
                renderer.text(
                    f"{timedelta(seconds=self.stop - self.start)}".rsplit(".", 1)[0],
                    color="red",
                )
            else:
                renderer.icon("timer")

    async def triggered(self, long_press: bool = False) -> None:
        if not self.start:
            self.start = time.monotonic()
            self.request_periodic_update(1.0)
            self.request_update()
            self.acquire_wake_lock()
        elif self.start and not self.stop:
            self.stop = time.monotonic()
            self.stop_periodic_update()
            self.request_update()
            self.release_wake_lock()
        else:
            self.stop_periodic_update()
            self.start = None
            self.stop = None
            self.request_update()

    @classmethod
    def get_config_schema(cls) -> Schema:
        schema = Schema({})
        return cls.add_defaults(schema)

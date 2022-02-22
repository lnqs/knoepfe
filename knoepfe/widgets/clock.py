from datetime import datetime
from typing import Any, Dict

from schema import Schema

from knoepfe.key import Key
from knoepfe.widgets.base import Widget


class Clock(Widget):
    def __init__(
        self, widget_config: Dict[str, Any], global_config: Dict[str, Any]
    ) -> None:
        super().__init__(widget_config, global_config)
        self.last_time = ""

    async def activate(self) -> None:
        self.request_periodic_update(1.0)

    async def deactivate(self) -> None:
        self.stop_periodic_update()
        self.last_time = ""

    async def update(self, key: Key) -> None:
        time = datetime.now().strftime(self.config["format"])
        if time != self.last_time:
            self.last_time = time

            with key.renderer() as renderer:
                renderer.text(
                    time,
                )

    @classmethod
    def get_config_schema(cls) -> Schema:
        schema = Schema({"format": str})
        return cls.add_defaults(schema)

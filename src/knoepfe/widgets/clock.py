from datetime import datetime
from typing import Any

from schema import Schema

from knoepfe.key import Key
from knoepfe.plugin_state import PluginState
from knoepfe.widgets.base import Widget


class Clock(Widget[PluginState]):
    name = "Clock"
    description = "Display current time"

    def __init__(self, widget_config: dict[str, Any], global_config: dict[str, Any], state: PluginState) -> None:
        super().__init__(widget_config, global_config, state)
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
                renderer.clear()
                renderer.text((48, 48), time, anchor="mm")

    @classmethod
    def get_config_schema(cls) -> Schema:
        schema = Schema({"format": str})
        return cls.add_defaults(schema)

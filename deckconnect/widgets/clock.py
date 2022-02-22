from datetime import datetime

from schema import Schema

from deckconnect.key import Key
from deckconnect.widgets.base import Widget


class Clock(Widget):
    async def activate(self) -> None:
        self.request_periodic_update(1.0)

    async def deactivate(self) -> None:
        self.stop_periodic_update()

    async def update(self, key: Key) -> None:
        with key.renderer() as renderer:
            renderer.text(
                datetime.now().strftime(self.config["format"]),
            )

    @classmethod
    def get_config_schema(cls) -> Schema:
        schema = Schema({"format": str})
        return cls.add_defaults(schema)

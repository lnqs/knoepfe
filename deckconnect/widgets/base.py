import time
from typing import Any, Dict

from schema import Optional, Schema

from deckconnect.deck import SwitchDeckException
from deckconnect.key import Key


class Widget:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.press_time: float | None = None

    async def update(self, key: Key) -> None:
        pass

    async def pressed(self) -> None:
        self.press_time = time.monotonic()

    async def released(self) -> None:
        long_press = (
            time.monotonic() - self.press_time >= 1.0 if self.press_time else False
        )
        self.press_time = None
        await self.triggered(long_press)

        if "switch_deck" in self.config:
            raise SwitchDeckException(self.config["switch_deck"])

    async def triggered(self, long_press: bool = False) -> None:
        pass

    @classmethod
    def get_config_schema(cls) -> Schema:
        return cls.add_defaults(Schema({}))

    @classmethod
    def add_defaults(cls, schema: Schema) -> Schema:
        schema.schema.update({Optional("switch_deck"): str})
        return schema

from schema import Schema

from knoepfe.key import Key
from knoepfe.widgets.base import Widget


class Text(Widget):
    async def update(self, key: Key) -> None:
        with key.renderer() as renderer:
            renderer.text(self.config["text"])

    @classmethod
    def get_config_schema(cls) -> Schema:
        schema = Schema({"text": str})
        return cls.add_defaults(schema)

from typing import Any

from schema import Schema

from knoepfe.key import Key
from knoepfe.plugin_state import PluginState
from knoepfe.widgets.base import Widget


class Text(Widget[PluginState]):
    name = "Text"
    description = "Display static text"

    def __init__(self, widget_config: dict[str, Any], global_config: dict[str, Any], state: PluginState) -> None:
        super().__init__(widget_config, global_config, state)

    async def update(self, key: Key) -> None:
        with key.renderer() as renderer:
            renderer.clear()
            renderer.text_wrapped(self.config["text"])

    @classmethod
    def get_config_schema(cls) -> Schema:
        schema = Schema({"text": str})
        return cls.add_defaults(schema)

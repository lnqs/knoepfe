from typing import Any

from knoepfe.key import Key
from schema import Schema

from .base import OBSWidget
from .state import OBSPluginState


class SwitchScene(OBSWidget):
    name = "OBSSwitchScene"

    relevant_events = [
        "ConnectionEstablished",
        "ConnectionLost",
        "SwitchScenes",
    ]

    def __init__(self, widget_config: dict[str, Any], global_config: dict[str, Any], state: OBSPluginState) -> None:
        super().__init__(widget_config, global_config, state)

    async def update(self, key: Key) -> None:
        color = "white"
        if not self.obs.connected:
            color = "#202020"
        elif self.obs.current_scene == self.config["scene"]:
            color = "red"

        with key.renderer() as renderer:
            renderer.clear()
            renderer.icon_and_text(
                "\ue40b",  # panorama (e40b)
                self.config["scene"],
                icon_size=64,
                text_size=16,
                icon_color=color,
                text_color=color,
            )

    async def triggered(self, long_press: bool = False) -> None:
        if self.obs.connected:
            await self.obs.set_scene(self.config["scene"])

    @classmethod
    def get_config_schema(cls) -> Schema:
        schema = Schema({"scene": str})
        return cls.add_defaults(schema)

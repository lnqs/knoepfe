from schema import Schema

from knoepfe.key import Key
from knoepfe.widgets.obs.base import OBSWidget
from knoepfe.widgets.obs.connector import obs


class SwitchScene(OBSWidget):
    relevant_events = [
        "ConnectionEstablished",
        "ConnectionLost",
        "SwitchScenes",
    ]

    async def update(self, key: Key) -> None:
        color = None
        if not obs.connected:
            color = "#202020"
        elif obs.current_scene == self.config["scene"]:
            color = "red"

        with key.renderer() as renderer:
            renderer.icon_and_text("panorama", self.config["scene"], color=color)

    async def triggered(self, long_press: bool = False) -> None:
        await obs.set_scene(self.config["scene"])

    @classmethod
    def get_config_schema(cls) -> Schema:
        schema = Schema({"scene": str})
        return cls.add_defaults(schema)

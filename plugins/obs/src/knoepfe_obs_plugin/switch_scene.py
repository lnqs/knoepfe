from knoepfe.key import Key
from schema import Schema

from knoepfe_obs_plugin.base import OBSWidget
from knoepfe_obs_plugin.connector import obs


class SwitchScene(OBSWidget):
    name = "OBSSwitchScene"

    relevant_events = [
        "ConnectionEstablished",
        "ConnectionLost",
        "SwitchScenes",
    ]

    async def update(self, key: Key) -> None:
        color = "white"
        if not obs.connected:
            color = "#202020"
        elif obs.current_scene == self.config["scene"]:
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
        if obs.connected:
            await obs.set_scene(self.config["scene"])

    @classmethod
    def get_config_schema(cls) -> Schema:
        schema = Schema({"scene": str})
        return cls.add_defaults(schema)

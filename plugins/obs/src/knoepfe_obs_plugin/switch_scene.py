from knoepfe.key import Key
from schema import Schema

from knoepfe_obs_plugin.base import OBSWidget
from knoepfe_obs_plugin.connector import obs


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
            renderer.text("\ue40b", font="Material Icons", size=64, color=color, anchor="mt")  # panorama (e40b)
            renderer.text_at((48, 80), self.config["scene"], size=16, color=color, anchor="mt")

    async def triggered(self, long_press: bool = False) -> None:
        if obs.connected:
            await obs.set_scene(self.config["scene"])

    @classmethod
    def get_config_schema(cls) -> Schema:
        schema = Schema({"scene": str})
        return cls.add_defaults(schema)

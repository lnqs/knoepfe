from knoepfe.key import Key
from schema import Schema

from knoepfe_obs_plugin.base import OBSWidget
from knoepfe_obs_plugin.connector import obs


class CurrentScene(OBSWidget):
    name = "OBSCurrentScene"

    relevant_events = [
        "ConnectionEstablished",
        "ConnectionLost",
        "CurrentProgramSceneChanged",
    ]

    async def update(self, key: Key) -> None:
        with key.renderer() as renderer:
            if obs.connected:
                # panorama icon (e40b) with text below
                renderer.text_at((48, 32), "\ue40b", font="Material Icons", size=64, anchor="mm")
                renderer.text_at((48, 80), obs.current_scene or "[none]", size=16, anchor="mt")
            else:
                # panorama icon (e40b) with text below, grayed out
                renderer.text_at((48, 32), "\ue40b", font="Material Icons", size=64, color="#202020", anchor="mm")
                renderer.text_at((48, 80), "[none]", size=16, color="#202020", anchor="mt")

    @classmethod
    def get_config_schema(cls) -> Schema:
        schema = Schema({})
        return cls.add_defaults(schema)

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
            renderer.clear()
            if obs.connected:
                # panorama icon (e40b) with text below
                renderer.icon_and_text(
                    "\ue40b",  # panorama (e40b)
                    obs.current_scene or "[none]",
                    icon_size=64,
                    text_size=16,
                )
            else:
                # panorama icon (e40b) only, grayed out (no text when disconnected)
                renderer.icon("\ue40b", size=64, color="#202020")  # panorama (e40b)

    @classmethod
    def get_config_schema(cls) -> Schema:
        schema = Schema({})
        return cls.add_defaults(schema)

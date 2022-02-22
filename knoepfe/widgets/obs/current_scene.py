from schema import Schema

from knoepfe.key import Key
from knoepfe.widgets.obs.base import OBSWidget
from knoepfe.widgets.obs.connector import obs


class CurrentScene(OBSWidget):
    relevant_events = [
        "ConnectionEstablished",
        "ConnectionLost",
        "SwitchScenes",
    ]

    async def update(self, key: Key) -> None:
        with key.renderer() as renderer:
            if obs.connected:
                renderer.icon_and_text("panorama", obs.current_scene or "[none]")
            else:
                renderer.icon_and_text("panorama", "[none]", color="#202020")

    @classmethod
    def get_config_schema(cls) -> Schema:
        schema = Schema({})
        return cls.add_defaults(schema)

from knoepfe.config.widget import WidgetConfig
from knoepfe.core.key import Key
from pydantic import Field

from ..context import OBSPluginContext
from .base import OBSWidget


class CurrentSceneConfig(WidgetConfig):
    """Configuration for CurrentScene widget."""

    icon: str = Field(default="\ue40b", description="Scene icon (unicode character or codepoint)")
    connected_color: str | None = Field(
        default=None, description="Icon/text color when connected (defaults to base color)"
    )


class CurrentScene(OBSWidget[CurrentSceneConfig]):
    name = "OBSCurrentScene"
    description = "Display currently active OBS scene"

    relevant_events = [
        "ConnectionEstablished",
        "ConnectionLost",
        "CurrentProgramSceneChanged",
    ]

    def __init__(self, config: CurrentSceneConfig, context: OBSPluginContext) -> None:
        super().__init__(config, context)

    async def update(self, key: Key) -> None:
        with key.renderer() as renderer:
            renderer.clear()
            if self.context.obs.connected:
                color = self.config.connected_color or self.config.color
                renderer.icon_and_text(
                    self.config.icon,
                    self.context.obs.current_scene or "[none]",
                    icon_size=64,
                    text_size=16,
                    icon_color=color,
                    text_color=color,
                )
            else:
                renderer.icon(self.config.icon, size=64, color=self.context.disconnected_color)

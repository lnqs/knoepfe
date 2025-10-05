from knoepfe.config.widget import WidgetConfig
from knoepfe.core.key import Key
from pydantic import Field

from ..context import OBSPluginContext
from .base import OBSWidget


class SwitchSceneConfig(WidgetConfig):
    """Configuration for SwitchScene widget."""

    scene: str = Field(..., description="Scene name to switch to")
    icon: str = Field(
        default="\uf01c5",  # nf-md-desktop_tower
        description="Scene icon (unicode character or codepoint)",
    )
    active_color: str = Field(default="red", description="Icon/text color when scene is active")
    inactive_color: str | None = Field(
        default=None, description="Icon/text color when scene is inactive (defaults to base color)"
    )


class SwitchScene(OBSWidget[SwitchSceneConfig]):
    name = "OBSSwitchScene"
    description = "Switch to a specific OBS scene"

    relevant_events = [
        "ConnectionEstablished",
        "ConnectionLost",
        "SwitchScenes",
    ]

    def __init__(self, config: SwitchSceneConfig, context: OBSPluginContext) -> None:
        super().__init__(config, context)

    async def update(self, key: Key) -> None:
        if not self.context.obs.connected:
            color = self.context.disconnected_color
        elif self.context.obs.current_scene == self.config.scene:
            color = self.config.active_color
        else:
            color = self.config.inactive_color or self.config.color

        with key.renderer() as renderer:
            renderer.clear()
            renderer.icon_and_text(
                self.config.icon,
                self.config.scene,
                icon_size=64,
                text_size=16,
                icon_color=color,
                text_color=color,
            )

    async def triggered(self, long_press: bool = False) -> None:
        if self.context.obs.connected:
            await self.context.obs.set_scene(self.config.scene)

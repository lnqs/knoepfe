from knoepfe.config.widget import WidgetConfig
from knoepfe.rendering import Renderer
from knoepfe.widgets.widget import UpdateResult
from pydantic import Field

from ..plugin import OBSPlugin
from .obs_widget import OBSWidget


class SwitchSceneConfig(WidgetConfig):
    """Configuration for SwitchScene widget."""

    scene: str = Field(..., description="Scene name to switch to")
    icon: str = Field(
        default="󰏜",  # nf-md-panorama
        description="Scene icon (unicode character or codepoint)",
    )
    active_color: str = Field(default="red", description="Icon/text color when scene is active")
    inactive_color: str | None = Field(
        default=None, description="Icon/text color when scene is inactive (defaults to base color)"
    )


class SwitchScene(OBSWidget[SwitchSceneConfig]):
    """Switch to a specific OBS scene."""

    name = "OBSSwitchScene"

    relevant_events = [
        "ConnectionEstablished",
        "ConnectionLost",
        "SwitchScenes",
    ]

    def __init__(self, config: SwitchSceneConfig, plugin: OBSPlugin) -> None:
        super().__init__(config, plugin)

    async def update(self, renderer: Renderer) -> UpdateResult:
        if not self.plugin.obs.connected:
            color = self.plugin.disconnected_color
        elif self.plugin.obs.current_scene == self.config.scene:
            color = self.config.active_color
        else:
            color = self.config.inactive_color or self.config.color

        renderer.clear()
        renderer.icon_and_text(
            self.config.icon,
            self.config.scene,
            icon_size=64,
            text_size=16,
            icon_color=color,
            text_color=color,
        )

        return UpdateResult.UPDATED

    async def triggered(self, long_press: bool = False) -> None:
        if self.plugin.obs.connected:
            await self.plugin.obs.set_scene(self.config.scene)

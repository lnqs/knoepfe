from knoepfe.config.widget import WidgetConfig
from knoepfe.rendering import Renderer
from knoepfe.widgets.actions import UpdateResult
from pydantic import Field

from ..plugin import OBSPlugin
from .obs_widget import OBSWidget


class CurrentSceneConfig(WidgetConfig):
    """Configuration for CurrentScene widget."""

    icon: str = Field(
        default="󰏜",  # nf-md-panorama
        description="Scene icon (unicode character or codepoint)",
    )
    connected_color: str | None = Field(
        default=None, description="Icon/text color when connected (defaults to base color)"
    )


class CurrentScene(OBSWidget[CurrentSceneConfig]):
    """Display currently active OBS scene."""

    name = "OBSCurrentScene"

    relevant_events = [
        "ConnectionEstablished",
        "ConnectionLost",
        "CurrentProgramSceneChanged",
    ]

    def __init__(self, config: CurrentSceneConfig, plugin: OBSPlugin) -> None:
        super().__init__(config, plugin)

    async def update(self, renderer: Renderer) -> UpdateResult:
        renderer.clear()
        if self.plugin.obs.connected:
            color = self.config.connected_color or self.config.color
            renderer.icon_and_text(
                self.config.icon,
                self.plugin.obs.current_scene or "[none]",
                icon_size=64,
                text_size=16,
                icon_color=color,
                text_color=color,
            )
        else:
            renderer.icon(self.config.icon, color=self.plugin.disconnected_color)

        return UpdateResult.UPDATED

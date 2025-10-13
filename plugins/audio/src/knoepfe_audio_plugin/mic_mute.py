"""Microphone mute control widget for PulseAudio."""

import logging

from knoepfe.config.widget import WidgetConfig
from knoepfe.rendering import Renderer
from knoepfe.widgets.actions import UpdateResult
from pydantic import Field

from .base import AudioWidget

logger = logging.getLogger(__name__)


class MicMuteConfig(WidgetConfig):
    """Configuration for MicMute widget."""

    source: str | None = Field(default=None, description="Audio source name to control")
    muted_icon: str = Field(
        default="󰍭",  # nf-md-microphone_off
        description="Icon to display when muted (unicode character or codepoint)",
    )
    unmuted_icon: str = Field(
        default="󰍬",  # nf-md-microphone
        description="Icon to display when unmuted (unicode character or codepoint)",
    )
    muted_color: str | None = Field(default=None, description="Icon color when muted (defaults to base color)")
    unmuted_color: str = Field(default="red", description="Icon color when unmuted")


class MicMute(AudioWidget[MicMuteConfig]):
    """Toggle microphone mute status.

    Displays a microphone icon (configurable color when unmuted, configurable color when muted)
    and toggles mute state on button press. Updates automatically when mute state changes.
    """

    name = "MicMute"
    relevant_events = ["SourceChanged"]

    async def update(self, renderer: Renderer) -> UpdateResult:
        """Update the key display based on current mute state."""
        source = await self.get_source()
        if not source:
            return UpdateResult.UNCHANGED

        renderer.clear()
        if source.mute:
            renderer.icon(self.config.muted_icon, color=self.config.muted_color or self.config.color)
        else:
            renderer.icon(self.config.unmuted_icon, color=self.config.unmuted_color)

        return UpdateResult.UPDATED

    async def triggered(self, long_press: bool = False) -> None:
        """Toggle microphone mute state."""
        source = await self.get_source()
        if not source:
            return

        await self.pulse.source_mute(source.index, mute=not source.mute)

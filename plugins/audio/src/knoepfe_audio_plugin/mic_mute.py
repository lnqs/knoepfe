"""Microphone mute control widget for PulseAudio."""

import logging

from knoepfe.config.widget import WidgetConfig
from knoepfe.core.key import Key
from pydantic import Field

from .base import AudioWidget

logger = logging.getLogger(__name__)


class MicMuteConfig(WidgetConfig):
    """Configuration for MicMute widget."""

    source: str | None = Field(default=None, description="Audio source name to control")
    muted_icon: str = Field(
        default="\uf036d",  # nf-md-microphone_off
        description="Icon to display when muted (unicode character or codepoint)",
    )
    unmuted_icon: str = Field(
        default="\uf036c",  # nf-md-microphone
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
    description = "Toggle microphone mute status"
    relevant_events = ["SourceChanged"]

    async def update(self, key: Key) -> None:
        """Update the key display based on current mute state."""
        source = await self.get_source()
        if not source:
            return

        with key.renderer() as renderer:
            renderer.clear()
            if source.mute:
                renderer.icon(self.config.muted_icon, size=86, color=self.config.muted_color or self.config.color)
            else:
                renderer.icon(self.config.unmuted_icon, size=86, color=self.config.unmuted_color)

    async def triggered(self, long_press: bool = False) -> None:
        """Toggle microphone mute state."""
        source = await self.get_source()
        if not source:
            return

        await self.pulse.source_mute(source.index, mute=not source.mute)

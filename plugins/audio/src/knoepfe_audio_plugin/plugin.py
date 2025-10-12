"""Audio plugin instance for knoepfe."""

import logging
from typing import TYPE_CHECKING

from knoepfe.plugins import Plugin

from .config import AudioPluginConfig
from .connector import PulseAudioConnector

if TYPE_CHECKING:
    from knoepfe.widgets.base import Widget

logger = logging.getLogger(__name__)


class AudioPlugin(Plugin):
    """Audio plugin instance for knoepfe.

    Provides shared state and resources for all audio widgets, including
    a single PulseAudio connection that is shared across all widgets.

    The PulseAudio connection is lazily initialized when the first widget
    is activated and remains connected for the lifetime of the plugin.

    Attributes:
        default_source: Default PulseAudio source name from plugin config.
        pulse: Shared PulseAudio connector instance.
        mute_states: Dictionary tracking mute states of sources.
    """

    def __init__(self, config: AudioPluginConfig):
        """Initialize the audio plugin instance.

        Args:
            config: Plugin configuration containing default_source and other settings.
        """
        super().__init__(config)

        # Plugin-specific state
        self.default_source = config.default_source
        self.pulse = PulseAudioConnector(self.tasks)
        self.mute_states: dict[str, bool] = {}

    async def on_widget_activate(self, widget: "Widget") -> None:
        """Connect to PulseAudio when first widget activates.

        This is called BEFORE the widget's activate() method.
        The connection remains active for the lifetime of the plugin.
        """
        await super().on_widget_activate(widget)

        # Connect to PulseAudio if not already connected
        if not self.pulse.connected:
            logger.info("Audio plugin: First widget activated, connecting to PulseAudio...")
            await self.pulse.connect()
        else:
            logger.debug(f"Audio plugin: Widget {widget.name} activated (PulseAudio already connected)")

    def sync_mute_state(self, source: str, muted: bool) -> None:
        """Synchronize mute state across all widgets.

        Args:
            source: The source name whose mute state changed.
            muted: The new mute state.
        """
        self.mute_states[source] = muted

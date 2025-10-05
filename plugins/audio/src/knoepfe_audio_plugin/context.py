"""Context container for audio plugin."""

from knoepfe.plugins import PluginContext

from .config import AudioPluginConfig
from .connector import PulseAudioConnector


class AudioPluginContext(PluginContext):
    """Context container for audio plugin widgets.

    Provides shared state and resources for all audio widgets, including
    a single PulseAudio connection that is shared across all widgets.

    Attributes:
        default_source: Default PulseAudio source name from plugin config.
        pulse: Shared PulseAudio connector instance.
        mute_states: Dictionary tracking mute states of sources.
    """

    def __init__(self, config: AudioPluginConfig):
        """Initialize the audio plugin context.

        Args:
            config: Plugin configuration containing default_source and other settings.
        """
        super().__init__(config)

        # Plugin-specific state
        self.default_source = config.default_source
        self.pulse = PulseAudioConnector()
        self.mute_states: dict[str, bool] = {}

    def sync_mute_state(self, source: str, muted: bool) -> None:
        """Synchronize mute state across all widgets.

        Args:
            source: The source name whose mute state changed.
            muted: The new mute state.
        """
        self.mute_states[source] = muted

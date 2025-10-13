from unittest.mock import AsyncMock, MagicMock, patch

from pytest import fixture

from knoepfe_obs_plugin.config import OBSPluginConfig
from knoepfe_obs_plugin.plugin import OBSPlugin
from knoepfe_obs_plugin.widgets.recording import Recording, RecordingConfig


@fixture
def mock_plugin():
    return OBSPlugin(OBSPluginConfig())


@fixture
def recording_widget(mock_plugin):
    return Recording(RecordingConfig(), mock_plugin)


def test_recording_init(mock_plugin):
    widget = Recording(RecordingConfig(), mock_plugin)
    assert not widget.recording
    assert not widget.show_help
    assert not widget.show_loading


async def test_recording_update_disconnected(recording_widget):
    with patch.object(recording_widget.plugin, "obs") as mock_obs:
        mock_obs.connected = False
        renderer = MagicMock()

        await recording_widget.update(renderer)

        renderer.clear.assert_called_once()
        renderer.icon.assert_called_with(
            "󰕨",  # nf-md-video_off
            color="#202020",
        )


async def test_recording_update_not_recording(recording_widget):
    with patch.object(recording_widget.plugin, "obs") as mock_obs:
        mock_obs.connected = True
        mock_obs.recording = False
        renderer = MagicMock()

        await recording_widget.update(renderer)

        renderer.clear.assert_called_once()
        renderer.icon.assert_called_with(
            "󰕨",  # nf-md-video_off
            color="white",
        )


async def test_recording_update_recording(recording_widget):
    with patch.object(recording_widget.plugin, "obs") as mock_obs:
        mock_obs.connected = True
        mock_obs.recording = True
        mock_obs.get_recording_timecode = AsyncMock(return_value="00:01:23.456")
        recording_widget.recording = True
        renderer = MagicMock()

        await recording_widget.update(renderer)

        # Check icon_and_text call for the recording state
        renderer.clear.assert_called_once()
        renderer.icon_and_text.assert_called_with(
            "󰕧",  # nf-md-video
            "00:01:23",  # timecode without milliseconds
            icon_color="red",
            text_color="red",
        )


async def test_recording_update_show_help(recording_widget):
    with patch.object(recording_widget.plugin, "obs") as mock_obs:
        mock_obs.recording = False
        mock_obs.connected = True
        recording_widget.show_help = True
        renderer = MagicMock()

        await recording_widget.update(renderer)

        renderer.clear.assert_called_once()
        renderer.text_wrapped.assert_called_with("long press\nto toggle", size=16)


async def test_recording_update_show_loading(recording_widget):
    with patch.object(recording_widget.plugin, "obs") as mock_obs:
        mock_obs.recording = False
        recording_widget.show_loading = True
        renderer = MagicMock()

        await recording_widget.update(renderer)

        renderer.clear.assert_called_once()
        renderer.icon.assert_called_with(
            "󰔟",  # nf-md-timer_sand
        )
        assert not recording_widget.show_loading


def test_recording_config():
    """Test that RecordingConfig validates correctly."""
    # Test with defaults
    config = RecordingConfig()
    assert config.recording_icon == "󰕧"  # nf-md-video
    assert config.stopped_icon == "󰕨"  # nf-md-video_off
    assert config.loading_icon == "󰔟"  # nf-md-timer_sand
    assert config.recording_color == "red"
    assert config.stopped_color is None
    assert config.color == "white"

    # Test with custom values
    config = RecordingConfig(
        recording_icon="🔴", stopped_icon="⏹️", loading_icon="⏳", recording_color="green", stopped_color="blue"
    )
    assert config.recording_icon == "🔴"
    assert config.stopped_icon == "⏹️"
    assert config.loading_icon == "⏳"
    assert config.recording_color == "green"
    assert config.stopped_color == "blue"

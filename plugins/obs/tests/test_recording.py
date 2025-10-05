from unittest.mock import AsyncMock, MagicMock, patch

from pytest import fixture

from knoepfe_obs_plugin.config import OBSPluginConfig
from knoepfe_obs_plugin.context import OBSPluginContext
from knoepfe_obs_plugin.widgets.recording import Recording, RecordingConfig


@fixture
def mock_context():
    return OBSPluginContext(OBSPluginConfig())


@fixture
def recording_widget(mock_context):
    return Recording(RecordingConfig(), mock_context)


def test_recording_init(mock_context):
    widget = Recording(RecordingConfig(), mock_context)
    assert not widget.recording
    assert not widget.show_help
    assert not widget.show_loading


async def test_recording_update_disconnected(recording_widget):
    with patch.object(recording_widget.context, "obs") as mock_obs:
        mock_obs.connected = False
        key = MagicMock()

        await recording_widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon.assert_called_with("\ue04c", size=86, color="#202020")


async def test_recording_update_not_recording(recording_widget):
    with patch.object(recording_widget.context, "obs") as mock_obs:
        mock_obs.connected = True
        mock_obs.recording = False
        key = MagicMock()

        await recording_widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon.assert_called_with("\ue04c", size=86, color="white")


async def test_recording_update_recording(recording_widget):
    with patch.object(recording_widget.context, "obs") as mock_obs:
        mock_obs.connected = True
        mock_obs.recording = True
        mock_obs.get_recording_timecode = AsyncMock(return_value="00:01:23.456")
        recording_widget.recording = True
        key = MagicMock()

        await recording_widget.update(key)

        # Check icon_and_text call for the recording state
        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon_and_text.assert_called_with(
            "\ue04b",  # videocam icon
            "00:01:23",  # timecode without milliseconds
            icon_size=64,
            text_size=16,
            icon_color="red",
            text_color="red",
        )


async def test_recording_update_show_help(recording_widget):
    with patch.object(recording_widget.context, "obs") as mock_obs:
        mock_obs.recording = False
        mock_obs.connected = True
        recording_widget.show_help = True
        key = MagicMock()

        await recording_widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.text_wrapped.assert_called_with("long press\nto toggle", size=16)


async def test_recording_update_show_loading(recording_widget):
    with patch.object(recording_widget.context, "obs") as mock_obs:
        mock_obs.recording = False
        recording_widget.show_loading = True
        key = MagicMock()

        await recording_widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon.assert_called_with("\ue5d3", size=86)
        assert not recording_widget.show_loading


def test_recording_config():
    """Test that RecordingConfig validates correctly."""
    # Test with defaults
    config = RecordingConfig()
    assert config.recording_icon == "\ue04b"
    assert config.stopped_icon == "\ue04c"
    assert config.loading_icon == "\ue5d3"
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

from unittest.mock import AsyncMock, MagicMock, patch

from pytest import fixture
from schema import Schema

from knoepfe_obs_plugin.recording import Recording
from knoepfe_obs_plugin.state import OBSPluginState


@fixture
def mock_state():
    return OBSPluginState({})


@fixture
def recording_widget(mock_state):
    return Recording({}, {}, mock_state)


def test_recording_init(mock_state):
    widget = Recording({}, {}, mock_state)
    assert not widget.recording
    assert not widget.show_help
    assert not widget.show_loading


async def test_recording_update_disconnected(recording_widget):
    with patch.object(recording_widget.state, "obs") as mock_obs:
        mock_obs.connected = False
        key = MagicMock()

        await recording_widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon.assert_called_with("\ue04c", size=86, color="#202020")


async def test_recording_update_not_recording(recording_widget):
    with patch.object(recording_widget.state, "obs") as mock_obs:
        mock_obs.connected = True
        mock_obs.recording = False
        key = MagicMock()

        await recording_widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon.assert_called_with("\ue04c", size=86)


async def test_recording_update_recording(recording_widget):
    with patch.object(recording_widget.state, "obs") as mock_obs:
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
    with patch.object(recording_widget.state, "obs") as mock_obs:
        mock_obs.recording = False
        mock_obs.connected = True
        recording_widget.show_help = True
        key = MagicMock()

        await recording_widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.text_wrapped.assert_called_with("long press\nto toggle", size=16)


async def test_recording_update_show_loading(recording_widget):
    with patch.object(recording_widget.state, "obs") as mock_obs:
        mock_obs.recording = False
        recording_widget.show_loading = True
        key = MagicMock()

        await recording_widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon.assert_called_with("\ue5d3", size=86)
        assert not recording_widget.show_loading


def test_recording_schema():
    assert isinstance(Recording.get_config_schema(), Schema)

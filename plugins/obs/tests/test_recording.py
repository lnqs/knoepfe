from unittest.mock import AsyncMock, MagicMock, patch

from pytest import fixture
from schema import Schema

from knoepfe_obs_plugin.recording import Recording


@fixture
def mock_obs():
    with patch("knoepfe_obs_plugin.recording.obs") as mock:
        mock.connected = True
        mock.recording = False
        mock.get_recording_timecode = AsyncMock(return_value="00:01:23.456")
        yield mock


@fixture
def recording_widget():
    return Recording({}, {})


def test_recording_init():
    widget = Recording({}, {})
    assert not widget.recording
    assert not widget.show_help
    assert not widget.show_loading


async def test_recording_update_disconnected(recording_widget, mock_obs):
    mock_obs.connected = False
    key = MagicMock()

    await recording_widget.update(key)

    key.renderer.return_value.__enter__.return_value.text.assert_called_with(
        "\ue04c", font="Material Icons", size=86, color="#202020", anchor="mm"
    )


async def test_recording_update_not_recording(recording_widget, mock_obs):
    mock_obs.connected = True
    mock_obs.recording = False
    key = MagicMock()

    await recording_widget.update(key)

    key.renderer.return_value.__enter__.return_value.text.assert_called_with(
        "\ue04c", font="Material Icons", size=86, anchor="mm"
    )


async def test_recording_update_recording(recording_widget, mock_obs):
    mock_obs.connected = True
    mock_obs.recording = True
    recording_widget.recording = True
    key = MagicMock()

    await recording_widget.update(key)

    # Check both text_at calls for the recording state
    renderer_mock = key.renderer.return_value.__enter__.return_value
    renderer_mock.text_at.assert_any_call((48, 32), "\ue04b", font="Material Icons", size=64, color="red", anchor="mm")
    renderer_mock.text_at.assert_any_call((48, 80), "00:01:23", size=16, color="red", anchor="mt")


async def test_recording_update_show_help(recording_widget, mock_obs):
    recording_widget.show_help = True
    key = MagicMock()

    await recording_widget.update(key)

    key.renderer.return_value.__enter__.return_value.text.assert_called_with("long press\nto toggle", size=16)


async def test_recording_update_show_loading(recording_widget, mock_obs):
    recording_widget.show_loading = True
    key = MagicMock()

    await recording_widget.update(key)

    key.renderer.return_value.__enter__.return_value.text.assert_called_with(
        "\ue5d3", font="Material Icons", size=86, anchor="mm"
    )
    assert not recording_widget.show_loading


def test_recording_schema():
    assert isinstance(Recording.get_config_schema(), Schema)

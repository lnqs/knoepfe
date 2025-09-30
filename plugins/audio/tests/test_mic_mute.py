from unittest.mock import AsyncMock, MagicMock, Mock, patch

from pytest import fixture
from schema import Schema

from knoepfe_audio_plugin.mic_mute import MicMute
from knoepfe_audio_plugin.state import AudioPluginState


@fixture
def mock_state():
    return AudioPluginState({})


@fixture
def mic_mute_widget(mock_state):
    return MicMute({}, {}, mock_state)


@fixture
def mock_pulse():
    mock = Mock()
    mock.connect = AsyncMock()
    mock.disconnect = Mock()
    mock.source_mute = AsyncMock()
    return mock


@fixture
def mock_source():
    source = Mock()
    source.mute = False
    source.index = 1
    source.name = "test_source"
    return source


def test_mic_mute_init(mock_state):
    widget = MicMute({}, {}, mock_state)
    assert widget.pulse is None
    assert widget.event_listener is None


async def test_mic_mute_activate(mic_mute_widget):
    with patch("knoepfe_audio_plugin.mic_mute.PulseAsync") as mock_pulse_class:
        mock_pulse = Mock()
        mock_pulse.connect = AsyncMock()
        mock_pulse_class.return_value = mock_pulse

        with patch("knoepfe_audio_plugin.mic_mute.get_event_loop") as mock_loop:
            mock_loop.return_value.create_task = Mock()

            await mic_mute_widget.activate()

            assert mic_mute_widget.pulse == mock_pulse
            mock_pulse.connect.assert_called_once()
            mock_loop.return_value.create_task.assert_called_once()


async def test_mic_mute_deactivate(mic_mute_widget):
    # Set up widget with active pulse and event listener
    mock_pulse = Mock()
    mock_pulse.disconnect = Mock()
    mock_event_listener = Mock()
    mock_event_listener.cancel = Mock()

    mic_mute_widget.pulse = mock_pulse
    mic_mute_widget.event_listener = mock_event_listener

    await mic_mute_widget.deactivate()

    mock_event_listener.cancel.assert_called_once()
    mock_pulse.disconnect.assert_called_once()
    assert mic_mute_widget.pulse is None
    assert mic_mute_widget.event_listener is None


async def test_mic_mute_update_muted(mic_mute_widget, mock_source):
    mock_source.mute = True
    key = MagicMock()

    with patch.object(mic_mute_widget, "get_source", AsyncMock(return_value=mock_source)):
        await mic_mute_widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon.assert_called_with("\ue02b", size=86)


async def test_mic_mute_update_unmuted(mic_mute_widget, mock_source):
    mock_source.mute = False
    key = MagicMock()

    with patch.object(mic_mute_widget, "get_source", AsyncMock(return_value=mock_source)):
        await mic_mute_widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon.assert_called_with("\ue029", size=86, color="red")


async def test_mic_mute_triggered(mic_mute_widget, mock_pulse, mock_source):
    mock_source.mute = False
    mic_mute_widget.pulse = mock_pulse

    with patch.object(mic_mute_widget, "get_source", AsyncMock(return_value=mock_source)):
        await mic_mute_widget.triggered()

        mock_pulse.source_mute.assert_called_once_with(mock_source.index, mute=True)


async def test_mic_mute_triggered_unmute(mic_mute_widget, mock_pulse, mock_source):
    mock_source.mute = True
    mic_mute_widget.pulse = mock_pulse

    with patch.object(mic_mute_widget, "get_source", AsyncMock(return_value=mock_source)):
        await mic_mute_widget.triggered()

        mock_pulse.source_mute.assert_called_once_with(mock_source.index, mute=False)


def test_mic_mute_schema():
    assert isinstance(MicMute.get_config_schema(), Schema)

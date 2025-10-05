from unittest.mock import AsyncMock, MagicMock, Mock, patch

from pytest import fixture

from knoepfe_audio_plugin.config import AudioPluginConfig
from knoepfe_audio_plugin.context import AudioPluginContext
from knoepfe_audio_plugin.mic_mute import MicMute, MicMuteConfig


@fixture
def mock_context():
    return AudioPluginContext(AudioPluginConfig())


@fixture
def mic_mute_widget(mock_context):
    return MicMute(MicMuteConfig(), mock_context)


@fixture
def mock_source():
    source = Mock()
    source.mute = False
    source.index = 1
    source.name = "test_source"
    return source


def test_mic_mute_init(mock_context):
    """Test MicMute widget initialization."""
    widget = MicMute(MicMuteConfig(), mock_context)
    assert widget.listening_task is None
    assert widget.pulse == mock_context.pulse


async def test_mic_mute_activate(mic_mute_widget):
    """Test widget activation connects to PulseAudio and starts listener."""
    with patch.object(mic_mute_widget.context.pulse, "connect", AsyncMock()) as mock_connect:
        with patch("knoepfe_audio_plugin.base.get_event_loop") as mock_loop:
            mock_task = Mock()
            mock_loop.return_value.create_task.return_value = mock_task

            await mic_mute_widget.activate()

            mock_connect.assert_called_once()
            mock_loop.return_value.create_task.assert_called_once()
            assert mic_mute_widget.listening_task == mock_task

            # Clean up the task to prevent warnings
            if mic_mute_widget.listening_task:
                mic_mute_widget.listening_task.cancel()
                mic_mute_widget.listening_task = None


async def test_mic_mute_deactivate(mic_mute_widget):
    """Test widget deactivation stops listener."""
    mock_event_listener = Mock()
    mock_event_listener.cancel = Mock()

    mic_mute_widget.listening_task = mock_event_listener

    await mic_mute_widget.deactivate()

    mock_event_listener.cancel.assert_called_once()
    assert mic_mute_widget.listening_task is None


async def test_mic_mute_update_muted(mic_mute_widget, mock_source):
    """Test update renders muted icon when source is muted."""
    mock_source.mute = True
    key = MagicMock()

    with patch.object(mic_mute_widget, "get_source", AsyncMock(return_value=mock_source)):
        await mic_mute_widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon.assert_called_with("\ue02b", size=86, color="white")


async def test_mic_mute_update_unmuted(mic_mute_widget, mock_source):
    """Test update renders unmuted icon when source is unmuted."""
    mock_source.mute = False
    key = MagicMock()

    with patch.object(mic_mute_widget, "get_source", AsyncMock(return_value=mock_source)):
        await mic_mute_widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon.assert_called_with("\ue029", size=86, color="red")


async def test_mic_mute_update_no_source(mic_mute_widget):
    """Test update handles missing source gracefully."""
    key = MagicMock()

    with patch.object(mic_mute_widget, "get_source", AsyncMock(return_value=None)):
        await mic_mute_widget.update(key)

        # Should return early without rendering
        key.renderer.assert_not_called()


async def test_mic_mute_triggered(mic_mute_widget, mock_source):
    """Test triggered toggles mute state from unmuted to muted."""
    mock_source.mute = False

    with patch.object(mic_mute_widget, "get_source", AsyncMock(return_value=mock_source)):
        with patch.object(mic_mute_widget.pulse, "source_mute", AsyncMock()) as mock_mute:
            await mic_mute_widget.triggered()

            mock_mute.assert_called_once_with(mock_source.index, mute=True)


async def test_mic_mute_triggered_unmute(mic_mute_widget, mock_source):
    """Test triggered toggles mute state from muted to unmuted."""
    mock_source.mute = True

    with patch.object(mic_mute_widget, "get_source", AsyncMock(return_value=mock_source)):
        with patch.object(mic_mute_widget.pulse, "source_mute", AsyncMock()) as mock_mute:
            await mic_mute_widget.triggered()

            mock_mute.assert_called_once_with(mock_source.index, mute=False)


async def test_mic_mute_triggered_no_source(mic_mute_widget):
    """Test triggered handles missing source gracefully."""
    with patch.object(mic_mute_widget, "get_source", AsyncMock(return_value=None)):
        with patch.object(mic_mute_widget.pulse, "source_mute", AsyncMock()) as mock_mute:
            await mic_mute_widget.triggered()

            # Should return early without calling source_mute
            mock_mute.assert_not_called()


def test_mic_mute_config():
    """Test that MicMuteConfig validates correctly."""
    # Test with defaults
    config = MicMuteConfig()
    assert config.source is None
    assert config.muted_icon == "\ue02b"
    assert config.unmuted_icon == "\ue029"
    assert config.muted_color is None  # Defaults to base color
    assert config.color == "white"  # Base color
    assert config.unmuted_color == "red"

    # Test with custom values
    config = MicMuteConfig(
        source="test_source",
        muted_icon="🔇",
        unmuted_icon="🎤",
        color="blue",  # Base color
        muted_color="gray",
        unmuted_color="green",
    )
    assert config.source == "test_source"
    assert config.muted_icon == "🔇"
    assert config.unmuted_icon == "🎤"
    assert config.color == "blue"
    assert config.muted_color == "gray"
    assert config.unmuted_color == "green"


async def test_get_source_widget_config(mic_mute_widget):
    """Test get_source uses widget config source when specified."""
    widget = MicMute(MicMuteConfig(source="widget_source"), mic_mute_widget.context)
    mock_source = Mock()

    with patch.object(widget.pulse, "get_source", AsyncMock(return_value=mock_source)) as mock_get:
        result = await widget.get_source()

        mock_get.assert_called_once_with("widget_source")
        assert result == mock_source


async def test_get_source_plugin_config(mic_mute_widget):
    """Test get_source falls back to plugin config default_source."""
    mic_mute_widget.context.default_source = "plugin_source"
    mock_source = Mock()

    with patch.object(mic_mute_widget.pulse, "get_source", AsyncMock(return_value=mock_source)) as mock_get:
        result = await mic_mute_widget.get_source()

        mock_get.assert_called_once_with("plugin_source")
        assert result == mock_source


async def test_get_source_system_default(mic_mute_widget):
    """Test get_source falls back to system default when no config specified."""
    mock_source = Mock()

    with patch.object(mic_mute_widget.pulse, "get_default_source", AsyncMock(return_value=mock_source)) as mock_get:
        result = await mic_mute_widget.get_source()

        mock_get.assert_called_once()
        assert result == mock_source

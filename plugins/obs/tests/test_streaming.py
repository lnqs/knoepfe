from unittest.mock import AsyncMock, MagicMock, patch

from pytest import fixture

from knoepfe_obs_plugin.config import OBSPluginConfig
from knoepfe_obs_plugin.context import OBSPluginContext
from knoepfe_obs_plugin.widgets.streaming import Streaming, StreamingConfig


@fixture
def mock_context():
    return OBSPluginContext(OBSPluginConfig())


@fixture
def streaming_widget(mock_context):
    return Streaming(StreamingConfig(), mock_context)


def test_streaming_init(mock_context):
    widget = Streaming(StreamingConfig(), mock_context)
    assert not widget.streaming
    assert not widget.show_help
    assert not widget.show_loading


async def test_streaming_update_disconnected(streaming_widget):
    with patch.object(streaming_widget.context, "obs") as mock_obs:
        mock_obs.connected = False
        key = MagicMock()

        await streaming_widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon.assert_called_with(
            "󰄘",  # nf-md-cast
            size=86,
            color="#202020",
        )


async def test_streaming_update_not_streaming(streaming_widget):
    with patch.object(streaming_widget.context, "obs") as mock_obs:
        mock_obs.connected = True
        mock_obs.streaming = False
        key = MagicMock()

        await streaming_widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon.assert_called_with(
            "󰄘",  # nf-md-cast
            size=86,
            color="white",
        )


async def test_streaming_update_streaming(streaming_widget):
    with patch.object(streaming_widget.context, "obs") as mock_obs:
        mock_obs.connected = True
        mock_obs.streaming = True
        mock_obs.get_streaming_timecode = AsyncMock(return_value="00:01:23.456")
        streaming_widget.streaming = True
        key = MagicMock()

        await streaming_widget.update(key)

        # Check icon_and_text call for the streaming state
        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon_and_text.assert_called_with(
            "󰄘",  # nf-md-cast
            "00:01:23",  # timecode without milliseconds
            icon_size=64,
            text_size=16,
            icon_color="red",
            text_color="red",
        )


async def test_streaming_update_show_help(streaming_widget):
    with patch.object(streaming_widget.context, "obs") as mock_obs:
        mock_obs.streaming = False
        mock_obs.connected = True
        streaming_widget.show_help = True
        key = MagicMock()

        await streaming_widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.text_wrapped.assert_called_with("long press\nto toggle", size=16)


async def test_streaming_update_show_loading(streaming_widget):
    with patch.object(streaming_widget.context, "obs") as mock_obs:
        mock_obs.streaming = False
        streaming_widget.show_loading = True
        key = MagicMock()

        await streaming_widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon.assert_called_with(
            "󰔟",  # nf-md-timer_sand
            size=86,
        )
        assert not streaming_widget.show_loading


async def test_streaming_triggered_long_press_start(streaming_widget):
    """Test long press starts streaming when not streaming."""
    with patch.object(streaming_widget.context, "obs") as mock_obs:
        mock_obs.connected = True
        mock_obs.streaming = False
        mock_obs.start_streaming = AsyncMock()

        await streaming_widget.triggered(long_press=True)

        mock_obs.start_streaming.assert_called_once()
        assert streaming_widget.show_loading


async def test_streaming_triggered_long_press_stop(streaming_widget):
    """Test long press stops streaming when streaming."""
    with patch.object(streaming_widget.context, "obs") as mock_obs:
        mock_obs.connected = True
        mock_obs.streaming = True
        mock_obs.stop_streaming = AsyncMock()

        await streaming_widget.triggered(long_press=True)

        mock_obs.stop_streaming.assert_called_once()
        assert streaming_widget.show_loading


async def test_streaming_triggered_long_press_disconnected(streaming_widget):
    """Test long press does nothing when disconnected."""
    with patch.object(streaming_widget.context, "obs") as mock_obs:
        mock_obs.connected = False
        mock_obs.start_streaming = AsyncMock()
        mock_obs.stop_streaming = AsyncMock()

        await streaming_widget.triggered(long_press=True)

        mock_obs.start_streaming.assert_not_called()
        mock_obs.stop_streaming.assert_not_called()


async def test_streaming_triggered_short_press(streaming_widget):
    """Test short press shows help text."""
    streaming_widget.request_update = MagicMock()

    with patch("knoepfe_obs_plugin.widgets.streaming.sleep", AsyncMock()):
        await streaming_widget.triggered(long_press=False)

        # Should set show_help and request updates
        assert streaming_widget.request_update.call_count == 2


async def test_streaming_update_starts_periodic_update(streaming_widget):
    """Test that update starts periodic updates when streaming starts."""
    streaming_widget.request_periodic_update = MagicMock()
    streaming_widget.stop_periodic_update = MagicMock()

    with patch.object(streaming_widget.context, "obs") as mock_obs:
        mock_obs.connected = True
        mock_obs.streaming = True
        mock_obs.get_streaming_timecode = AsyncMock(return_value="00:00:00.000")
        key = MagicMock()

        await streaming_widget.update(key)

        streaming_widget.request_periodic_update.assert_called_once_with(1.0)


async def test_streaming_update_stops_periodic_update(streaming_widget):
    """Test that update stops periodic updates when streaming stops."""
    streaming_widget.streaming = True  # Widget thinks it's streaming
    streaming_widget.request_periodic_update = MagicMock()
    streaming_widget.stop_periodic_update = MagicMock()

    with patch.object(streaming_widget.context, "obs") as mock_obs:
        mock_obs.connected = True
        mock_obs.streaming = False  # But OBS says it's not
        key = MagicMock()

        await streaming_widget.update(key)

        streaming_widget.stop_periodic_update.assert_called_once()


def test_streaming_config():
    """Test that StreamingConfig validates correctly."""
    # Test with defaults
    config = StreamingConfig()
    assert config.streaming_icon == "󰄘"  # nf-md-cast
    assert config.stopped_icon == "󰄘"  # nf-md-cast
    assert config.loading_icon == "󰔟"  # nf-md-timer_sand
    assert config.streaming_color == "red"
    assert config.stopped_color is None
    assert config.color == "white"

    # Test with custom values
    config = StreamingConfig(
        streaming_icon="📡",
        stopped_icon="🚫",
        loading_icon="⏳",
        streaming_color="green",
        stopped_color="blue",
    )
    assert config.streaming_icon == "📡"
    assert config.stopped_icon == "🚫"
    assert config.loading_icon == "⏳"
    assert config.streaming_color == "green"
    assert config.stopped_color == "blue"

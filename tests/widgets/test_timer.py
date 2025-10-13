from unittest.mock import MagicMock, patch

import pytest

from knoepfe.config.plugin import EmptyPluginConfig
from knoepfe.plugins import Plugin
from knoepfe.widgets.builtin.timer import Timer, TimerConfig


@pytest.fixture
def plugin():
    """Create a plugin instance for testing."""
    config = EmptyPluginConfig()
    return Plugin(config)


async def test_timer_idle_with_defaults(plugin) -> None:
    """Test that Timer displays icon when idle with default configuration."""
    widget = Timer(TimerConfig(), plugin)

    # Mock renderer
    renderer = MagicMock()

    # Update widget (idle state)
    await widget.update(renderer)

    # Verify icon was called with defaults
    renderer.clear.assert_called_once()
    renderer.icon.assert_called_once_with(
        "󱎫",  # nf-md-timer
        color="white",
    )


async def test_timer_idle_with_custom_icon_and_color(plugin) -> None:
    """Test that Timer uses custom icon and base color when idle."""
    widget = Timer(TimerConfig(icon="⏱️", color="#00ff00"), plugin)

    # Mock renderer
    renderer = MagicMock()

    # Update widget (idle state)
    await widget.update(renderer)

    # Verify icon was called with custom values
    renderer.icon.assert_called_once_with("⏱️", color="#00ff00")


async def test_timer_running_with_custom_font_and_color(plugin) -> None:
    """Test that Timer uses custom font and color when running."""
    widget = Timer(TimerConfig(font="monospace:style=Bold", running_color="#00ff00"), plugin)

    # Set timer to running state
    with patch("knoepfe.widgets.builtin.timer.time.monotonic", return_value=100.0):
        widget.start = 95.0  # 5 seconds elapsed

    # Mock renderer
    renderer = MagicMock()

    # Update widget (running state)
    await widget.update(renderer)

    # Verify text was called with custom font and running color
    renderer.clear.assert_called_once()
    renderer.text.assert_called_once()
    call_args = renderer.text.call_args
    assert call_args[1]["font"] == "monospace:style=Bold"
    assert call_args[1]["color"] == "#00ff00"
    assert call_args[1]["anchor"] == "mm"


async def test_timer_stopped_with_custom_color(plugin) -> None:
    """Test that Timer uses custom stopped color when stopped."""
    widget = Timer(TimerConfig(font="sans:style=Bold", stopped_color="#ff00ff"), plugin)

    # Set timer to stopped state
    widget.start = 95.0
    widget.stop = 100.0  # 5 seconds elapsed

    # Mock renderer
    renderer = MagicMock()

    # Update widget (stopped state)
    await widget.update(renderer)

    # Verify text was called with stopped color
    renderer.clear.assert_called_once()
    renderer.text.assert_called_once()
    call_args = renderer.text.call_args
    assert call_args[1]["color"] == "#ff00ff"
    assert call_args[1]["anchor"] == "mm"


async def test_timer_start_stop_reset_cycle(plugin) -> None:
    """Test the complete timer lifecycle: start, stop, reset."""
    widget = Timer(TimerConfig(), plugin)
    widget.request_periodic_update = MagicMock()
    widget.stop_periodic_update = MagicMock()
    widget.request_update = MagicMock()
    widget.acquire_wake_lock = MagicMock()
    widget.release_wake_lock = MagicMock()

    # Start timer
    with patch("knoepfe.widgets.builtin.timer.time.monotonic", return_value=100.0):
        await widget.triggered()
        assert widget.start == 100.0
        assert widget.stop is None
        widget.request_periodic_update.assert_called_once_with(1.0)
        widget.acquire_wake_lock.assert_called_once()

    # Stop timer
    widget.request_periodic_update.reset_mock()
    with patch("knoepfe.widgets.builtin.timer.time.monotonic", return_value=105.0):
        await widget.triggered()
        assert widget.start == 100.0
        assert widget.stop == 105.0
        widget.stop_periodic_update.assert_called_once()
        widget.release_wake_lock.assert_called_once()

    # Reset timer
    widget.stop_periodic_update.reset_mock()
    await widget.triggered()
    assert widget.start is None
    assert widget.stop is None
    assert widget.stop_periodic_update.call_count == 1


async def test_timer_deactivate_cleanup(plugin) -> None:
    """Test that deactivate preserves timer state for running timers."""
    widget = Timer(TimerConfig(), plugin)
    widget.release_wake_lock = MagicMock()

    # Test 1: Timer is running - state should be preserved, wake lock kept
    widget.start = 100.0
    widget.stop = None

    await widget.deactivate()

    # Timer state should be preserved for running timers
    assert widget.start == 100.0
    assert widget.stop is None
    # Wake lock should NOT be released for running timer
    widget.release_wake_lock.assert_not_called()

    # Test 2: Timer is stopped - wake lock should be released
    widget.start = 100.0
    widget.stop = 150.0

    await widget.deactivate()

    # Timer state should still be preserved
    assert widget.start == 100.0
    assert widget.stop == 150.0
    # Wake lock should be released for stopped timer
    widget.release_wake_lock.assert_called_once()


def test_timer_config_defaults() -> None:
    """Test TimerConfig default values."""
    config = TimerConfig()
    assert config.icon == "󱎫"  # nf-md-timer
    assert config.font is None
    assert config.color == "white"  # Base color
    assert config.running_color is None  # Defaults to base color
    assert config.stopped_color == "red"


def test_timer_config_custom_values() -> None:
    """Test TimerConfig with custom values."""
    config = TimerConfig(
        icon="⏱️",
        font="Ubuntu:style=Bold",
        color="#0000ff",  # Base color for idle icon
        running_color="#00ff00",
        stopped_color="#ff00ff",
    )
    assert config.icon == "⏱️"
    assert config.font == "Ubuntu:style=Bold"
    assert config.color == "#0000ff"
    assert config.running_color == "#00ff00"
    assert config.stopped_color == "#ff00ff"

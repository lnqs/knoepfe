from unittest.mock import MagicMock, patch

import pytest

from knoepfe.config.plugin import EmptyPluginConfig
from knoepfe.plugins.context import PluginContext
from knoepfe.widgets.builtin.clock import Clock, ClockConfig


@pytest.fixture
def context():
    """Create a plugin context for testing."""
    config = EmptyPluginConfig()
    return PluginContext(config)


async def test_clock_update_with_defaults(context) -> None:
    """Test that Clock widget updates with default configuration."""
    widget = Clock(ClockConfig(), context)

    # Mock key
    key = MagicMock()

    # Update widget
    await widget.update(key)

    # Verify text was called with defaults
    renderer = key.renderer.return_value.__enter__.return_value
    renderer.clear.assert_called_once()
    renderer.text.assert_called_once()
    call_args = renderer.text.call_args
    assert call_args[1]["anchor"] == "mm"
    assert call_args[1]["font"] is None
    assert call_args[1]["color"] == "white"


async def test_clock_update_with_custom_font_and_color(context) -> None:
    """Test that Clock widget uses custom font and color."""
    widget = Clock(ClockConfig(format="%H:%M:%S", font="monospace:style=Bold", color="#00ff00"), context)

    # Mock key
    key = MagicMock()

    # Update widget
    await widget.update(key)

    # Verify text was called with custom font and color
    renderer = key.renderer.return_value.__enter__.return_value
    renderer.clear.assert_called_once()
    renderer.text.assert_called_once()
    call_args = renderer.text.call_args
    assert call_args[1]["font"] == "monospace:style=Bold"
    assert call_args[1]["color"] == "#00ff00"


async def test_clock_update_only_when_time_changes(context) -> None:
    """Test that Clock widget only updates when time changes."""
    widget = Clock(ClockConfig(format="%H:%M"), context)

    # Mock key
    key = MagicMock()

    # First update
    with patch("knoepfe.widgets.builtin.clock.datetime") as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = "12:34"
        await widget.update(key)
        assert widget.last_time == "12:34"
        assert key.renderer.return_value.__enter__.return_value.text.call_count == 1

    # Second update with same time - should not render
    key.reset_mock()
    with patch("knoepfe.widgets.builtin.clock.datetime") as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = "12:34"
        await widget.update(key)
        # Should return early, not call renderer
        key.renderer.assert_not_called()

    # Third update with different time - should render
    key.reset_mock()
    with patch("knoepfe.widgets.builtin.clock.datetime") as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = "12:35"
        await widget.update(key)
        assert widget.last_time == "12:35"
        assert key.renderer.return_value.__enter__.return_value.text.call_count == 1


async def test_clock_activate_starts_periodic_update(context) -> None:
    """Test that activate starts periodic updates."""
    widget = Clock(ClockConfig(), context)
    widget.request_periodic_update = MagicMock()

    await widget.activate()

    widget.request_periodic_update.assert_called_once_with(1.0)


async def test_clock_deactivate_stops_periodic_update(context) -> None:
    """Test that deactivate stops periodic updates and resets state."""
    widget = Clock(ClockConfig(), context)
    widget.stop_periodic_update = MagicMock()
    widget.last_time = "12:34"

    await widget.deactivate()

    widget.stop_periodic_update.assert_called_once()
    assert widget.last_time == ""


def test_clock_config_defaults() -> None:
    """Test ClockConfig default values."""
    config = ClockConfig()
    assert config.format == "%H:%M"
    assert config.font is None
    assert config.color == "white"


def test_clock_config_custom_values() -> None:
    """Test ClockConfig with custom values."""
    config = ClockConfig(format="%Y-%m-%d %H:%M:%S", font="Ubuntu:style=Bold", color="#ff0000")
    assert config.format == "%Y-%m-%d %H:%M:%S"
    assert config.font == "Ubuntu:style=Bold"
    assert config.color == "#ff0000"

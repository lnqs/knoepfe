from unittest.mock import MagicMock, patch

import pytest

from knoepfe.config.plugin import EmptyPluginConfig
from knoepfe.plugins.plugin import Plugin
from knoepfe.widgets.builtin.clock import Clock, ClockConfig, ClockSegment


@pytest.fixture
def plugin():
    """Create a plugin instance for testing."""
    config = EmptyPluginConfig()
    return Plugin(config)


async def test_clock_update_with_defaults(plugin) -> None:
    """Test that Clock widget updates with default configuration."""
    widget = Clock(ClockConfig(), plugin)

    # Mock key and renderer
    key = MagicMock()
    renderer = key.renderer.return_value.__enter__.return_value
    renderer.measure_text.return_value = (50, 20)  # Mock text dimensions

    # Update widget
    await widget.update(key)

    # Verify renderer was used
    renderer.clear.assert_called_once()
    renderer.text.assert_called_once()
    call_args = renderer.text.call_args
    assert call_args[1]["anchor"] == "mm"
    assert call_args[1]["font"] is None
    assert call_args[1]["color"] == "white"


async def test_clock_update_with_custom_segments(plugin) -> None:
    """Test that Clock widget uses custom segments."""
    config = ClockConfig(
        font="Roboto",
        color="#fefefe",
        segments=[
            ClockSegment(format="%H", x=0, y=0, width=72, height=24, font="Roboto:style=Bold"),
            ClockSegment(format="%M", x=0, y=24, width=72, height=24),
            ClockSegment(format="%S", x=0, y=48, width=72, height=24, font="Roboto:style=Thin"),
        ],
    )
    widget = Clock(config, plugin)

    # Mock key and renderer
    key = MagicMock()
    renderer = key.renderer.return_value.__enter__.return_value
    renderer.measure_text.return_value = (50, 20)  # Mock text dimensions

    # Update widget
    await widget.update(key)

    # Verify renderer was called for each segment
    renderer.clear.assert_called_once()
    assert renderer.text.call_count == 3

    # Check first segment uses custom font
    first_call = renderer.text.call_args_list[0]
    assert first_call[1]["font"] == "Roboto:style=Bold"
    assert first_call[1]["color"] == "#fefefe"

    # Check second segment inherits widget font
    second_call = renderer.text.call_args_list[1]
    assert second_call[1]["font"] == "Roboto"
    assert second_call[1]["color"] == "#fefefe"

    # Check third segment uses custom font
    third_call = renderer.text.call_args_list[2]
    assert third_call[1]["font"] == "Roboto:style=Thin"
    assert third_call[1]["color"] == "#fefefe"


async def test_clock_update_only_when_time_changes(plugin) -> None:
    """Test that Clock widget only updates when time changes."""
    widget = Clock(ClockConfig(), plugin)

    # Mock key and renderer
    key = MagicMock()
    renderer = key.renderer.return_value.__enter__.return_value
    renderer.measure_text.return_value = (50, 20)

    # First update
    with patch("knoepfe.widgets.builtin.clock.datetime") as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = "12:34"
        await widget.update(key)
        assert widget.last_time == "12:34"
        assert renderer.text.call_count == 1

    # Second update with same time - should not render
    key.reset_mock()
    with patch("knoepfe.widgets.builtin.clock.datetime") as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = "12:34"
        await widget.update(key)
        # Should return early, not call renderer
        key.renderer.assert_not_called()

    # Third update with different time - should render
    key.reset_mock()
    renderer = key.renderer.return_value.__enter__.return_value
    renderer.measure_text.return_value = (50, 20)
    with patch("knoepfe.widgets.builtin.clock.datetime") as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = "12:35"
        await widget.update(key)
        assert widget.last_time == "12:35"
        assert renderer.text.call_count == 1


async def test_clock_activate_starts_periodic_update(plugin) -> None:
    """Test that activate starts periodic updates."""
    widget = Clock(ClockConfig(interval=2.0), plugin)
    widget.request_periodic_update = MagicMock()

    await widget.activate()

    widget.request_periodic_update.assert_called_once_with(2.0)


async def test_clock_deactivate_resets_state(plugin) -> None:
    """Test that deactivate resets state."""
    widget = Clock(ClockConfig(), plugin)
    widget.last_time = "12:34"

    await widget.deactivate()

    # Tasks are cleaned up automatically by Deck, not by widget
    assert widget.last_time == ""


def test_clock_config_defaults() -> None:
    """Test ClockConfig default values."""
    config = ClockConfig()
    assert len(config.segments) == 1
    assert config.segments[0].format == "%H:%M"
    assert config.segments[0].x == 0
    assert config.segments[0].y == 0
    assert config.segments[0].width == 96
    assert config.segments[0].height == 96
    assert config.font is None
    assert config.color == "white"
    assert config.interval == 1.0


def test_clock_config_custom_segments() -> None:
    """Test ClockConfig with custom segments."""
    config = ClockConfig(
        font="Ubuntu:style=Bold",
        color="#ff0000",
        interval=0.5,
        segments=[
            ClockSegment(format="%H", x=0, y=0, width=48, height=32),
            ClockSegment(format="%M", x=48, y=0, width=48, height=32),
        ],
    )
    assert len(config.segments) == 2
    assert config.segments[0].format == "%H"
    assert config.segments[0].x == 0
    assert config.segments[0].width == 48
    assert config.segments[1].format == "%M"
    assert config.segments[1].x == 48
    assert config.font == "Ubuntu:style=Bold"
    assert config.color == "#ff0000"
    assert config.interval == 0.5


def test_clock_segment_defaults() -> None:
    """Test ClockSegment default values."""
    segment = ClockSegment(format="%H", x=10, y=20, width=30, height=40)
    assert segment.format == "%H"
    assert segment.x == 10
    assert segment.y == 20
    assert segment.width == 30
    assert segment.height == 40
    assert segment.font is None
    assert segment.color is None
    assert segment.anchor == "mm"


def test_clock_segment_custom_values() -> None:
    """Test ClockSegment with custom values."""
    segment = ClockSegment(
        format="%M",
        x=5,
        y=10,
        width=50,
        height=25,
        font="monospace",
        color="#00ff00",
        anchor="lt",
    )
    assert segment.format == "%M"
    assert segment.x == 5
    assert segment.y == 10
    assert segment.width == 50
    assert segment.height == 25
    assert segment.font == "monospace"
    assert segment.color == "#00ff00"
    assert segment.anchor == "lt"

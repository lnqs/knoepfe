from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from knoepfe.config.plugin import EmptyPluginConfig
from knoepfe.plugins import Plugin
from knoepfe.widgets.builtin.text import Text, TextConfig


async def test_text_update() -> None:
    """Test that Text widget updates correctly."""
    # Create plugin instance
    config = EmptyPluginConfig()
    plugin = Plugin(config)

    # Create widget with config
    widget = Text(TextConfig(text="Test Text"), plugin)

    # Mock renderer
    renderer = MagicMock()

    # Update widget
    await widget.update(renderer)

    # Verify text_wrapped was called
    assert renderer.text_wrapped.called


def test_text_config_validation() -> None:
    """Test that Text widget validates config correctly."""

    config = EmptyPluginConfig()
    plugin = Plugin(config)

    # Valid config should work
    widget = Text(TextConfig(text="Valid"), plugin)
    assert widget.config.text == "Valid"

    # Missing required field should raise ValidationError
    with pytest.raises(ValidationError):
        TextConfig()  # type: ignore[call-arg]


async def test_text_with_font_and_color() -> None:
    """Test that Text widget uses custom font and color."""
    config = EmptyPluginConfig()
    plugin = Plugin(config)

    # Create widget with custom font and color
    widget = Text(TextConfig(text="Styled Text", font="sans:style=Bold", color="#ff0000"), plugin)

    # Mock renderer
    renderer = MagicMock()

    # Update widget
    await widget.update(renderer)

    # Verify text_wrapped was called with font and color
    renderer.text_wrapped.assert_called_once_with("Styled Text", font="sans:style=Bold", color="#ff0000")


async def test_text_with_defaults() -> None:
    """Test that Text widget works with default font and color."""
    config = EmptyPluginConfig()
    plugin = Plugin(config)

    # Create widget with defaults
    widget = Text(TextConfig(text="Plain Text"), plugin)

    # Mock renderer
    renderer = MagicMock()

    # Update widget
    await widget.update(renderer)

    # Verify text_wrapped was called with default color (font is None)
    renderer.text_wrapped.assert_called_once_with("Plain Text", font=None, color="white")

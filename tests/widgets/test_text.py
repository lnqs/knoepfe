from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from knoepfe.config.plugin import EmptyPluginConfig
from knoepfe.plugins import PluginContext
from knoepfe.widgets.builtin.text import Text, TextConfig


async def test_text_update() -> None:
    """Test that Text widget updates correctly."""
    # Create plugin context
    config = EmptyPluginConfig()
    context = PluginContext(config)

    # Create widget with config
    widget = Text(TextConfig(text="Test Text"), context)

    # Mock key
    key = MagicMock()

    # Update widget
    await widget.update(key)

    # Verify text_wrapped was called
    assert key.renderer.return_value.__enter__.return_value.text_wrapped.called


def test_text_config_validation() -> None:
    """Test that Text widget validates config correctly."""

    config = EmptyPluginConfig()
    context = PluginContext(config)

    # Valid config should work
    widget = Text(TextConfig(text="Valid"), context)
    assert widget.config.text == "Valid"

    # Missing required field should raise ValidationError
    with pytest.raises(ValidationError):
        TextConfig()


async def test_text_with_font_and_color() -> None:
    """Test that Text widget uses custom font and color."""
    config = EmptyPluginConfig()
    context = PluginContext(config)

    # Create widget with custom font and color
    widget = Text(TextConfig(text="Styled Text", font="sans:style=Bold", color="#ff0000"), context)

    # Mock key
    key = MagicMock()

    # Update widget
    await widget.update(key)

    # Verify text_wrapped was called with font and color
    renderer = key.renderer.return_value.__enter__.return_value
    renderer.text_wrapped.assert_called_once_with("Styled Text", font="sans:style=Bold", color="#ff0000")


async def test_text_with_defaults() -> None:
    """Test that Text widget works with default font and color."""
    config = EmptyPluginConfig()
    context = PluginContext(config)

    # Create widget with defaults
    widget = Text(TextConfig(text="Plain Text"), context)

    # Mock key
    key = MagicMock()

    # Update widget
    await widget.update(key)

    # Verify text_wrapped was called with default color (font is None)
    renderer = key.renderer.return_value.__enter__.return_value
    renderer.text_wrapped.assert_called_once_with("Plain Text", font=None, color="white")

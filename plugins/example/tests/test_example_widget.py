"""Tests for the ExampleWidget."""

from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from knoepfe_example_plugin.config import ExamplePluginConfig
from knoepfe_example_plugin.context import ExamplePluginContext
from knoepfe_example_plugin.example_widget import ExampleWidget, ExampleWidgetConfig


class TestExampleWidget:
    """Test cases for ExampleWidget."""

    def test_init_with_defaults(self):
        """Test widget initialization with default configuration."""
        widget_config = ExampleWidgetConfig()
        context = ExamplePluginContext(ExamplePluginConfig())

        widget = ExampleWidget(widget_config, context)

        assert widget._click_count == 0
        assert widget.config.message == "Example"  # Default value

    def test_init_with_custom_config(self):
        """Test widget initialization with custom configuration."""
        widget_config = ExampleWidgetConfig(message="Custom Message")
        context = ExamplePluginContext(ExamplePluginConfig())

        widget = ExampleWidget(widget_config, context)

        assert widget.config.message == "Custom Message"

    @pytest.mark.asyncio
    async def test_activate_resets_click_count(self):
        """Test that activate resets the click count."""
        context = ExamplePluginContext(ExamplePluginConfig())
        widget = ExampleWidget(ExampleWidgetConfig(), context)
        widget._click_count = 5

        await widget.activate()

        assert widget._click_count == 0

    @pytest.mark.asyncio
    async def test_deactivate(self):
        """Test deactivate method."""
        context = ExamplePluginContext(ExamplePluginConfig())
        widget = ExampleWidget(ExampleWidgetConfig(), context)

        # Should not raise any exceptions
        await widget.deactivate()

    @pytest.mark.asyncio
    async def test_update_with_defaults(self):
        """Test update method with default configuration."""
        context = ExamplePluginContext(ExamplePluginConfig())
        widget = ExampleWidget(ExampleWidgetConfig(), context)

        # Mock the key and renderer
        mock_renderer = Mock()
        mock_key = Mock()
        mock_key.renderer.return_value.__enter__ = Mock(return_value=mock_renderer)
        mock_key.renderer.return_value.__exit__ = Mock(return_value=None)

        await widget.update(mock_key)

        # Verify renderer was called
        mock_key.renderer.assert_called_once()
        mock_renderer.clear.assert_called_once()
        mock_renderer.text_wrapped.assert_called_once_with("Example\nClick me!")

    @pytest.mark.asyncio
    async def test_update_with_custom_config(self):
        """Test update method with custom configuration."""
        widget_config = ExampleWidgetConfig(message="Hello")
        context = ExamplePluginContext(ExamplePluginConfig())
        widget = ExampleWidget(widget_config, context)

        # Mock the key and renderer
        mock_renderer = Mock()
        mock_key = Mock()
        mock_key.renderer.return_value.__enter__ = Mock(return_value=mock_renderer)
        mock_key.renderer.return_value.__exit__ = Mock(return_value=None)

        await widget.update(mock_key)

        # Verify renderer was called with custom values
        mock_renderer.clear.assert_called_once()
        mock_renderer.text_wrapped.assert_called_once_with("Hello\nClick me!")

    @pytest.mark.asyncio
    async def test_update_after_clicks(self):
        """Test update method after some clicks."""
        context = ExamplePluginContext(ExamplePluginConfig())
        widget = ExampleWidget(ExampleWidgetConfig(), context)
        widget._click_count = 3

        # Mock the key and renderer
        mock_renderer = Mock()
        mock_key = Mock()
        mock_key.renderer.return_value.__enter__ = Mock(return_value=mock_renderer)
        mock_key.renderer.return_value.__exit__ = Mock(return_value=None)

        await widget.update(mock_key)

        # Verify renderer shows click count
        mock_renderer.clear.assert_called_once()
        mock_renderer.text_wrapped.assert_called_once_with("Example\nClicked 3x")

    @pytest.mark.asyncio
    async def test_on_key_down_increments_counter(self):
        """Test that key down increments click counter."""
        context = ExamplePluginContext(ExamplePluginConfig())
        widget = ExampleWidget(ExampleWidgetConfig(), context)
        widget.request_update = Mock()  # Mock the request_update method

        initial_count = widget._click_count

        await widget.on_key_down()

        assert widget._click_count == initial_count + 1
        widget.request_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_key_up(self):
        """Test key up handler."""
        context = ExamplePluginContext(ExamplePluginConfig())
        widget = ExampleWidget(ExampleWidgetConfig(), context)

        # Should not raise any exceptions
        await widget.on_key_up()

    def test_widget_config_validation(self):
        """Test configuration validation with Pydantic."""
        # Test that config validates correct configurations
        valid_config = ExampleWidgetConfig(message="Test Message")
        assert valid_config.message == "Test Message"

        # Test defaults
        minimal_config = ExampleWidgetConfig()
        assert minimal_config.message == "Example"

    def test_config_validation_error(self):
        """Test that invalid configuration raises validation error."""
        # Invalid configuration (wrong type)
        with pytest.raises(ValidationError):
            ExampleWidgetConfig(message=123)  # Should be string

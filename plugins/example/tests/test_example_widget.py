"""Tests for the ExampleWidget."""

from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from knoepfe_example_plugin.config import ExamplePluginConfig
from knoepfe_example_plugin.plugin import ExamplePlugin
from knoepfe_example_plugin.widgets.example_widget import ExampleWidget, ExampleWidgetConfig


class TestExampleWidget:
    """Test cases for ExampleWidget."""

    def test_init_with_defaults(self):
        """Test widget initialization with default configuration."""
        widget_config = ExampleWidgetConfig()
        plugin = ExamplePlugin(ExamplePluginConfig())

        widget = ExampleWidget(widget_config, plugin)

        assert widget._click_count == 0
        assert widget.config.message == "Example"  # Default value

    def test_init_with_custom_config(self):
        """Test widget initialization with custom configuration."""
        widget_config = ExampleWidgetConfig(message="Custom Message")
        plugin = ExamplePlugin(ExamplePluginConfig())

        widget = ExampleWidget(widget_config, plugin)

        assert widget.config.message == "Custom Message"

    @pytest.mark.asyncio
    async def test_activate_resets_click_count(self):
        """Test that activate resets the click count."""
        plugin = ExamplePlugin(ExamplePluginConfig())
        widget = ExampleWidget(ExampleWidgetConfig(), plugin)
        widget._click_count = 5

        await widget.activate()

        assert widget._click_count == 0

    @pytest.mark.asyncio
    async def test_deactivate(self):
        """Test deactivate method."""
        plugin = ExamplePlugin(ExamplePluginConfig())
        widget = ExampleWidget(ExampleWidgetConfig(), plugin)

        # Should not raise any exceptions
        await widget.deactivate()

    @pytest.mark.asyncio
    async def test_update_with_defaults(self):
        """Test update method with default configuration."""
        plugin = ExamplePlugin(ExamplePluginConfig())
        widget = ExampleWidget(ExampleWidgetConfig(), plugin)

        # Mock the renderer
        mock_renderer = Mock()

        await widget.update(mock_renderer)

        # Verify renderer was called
        mock_renderer.clear.assert_called_once()
        mock_renderer.text_multiline.assert_called_once_with("Example\nClick me!")

    @pytest.mark.asyncio
    async def test_update_with_custom_config(self):
        """Test update method with custom configuration."""
        widget_config = ExampleWidgetConfig(message="Hello")
        plugin = ExamplePlugin(ExamplePluginConfig())
        widget = ExampleWidget(widget_config, plugin)

        # Mock the renderer
        mock_renderer = Mock()

        await widget.update(mock_renderer)

        # Verify renderer was called with custom values
        mock_renderer.clear.assert_called_once()
        mock_renderer.text_multiline.assert_called_once_with("Hello\nClick me!")

    @pytest.mark.asyncio
    async def test_update_after_clicks(self):
        """Test update method after some clicks."""
        plugin = ExamplePlugin(ExamplePluginConfig())
        widget = ExampleWidget(ExampleWidgetConfig(), plugin)
        widget._click_count = 3

        # Mock the renderer
        mock_renderer = Mock()

        await widget.update(mock_renderer)

        # Verify renderer shows click count
        mock_renderer.clear.assert_called_once()
        mock_renderer.text_multiline.assert_called_once_with("Example\nClicked 3x")

    @pytest.mark.asyncio
    async def test_on_key_down_increments_counter(self):
        """Test that key down increments click counter."""
        plugin = ExamplePlugin(ExamplePluginConfig())
        widget = ExampleWidget(ExampleWidgetConfig(), plugin)
        widget.request_update = Mock()  # Mock the request_update method

        initial_count = widget._click_count

        await widget.on_key_down()

        assert widget._click_count == initial_count + 1
        widget.request_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_key_up(self):
        """Test key up handler."""
        plugin = ExamplePlugin(ExamplePluginConfig())
        widget = ExampleWidget(ExampleWidgetConfig(), plugin)

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
            ExampleWidgetConfig(message=123)  # type: ignore[arg-type]  # Should be string

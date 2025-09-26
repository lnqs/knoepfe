"""Tests for the ExampleWidget."""

from unittest.mock import Mock

import pytest
from schema import SchemaError

from knoepfe_example_plugin.example_widget import ExampleWidget


class TestExampleWidget:
    """Test cases for ExampleWidget."""

    def test_init_with_defaults(self):
        """Test widget initialization with default configuration."""
        widget_config = {}
        global_config = {}

        widget = ExampleWidget(widget_config, global_config)

        assert widget._click_count == 0
        assert widget.config == widget_config
        assert widget.global_config == global_config

    def test_init_with_custom_config(self):
        """Test widget initialization with custom configuration."""
        widget_config = {"message": "Custom Message"}
        global_config = {}

        widget = ExampleWidget(widget_config, global_config)

        assert widget.config["message"] == "Custom Message"

    @pytest.mark.asyncio
    async def test_activate_resets_click_count(self):
        """Test that activate resets the click count."""
        widget = ExampleWidget({}, {})
        widget._click_count = 5

        await widget.activate()

        assert widget._click_count == 0

    @pytest.mark.asyncio
    async def test_deactivate(self):
        """Test deactivate method."""
        widget = ExampleWidget({}, {})

        # Should not raise any exceptions
        await widget.deactivate()

    @pytest.mark.asyncio
    async def test_update_with_defaults(self):
        """Test update method with default configuration."""
        widget = ExampleWidget({}, {})

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
        widget_config = {"message": "Hello"}
        widget = ExampleWidget(widget_config, {})

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
        widget = ExampleWidget({}, {})
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
        widget = ExampleWidget({}, {})
        widget.request_update = Mock()  # Mock the request_update method

        initial_count = widget._click_count

        await widget.on_key_down()

        assert widget._click_count == initial_count + 1
        widget.request_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_key_up(self):
        """Test key up handler."""
        widget = ExampleWidget({}, {})

        # Should not raise any exceptions
        await widget.on_key_up()

    def test_get_config_schema(self):
        """Test configuration schema."""
        schema = ExampleWidget.get_config_schema()

        # Test that schema validates correct configurations
        valid_config = {"message": "Test Message"}
        validated = schema.validate(valid_config)
        assert validated["message"] == "Test Message"

        # Test defaults
        minimal_config = {}
        validated = schema.validate(minimal_config)
        assert validated["message"] == "Example"

    def test_config_schema_validation_error(self):
        """Test that invalid configuration raises validation error."""
        schema = ExampleWidget.get_config_schema()

        # Invalid configuration (wrong type)
        invalid_config = {
            "message": 123,  # Should be string
        }

        with pytest.raises(SchemaError):  # Schema validation error
            schema.validate(invalid_config)

from unittest.mock import Mock, patch

import pytest
from schema import Schema

from knoepfe.plugin_manager import PluginManager, plugin_manager
from knoepfe.widgets.base import Widget


class MockWidget(Widget):
    """Mock widget for testing."""

    def __init__(self, widget_config: dict, global_config: dict):
        super().__init__(widget_config, global_config)

    @classmethod
    def get_config_schema(cls) -> Schema:
        return Schema({"test_param": str})


class MockWidgetNoSchema(Widget):
    """Mock widget without schema for testing."""

    def __init__(self, widget_config: dict, global_config: dict):
        super().__init__(widget_config, global_config)

    # Intentionally no get_config_schema method to test the case where it's missing


def test_plugin_manager_init():
    """Test PluginManager initialization."""
    with patch("knoepfe.plugin_manager.entry_points") as mock_entry_points:
        # Mock entry points
        mock_ep1 = Mock()
        mock_ep1.name = "TestWidget"
        mock_ep1.load.return_value = MockWidget
        mock_ep1.dist = "test-package"

        mock_ep2 = Mock()
        mock_ep2.name = "AnotherWidget"
        mock_ep2.load.return_value = MockWidgetNoSchema
        mock_ep2.dist = "another-package"

        mock_entry_points.return_value = [mock_ep1, mock_ep2]

        pm = PluginManager()

        assert "TestWidget" in pm._widget_plugins
        assert "AnotherWidget" in pm._widget_plugins
        assert pm._widget_plugins["TestWidget"] == MockWidget
        assert pm._widget_plugins["AnotherWidget"] == MockWidgetNoSchema


def test_plugin_manager_load_plugins_with_error():
    """Test PluginManager handles loading errors gracefully."""
    with patch("knoepfe.plugin_manager.entry_points") as mock_entry_points:
        # Mock entry point that fails to load
        mock_ep = Mock()
        mock_ep.name = "FailingWidget"
        mock_ep.load.side_effect = ImportError("Module not found")

        mock_entry_points.return_value = [mock_ep]

        with patch("knoepfe.plugin_manager.logger") as mock_logger:
            pm = PluginManager()

            # Should not contain the failing widget
            assert "FailingWidget" not in pm._widget_plugins
            # Should log the error
            mock_logger.error.assert_called_once()


def test_plugin_manager_get_widget_success():
    """Test getting a widget successfully."""
    pm = PluginManager()
    pm._widget_plugins["TestWidget"] = MockWidget

    widget_class = pm.get_widget("TestWidget")
    assert widget_class == MockWidget


def test_plugin_manager_get_widget_not_found():
    """Test getting a non-existent widget raises ValueError."""
    pm = PluginManager()
    pm._widget_plugins = {"ExistingWidget": MockWidget}

    with pytest.raises(ValueError, match="Widget 'NonExistentWidget' not found"):
        pm.get_widget("NonExistentWidget")


def test_plugin_manager_list_widgets():
    """Test listing all available widgets."""
    pm = PluginManager()
    pm._widget_plugins = {
        "Widget1": MockWidget,
        "Widget2": MockWidgetNoSchema,
    }

    widgets = pm.list_widgets()
    assert set(widgets) == {"Widget1", "Widget2"}


def test_plugin_manager_list_widgets_empty():
    """Test listing widgets when none are available."""
    pm = PluginManager()
    pm._widget_plugins = {}

    widgets = pm.list_widgets()
    assert widgets == []


def test_global_plugin_manager_instance():
    """Test that the global plugin_manager instance exists."""
    assert isinstance(plugin_manager, PluginManager)


def test_plugin_manager_integration_with_entry_points():
    """Test plugin manager integration with real entry points (if available)."""
    # This test uses the actual entry points system
    pm = PluginManager()

    # Should at least have the built-in widgets
    widgets = pm.list_widgets()
    assert len(widgets) >= 3  # Clock, Text, Timer at minimum

    # Test getting a built-in widget
    if "Clock" in widgets:
        clock_class = pm.get_widget("Clock")
        assert clock_class.__name__ == "Clock"
        assert "knoepfe.widgets.clock" in clock_class.__module__

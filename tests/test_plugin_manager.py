"""Tests for plugin manager functionality."""

from unittest.mock import Mock, patch

import pytest
from schema import Schema

from knoepfe.plugin import Plugin
from knoepfe.plugin_manager import PluginManager, PluginNotFoundError
from knoepfe.widgets.base import Widget


class MockWidget(Widget):
    name = "MockWidget"

    @classmethod
    def get_config_schema(cls) -> Schema:
        return Schema({"test": str})


class MockWidgetNoSchema(Widget):
    name = "MockWidgetNoSchema"


class MockPlugin(Plugin):
    name = "MockPlugin"

    def __init__(self, config: dict):
        super().__init__(config)

    @property
    def widgets(self) -> list[type[Widget]]:
        return [MockWidget, MockWidgetNoSchema]

    @property
    def config_schema(self) -> Schema | None:
        return Schema({"test_config": str})


class MockPlugin1(Plugin):
    name = "Plugin1"

    def __init__(self, config: dict):
        super().__init__(config)

    @property
    def widgets(self) -> list[type[Widget]]:
        return []

    @property
    def config_schema(self) -> Schema | None:
        return None


class MockPlugin2(Plugin):
    name = "Plugin2"

    def __init__(self, config: dict):
        super().__init__(config)

    @property
    def widgets(self) -> list[type[Widget]]:
        return []

    @property
    def config_schema(self) -> Schema | None:
        return None


def test_plugin_manager_init():
    """Test PluginManager initialization."""
    with patch("knoepfe.plugin_manager.entry_points") as mock_entry_points:
        # Mock plugin entry points
        mock_ep1 = Mock()
        mock_ep1.name = "test"
        mock_ep1.load.return_value = MockPlugin
        # Mock the distribution object properly
        mock_dist = Mock()
        mock_dist.name = "test-package"
        mock_dist.version = "1.0.0"
        mock_dist.metadata = {"Summary": "Test plugin for testing"}
        mock_ep1.dist = mock_dist

        mock_entry_points.return_value = [mock_ep1]

        # Set plugin config to satisfy schema requirements
        pm = PluginManager()
        pm.set_plugin_config("test", {"test_config": "value"})

        # Reload plugins to pick up the config
        pm._load_plugins()

        # Check that plugin is registered
        assert "MockPlugin" in pm.list_plugins()

        # Check that plugin widgets are available from plugin manager
        widgets = pm.get_all_widgets()
        widget_names = [w.name for w in widgets]
        assert "MockWidget" in widget_names
        assert "MockWidgetNoSchema" in widget_names


def test_plugin_manager_load_plugins_with_error():
    """Test PluginManager handles loading errors gracefully."""
    with patch("knoepfe.plugin_manager.entry_points") as mock_entry_points:
        # Mock entry point that fails to load
        mock_ep = Mock()
        mock_ep.name = "failing_plugin"
        mock_ep.load.side_effect = Exception("Failed to load")

        mock_entry_points.return_value = [mock_ep]

        with patch("knoepfe.plugin_manager.logger") as mock_logger:
            pm = PluginManager()

            # Should not have registered the failing plugin
            assert "failing_plugin" not in pm.list_plugins()
            mock_logger.exception.assert_called_once()


def test_plugin_manager_get_plugin():
    """Test getting a plugin successfully."""
    pm = PluginManager()
    plugin = MockPlugin({"test_config": "value"})
    pm.register_plugin(plugin, "1.0.0", "Test plugin")

    retrieved_plugin = pm.get_plugin("MockPlugin")
    assert retrieved_plugin == plugin


def test_plugin_manager_get_nonexistent_plugin():
    """Test getting a non-existent plugin raises PluginNotFoundError."""
    pm = PluginManager()

    with pytest.raises(PluginNotFoundError):
        pm.get_plugin("NonExistentPlugin")


def test_plugin_manager_list_plugins():
    """Test listing all available plugins."""
    pm = PluginManager()
    plugin1 = MockPlugin1({})
    plugin2 = MockPlugin2({})

    pm.register_plugin(plugin1, "1.0.0", "Test plugin 1")
    pm.register_plugin(plugin2, "1.0.0", "Test plugin 2")

    plugins = pm.list_plugins()
    assert "Plugin1" in plugins
    assert "Plugin2" in plugins


def test_plugin_manager_set_plugin_config():
    """Test setting plugin configuration."""
    pm = PluginManager()
    config = {"test_key": "test_value"}

    pm.set_plugin_config("test_plugin", config)
    assert pm._plugin_configs["test_plugin"] == config


def test_plugin_manager_register_plugin():
    """Test registering a plugin."""
    pm = PluginManager()
    plugin = MockPlugin({"test_config": "value"})

    pm.register_plugin(plugin, "1.0.0", "Test plugin")

    assert "MockPlugin" in pm.list_plugins()
    assert pm.get_plugin("MockPlugin") == plugin

    # Check that plugin widgets are available from plugin manager
    widgets = pm.get_all_widgets()
    widget_names = [w.name for w in widgets]
    assert "MockWidget" in widget_names
    assert "MockWidgetNoSchema" in widget_names


def test_plugin_manager_register_duplicate_plugin():
    """Test registering a plugin with duplicate name raises error."""
    pm = PluginManager()
    plugin1 = MockPlugin({"test_config": "value"})
    plugin2 = MockPlugin({"test_config": "value"})

    pm.register_plugin(plugin1, "1.0.0", "Test plugin 1")

    with pytest.raises(ValueError, match="Plugin name 'MockPlugin' already in use"):
        pm.register_plugin(plugin2, "1.0.0", "Test plugin 2")


def test_plugin_manager_register_plugin_with_duplicate_widget():
    """Test that PluginManager can register plugins with duplicate widget names."""
    pm = PluginManager()

    # Register two plugins with the same widget
    plugin1 = MockPlugin({"test_config": "value"})
    plugin2 = MockPlugin({"test_config": "value"})
    plugin2.name = "MockPlugin2"  # Different plugin name

    pm.register_plugin(plugin1, "1.0.0", "Test plugin 1")
    # This should work since PluginManager doesn't enforce widget uniqueness
    pm.register_plugin(plugin2, "1.0.0", "Test plugin 2")

    # Both plugins should be registered
    assert "MockPlugin" in pm.list_plugins()
    assert "MockPlugin2" in pm.list_plugins()


def test_plugin_manager_get_config_schema():
    """Test getting config schema by plugin name."""
    pm = PluginManager()
    plugin = MockPlugin({"test_config": "value"})
    pm.register_plugin(plugin, "1.0.0", "Test plugin")

    schema = pm.get_config_schema("MockPlugin")
    assert isinstance(schema, Schema)


def test_plugin_manager_get_config_schema_nonexistent():
    """Test getting config schema for non-existent plugin raises error."""
    pm = PluginManager()

    with pytest.raises(PluginNotFoundError):
        pm.get_config_schema("NonExistentPlugin")


def test_plugin_manager_shutdown_all():
    """Test shutting down all plugins."""
    pm = PluginManager()
    plugin = MockPlugin({"test_config": "value"})
    plugin.shutdown = Mock()  # Mock the shutdown method
    pm.register_plugin(plugin, "1.0.0", "Test plugin")

    pm.shutdown_all()
    plugin.shutdown.assert_called_once()

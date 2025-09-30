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
    def config_schema(self) -> Schema:
        return Schema({"test_config": str})


class MockPlugin1(Plugin):
    name = "Plugin1"

    def __init__(self, config: dict):
        super().__init__(config)

    @property
    def widgets(self) -> list[type[Widget]]:
        return []

    @property
    def config_schema(self) -> Schema:
        return Schema({})


class MockPlugin2(Plugin):
    name = "Plugin2"

    def __init__(self, config: dict):
        super().__init__(config)

    @property
    def widgets(self) -> list[type[Widget]]:
        return []

    @property
    def config_schema(self) -> Schema:
        return Schema({})


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

        # Check that plugin is registered (name comes from entry point, not class)
        assert "test" in pm._plugins

        # Check that plugin widgets are available from plugin manager
        assert "MockWidget" in pm._widgets
        assert "MockWidgetNoSchema" in pm._widgets


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
            assert "failing_plugin" not in pm._plugins
            mock_logger.exception.assert_called_once()


def test_plugin_manager_get_plugin():
    """Test getting a plugin successfully."""
    with patch("knoepfe.plugin_manager.entry_points") as mock_entry_points:
        # Mock plugin entry point
        mock_ep = Mock()
        mock_ep.name = "test_plugin"
        mock_ep.load.return_value = MockPlugin
        mock_dist = Mock()
        mock_dist.name = "test-package"
        mock_dist.version = "1.0.0"
        mock_dist.metadata = {"Summary": "Test plugin"}
        mock_ep.dist = mock_dist
        mock_entry_points.return_value = [mock_ep]

        pm = PluginManager()
        pm.set_plugin_config("test_plugin", {"test_config": "value"})
        pm._load_plugins()

        retrieved_plugin = pm.get_plugin("test_plugin")
        assert isinstance(retrieved_plugin, MockPlugin)


def test_plugin_manager_get_nonexistent_plugin():
    """Test getting a non-existent plugin raises PluginNotFoundError."""
    pm = PluginManager()

    with pytest.raises(PluginNotFoundError):
        pm.get_plugin("NonExistentPlugin")


def test_plugin_manager_list_plugins():
    """Test listing all available plugins."""
    with patch("knoepfe.plugin_manager.entry_points") as mock_entry_points:
        # Mock two plugin entry points
        mock_ep1 = Mock()
        mock_ep1.name = "plugin1"
        mock_ep1.load.return_value = MockPlugin1
        mock_dist1 = Mock()
        mock_dist1.name = "plugin1-package"
        mock_dist1.version = "1.0.0"
        mock_dist1.metadata = {"Summary": "Test plugin 1"}
        mock_ep1.dist = mock_dist1

        mock_ep2 = Mock()
        mock_ep2.name = "plugin2"
        mock_ep2.load.return_value = MockPlugin2
        mock_dist2 = Mock()
        mock_dist2.name = "plugin2-package"
        mock_dist2.version = "1.0.0"
        mock_dist2.metadata = {"Summary": "Test plugin 2"}
        mock_ep2.dist = mock_dist2

        mock_entry_points.return_value = [mock_ep1, mock_ep2]

        pm = PluginManager()

        assert "plugin1" in pm._plugins
        assert "plugin2" in pm._plugins


def test_plugin_manager_set_plugin_config():
    """Test setting plugin configuration."""
    pm = PluginManager()
    config = {"test_key": "test_value"}

    pm.set_plugin_config("test_plugin", config)
    assert pm._plugin_configs["test_plugin"] == config


def test_plugin_manager_register_plugin():
    """Test that plugins are registered via entry points."""
    with patch("knoepfe.plugin_manager.entry_points") as mock_entry_points:
        # Mock plugin entry point
        mock_ep = Mock()
        mock_ep.name = "test_plugin"
        mock_ep.load.return_value = MockPlugin
        mock_dist = Mock()
        mock_dist.name = "test-package"
        mock_dist.version = "1.0.0"
        mock_dist.metadata = {"Summary": "Test plugin"}
        mock_ep.dist = mock_dist
        mock_entry_points.return_value = [mock_ep]

        pm = PluginManager()
        pm.set_plugin_config("test_plugin", {"test_config": "value"})
        pm._load_plugins()

        assert "test_plugin" in pm._plugins
        assert isinstance(pm.get_plugin("test_plugin"), MockPlugin)

        # Check that plugin widgets are available from plugin manager
        assert "MockWidget" in pm._widgets
        assert "MockWidgetNoSchema" in pm._widgets


def test_plugin_manager_register_duplicate_plugin():
    """Test that duplicate plugin names in entry points are handled."""
    with patch("knoepfe.plugin_manager.entry_points") as mock_entry_points:
        # Mock two entry points with the same name (shouldn't happen in practice)
        mock_ep1 = Mock()
        mock_ep1.name = "test_plugin"
        mock_ep1.load.return_value = MockPlugin
        mock_dist1 = Mock()
        mock_dist1.name = "test-package-1"
        mock_dist1.version = "1.0.0"
        mock_dist1.metadata = {"Summary": "Test plugin 1"}
        mock_ep1.dist = mock_dist1

        mock_ep2 = Mock()
        mock_ep2.name = "test_plugin"  # Same name
        mock_ep2.load.return_value = MockPlugin
        mock_dist2 = Mock()
        mock_dist2.name = "test-package-2"
        mock_dist2.version = "1.0.0"
        mock_dist2.metadata = {"Summary": "Test plugin 2"}
        mock_ep2.dist = mock_dist2

        mock_entry_points.return_value = [mock_ep1, mock_ep2]

        pm = PluginManager()
        pm.set_plugin_config("test_plugin", {"test_config": "value"})
        pm._load_plugins()

        # Second plugin should overwrite the first
        assert "test_plugin" in pm._plugins
        assert len([p for p in pm._plugins if p == "test_plugin"]) == 1


def test_plugin_manager_register_plugin_with_duplicate_widget():
    """Test that PluginManager warns about duplicate widget names."""
    with patch("knoepfe.plugin_manager.entry_points") as mock_entry_points:
        with patch("knoepfe.plugin_manager.logger") as mock_logger:
            # Mock two plugins with the same widget names
            mock_ep1 = Mock()
            mock_ep1.name = "plugin1"
            mock_ep1.load.return_value = MockPlugin
            mock_dist1 = Mock()
            mock_dist1.name = "plugin1-package"
            mock_dist1.version = "1.0.0"
            mock_dist1.metadata = {"Summary": "Test plugin 1"}
            mock_ep1.dist = mock_dist1

            mock_ep2 = Mock()
            mock_ep2.name = "plugin2"
            mock_ep2.load.return_value = MockPlugin  # Same widgets
            mock_dist2 = Mock()
            mock_dist2.name = "plugin2-package"
            mock_dist2.version = "1.0.0"
            mock_dist2.metadata = {"Summary": "Test plugin 2"}
            mock_ep2.dist = mock_dist2

            mock_entry_points.return_value = [mock_ep1, mock_ep2]

            pm = PluginManager()
            pm.set_plugin_config("plugin1", {"test_config": "value"})
            pm.set_plugin_config("plugin2", {"test_config": "value"})
            pm._load_plugins()

            # Both plugins should be registered
            assert "plugin1" in pm._plugins
            assert "plugin2" in pm._plugins

            # Should have logged warnings about duplicate widgets
            assert mock_logger.warning.called


def test_plugin_manager_get_config_schema():
    """Test getting config schema by plugin name."""
    with patch("knoepfe.plugin_manager.entry_points") as mock_entry_points:
        # Mock plugin entry point
        mock_ep = Mock()
        mock_ep.name = "test_plugin"
        mock_ep.load.return_value = MockPlugin
        mock_dist = Mock()
        mock_dist.name = "test-package"
        mock_dist.version = "1.0.0"
        mock_dist.metadata = {"Summary": "Test plugin"}
        mock_ep.dist = mock_dist
        mock_entry_points.return_value = [mock_ep]

        pm = PluginManager()
        pm.set_plugin_config("test_plugin", {"test_config": "value"})
        pm._load_plugins()

        plugin = pm.get_plugin("test_plugin")
        schema = plugin.config_schema
        assert isinstance(schema, Schema)


def test_plugin_manager_get_config_schema_nonexistent():
    """Test getting config schema for non-existent plugin raises error."""
    pm = PluginManager()

    with pytest.raises(PluginNotFoundError):
        pm.get_plugin("NonExistentPlugin")


def test_plugin_manager_shutdown_all():
    """Test shutting down all plugins."""
    with patch("knoepfe.plugin_manager.entry_points") as mock_entry_points:
        # Mock plugin entry point
        mock_ep = Mock()
        mock_ep.name = "test_plugin"
        mock_ep.load.return_value = MockPlugin
        mock_dist = Mock()
        mock_dist.name = "test-package"
        mock_dist.version = "1.0.0"
        mock_dist.metadata = {"Summary": "Test plugin"}
        mock_ep.dist = mock_dist
        mock_entry_points.return_value = [mock_ep]

        pm = PluginManager()
        pm.set_plugin_config("test_plugin", {"test_config": "value"})
        pm._load_plugins()

        # Get the plugin instance and mock its shutdown method
        plugin = pm.get_plugin("test_plugin")
        plugin.shutdown = Mock()

        pm.shutdown_all()
        plugin.shutdown.assert_called_once()

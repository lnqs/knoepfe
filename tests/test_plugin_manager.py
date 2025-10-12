"""Tests for plugin manager functionality."""

from unittest.mock import Mock, patch

import pytest
from pydantic import Field

from knoepfe.config.plugin import EmptyPluginConfig, PluginConfig
from knoepfe.config.widget import EmptyConfig
from knoepfe.plugins.descriptor import PluginDescriptor
from knoepfe.plugins.manager import PluginManager
from knoepfe.plugins.plugin import Plugin
from knoepfe.widgets.base import Widget


class MockWidgetConfig(EmptyConfig):
    """Config for mock widget."""

    pass


class MockWidget(Widget[MockWidgetConfig, Plugin]):
    name = "MockWidget"
    description = "A mock widget for testing"

    async def update(self, key):
        pass


class MockWidgetNoSchema(Widget[EmptyConfig, Plugin]):
    name = "MockWidgetNoSchema"

    async def update(self, key):
        pass


class MockPluginDescriptorConfig(PluginConfig):
    """Config for mock plugin."""

    test_config: str = Field(default="default", description="Test configuration")


class MockPluginDescriptor(PluginDescriptor[MockPluginDescriptorConfig, Plugin]):
    @classmethod
    def widgets(cls) -> list[type[Widget]]:
        return [MockWidget, MockWidgetNoSchema]


class MockPluginDescriptor1(PluginDescriptor[EmptyPluginConfig, Plugin]):
    @classmethod
    def widgets(cls) -> list[type[Widget]]:
        return []


class MockPluginDescriptor2(PluginDescriptor[EmptyPluginConfig, Plugin]):
    @classmethod
    def widgets(cls) -> list[type[Widget]]:
        return []


def test_plugin_manager_init():
    """Test PluginManager initialization."""
    with patch("knoepfe.plugins.manager.entry_points") as mock_entry_points:
        # Mock plugin entry points
        mock_ep1 = Mock()
        mock_ep1.name = "test"
        mock_ep1.load.return_value = MockPluginDescriptor
        # Mock the distribution object properly
        mock_dist = Mock()
        mock_dist.name = "test-package"
        mock_dist.version = "1.0.0"
        mock_dist.metadata = {"Summary": "Test plugin for testing"}
        mock_ep1.dist = mock_dist

        mock_entry_points.return_value = [mock_ep1]

        # Create plugin manager with config
        pm = PluginManager({"test": {"test_config": "value"}})

        # Check that plugin is registered (name comes from entry point, not class)
        assert "test" in pm._plugins

        # Check that plugin widgets are available from plugin manager
        assert "MockWidget" in pm._widgets
        assert "MockWidgetNoSchema" in pm._widgets


def test_plugin_manager_load_plugins_with_error():
    """Test PluginManager handles loading errors gracefully."""
    with patch("knoepfe.plugins.manager.entry_points") as mock_entry_points:
        # Mock entry point that fails to load
        mock_ep = Mock()
        mock_ep.name = "failing_plugin"
        mock_ep.load.side_effect = Exception("Failed to load")

        mock_entry_points.return_value = [mock_ep]

        with patch("knoepfe.plugins.manager.logger") as mock_logger:
            pm = PluginManager()

            # Should not have registered the failing plugin
            assert "failing_plugin" not in pm._plugins
            mock_logger.exception.assert_called_once()


def test_plugin_manager_get_plugin():
    """Test getting plugin instance successfully."""
    with patch("knoepfe.plugins.manager.entry_points") as mock_entry_points:
        # Mock plugin entry point
        mock_ep = Mock()
        mock_ep.name = "test_plugin"
        mock_ep.load.return_value = MockPluginDescriptor
        mock_dist = Mock()
        mock_dist.name = "test-package"
        mock_dist.version = "1.0.0"
        mock_dist.metadata = {"Summary": "Test plugin"}
        mock_ep.dist = mock_dist
        mock_entry_points.return_value = [mock_ep]

        pm = PluginManager({"test_plugin": {"test_config": "value"}})

        retrieved_plugin = pm.plugins["test_plugin"].plugin
        assert isinstance(retrieved_plugin, Plugin)


def test_plugin_manager_get_nonexistent_plugin():
    """Test getting a non-existent plugin raises KeyError."""
    pm = PluginManager()

    with pytest.raises(KeyError):
        pm.plugins["NonExistentPlugin"]


def test_plugin_manager_list_plugins():
    """Test listing all available plugins."""
    with patch("knoepfe.plugins.manager.entry_points") as mock_entry_points:
        # Mock two plugin entry points
        mock_ep1 = Mock()
        mock_ep1.name = "plugin1"
        mock_ep1.load.return_value = MockPluginDescriptor1
        mock_dist1 = Mock()
        mock_dist1.name = "plugin1-package"
        mock_dist1.version = "1.0.0"
        mock_dist1.metadata = {"Summary": "Test plugin 1"}
        mock_ep1.dist = mock_dist1

        mock_ep2 = Mock()
        mock_ep2.name = "plugin2"
        mock_ep2.load.return_value = MockPluginDescriptor2
        mock_dist2 = Mock()
        mock_dist2.name = "plugin2-package"
        mock_dist2.version = "1.0.0"
        mock_dist2.metadata = {"Summary": "Test plugin 2"}
        mock_ep2.dist = mock_dist2

        mock_entry_points.return_value = [mock_ep1, mock_ep2]

        pm = PluginManager()

        assert "plugin1" in pm._plugins
        assert "plugin2" in pm._plugins


def test_plugin_manager_with_plugin_config():
    """Test plugin manager accepts configuration in constructor."""
    config = {"test_key": "test_value"}
    pm = PluginManager({"test_plugin": config})
    assert pm._plugin_configs["test_plugin"] == config


def test_plugin_manager_register_plugin():
    """Test that plugins are registered via entry points."""
    with patch("knoepfe.plugins.manager.entry_points") as mock_entry_points:
        # Mock plugin entry point
        mock_ep = Mock()
        mock_ep.name = "test_plugin"
        mock_ep.load.return_value = MockPluginDescriptor
        mock_dist = Mock()
        mock_dist.name = "test-package"
        mock_dist.version = "1.0.0"
        mock_dist.metadata = {"Summary": "Test plugin"}
        mock_ep.dist = mock_dist
        mock_entry_points.return_value = [mock_ep]

        pm = PluginManager({"test_plugin": {"test_config": "value"}})

        assert "test_plugin" in pm.plugins
        # Verify plugin info contains the plugin class
        assert pm.plugins["test_plugin"].descriptor_class == MockPluginDescriptor
        # Verify plugin was created
        assert isinstance(pm.plugins["test_plugin"].plugin, Plugin)

        # Check that plugin widgets are available from plugin manager
        assert "MockWidget" in pm.widgets
        assert "MockWidgetNoSchema" in pm.widgets


def test_plugin_manager_register_duplicate_plugin():
    """Test that duplicate plugin names in entry points are handled."""
    with patch("knoepfe.plugins.manager.entry_points") as mock_entry_points:
        # Mock two entry points with the same name (shouldn't happen in practice)
        mock_ep1 = Mock()
        mock_ep1.name = "test_plugin"
        mock_ep1.load.return_value = MockPluginDescriptor
        mock_dist1 = Mock()
        mock_dist1.name = "test-package-1"
        mock_dist1.version = "1.0.0"
        mock_dist1.metadata = {"Summary": "Test plugin 1"}
        mock_ep1.dist = mock_dist1

        mock_ep2 = Mock()
        mock_ep2.name = "test_plugin"  # Same name
        mock_ep2.load.return_value = MockPluginDescriptor
        mock_dist2 = Mock()
        mock_dist2.name = "test-package-2"
        mock_dist2.version = "1.0.0"
        mock_dist2.metadata = {"Summary": "Test plugin 2"}
        mock_ep2.dist = mock_dist2

        mock_entry_points.return_value = [mock_ep1, mock_ep2]

        pm = PluginManager({"test_plugin": {"test_config": "value"}})

        # Second plugin should overwrite the first
        assert "test_plugin" in pm._plugins
        assert len([p for p in pm._plugins if p == "test_plugin"]) == 1


def test_plugin_manager_register_plugin_with_duplicate_widget():
    """Test that PluginManager warns about duplicate widget names."""
    with patch("knoepfe.plugins.manager.entry_points") as mock_entry_points:
        with patch("knoepfe.plugins.manager.logger") as mock_logger:
            # Mock two plugins with the same widget names
            mock_ep1 = Mock()
            mock_ep1.name = "plugin1"
            mock_ep1.load.return_value = MockPluginDescriptor
            mock_dist1 = Mock()
            mock_dist1.name = "plugin1-package"
            mock_dist1.version = "1.0.0"
            mock_dist1.metadata = {"Summary": "Test plugin 1"}
            mock_ep1.dist = mock_dist1

            mock_ep2 = Mock()
            mock_ep2.name = "plugin2"
            mock_ep2.load.return_value = MockPluginDescriptor  # Same widgets
            mock_dist2 = Mock()
            mock_dist2.name = "plugin2-package"
            mock_dist2.version = "1.0.0"
            mock_dist2.metadata = {"Summary": "Test plugin 2"}
            mock_ep2.dist = mock_dist2

            mock_entry_points.return_value = [mock_ep1, mock_ep2]

            pm = PluginManager({"plugin1": {"test_config": "value"}, "plugin2": {"test_config": "value"}})

            # Both plugins should be registered
            assert "plugin1" in pm._plugins
            assert "plugin2" in pm._plugins

            # Should have logged warnings about duplicate widgets
            assert mock_logger.warning.called


def test_plugin_manager_shutdown_all():
    """Test shutting down all plugins."""
    with patch("knoepfe.plugins.manager.entry_points") as mock_entry_points:
        # Mock plugin entry point
        mock_ep = Mock()
        mock_ep.name = "test_plugin"
        mock_ep.load.return_value = MockPluginDescriptor
        mock_dist = Mock()
        mock_dist.name = "test-package"
        mock_dist.version = "1.0.0"
        mock_dist.metadata = {"Summary": "Test plugin"}
        mock_ep.dist = mock_dist
        mock_entry_points.return_value = [mock_ep]

        pm = PluginManager({"test_plugin": {"test_config": "value"}})

        # Get the plugin instance and mock its shutdown method
        plugin = pm.plugins["test_plugin"].plugin
        plugin.shutdown = Mock()

        pm.shutdown_all()
        plugin.shutdown.assert_called_once()


def test_plugin_manager_disabled_plugin():
    """Test that disabled plugins are not loaded."""
    with patch("knoepfe.plugins.manager.entry_points") as mock_entry_points:
        with patch("knoepfe.plugins.manager.logger") as mock_logger:
            # Mock plugin entry point
            mock_ep = Mock()
            mock_ep.name = "test_plugin"
            mock_ep.load.return_value = MockPluginDescriptor
            mock_dist = Mock()
            mock_dist.name = "test-package"
            mock_dist.version = "1.0.0"
            mock_dist.metadata = {"Summary": "Test plugin"}
            mock_ep.dist = mock_dist
            mock_entry_points.return_value = [mock_ep]

            # Create plugin manager with disabled plugin
            pm = PluginManager({"test_plugin": {"enabled": False}})

            # Plugin should not be registered
            assert "test_plugin" not in pm._plugins

            # Widgets from disabled plugin should not be available
            assert "MockWidget" not in pm._widgets
            assert "MockWidgetNoSchema" not in pm._widgets

            # Should have logged that plugin was skipped
            mock_logger.info.assert_called_with("Plugin 'test_plugin' is disabled in config, skipping")


def test_plugin_manager_enabled_plugin_explicit():
    """Test that explicitly enabled plugins are loaded."""
    with patch("knoepfe.plugins.manager.entry_points") as mock_entry_points:
        # Mock plugin entry point
        mock_ep = Mock()
        mock_ep.name = "test_plugin"
        mock_ep.load.return_value = MockPluginDescriptor
        mock_dist = Mock()
        mock_dist.name = "test-package"
        mock_dist.version = "1.0.0"
        mock_dist.metadata = {"Summary": "Test plugin"}
        mock_ep.dist = mock_dist
        mock_entry_points.return_value = [mock_ep]

        # Create plugin manager with explicitly enabled plugin
        pm = PluginManager({"test_plugin": {"enabled": True, "test_config": "value"}})

        # Plugin should be registered
        assert "test_plugin" in pm._plugins

        # Widgets should be available
        assert "MockWidget" in pm._widgets
        assert "MockWidgetNoSchema" in pm._widgets


def test_plugin_manager_enabled_by_default():
    """Test that plugins are enabled by default when enabled field is not specified."""
    with patch("knoepfe.plugins.manager.entry_points") as mock_entry_points:
        # Mock plugin entry point
        mock_ep = Mock()
        mock_ep.name = "test_plugin"
        mock_ep.load.return_value = MockPluginDescriptor
        mock_dist = Mock()
        mock_dist.name = "test-package"
        mock_dist.version = "1.0.0"
        mock_dist.metadata = {"Summary": "Test plugin"}
        mock_ep.dist = mock_dist
        mock_entry_points.return_value = [mock_ep]

        # Create plugin manager without specifying enabled field
        pm = PluginManager({"test_plugin": {"test_config": "value"}})

        # Plugin should be registered (enabled by default)
        assert "test_plugin" in pm._plugins

        # Widgets should be available
        assert "MockWidget" in pm._widgets
        assert "MockWidgetNoSchema" in pm._widgets


def test_plugin_manager_mixed_enabled_disabled():
    """Test loading multiple plugins with different enabled states."""
    with patch("knoepfe.plugins.manager.entry_points") as mock_entry_points:
        # Mock two plugin entry points
        mock_ep1 = Mock()
        mock_ep1.name = "enabled_plugin"
        mock_ep1.load.return_value = MockPluginDescriptor1
        mock_dist1 = Mock()
        mock_dist1.name = "enabled-package"
        mock_dist1.version = "1.0.0"
        mock_dist1.metadata = {"Summary": "Enabled plugin"}
        mock_ep1.dist = mock_dist1

        mock_ep2 = Mock()
        mock_ep2.name = "disabled_plugin"
        mock_ep2.load.return_value = MockPluginDescriptor2
        mock_dist2 = Mock()
        mock_dist2.name = "disabled-package"
        mock_dist2.version = "1.0.0"
        mock_dist2.metadata = {"Summary": "Disabled plugin"}
        mock_ep2.dist = mock_dist2

        mock_entry_points.return_value = [mock_ep1, mock_ep2]

        # Create plugin manager with one enabled and one disabled
        pm = PluginManager({"enabled_plugin": {"enabled": True}, "disabled_plugin": {"enabled": False}})

        # Only enabled plugin should be registered
        assert "enabled_plugin" in pm._plugins
        assert "disabled_plugin" not in pm._plugins

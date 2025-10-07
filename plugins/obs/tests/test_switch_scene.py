from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from knoepfe_obs_plugin.config import OBSPluginConfig
from knoepfe_obs_plugin.context import OBSPluginContext
from knoepfe_obs_plugin.widgets.switch_scene import SwitchScene, SwitchSceneConfig


@pytest.fixture
def mock_context():
    return OBSPluginContext(OBSPluginConfig())


@pytest.fixture
def switch_scene_widget(mock_context):
    return SwitchScene(SwitchSceneConfig(scene="Gaming"), mock_context)


def test_switch_scene_init(mock_context):
    """Test SwitchScene widget initialization."""
    widget = SwitchScene(SwitchSceneConfig(scene="Gaming"), mock_context)
    assert widget.config.scene == "Gaming"
    assert widget.relevant_events == [
        "ConnectionEstablished",
        "ConnectionLost",
        "SwitchScenes",
    ]


async def test_switch_scene_update_disconnected(switch_scene_widget):
    """Test update when disconnected."""
    with patch.object(switch_scene_widget.context, "obs") as mock_obs:
        mock_obs.connected = False
        key = MagicMock()

        await switch_scene_widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon_and_text.assert_called_with(
            "󰏜",  # nf-md-panorama
            "Gaming",
            icon_size=64,
            text_size=16,
            icon_color="#202020",
            text_color="#202020",
        )


async def test_switch_scene_update_active(switch_scene_widget):
    """Test update when the configured scene is active."""
    with patch.object(switch_scene_widget.context, "obs") as mock_obs:
        mock_obs.connected = True
        mock_obs.current_scene = "Gaming"
        key = MagicMock()

        await switch_scene_widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon_and_text.assert_called_with(
            "󰏜",  # nf-md-panorama
            "Gaming",
            icon_size=64,
            text_size=16,
            icon_color="red",
            text_color="red",
        )


async def test_switch_scene_update_inactive(switch_scene_widget):
    """Test update when a different scene is active."""
    with patch.object(switch_scene_widget.context, "obs") as mock_obs:
        mock_obs.connected = True
        mock_obs.current_scene = "Chatting"
        key = MagicMock()

        await switch_scene_widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon_and_text.assert_called_with(
            "󰏜",  # nf-md-panorama
            "Gaming",
            icon_size=64,
            text_size=16,
            icon_color="white",
            text_color="white",
        )


async def test_switch_scene_triggered_connected(switch_scene_widget):
    """Test triggered when connected switches to the scene."""
    with patch.object(switch_scene_widget.context, "obs") as mock_obs:
        mock_obs.connected = True
        mock_obs.set_scene = AsyncMock()

        await switch_scene_widget.triggered()

        mock_obs.set_scene.assert_called_once_with("Gaming")


async def test_switch_scene_triggered_disconnected(switch_scene_widget):
    """Test triggered when disconnected does nothing."""
    with patch.object(switch_scene_widget.context, "obs") as mock_obs:
        mock_obs.connected = False
        mock_obs.set_scene = AsyncMock()

        await switch_scene_widget.triggered()

        mock_obs.set_scene.assert_not_called()


async def test_switch_scene_triggered_long_press(switch_scene_widget):
    """Test triggered with long press (should behave the same as short press)."""
    with patch.object(switch_scene_widget.context, "obs") as mock_obs:
        mock_obs.connected = True
        mock_obs.set_scene = AsyncMock()

        await switch_scene_widget.triggered(long_press=True)

        mock_obs.set_scene.assert_called_once_with("Gaming")


async def test_switch_scene_update_with_custom_config(mock_context):
    """Test update with custom configuration."""
    config = SwitchSceneConfig(
        scene="Chatting",
        icon="🎮",
        active_color="green",
        inactive_color="gray",
    )
    widget = SwitchScene(config, mock_context)

    with patch.object(widget.context, "obs") as mock_obs:
        mock_obs.connected = True
        mock_obs.current_scene = "Chatting"
        key = MagicMock()

        await widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon_and_text.assert_called_with(
            "🎮",
            "Chatting",
            icon_size=64,
            text_size=16,
            icon_color="green",
            text_color="green",
        )


def test_switch_scene_config():
    """Test that SwitchSceneConfig validates correctly."""
    # Test with required scene parameter
    config = SwitchSceneConfig(scene="Gaming")
    assert config.scene == "Gaming"
    assert config.icon == "󰏜"  # nf-md-panorama
    assert config.active_color == "red"
    assert config.inactive_color is None
    assert config.color == "white"

    # Test with custom values
    config = SwitchSceneConfig(
        scene="Chatting",
        icon="🎮",
        active_color="green",
        inactive_color="gray",
    )
    assert config.scene == "Chatting"
    assert config.icon == "🎮"
    assert config.active_color == "green"
    assert config.inactive_color == "gray"


def test_switch_scene_config_requires_scene():
    """Test that SwitchSceneConfig requires scene parameter."""
    with pytest.raises(ValidationError):
        SwitchSceneConfig()

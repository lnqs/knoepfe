from unittest.mock import MagicMock, patch

from pytest import fixture

from knoepfe_obs_plugin.config import OBSPluginConfig
from knoepfe_obs_plugin.plugin import OBSPlugin
from knoepfe_obs_plugin.widgets.current_scene import CurrentScene, CurrentSceneConfig


@fixture
def mock_plugin():
    return OBSPlugin(OBSPluginConfig())


@fixture
def current_scene_widget(mock_plugin):
    return CurrentScene(CurrentSceneConfig(), mock_plugin)


def test_current_scene_init(mock_plugin):
    """Test CurrentScene widget initialization."""
    widget = CurrentScene(CurrentSceneConfig(), mock_plugin)
    assert widget.relevant_events == [
        "ConnectionEstablished",
        "ConnectionLost",
        "CurrentProgramSceneChanged",
    ]


async def test_current_scene_update_connected_with_scene(current_scene_widget):
    """Test update when connected with a current scene."""
    with patch.object(current_scene_widget.plugin, "obs") as mock_obs:
        mock_obs.connected = True
        mock_obs.current_scene = "Gaming"
        key = MagicMock()

        await current_scene_widget.update(key)

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


async def test_current_scene_update_connected_no_scene(current_scene_widget):
    """Test update when connected but no scene is set."""
    with patch.object(current_scene_widget.plugin, "obs") as mock_obs:
        mock_obs.connected = True
        mock_obs.current_scene = None
        key = MagicMock()

        await current_scene_widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon_and_text.assert_called_with(
            "󰏜",  # nf-md-panorama
            "[none]",
            icon_size=64,
            text_size=16,
            icon_color="white",
            text_color="white",
        )


async def test_current_scene_update_disconnected(current_scene_widget):
    """Test update when disconnected."""
    with patch.object(current_scene_widget.plugin, "obs") as mock_obs:
        mock_obs.connected = False
        key = MagicMock()

        await current_scene_widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon.assert_called_with(
            "󰏜",  # nf-md-panorama
            size=64,
            color="#202020",
        )


async def test_current_scene_update_with_custom_config(mock_plugin):
    """Test update with custom configuration."""
    config = CurrentSceneConfig(icon="🎬", connected_color="cyan")
    widget = CurrentScene(config, mock_plugin)

    with patch.object(widget.plugin, "obs") as mock_obs:
        mock_obs.connected = True
        mock_obs.current_scene = "Chatting"
        key = MagicMock()

        await widget.update(key)

        renderer_mock = key.renderer.return_value.__enter__.return_value
        renderer_mock.clear.assert_called_once()
        renderer_mock.icon_and_text.assert_called_with(
            "🎬",
            "Chatting",
            icon_size=64,
            text_size=16,
            icon_color="cyan",
            text_color="cyan",
        )


def test_current_scene_config():
    """Test that CurrentSceneConfig validates correctly."""
    # Test with defaults
    config = CurrentSceneConfig()
    assert config.icon == "󰏜"  # nf-md-panorama
    assert config.connected_color is None
    assert config.color == "white"

    # Test with custom values
    config = CurrentSceneConfig(icon="🎬", connected_color="cyan")
    assert config.icon == "🎬"
    assert config.connected_color == "cyan"

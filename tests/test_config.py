from pathlib import Path
from unittest.mock import Mock, mock_open, patch

from pytest import raises
from schema import Schema, SchemaError

from knoepfe.config import (
    create_widget,
    exec_config,
    get_config_path,
    process_config,
)
from knoepfe.plugin_manager import PluginManager
from knoepfe.widget_manager import WidgetManager, WidgetNotFoundError
from knoepfe.widgets.base import Widget

# Updated test configs using new syntax
test_config = """
deck("main", [widget("test")])
deck("other", [widget("test")])
"""

test_config_multiple_device_config = """
config("device", {'brightness': 100})
config("device", {'brightness': 90})
"""

test_config_no_main = """
deck("other", [widget("test")])
"""

test_config_multiple_main = """
deck("main", [widget("test")])
deck("main", [widget("test")])
"""


def test_config_path() -> None:
    assert get_config_path(Path("path")) == Path("path")

    with patch("pathlib.Path.exists", return_value=True):
        assert str(get_config_path()).endswith(".config/knoepfe/knoepfe.cfg")

    with patch("pathlib.Path.exists", return_value=False):
        assert str(get_config_path()).endswith("knoepfe/default.cfg")


def test_exec_config_success() -> None:
    mock_wm = Mock(spec=WidgetManager)
    mock_pm = Mock(spec=PluginManager)

    with patch("knoepfe.config.create_widget") as create_widget_mock:
        create_widget_mock.return_value = Mock()
        global_config, main_deck, decks = exec_config(test_config, mock_wm, mock_pm)

    assert create_widget_mock.called
    assert main_deck is not None
    assert main_deck.id == "main"
    assert len(decks) == 2  # main and other


def test_exec_config_multiple_device_config() -> None:
    # Multiple device configs should be allowed (last one wins)
    mock_wm = Mock(spec=WidgetManager)
    mock_pm = Mock(spec=PluginManager)

    with patch("knoepfe.config.create_widget") as create_widget_mock:
        create_widget_mock.return_value = Mock()
        global_config, main_deck, decks = exec_config(
            test_config_multiple_device_config + '\ndeck("main", [widget("test")])', mock_wm, mock_pm
        )

    # Should have the last device config
    assert global_config["knoepfe.config.device"]["brightness"] == 90


def test_exec_config_multiple_main() -> None:
    mock_wm = Mock(spec=WidgetManager)
    mock_pm = Mock(spec=PluginManager)

    with patch("knoepfe.config.create_widget"):
        with raises(RuntimeError, match="Main deck already defined"):
            exec_config(test_config_multiple_main, mock_wm, mock_pm)


def test_exec_config_no_main() -> None:
    mock_wm = Mock(spec=WidgetManager)
    mock_pm = Mock(spec=PluginManager)

    with patch("knoepfe.config.create_widget"):
        with raises(RuntimeError, match="No 'main' deck specified"):
            exec_config(test_config_no_main, mock_wm, mock_pm)


def test_process_config() -> None:
    with (
        patch("knoepfe.config.exec_config", return_value=({}, Mock(), [Mock()])) as exec_config_mock,
        patch("builtins.open", mock_open(read_data=test_config)),
    ):
        process_config(Path("file"), Mock(spec=WidgetManager), Mock(spec=PluginManager))
    assert exec_config_mock.called


def test_create_widget_success() -> None:
    class TestWidget(Widget):
        name = "TestWidget"

        async def update(self, key):
            pass

        @classmethod
        def get_config_schema(cls) -> Schema:
            return Schema({})

    mock_wm = Mock(spec=WidgetManager)
    mock_wm.get_widget.return_value = TestWidget

    w = create_widget("TestWidget", {}, {}, mock_wm)
    assert isinstance(w, TestWidget)


def test_create_widget_invalid_type() -> None:
    mock_wm = Mock(spec=WidgetManager)
    mock_wm.get_widget.side_effect = WidgetNotFoundError("NonExistentWidget")

    with raises(WidgetNotFoundError):
        create_widget("NonExistentWidget", {}, {}, mock_wm)


def test_device_config_validation() -> None:
    """Test that device config is validated properly."""

    device_config = """
config("device", {'brightness': 150})  # Invalid brightness > 100
deck("main", [widget("test")])
"""

    mock_wm = Mock(spec=WidgetManager)
    mock_pm = Mock(spec=PluginManager)

    with patch("knoepfe.config.create_widget"):
        with raises(SchemaError):  # Should raise validation error
            exec_config(device_config, mock_wm, mock_pm)


def test_plugin_config_storage() -> None:
    """Test that plugin configs are stored correctly."""
    plugin_config = """
config("obs", {'host': 'localhost', 'port': 4455})
deck("main", [widget("test")])
"""

    mock_wm = Mock(spec=WidgetManager)
    mock_pm = Mock(spec=PluginManager)

    with patch("knoepfe.config.create_widget") as create_widget_mock:
        create_widget_mock.return_value = Mock()
        global_config, main_deck, decks = exec_config(plugin_config, mock_wm, mock_pm)

        # Check that plugin config was set
        mock_pm.set_plugin_config.assert_called_with("obs", {"host": "localhost", "port": 4455})

        # Check that it's also in global config
        assert global_config["obs"] == {"host": "localhost", "port": 4455}

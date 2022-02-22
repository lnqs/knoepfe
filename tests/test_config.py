from pathlib import Path
from unittest.mock import Mock, mock_open, patch

from pytest import raises
from schema import Schema

from deckconnect.config import (
    create_deck,
    create_widget,
    exec_config,
    get_config_path,
    process_config,
)
from deckconnect.widgets.base import Widget

test_config = """
deck({ 'widgets': [widget({'type': 'test'})] })
default_deck({ 'widgets': [widget({'type': 'test'})] })
"""

test_config_multiple_config = """
config({ 'type': 'deckconnect.config.device', 'brightness': 100 })
config({ 'type': 'deckconnect.config.device', 'brightness': 90 })
"""

test_config_no_default = """
deck({ 'widgets': [widget({'type': 'test'})] })
"""

test_config_multiple_default = """
default_deck({ 'widgets': [widget({'type': 'test'})] })
default_deck({ 'widgets': [widget({'type': 'test'})] })
"""


def test_config_path() -> None:
    assert get_config_path(Path("path")) == Path("path")

    with patch("pathlib.Path.exists", return_value=True):
        assert str(get_config_path()).endswith(".config/deckconnect/default.cfg")

    assert str(get_config_path()).endswith("deckconnect/default.cfg")


def test_exec_config_success() -> None:
    with patch("deckconnect.config.create_deck") as create_deck, patch(
        "deckconnect.config.create_widget"
    ) as create_widget:
        exec_config(test_config)
    assert create_deck.called
    assert create_widget.called


def test_exec_config_multiple_config() -> None:
    with raises(RuntimeError):
        exec_config(test_config_multiple_config)


def test_exec_config_multiple_default() -> None:
    with patch("deckconnect.config.create_deck"), patch(
        "deckconnect.config.create_widget"
    ):
        with raises(RuntimeError):
            exec_config(test_config_multiple_default)


def test_exec_config_invalid_global() -> None:
    with patch("deckconnect.config.import_module", return_value=Mock(Class=int)):
        with raises(RuntimeError):
            exec_config(test_config_multiple_config)


def test_exec_config_no_default() -> None:
    with patch("deckconnect.config.create_deck"), patch(
        "deckconnect.config.create_widget"
    ):
        with raises(RuntimeError):
            exec_config(test_config_no_default)


def test_process_config() -> None:
    with patch(
        "deckconnect.config.exec_config", return_value=(Mock(), [Mock()])
    ) as exec_config, patch("builtins.open", mock_open(read_data=test_config)):
        process_config(Path("file"))
    assert exec_config.called


def test_create_deck() -> None:
    with patch("deckconnect.config.Deck") as deck:
        create_deck({"id": "id", "widgets": []})
    assert deck.called


def test_create_widget_success() -> None:
    class TestWidget(Widget):
        def get_schema(self) -> Schema:
            return Schema({})

    with patch("deckconnect.config.import_module", return_value=Mock(Class=TestWidget)):
        w = create_widget({"type": "a.b.c.Class"}, {})
    assert isinstance(w, TestWidget)


def test_create_widget_invalid_type() -> None:
    with patch("deckconnect.config.import_module", return_value=Mock(Class=int)):
        with raises(Exception):
            create_widget({"type": "a.b.c.Class"}, {})

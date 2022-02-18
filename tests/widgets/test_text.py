from schema import Schema

from deckconnect.widgets import Text


def test_text() -> None:
    assert isinstance(Text.get_config_schema(), Schema)

    w = Text({"text": "Hi there!"})
    assert w.config["text"] == "Hi there!"

from unittest.mock import MagicMock

from schema import Schema

from knoepfe.widgets import Text


async def test_text_update() -> None:
    widget = Text({"text": "Text"}, {})
    key = MagicMock()
    await widget.update(key)
    assert key.renderer.return_value.__enter__.return_value.text.called


def test_text_schema() -> None:
    assert isinstance(Text.get_config_schema(), Schema)

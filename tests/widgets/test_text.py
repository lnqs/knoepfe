from unittest.mock import MagicMock

from schema import Schema

from knoepfe.builtin_plugin import BuiltinPlugin
from knoepfe.widgets.text import Text


async def test_text_update() -> None:
    widget = Text({"text": "Text"}, {}, BuiltinPlugin({}))
    key = MagicMock()
    await widget.update(key)
    assert key.renderer.return_value.__enter__.return_value.text_wrapped.called


def test_text_schema() -> None:
    assert isinstance(Text.get_config_schema(), Schema)

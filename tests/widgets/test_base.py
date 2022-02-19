from unittest.mock import Mock, patch

from pytest import raises

from deckconnect.deck import SwitchDeckException
from deckconnect.widgets.base import Widget


async def test_base_update() -> None:
    # Not really a useful test. But let's stick to 100% coverage.
    widget = Widget({})
    await widget.update(Mock())


async def test_presses() -> None:
    widget = Widget({})
    with patch.object(widget, "triggered") as triggered:
        await widget.pressed()
        await widget.released()
    assert triggered.call_args[0][0] is False

    with patch.object(widget, "triggered") as triggered:
        await widget.pressed()
        widget.press_time = -2.0
        await widget.released()
    assert triggered.call_args[0][0] is True


async def test_switch_deck() -> None:
    widget = Widget({"switch_deck": "new_deck"})
    with raises(SwitchDeckException) as e:
        await widget.released()
    assert e.value.new_deck == "new_deck"

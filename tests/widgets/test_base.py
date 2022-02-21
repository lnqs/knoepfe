from unittest.mock import patch

from pytest import raises

from deckconnect.deck import SwitchDeckException
from deckconnect.widgets.base import Widget


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


async def test_request_update() -> None:
    widget = Widget({})
    with patch.object(widget, "update_requested_event") as event:
        widget.request_update()
    assert event.set.called
    assert widget.needs_update

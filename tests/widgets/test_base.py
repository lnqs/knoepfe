from asyncio import sleep
from unittest.mock import AsyncMock, Mock, patch

from pytest import raises

from deckconnect.deck import SwitchDeckException
from deckconnect.widgets.base import Widget


async def test_presses() -> None:
    widget = Widget({}, {})
    with patch.object(widget, "triggered") as triggered:
        await widget.pressed()
        await widget.released()
    assert triggered.call_args[0][0] is False

    with patch.object(widget, "triggered") as triggered, patch(
        "deckconnect.widgets.base.sleep", AsyncMock()
    ):
        await widget.pressed()
        await sleep(0.1)
        await widget.released()
    assert triggered.call_count == 1
    assert triggered.call_args[0][0] is True


async def test_switch_deck() -> None:
    widget = Widget({"switch_deck": "new_deck"}, {})
    with raises(SwitchDeckException) as e:
        widget.long_press_task = Mock()
        await widget.released()
    assert e.value.new_deck == "new_deck"


async def test_request_update() -> None:
    widget = Widget({}, {})
    with patch.object(widget, "update_requested_event") as event:
        widget.request_update()
    assert event.set.called
    assert widget.needs_update

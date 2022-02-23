from asyncio import sleep
from unittest.mock import AsyncMock, Mock, patch

from pytest import raises

from knoepfe.deck import SwitchDeckException
from knoepfe.wakelock import WakeLock
from knoepfe.widgets.base import Widget


async def test_presses() -> None:
    widget = Widget({}, {})
    with patch.object(widget, "triggered") as triggered:
        await widget.pressed()
        await widget.released()
    assert triggered.call_args[0][0] is False

    with patch.object(widget, "triggered") as triggered, patch(
        "knoepfe.widgets.base.sleep", AsyncMock()
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


async def test_periodic_update() -> None:
    widget = Widget({}, {})

    with patch.object(widget, "request_update") as request_update:
        widget.request_periodic_update(0.0)
        await sleep(0.01)
        assert request_update.called
        count = request_update.call_count

        widget.stop_periodic_update()
        await sleep(0.01)
        assert request_update.call_count == count


async def test_wake_lock() -> None:
    widget = Widget({}, {})
    widget.wake_lock = WakeLock(Mock())

    widget.acquire_wake_lock()
    assert widget.wake_lock.count == 1
    widget.acquire_wake_lock()
    assert widget.wake_lock.count == 1

    widget.release_wake_lock()
    assert widget.wake_lock.count == 0
    widget.release_wake_lock()
    assert widget.wake_lock.count == 0

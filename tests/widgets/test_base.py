from asyncio import sleep
from unittest.mock import AsyncMock, Mock, patch

from knoepfe.key import Key
from knoepfe.wakelock import WakeLock
from knoepfe.widgets.actions import SwitchDeckAction
from knoepfe.widgets.base import Widget


class ConcreteWidget(Widget):
    """Concrete test widget for testing base functionality."""

    name = "ConcreteWidget"

    async def update(self, key: Key) -> None:
        pass


async def test_presses() -> None:
    widget = ConcreteWidget({}, {})
    with patch.object(widget, "triggered") as triggered:
        await widget.pressed()
        await widget.released()
    assert triggered.call_args[0][0] is False

    with (
        patch.object(widget, "triggered") as triggered,
        patch("knoepfe.widgets.base.sleep", AsyncMock()),
    ):
        await widget.pressed()
        await sleep(0.1)
        await widget.released()
    assert triggered.call_count == 1
    assert triggered.call_args[0][0] is True


async def test_switch_deck() -> None:
    widget = ConcreteWidget({"switch_deck": "new_deck"}, {})
    widget.long_press_task = Mock()
    action = await widget.released()
    assert isinstance(action, SwitchDeckAction)
    assert action.target_deck == "new_deck"


async def test_no_switch_deck() -> None:
    widget = ConcreteWidget({}, {})
    widget.long_press_task = Mock()
    action = await widget.released()
    assert action is None


async def test_request_update() -> None:
    widget = ConcreteWidget({}, {})
    with patch.object(widget, "update_requested_event") as event:
        widget.request_update()
    assert event.set.called
    assert widget.needs_update


async def test_periodic_update() -> None:
    widget = ConcreteWidget({}, {})

    with patch.object(widget, "request_update") as request_update:
        widget.request_periodic_update(0.0)
        await sleep(0.01)
        assert request_update.called
        count = request_update.call_count

        widget.stop_periodic_update()
        await sleep(0.01)
        assert request_update.call_count == count


async def test_wake_lock() -> None:
    widget = ConcreteWidget({}, {})
    widget.wake_lock = WakeLock(Mock())

    widget.acquire_wake_lock()
    assert widget.wake_lock.count == 1
    widget.acquire_wake_lock()
    assert widget.wake_lock.count == 1

    widget.release_wake_lock()
    assert widget.wake_lock.count == 0
    widget.release_wake_lock()
    assert widget.wake_lock.count == 0

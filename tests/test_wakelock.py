from asyncio import Event

from knoepfe.wakelock import WakeLock


def test_wake_lock() -> None:
    event = Event()
    wake_lock = WakeLock(event)

    wake_lock.acquire()
    assert event.is_set()
    assert wake_lock.held()

    wake_lock.release()
    assert not wake_lock.held()

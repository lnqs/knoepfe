"""Tests for TaskManager."""

from asyncio import Event, sleep

import pytest

from knoepfe.utils.task_manager import TaskManager


@pytest.mark.asyncio
async def test_start_task():
    """Test starting a basic task."""
    manager = TaskManager()
    event = Event()

    async def test_coro():
        event.set()

    manager.start_task("test", test_coro())
    await sleep(0.1)

    assert event.is_set()
    assert not manager.is_running("test")  # Task completed


@pytest.mark.asyncio
async def test_start_task_idempotent():
    """Test that starting same task twice returns existing task."""
    manager = TaskManager()

    async def test_coro():
        await sleep(10)

    # Start the first task
    task1 = manager.start_task("test", test_coro())

    # Try to start a second task with the same name
    # Create the coroutine but close it immediately since it won't be used
    coro2 = test_coro()
    task2 = manager.start_task("test", coro2)
    coro2.close()  # Close the unused coroutine to prevent warning

    assert task1 is task2
    manager.stop_all()


@pytest.mark.asyncio
async def test_start_task_restart():
    """Test restarting a running task."""
    manager = TaskManager()
    counter = {"value": 0}

    async def test_coro():
        counter["value"] += 1
        await sleep(10)

    task1 = manager.start_task("test", test_coro())
    await sleep(0.1)
    assert counter["value"] == 1

    task2 = manager.start_task("test", test_coro(), restart_if_running=True)
    await sleep(0.1)
    assert counter["value"] == 2
    assert task1 is not task2

    manager.stop_all()


@pytest.mark.asyncio
async def test_stop_task():
    """Test stopping a task."""
    manager = TaskManager()

    async def test_coro():
        await sleep(10)

    manager.start_task("test", test_coro())
    assert manager.is_running("test")

    result = manager.stop_task("test")
    assert result is True
    assert not manager.is_running("test")

    result = manager.stop_task("nonexistent")
    assert result is False


@pytest.mark.asyncio
async def test_cleanup():
    """Test cleanup of all tasks."""
    manager = TaskManager()

    async def test_coro():
        await sleep(10)

    manager.start_task("task1", test_coro())
    manager.start_task("task2", test_coro())
    manager.start_task("task3", test_coro())

    assert manager.is_running("task1")
    assert manager.is_running("task2")
    assert manager.is_running("task3")

    manager.cleanup()

    assert not manager.is_running("task1")
    assert not manager.is_running("task2")
    assert not manager.is_running("task3")


@pytest.mark.asyncio
async def test_stop_all():
    """Test stopping all tasks."""
    manager = TaskManager()

    async def test_coro():
        await sleep(10)

    manager.start_task("task1", test_coro())
    manager.start_task("task2", test_coro())
    manager.start_task("task3", test_coro())

    assert manager.is_running("task1")
    assert manager.is_running("task2")
    assert manager.is_running("task3")

    manager.stop_all()

    assert not manager.is_running("task1")
    assert not manager.is_running("task2")
    assert not manager.is_running("task3")


@pytest.mark.asyncio
async def test_task_auto_cleanup_on_completion():
    """Test that tasks are automatically removed when they complete."""
    manager = TaskManager()
    event = Event()

    async def test_coro():
        event.set()

    manager.start_task("test", test_coro())
    await sleep(0.1)

    # Task should have completed and been auto-removed
    assert not manager.is_running("test")
    assert event.is_set()


@pytest.mark.asyncio
async def test_multiple_managers_independent():
    """Test that multiple TaskManagers are independent."""
    manager1 = TaskManager()
    manager2 = TaskManager()

    async def test_coro():
        await sleep(10)

    manager1.start_task("test", test_coro())
    manager2.start_task("test", test_coro())

    assert manager1.is_running("test")
    assert manager2.is_running("test")

    manager1.stop_task("test")

    assert not manager1.is_running("test")
    assert manager2.is_running("test")  # Should still be running

    manager2.stop_all()

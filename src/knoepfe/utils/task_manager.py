"""Background task management for widgets and plugins."""

from asyncio import Task, get_event_loop
from logging import getLogger
from typing import Any, Coroutine

logger = getLogger(__name__)


class TaskManager:
    """Manages background tasks with automatic lifecycle management.

    This class provides a unified API for creating and managing background tasks
    in both widgets (per-widget tasks) and plugins (plugin-wide tasks).

    Tasks are automatically cleaned up when cleanup() is called:
    - For widgets: cleanup() is called in widget.deactivate()
    - For plugins: cleanup() is called in plugin.shutdown()

    Features:
    - Named tasks for easy identification
    - Automatic cleanup on deactivate/shutdown
    - Safe task restart and cancellation

    Example (Widget):
        # In widget __init__
        self.tasks = TaskManager()

        # In widget activate()
        async def my_task():
            while True:
                await sleep(1.0)
                self.request_update()
        self.tasks.start_task("my_task", my_task())

        # Automatic cleanup on deactivate - no code needed!

    Example (Plugin):
        # In plugin __init__
        self.tasks = TaskManager()

        # In connector connect()
        self.tasks.start_task("event_watcher", self._watch_events())

        # Automatic cleanup on shutdown - no code needed!
    """

    def __init__(self):
        """Initialize task manager."""
        self._tasks: dict[str, Task[None]] = {}

    def start_task(
        self,
        name: str,
        coro: Coroutine[Any, Any, None],
        restart_if_running: bool = False,
    ) -> Task[None]:
        """Start a named background task.

        The task will be automatically cleaned up based on the scope set during
        TaskManager initialization.

        Args:
            name: Unique identifier for this task
            coro: Coroutine to run as a background task
            restart_if_running: If True, cancel and restart if task already exists

        Returns:
            The created Task object

        Example:
            # Start a task that monitors external events
            self.tasks.start_task("event_watcher", self._watch_events())
        """
        if name in self._tasks:
            if restart_if_running:
                self.stop_task(name)
            else:
                return self._tasks[name]

        task: Task[None] = get_event_loop().create_task(coro)
        self._tasks[name] = task

        # Auto-cleanup when task completes
        def cleanup(t: Task[None]) -> None:
            self._tasks.pop(name, None)

        task.add_done_callback(cleanup)
        logger.debug(f"Started task '{name}'")
        return task

    def stop_task(self, name: str) -> bool:
        """Stop a named background task.

        Args:
            name: Task identifier

        Returns:
            True if task was stopped, False if task not found

        Example:
            self.tasks.stop_task("periodic_update")
        """
        if task := self._tasks.pop(name, None):
            task.cancel()
            logger.debug(f"Stopped task '{name}'")
            return True
        return False

    def is_running(self, name: str) -> bool:
        """Check if a named task is currently running.

        Args:
            name: Task identifier

        Returns:
            True if task exists and is running

        Example:
            if not self.tasks.is_running("event_watcher"):
                self.tasks.start_task("event_watcher", self._watch_events())
        """
        if name in self._tasks:
            task = self._tasks[name]
            return not task.done()
        return False

    def cleanup(self) -> None:
        """Stop all tasks managed by this TaskManager.

        This is called automatically:
        - For widgets: When widget.deactivate() is called
        - For plugins: When plugin.shutdown() is called

        Example:
            # Called automatically by Widget.deactivate()
            self.tasks.cleanup()
        """
        task_count = len(self._tasks)
        if task_count > 0:
            for name in list(self._tasks.keys()):
                self.stop_task(name)
            logger.debug(f"Cleaned up {task_count} tasks")

    def stop_all(self) -> None:
        """Stop all tasks regardless of scope.

        This is useful for emergency cleanup or testing.

        Example:
            self.tasks.stop_all()
        """
        for name in list(self._tasks.keys()):
            self.stop_task(name)

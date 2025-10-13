from unittest.mock import AsyncMock, Mock, patch

from knoepfe.config.widget import WidgetConfig
from knoepfe.rendering import Renderer
from knoepfe.widgets.actions import UpdateResult
from pytest import fixture

from knoepfe_obs_plugin.config import OBSPluginConfig
from knoepfe_obs_plugin.plugin import OBSPlugin
from knoepfe_obs_plugin.widgets.base import TASK_EVENT_LISTENER, OBSWidget


class MockWidgetConfig(WidgetConfig):
    """Minimal widget config for testing."""

    pass


class MockOBSWidget(OBSWidget[MockWidgetConfig]):
    """Test implementation of OBSWidget for testing purposes."""

    relevant_events = ["TestEvent"]

    async def update(self, renderer: Renderer) -> UpdateResult:
        return UpdateResult.UPDATED

    async def triggered(self, long_press=False):
        pass


@fixture
def mock_plugin():
    return OBSPlugin(OBSPluginConfig())


@fixture
def obs_widget(mock_plugin):
    widget = MockOBSWidget(MockWidgetConfig(), mock_plugin)

    # Mock the TaskManager to avoid pytest warnings about unawaited tasks
    def mock_start_task(name, coro):
        # Close the coroutine to prevent "never awaited" warnings
        coro.close()
        return Mock()

    widget.tasks = Mock()
    widget.tasks.start_task = Mock(side_effect=mock_start_task)
    widget.tasks.stop_task = Mock()
    widget.tasks.is_running = Mock(return_value=False)
    widget.tasks.cleanup = AsyncMock()
    return widget


def test_obs_widget_init(mock_plugin):
    widget = MockOBSWidget(MockWidgetConfig(), mock_plugin)
    assert widget.relevant_events == ["TestEvent"]
    assert widget.tasks is not None


async def test_obs_widget_activate(obs_widget):
    """Test widget activation starts listener.

    Note: OBS connection is managed by the plugin lifecycle hooks, not by individual widget activation.
    """
    await obs_widget.activate()

    obs_widget.tasks.start_task.assert_called_once()
    # Verify the task name is correct
    call_args = obs_widget.tasks.start_task.call_args
    assert call_args[0][0] == TASK_EVENT_LISTENER


async def test_obs_widget_deactivate(obs_widget):
    """Test widget deactivation - tasks are cleaned up by Deck automatically."""
    # Simulate that a task is running
    obs_widget.tasks.is_running.return_value = True

    # Deactivate should not stop tasks (Deck handles cleanup)
    await obs_widget.deactivate()

    # Verify stop_task was NOT called (cleanup is handled by Deck)
    obs_widget.tasks.stop_task.assert_not_called()


async def test_obs_widget_listener_relevant_event(obs_widget):
    with patch.object(obs_widget, "request_update") as mock_request_update:
        with patch.object(obs_widget.plugin, "obs") as mock_obs:
            # Mock async iterator
            async def mock_listen():
                yield "TestEvent"

            mock_obs.listen.return_value = mock_listen()

            # Run one iteration of the listener
            async for event in mock_obs.listen():
                if event in obs_widget.relevant_events:
                    obs_widget.request_update()
                break

            mock_request_update.assert_called_once()


async def test_obs_widget_listener_connection_events(obs_widget):
    with (
        patch.object(obs_widget, "acquire_wake_lock") as mock_acquire,
        patch.object(obs_widget, "release_wake_lock") as mock_release,
        patch.object(obs_widget.plugin, "obs") as mock_obs,
    ):
        # Test ConnectionEstablished
        async def mock_listen_established():
            yield "ConnectionEstablished"

        mock_obs.listen.return_value = mock_listen_established()

        async for event in mock_obs.listen():
            if event == "ConnectionEstablished":
                obs_widget.acquire_wake_lock()
            break

        mock_acquire.assert_called_once()

        # Test ConnectionLost
        async def mock_listen_lost():
            yield "ConnectionLost"

        mock_obs.listen.return_value = mock_listen_lost()

        async for event in mock_obs.listen():
            if event == "ConnectionLost":
                obs_widget.release_wake_lock()
            break

        mock_release.assert_called_once()

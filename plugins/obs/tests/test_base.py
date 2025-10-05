from unittest.mock import AsyncMock, Mock, patch

from knoepfe.config.widget import WidgetConfig
from pytest import fixture

from knoepfe_obs_plugin.config import OBSPluginConfig
from knoepfe_obs_plugin.context import OBSPluginContext
from knoepfe_obs_plugin.widgets.base import OBSWidget


class MockWidgetConfig(WidgetConfig):
    """Minimal widget config for testing."""

    pass


class MockOBSWidget(OBSWidget[MockWidgetConfig]):
    """Test implementation of OBSWidget for testing purposes."""

    relevant_events = ["TestEvent"]

    async def update(self, key):
        pass

    async def triggered(self, long_press=False):
        pass


@fixture
def mock_context():
    return OBSPluginContext(OBSPluginConfig())


@fixture
def obs_widget(mock_context):
    return MockOBSWidget(MockWidgetConfig(), mock_context)


def test_obs_widget_init(mock_context):
    widget = MockOBSWidget(MockWidgetConfig(), mock_context)
    assert widget.relevant_events == ["TestEvent"]
    assert widget.listening_task is None


async def test_obs_widget_activate(obs_widget):
    with patch.object(obs_widget.context, "obs") as mock_obs:
        mock_obs.connect = AsyncMock()

        # Mock listen to return an empty async iterator to prevent unawaited coroutine warning
        async def mock_listen():
            return
            yield  # Make it an async generator

        mock_obs.listen.return_value = mock_listen()

        with patch("knoepfe_obs_plugin.widgets.base.get_event_loop") as mock_loop:
            mock_task = Mock()
            mock_loop.return_value.create_task.return_value = mock_task

            await obs_widget.activate()

            # OBS connect is called without arguments (config is in OBS __init__)
            mock_obs.connect.assert_called_once_with()
            mock_loop.return_value.create_task.assert_called_once()
            assert obs_widget.listening_task == mock_task

            # Clean up the task to prevent warnings
            if obs_widget.listening_task:
                obs_widget.listening_task.cancel()
                obs_widget.listening_task = None


async def test_obs_widget_deactivate(obs_widget):
    # Set up widget with active listening task
    mock_task = Mock()
    mock_task.cancel = Mock()
    obs_widget.listening_task = mock_task

    await obs_widget.deactivate()

    mock_task.cancel.assert_called_once()
    assert obs_widget.listening_task is None


async def test_obs_widget_listener_relevant_event(obs_widget):
    with patch.object(obs_widget, "request_update") as mock_request_update:
        with patch.object(obs_widget.context, "obs") as mock_obs:
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
        patch.object(obs_widget.context, "obs") as mock_obs,
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

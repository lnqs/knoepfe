from unittest.mock import AsyncMock, Mock, patch

from knoepfe_obs_plugin.base import OBSWidget
from pytest import fixture


class MockOBSWidget(OBSWidget):
    """Test implementation of OBSWidget for testing purposes."""

    relevant_events = ["TestEvent"]

    async def update(self, key):
        pass

    async def triggered(self, long_press=False):
        pass


@fixture
def obs_widget():
    return MockOBSWidget({}, {})


def test_obs_widget_init():
    widget = MockOBSWidget({}, {})
    assert widget.relevant_events == ["TestEvent"]
    assert widget.listening_task is None


async def test_obs_widget_activate(obs_widget):
    with patch("knoepfe_obs_plugin.base.obs") as mock_obs:
        mock_obs.connect = AsyncMock()

        with patch("knoepfe_obs_plugin.base.get_event_loop") as mock_loop:
            mock_task = Mock()
            mock_loop.return_value.create_task.return_value = mock_task

            await obs_widget.activate()

            mock_obs.connect.assert_called_once_with({})
            mock_loop.return_value.create_task.assert_called_once()
            assert obs_widget.listening_task == mock_task


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
        with patch("knoepfe_obs_plugin.base.obs") as mock_obs:
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
        patch("knoepfe_obs_plugin.base.obs") as mock_obs,
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

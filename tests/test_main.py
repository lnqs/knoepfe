from unittest.mock import AsyncMock, Mock, patch

from pytest import raises
from StreamDeck.Transport.Transport import TransportError

from knoepfe.cli import main
from knoepfe.core.app import Knoepfe


def test_main_success() -> None:
    with (
        patch("knoepfe.cli.Knoepfe") as knoepfe,
        patch("sys.argv", ["knoepfe"]),
    ):
        with raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
    assert knoepfe.return_value.run_sync.called


async def test_run() -> None:
    knoepfe = Knoepfe()

    # Test config loading error - should fail before trying to connect to device
    # Patch where load_config is USED (in app.py), not where it's defined
    with patch("knoepfe.core.app.load_config", side_effect=RuntimeError("Error")):
        with raises(RuntimeError, match="Error"):
            await knoepfe.run(None)

    # Test normal run with TransportError retry then SystemExit
    with (
        patch.object(knoepfe, "connect_device", AsyncMock(return_value=Mock())),
        patch("knoepfe.core.app.load_config") as mock_load_config,
        patch("knoepfe.core.app.create_decks") as mock_create_decks,
        patch("knoepfe.core.app.DeckManager") as MockDeckManager,
    ):
        # Setup mocks
        mock_load_config.return_value = Mock()
        mock_create_decks.return_value = [Mock()]

        # Create mock DeckManager that raises exceptions on run()
        # First run() raises TransportError (triggers retry), second raises SystemExit (exits loop)
        mock_deck_manager = Mock()
        mock_deck_manager.run = AsyncMock(side_effect=[TransportError(), SystemExit()])
        MockDeckManager.return_value = mock_deck_manager

        with raises(SystemExit):
            await knoepfe.run(None)

        # Verify DeckManager was instantiated twice (once for TransportError, once for SystemExit)
        assert MockDeckManager.call_count == 2
        # Verify run() was called twice
        assert mock_deck_manager.run.call_count == 2


async def test_connect_device() -> None:
    knoepfe = Knoepfe()

    with (
        patch(
            "knoepfe.core.app.DeviceManager.enumerate",
            side_effect=([], [Mock(key_layout=Mock(return_value=(2, 2)))]),
        ) as device_manager_enumerate,
        patch("knoepfe.core.app.sleep", AsyncMock()),
    ):
        await knoepfe.connect_device()

    assert device_manager_enumerate.called

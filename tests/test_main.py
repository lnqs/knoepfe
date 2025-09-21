from unittest.mock import AsyncMock, Mock, patch

from pytest import raises
from StreamDeck.Transport.Transport import TransportError

from knoepfe.app import Knoepfe
from knoepfe.cli import main


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

    with patch("knoepfe.app.process_config", side_effect=RuntimeError("Error")):
        with raises(RuntimeError):
            await knoepfe.run(None)

    with (
        patch.object(knoepfe, "connect_device", AsyncMock(return_value=Mock())),
        patch.multiple(
            "knoepfe.app",
            process_config=Mock(return_value=({}, Mock(), [Mock()])),
            DeckManager=Mock(return_value=Mock(run=Mock(side_effect=[TransportError(), SystemExit()]))),
        ),
    ):
        with raises(SystemExit):
            await knoepfe.run(None)


async def test_connect_device() -> None:
    knoepfe = Knoepfe()

    with (
        patch(
            "knoepfe.app.DeviceManager.enumerate",
            side_effect=([], [Mock(key_layout=Mock(return_value=(2, 2)))]),
        ) as device_manager_enumerate,
        patch("knoepfe.app.sleep", AsyncMock()),
    ):
        await knoepfe.connect_device()

    assert device_manager_enumerate.called

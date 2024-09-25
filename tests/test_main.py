from unittest.mock import AsyncMock, Mock, patch

from pytest import raises
from StreamDeck.Transport.Transport import TransportError

from knoepfe.__main__ import Knoepfe, main


def test_main_success() -> None:
    with patch("knoepfe.__main__.run"), patch("knoepfe.__main__.Knoepfe") as knoepfe:
        main()
    assert knoepfe.return_value.run.called


async def test_run() -> None:
    knoepfe = Knoepfe()

    with patch("knoepfe.__main__.process_config", side_effect=RuntimeError("Error")):
        with raises(RuntimeError):
            await knoepfe.run(None)

    with patch.object(
        knoepfe, "connect_device", AsyncMock(return_value=Mock())
    ), patch.multiple(
        "knoepfe.__main__",
        process_config=Mock(return_value=({}, Mock(), [Mock()])),
        DeckManager=Mock(
            return_value=Mock(run=Mock(side_effect=[TransportError(), SystemExit()]))
        ),
    ):
        with raises(SystemExit):
            await knoepfe.run(None)


async def test_connect_device() -> None:
    knoepfe = Knoepfe()

    with patch(
        "knoepfe.__main__.DeviceManager.enumerate",
        side_effect=([], [Mock(key_layout=Mock(return_value=(2, 2)))]),
    ) as device_manager_enumerate, patch("knoepfe.__main__.sleep", AsyncMock()):
        await knoepfe.connect_device()

    assert device_manager_enumerate.called

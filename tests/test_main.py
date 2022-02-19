from unittest.mock import AsyncMock, Mock, patch

from pytest import raises
from StreamDeck.Transport.Transport import TransportError

from deckconnect.__main__ import connect_device, main, run


def test_main_success() -> None:
    with patch("deckconnect.__main__.run") as run, patch("sys.argv", ["deckconnect"]):
        main()
    assert run.called

    with patch(
        "deckconnect.__main__.run", side_effect=Exception("Error!")
    ) as run, patch("sys.argv", ["deckconnect"]):
        with raises(SystemExit):
            main()
    assert run.called

    with patch(
        "deckconnect.__main__.run", side_effect=Exception("Error!")
    ) as run, patch("sys.argv", ["deckconnect", "--verbose"]):
        with raises(Exception):
            main()
    assert run.called


async def test_run() -> None:
    with patch("deckconnect.__main__.process_config", side_effect=Exception("Error")):
        with raises(Exception):
            await run(None)

    with patch.multiple(
        "deckconnect.__main__",
        process_config=Mock(return_value=(Mock(), [Mock()])),
        connect_device=AsyncMock(return_value=Mock()),
        DeckManager=Mock(
            return_value=Mock(
                run=Mock(side_effect=[TransportError(), Exception("Error")])
            )
        ),
    ):
        with raises(Exception):
            await run(None)


async def test_connect_device() -> None:
    with patch(
        "deckconnect.__main__.DeviceManager.enumerate",
        side_effect=([], [Mock(key_layout=Mock(return_value=(2, 2)))]),
    ) as device_manager_enumerate, patch("deckconnect.__main__.sleep", AsyncMock()):
        await connect_device()
    assert device_manager_enumerate.called

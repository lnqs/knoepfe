from typing import List
from unittest.mock import AsyncMock, MagicMock, Mock

from pytest import raises
from StreamDeck.Devices import StreamDeck

from deckconnect.deck import Deck
from deckconnect.widgets.base import Widget


def test_deck_init() -> None:
    widgets: List[Widget | None] = [Mock()]
    deck = Deck("id", widgets)
    assert deck.widgets == widgets


async def test_deck_activate() -> None:
    device: StreamDeck = MagicMock(key_count=Mock(return_value=4))
    deck = Deck("id", [])
    await deck.activate(device)
    assert device.set_key_image.called


async def test_deck_update() -> None:
    device: StreamDeck = MagicMock(key_count=Mock(return_value=1))
    deck = Deck("id", [Mock(), Mock()])

    with raises(RuntimeError):
        await deck.update(device)

    device = MagicMock(key_count=Mock(return_value=4))
    deck = Deck("id", [Mock(update=AsyncMock()), None, Mock(update=AsyncMock())])

    await deck.update(device)
    assert deck.widgets[0].update.called  # type: ignore
    assert deck.widgets[2].update.called  # type: ignore


async def test_deck_handle_key() -> None:
    deck = Deck(
        "id", [Mock(pressed=AsyncMock(), released=AsyncMock()) for i in range(3)]
    )
    await deck.handle_key(0, True)
    assert deck.widgets[0].pressed.called  # type: ignore
    assert not deck.widgets[0].released.called  # type: ignore
    await deck.handle_key(0, False)
    assert deck.widgets[0].released.called  # type: ignore

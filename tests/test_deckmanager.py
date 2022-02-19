from unittest.mock import AsyncMock, Mock, patch

from pytest import raises

from deckconnect.deck import SwitchDeckException
from deckconnect.deckmanager import DeckManager


async def test_deck_manager_run() -> None:
    deck = Mock(
        activate=AsyncMock(), update=AsyncMock(side_effect=[None, Exception("Error")])
    )
    deck_manager = DeckManager(deck, [deck], Mock())

    with patch("deckconnect.deckmanager.sleep", AsyncMock()):
        with raises(Exception):
            await deck_manager.run()


async def test_deck_manager_key_callback() -> None:
    deck = Mock(handle_key=AsyncMock(side_effect=SwitchDeckException("new_deck")))
    deck_manager = DeckManager(deck, [deck], Mock())

    with patch.object(deck_manager, "switch_deck", AsyncMock()) as switch_deck:
        await deck_manager.key_callback(Mock(), 0, False)
        assert switch_deck.called

    deck = Mock(handle_key=AsyncMock(side_effect=Exception("Error")))
    deck_manager = DeckManager(deck, [deck], Mock())

    await deck_manager.key_callback(Mock(), 0, False)


async def test_deck_manager_switch_deck() -> None:
    deck1 = Mock(
        id="deck",
        activate=AsyncMock(),
        update=AsyncMock(side_effect=[None, Exception("Error")]),
    )
    deck2 = Mock(
        id="other",
        activate=AsyncMock(),
        update=AsyncMock(side_effect=[None, Exception("Error")]),
    )
    deck_manager = DeckManager(deck1, [deck1, deck2], Mock())

    await deck_manager.switch_deck("other")
    assert deck_manager.active_deck == deck2
    assert deck2.activate.called
    assert deck2.update.called

    with raises(RuntimeError):
        await deck_manager.switch_deck("none")

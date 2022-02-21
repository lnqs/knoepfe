from asyncio import TimeoutError
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from pytest import raises

from deckconnect.deck import Deck, SwitchDeckException
from deckconnect.deckmanager import DeckManager


async def test_deck_manager_run() -> None:
    deck = Mock(
        activate=AsyncMock(), update=AsyncMock(side_effect=[None, SystemExit()])
    )
    deck_manager = DeckManager(deck, [deck], {}, Mock())

    with patch.object(deck_manager.update_requested_event, "wait", AsyncMock()):
        with raises(SystemExit):
            await deck_manager.run()


async def test_deck_manager_key_callback() -> None:
    deck = Mock(handle_key=AsyncMock(side_effect=SwitchDeckException("new_deck")))
    deck_manager = DeckManager(deck, [deck], {}, Mock())

    with patch.object(deck_manager, "switch_deck", AsyncMock()) as switch_deck:
        await deck_manager.key_callback(Mock(), 0, False)
        assert switch_deck.called

    deck = Mock(handle_key=AsyncMock(side_effect=Exception("Error")))
    deck_manager = DeckManager(deck, [deck], {}, Mock())

    await deck_manager.key_callback(Mock(), 0, False)

    deck = Mock(handle_key=AsyncMock(side_effect=SwitchDeckException("new_deck")))
    deck_manager = DeckManager(deck, [deck], {}, Mock())

    with patch.object(
        deck_manager, "switch_deck", AsyncMock(side_effect=Exception("Error"))
    ) as switch_deck:
        await deck_manager.key_callback(Mock(), 0, False)
        assert switch_deck.called


async def test_deck_manager_switch_deck() -> None:
    deck1 = Mock(
        id="deck",
        activate=AsyncMock(),
        deactivate=AsyncMock(),
    )
    deck2 = Mock(
        id="other",
        activate=AsyncMock(),
        deactivate=AsyncMock(),
    )
    deck_manager = DeckManager(deck1, [deck1, deck2], {}, Mock())

    await deck_manager.switch_deck("other")
    assert deck_manager.active_deck == deck2
    assert deck1.deactivate.called
    assert deck2.activate.called

    with raises(RuntimeError):
        await deck_manager.switch_deck("none")


async def test_deck_manager_sleep_activation() -> None:
    deck = Mock(spec=Deck)
    deck_manager = DeckManager(deck, [deck], {"sleep_timeout": 1.0}, MagicMock())
    deck_manager.last_action = 0.0

    with patch("time.monotonic", side_effect=[0.0, 0.0, 10.0]), patch.object(
        deck_manager, "sleep", AsyncMock()
    ), patch.object(
        deck_manager.update_requested_event,
        "wait",
        Mock(side_effect=[TimeoutError(), SystemExit()]),
    ):
        with raises(SystemExit):
            await deck_manager.run()


async def test_deck_manager_sleep() -> None:
    deck_manager = DeckManager(Mock(), [], {}, MagicMock())
    with patch("deckconnect.deckmanager.sleep", AsyncMock()):
        await deck_manager.sleep()
    assert deck_manager.sleeping


async def test_deck_wake_up() -> None:
    deck = Mock(handle_key=AsyncMock(side_effect=SwitchDeckException("new_deck")))
    deck_manager = DeckManager(deck, [deck], {}, MagicMock())
    deck_manager.sleeping = True

    with patch.object(deck_manager, "switch_deck", AsyncMock()) as switch_deck:
        await deck_manager.key_callback(Mock(), 0, False)
        assert not switch_deck.called
        assert not deck_manager.sleeping

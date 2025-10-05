from asyncio import TimeoutError
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from pytest import raises

from knoepfe.config.models import DeckConfig, DeviceConfig, GlobalConfig
from knoepfe.core.deck import Deck
from knoepfe.core.deckmanager import DeckManager
from knoepfe.widgets.actions import SwitchDeckAction


def make_global_config() -> GlobalConfig:
    """Helper to create a minimal GlobalConfig for tests."""
    return GlobalConfig(decks={"main": DeckConfig(name="main", widgets=[])})


async def test_deck_manager_run() -> None:
    deck = Mock(id="main", activate=AsyncMock(), update=AsyncMock(side_effect=[None, SystemExit()]))
    deck_manager = DeckManager([deck], make_global_config(), Mock())

    with patch.object(deck_manager.update_requested_event, "wait", AsyncMock()):
        with raises(SystemExit):
            await deck_manager.run()


async def test_deck_manager_key_callback() -> None:
    deck = Mock(id="main", handle_key=AsyncMock(return_value=SwitchDeckAction("new_deck")))
    deck_manager = DeckManager([deck], make_global_config(), Mock())

    with patch.object(deck_manager, "switch_deck", AsyncMock()) as switch_deck:
        await deck_manager.key_callback(Mock(), 0, False)
        assert switch_deck.called
        switch_deck.assert_called_with("new_deck")

    deck = Mock(id="main", handle_key=AsyncMock(side_effect=Exception("Error")))
    deck_manager = DeckManager([deck], make_global_config(), Mock())

    await deck_manager.key_callback(Mock(), 0, False)

    deck = Mock(id="main", handle_key=AsyncMock(return_value=SwitchDeckAction("new_deck")))
    deck_manager = DeckManager([deck], make_global_config(), Mock())

    with patch.object(deck_manager, "switch_deck", AsyncMock(side_effect=Exception("Error"))) as switch_deck:
        await deck_manager.key_callback(Mock(), 0, False)
        assert switch_deck.called
        switch_deck.assert_called_with("new_deck")


async def test_deck_manager_switch_deck() -> None:
    deck1 = Mock(
        id="main",
        activate=AsyncMock(),
        deactivate=AsyncMock(),
    )
    deck2 = Mock(
        id="other",
        activate=AsyncMock(),
        deactivate=AsyncMock(),
    )
    deck_manager = DeckManager([deck1, deck2], make_global_config(), Mock())

    await deck_manager.switch_deck("other")
    assert deck_manager.active_deck == deck2
    assert deck1.deactivate.called
    assert deck2.activate.called

    with raises(RuntimeError):
        await deck_manager.switch_deck("none")


async def test_deck_manager_sleep_activation() -> None:
    deck = Mock(id="main", spec=Deck)
    config = GlobalConfig(
        device=DeviceConfig(sleep_timeout=1.0),
        decks={"main": DeckConfig(name="main", widgets=[])},
    )
    deck_manager = DeckManager([deck], config, MagicMock())
    deck_manager.last_action = 0.0

    with (
        patch("time.monotonic", side_effect=[0.0, 0.0, 10.0]),
        patch.object(deck_manager, "sleep", AsyncMock()),
        patch.object(
            deck_manager.update_requested_event,
            "wait",
            Mock(side_effect=[TimeoutError(), SystemExit()]),
        ),
    ):
        with raises(SystemExit):
            await deck_manager.run()


async def test_deck_manager_sleep() -> None:
    deck = Mock(id="main")
    deck_manager = DeckManager([deck], make_global_config(), MagicMock())
    with patch("knoepfe.core.deckmanager.sleep", AsyncMock()):
        await deck_manager.sleep()
    assert deck_manager.sleeping


async def test_deck_wake_up() -> None:
    deck = Mock(
        id="main",
        activate=AsyncMock(),
        handle_key=AsyncMock(return_value=SwitchDeckAction("new_deck")),
    )
    deck_manager = DeckManager([deck], make_global_config(), MagicMock())
    deck_manager.sleeping = True

    with patch.object(deck_manager, "switch_deck", AsyncMock()) as switch_deck:
        await deck_manager.key_callback(Mock(), 0, False)
        assert not switch_deck.called
        assert not deck_manager.sleeping

    deck = Mock(id="main", activate=AsyncMock())
    deck_manager = DeckManager([deck], make_global_config(), MagicMock())
    deck_manager.sleeping = True
    deck_manager.wake_lock.acquire()

    with (
        patch.object(deck_manager, "wake_up", AsyncMock()) as wake_up,
        patch.object(
            deck_manager.update_requested_event,
            "wait",
            AsyncMock(side_effect=SystemExit()),
        ),
    ):
        with raises(SystemExit):
            await deck_manager.run()

        assert wake_up.called

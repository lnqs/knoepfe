from typing import List
from unittest.mock import AsyncMock, MagicMock, Mock

from pytest import raises
from StreamDeck.Devices.StreamDeck import StreamDeck

from knoepfe.config.models import GlobalConfig
from knoepfe.core.deck import Deck
from knoepfe.widgets.base import Widget


def test_deck_init() -> None:
    widgets: List[Widget | None] = [Mock(spec=Widget)]
    deck = Deck("id", widgets, GlobalConfig())
    assert deck.widgets == widgets


async def test_deck_activate() -> None:
    device: StreamDeck = MagicMock(key_count=Mock(return_value=4))
    widget = Mock(spec=Widget)
    deck = Deck("id", [widget], GlobalConfig())
    await deck.activate(device, Mock(), Mock())
    assert device.set_key_image.called
    assert widget.activate.called


async def test_deck_deactivate() -> None:
    device: StreamDeck = MagicMock(key_count=Mock(return_value=4))
    widget = Mock(spec=Widget)
    widget.tasks = Mock()  # Add tasks mock
    deck = Deck("id", [widget], GlobalConfig())
    await deck.deactivate(device)
    assert widget.tasks.cleanup.called  # Verify cleanup was called
    assert widget.deactivate.called


async def test_deck_update() -> None:
    device: StreamDeck = MagicMock(key_count=Mock(return_value=1))
    deck = Deck("id", [Mock(), Mock()], GlobalConfig())

    with raises(RuntimeError):
        await deck.update(device)

    device = MagicMock(key_count=Mock(return_value=4))
    mock_widget_0 = Mock(spec=Widget)
    mock_widget_0.update = AsyncMock()
    mock_widget_0.needs_update = True
    mock_widget_2 = Mock(spec=Widget)
    mock_widget_2.update = AsyncMock()
    mock_widget_2.needs_update = True
    deck = Deck("id", [mock_widget_0, None, mock_widget_2], GlobalConfig())

    await deck.update(device)
    assert mock_widget_0.update.called
    assert mock_widget_2.update.called


async def test_deck_handle_key() -> None:
    mock_widgets = []
    for _ in range(3):
        mock_widget = Mock(spec=Widget)
        mock_widget.pressed = AsyncMock()
        mock_widget.released = AsyncMock()
        mock_widgets.append(mock_widget)

    deck = Deck("id", mock_widgets, GlobalConfig())
    await deck.handle_key(0, True)
    assert mock_widgets[0].pressed.called
    assert not mock_widgets[0].released.called
    await deck.handle_key(0, False)
    assert mock_widgets[0].released.called

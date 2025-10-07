from typing import List
from unittest.mock import AsyncMock, MagicMock, Mock

from StreamDeck.Devices.StreamDeck import StreamDeck

from knoepfe.config.models import GlobalConfig
from knoepfe.core.deck import Deck
from knoepfe.widgets.base import Widget


def create_mock_widget(index: int | None = None) -> Mock:
    """Helper to create a properly mocked widget with config.index."""
    widget = Mock(spec=Widget)
    widget.config = Mock()
    widget.config.index = index
    return widget


def test_deck_init() -> None:
    widgets: List[Widget] = [create_mock_widget()]
    deck = Deck("id", widgets, GlobalConfig())
    assert len(deck.widgets) == 1


async def test_deck_activate() -> None:
    device: StreamDeck = MagicMock(key_count=Mock(return_value=4))
    widget = create_mock_widget()
    deck = Deck("id", [widget], GlobalConfig())
    await deck.activate(device, Mock(), Mock())
    assert device.set_key_image.called
    assert widget.activate.called


async def test_deck_deactivate() -> None:
    device: StreamDeck = MagicMock(key_count=Mock(return_value=4))
    widget = create_mock_widget()
    widget.tasks = Mock()  # Add tasks mock
    deck = Deck("id", [widget], GlobalConfig())
    await deck.deactivate(device)
    assert widget.tasks.cleanup.called  # Verify cleanup was called
    assert widget.deactivate.called


async def test_deck_update() -> None:
    device: StreamDeck = MagicMock(key_count=Mock(return_value=4))
    mock_widget_0 = create_mock_widget()
    mock_widget_0.update = AsyncMock()
    mock_widget_0.needs_update = True
    mock_widget_1 = create_mock_widget()
    mock_widget_1.update = AsyncMock()
    mock_widget_1.needs_update = True
    deck = Deck("id", [mock_widget_0, mock_widget_1], GlobalConfig())

    await deck.update(device)
    assert mock_widget_0.update.called
    assert mock_widget_1.update.called


async def test_deck_handle_key() -> None:
    mock_widgets = []
    for _ in range(3):
        mock_widget = create_mock_widget()
        mock_widget.pressed = AsyncMock()
        mock_widget.released = AsyncMock()
        mock_widgets.append(mock_widget)

    deck = Deck("id", mock_widgets, GlobalConfig())
    await deck.handle_key(0, True)
    assert mock_widgets[0].pressed.called
    assert not mock_widgets[0].released.called
    await deck.handle_key(0, False)
    assert mock_widgets[0].released.called


def test_deck_index_assignment_unindexed() -> None:
    """Test that unindexed widgets are assigned sequential indices starting from 0."""
    widget_a = create_mock_widget(None)
    widget_b = create_mock_widget(None)
    widget_c = create_mock_widget(None)

    deck = Deck("id", [widget_a, widget_b, widget_c], GlobalConfig())

    # Verify widgets are in order and have correct indices assigned
    assert len(deck.widgets) == 3
    assert deck.widgets[0] == widget_a
    assert deck.widgets[1] == widget_b
    assert deck.widgets[2] == widget_c
    assert widget_a.config.index == 0
    assert widget_b.config.index == 1
    assert widget_c.config.index == 2


def test_deck_index_assignment_mixed_no_gaps() -> None:
    """Test mixed explicit and auto-assigned indices without gaps."""
    widget_a = create_mock_widget(0)  # Explicit index 0
    widget_b = create_mock_widget(None)  # Should get index 1
    widget_c = create_mock_widget(2)  # Explicit index 2
    widget_d = create_mock_widget(None)  # Should get index 3

    deck = Deck("id", [widget_a, widget_b, widget_c, widget_d], GlobalConfig())

    # Verify correct ordering and index assignment
    assert len(deck.widgets) == 4
    assert deck.widgets[0] == widget_a
    assert deck.widgets[1] == widget_b
    assert deck.widgets[2] == widget_c
    assert deck.widgets[3] == widget_d
    assert widget_a.config.index == 0
    assert widget_b.config.index == 1
    assert widget_c.config.index == 2
    assert widget_d.config.index == 3


def test_deck_index_assignment_explicit_with_gaps() -> None:
    """Test explicit indices with gaps (sparse list)."""
    widget_a = create_mock_widget(0)
    widget_b = create_mock_widget(3)
    widget_c = create_mock_widget(5)

    deck = Deck("id", [widget_a, widget_b, widget_c], GlobalConfig())

    # Verify widgets are at their explicit positions
    assert len(deck.widgets) == 3
    assert deck.widgets[0] == widget_a
    assert deck.widgets[1] == widget_b
    assert deck.widgets[2] == widget_c
    assert widget_a.config.index == 0
    assert widget_b.config.index == 3
    assert widget_c.config.index == 5


def test_deck_index_assignment_mixed_with_gaps() -> None:
    """Test mixed explicit and auto-assigned indices with gaps."""
    widget_a = create_mock_widget(0)  # Explicit index 0
    widget_b = create_mock_widget(None)  # Should fill gap at index 1
    widget_c = create_mock_widget(5)  # Explicit index 5 (creates gap)
    widget_d = create_mock_widget(None)  # Should fill gap at index 2
    widget_e = create_mock_widget(None)  # Should fill gap at index 3

    deck = Deck("id", [widget_a, widget_b, widget_c, widget_d, widget_e], GlobalConfig())

    # Verify correct ordering and gap filling
    assert len(deck.widgets) == 5
    assert deck.widgets[0] == widget_a
    assert deck.widgets[1] == widget_b
    assert deck.widgets[2] == widget_d
    assert deck.widgets[3] == widget_e
    assert deck.widgets[4] == widget_c
    assert widget_a.config.index == 0
    assert widget_b.config.index == 1
    assert widget_c.config.index == 5
    assert widget_d.config.index == 2
    assert widget_e.config.index == 3


def test_deck_index_assignment_out_of_order() -> None:
    """Test that widgets with out-of-order explicit indices are placed correctly."""
    widget_a = create_mock_widget(3)
    widget_b = create_mock_widget(1)
    widget_c = create_mock_widget(0)
    widget_d = create_mock_widget(2)

    deck = Deck("id", [widget_a, widget_b, widget_c, widget_d], GlobalConfig())

    # Verify widgets are reordered by their indices
    assert len(deck.widgets) == 4
    assert deck.widgets[0] == widget_c  # index 0
    assert deck.widgets[1] == widget_b  # index 1
    assert deck.widgets[2] == widget_d  # index 2
    assert deck.widgets[3] == widget_a  # index 3
    assert widget_a.config.index == 3
    assert widget_b.config.index == 1
    assert widget_c.config.index == 0
    assert widget_d.config.index == 2


async def test_deck_update_respects_indices() -> None:
    """Test that widgets are rendered to the correct physical keys based on their indices."""
    device: StreamDeck = MagicMock(key_count=Mock(return_value=10))

    # Create widgets with specific indices
    widget_at_0 = create_mock_widget(0)
    widget_at_0.update = AsyncMock()
    widget_at_0.needs_update = True

    widget_at_5 = create_mock_widget(5)
    widget_at_5.update = AsyncMock()
    widget_at_5.needs_update = True

    widget_auto = create_mock_widget(None)  # Should get index 1
    widget_auto.update = AsyncMock()
    widget_auto.needs_update = True

    deck = Deck("id", [widget_at_0, widget_at_5, widget_auto], GlobalConfig())
    await deck.update(device, force=True)

    # Verify each widget was rendered to the correct key
    assert widget_at_0.update.called
    assert widget_at_5.update.called
    assert widget_auto.update.called

    # Check the Key objects passed to each widget's update method
    # widget_at_0 should be rendered to key 0
    key_0 = widget_at_0.update.call_args[0][0]
    assert key_0.index == 0

    # widget_auto should be rendered to key 1 (next available after 0)
    key_1 = widget_auto.update.call_args[0][0]
    assert key_1.index == 1

    # widget_at_5 should be rendered to key 2 (position in list)
    key_2 = widget_at_5.update.call_args[0][0]
    assert key_2.index == 2

from typing import List
from unittest.mock import Mock

from deckconnect.deck import Deck
from deckconnect.widgets.base import Widget


def test_deck() -> None:
    widgets: List[Widget] = [Mock()]
    d = Deck(widgets)
    assert d.widgets == widgets

from typing import List

from deckconnect.widgets.base import Widget


class Deck:
    def __init__(self, widgets: List[Widget]) -> None:
        self.widgets = widgets

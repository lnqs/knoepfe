"""Actions that widgets can request from the deck management system."""

from dataclasses import dataclass
from enum import Enum


class WidgetActionType(Enum):
    """Types of actions a widget can request."""

    SWITCH_DECK = "switch_deck"


@dataclass
class WidgetAction:
    """Base class for widget actions."""

    action_type: WidgetActionType


@dataclass
class SwitchDeckAction(WidgetAction):
    """Action to switch to a different deck."""

    target_deck: str

    def __init__(self, target_deck: str):
        super().__init__(WidgetActionType.SWITCH_DECK)
        self.target_deck = target_deck

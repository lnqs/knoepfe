from dataclasses import dataclass
from enum import Enum


class UpdateResult(Enum):
    """Result of a widget update operation indicating whether the renderer's canvas should be used."""

    UPDATED = "updated"  # Widget updated the canvas, push to device
    UNCHANGED = "unchanged"  # Widget didn't update canvas, keep current display


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

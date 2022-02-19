import asyncio
from typing import TYPE_CHECKING, List, Optional

from StreamDeck.Devices import StreamDeck

from deckconnect.key import Key

if TYPE_CHECKING:  # pragma: no cover
    from deckconnect.widgets.base import Widget


class SwitchDeckException(BaseException):
    def __init__(self, new_deck: str) -> None:
        self.new_deck = new_deck


class Deck:
    def __init__(self, id: str, widgets: List[Optional["Widget"]]) -> None:
        self.id = id
        self.widgets = widgets

    async def activate(self, device: StreamDeck) -> None:
        with device:
            for i in range(device.key_count()):
                device.set_key_image(i, None)

    async def update(self, device: StreamDeck) -> None:
        if len(self.widgets) > device.key_count():
            raise RuntimeError("Number of widgets exceeds number of device keys")

        await asyncio.gather(
            *[
                widget.update(Key(device, index))
                for index, widget in enumerate(self.widgets)
                if widget
            ]
        )

    async def handle_key(self, index: int, pressed: bool) -> None:
        if index < len(self.widgets):
            widget = self.widgets[index]
            if widget:
                if pressed:
                    await widget.pressed()
                else:
                    await widget.released()

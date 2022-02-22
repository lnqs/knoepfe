import asyncio
from asyncio import Event
from typing import TYPE_CHECKING, List, Optional

from StreamDeck.Devices import StreamDeck

from knoepfe.key import Key
from knoepfe.log import debug
from knoepfe.wakelock import WakeLock

if TYPE_CHECKING:  # pragma: no cover
    from knoepfe.widgets.base import Widget


class SwitchDeckException(BaseException):
    def __init__(self, new_deck: str) -> None:
        self.new_deck = new_deck


class Deck:
    def __init__(self, id: str, widgets: List[Optional["Widget"]]) -> None:
        self.id = id
        self.widgets = widgets

    async def activate(
        self, device: StreamDeck, update_requested_event: Event, wake_lock: WakeLock
    ) -> None:
        with device:
            for i in range(device.key_count()):
                device.set_key_image(i, None)

        for widget in self.widgets:
            if widget:
                widget.update_requested_event = update_requested_event
                widget.wake_lock = wake_lock
        await asyncio.gather(*[w.activate() for w in self.widgets if w])
        await self.update(device, True)

    async def deactivate(self, device: StreamDeck) -> None:
        await asyncio.gather(*[w.deactivate() for w in self.widgets if w])

    async def update(self, device: StreamDeck, force: bool = False) -> None:
        if len(self.widgets) > device.key_count():
            raise RuntimeError("Number of widgets exceeds number of device keys")

        async def update_widget(w: Optional["Widget"], i: int) -> None:
            if w and (force or w.needs_update):
                debug(f"Updating widget on key {i}")
                await w.update(Key(device, i))
                w.needs_update = False

        await asyncio.gather(
            *[update_widget(widget, index) for index, widget in enumerate(self.widgets)]
        )

    async def handle_key(self, index: int, pressed: bool) -> None:
        if index < len(self.widgets):
            widget = self.widgets[index]
            if widget:
                if pressed:
                    await widget.pressed()
                else:
                    await widget.released()

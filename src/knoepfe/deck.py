import asyncio
import logging
from asyncio import Event
from typing import Any

from StreamDeck.Devices.StreamDeck import StreamDeck

from knoepfe.key import Key
from knoepfe.wakelock import WakeLock
from knoepfe.widgets.actions import WidgetAction
from knoepfe.widgets.base import Widget

logger = logging.getLogger(__name__)


class Deck:
    def __init__(self, id: str, widgets: list[Widget | None], global_config: dict[str, Any] | None = None) -> None:
        self.id = id
        self.widgets = widgets
        self.global_config = global_config or {}

    async def activate(self, device: StreamDeck, update_requested_event: Event, wake_lock: WakeLock) -> None:
        with device:
            for i in range(device.key_count()):
                device.set_key_image(i, b"")

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

        async def update_widget(w: Widget | None, i: int) -> None:
            if w and (force or w.needs_update):
                logger.debug(f"Updating widget on key {i}")
                await w.update(Key(device, i, self.global_config))
                w.needs_update = False

        await asyncio.gather(*[update_widget(widget, index) for index, widget in enumerate(self.widgets)])

    async def handle_key(self, index: int, pressed: bool) -> WidgetAction | None:
        if index < len(self.widgets):
            widget = self.widgets[index]
            if widget:
                if pressed:
                    await widget.pressed()
                    return None
                else:
                    return await widget.released()
        return None

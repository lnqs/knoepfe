import asyncio
import logging
from asyncio import Event

from StreamDeck.Devices.StreamDeck import StreamDeck
from StreamDeck.ImageHelpers import PILHelper

from ..config import ConfigError
from ..config.models import GlobalConfig
from ..rendering import Renderer
from ..utils.wakelock import WakeLock
from ..widgets.widget import UpdateResult, Widget
from .actions import WidgetAction

logger = logging.getLogger(__name__)


class Deck:
    def __init__(self, id: str, widgets: list[Widget], global_config: GlobalConfig) -> None:
        self.id = id
        self.global_config = global_config
        # Assign widgets to indices based on their config.index
        self.widgets = self._assign_indices(widgets)

    def _assign_indices(self, widgets: list[Widget]) -> list[Widget]:
        """Assign widgets to physical key indices.

        Widgets with explicit indices are placed at those positions.
        Widgets without indices fill in the gaps starting from 0.

        Args:
            widgets: List of widgets from config

        Returns:
            Sparse list with widgets at their assigned indices, None for empty positions
        """
        # Step 1: Separate widgets with explicit indices from those without
        explicit: dict[int, Widget] = {}
        none_list: list[Widget] = []

        for widget in widgets:
            if widget.config.index is not None:
                index = widget.config.index
                # Step 2: Validate indices
                if index < 0:
                    raise ConfigError(f"Widget index must be non-negative, got {index} in deck '{self.id}'")
                if index in explicit:
                    raise ConfigError(f"Duplicate widget index {index} in deck '{self.id}'")
                explicit[index] = widget
            else:
                none_list.append(widget)

        # Step 3: Build the ordered list and assign indices to unindexed widgets
        # Determine the range we need to cover (highest explicit index or enough for all widgets)
        if explicit:
            max_explicit = max(explicit.keys())
            # We need at least enough positions for all widgets
            max_pos = max(max_explicit, len(widgets) - 1)
        else:
            max_pos = len(widgets) - 1

        result = []
        none_i = 0

        for pos in range(max_pos + 1):
            if pos in explicit:
                # Place widget with explicit index
                result.append(explicit[pos])
            elif none_i < len(none_list):
                # Fill gap with next unindexed widget and assign it this index
                widget = none_list[none_i]
                widget.config.index = pos
                result.append(widget)
                none_i += 1

        return result

    async def activate(self, device: StreamDeck, update_requested_event: Event, wake_lock: WakeLock) -> None:
        # Check if any widgets exceed device capacity and log warning once
        if len(self.widgets) > device.key_count():
            logger.info(
                f"Deck '{self.id}' has {len(self.widgets)} widgets but device only has {device.key_count()} keys. "
                f"Widgets at positions {device.key_count()} and above will not be displayed."
            )

        for i in range(device.key_count()):
            device.set_key_image(i, b"")

        for widget in self.widgets:
            widget.update_requested_event = update_requested_event
            widget.wake_lock = wake_lock

        # Notify plugins before widget activation
        await asyncio.gather(*[w.plugin.on_widget_activate(w) for w in self.widgets])

        # Activate widgets
        await asyncio.gather(*[w.activate() for w in self.widgets])
        await self.update(device, True)

    async def deactivate(self, device: StreamDeck) -> None:
        # Cleanup tasks for all widgets before deactivating
        for widget in self.widgets:
            widget.tasks.cleanup()

        # Deactivate widgets first
        await asyncio.gather(*[w.deactivate() for w in self.widgets])

        # Notify plugins after widget deactivation
        await asyncio.gather(*[w.plugin.on_widget_deactivate(w) for w in self.widgets])

    async def update(self, device: StreamDeck, force: bool = False) -> None:
        async def update_widget(w: Widget, i: int) -> None:
            # Only update widgets that fit on the device
            if i < device.key_count() and (force or w.needs_update):
                logger.debug(f"Updating widget on key {i}")

                # Create renderer and let widget draw
                renderer = Renderer(
                    self.global_config.device.default_text_font,
                    self.global_config.device.default_icons_font,
                )
                result = await w.update(renderer)

                # Only push to device if widget actually rendered
                if result != UpdateResult.UPDATED:
                    return

                image = PILHelper.to_native_format(device, renderer.canvas)
                device.set_key_image(i, image)

                w.needs_update = False

        await asyncio.gather(*[update_widget(widget, index) for index, widget in enumerate(self.widgets)])

    async def handle_key(self, index: int, pressed: bool) -> WidgetAction | None:
        if index < len(self.widgets):
            widget = self.widgets[index]
            if pressed:
                await widget.pressed()
                return None
            else:
                return await widget.released()
        return None

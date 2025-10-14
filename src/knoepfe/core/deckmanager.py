import logging
import time
from asyncio import Event, TimeoutError, sleep, wait_for
from typing import cast

from StreamDeck.Devices.StreamDeck import StreamDeck

from ..config.models import GlobalConfig
from ..utils.wakelock import WakeLock
from .actions import SwitchDeckAction, WidgetActionType
from .deck import Deck

logger = logging.getLogger(__name__)


class DeckManager:
    def __init__(
        self,
        decks: list[Deck],
        global_config: GlobalConfig,
        device: StreamDeck,
    ) -> None:
        self.decks = decks
        self.active_deck = next((deck for deck in decks if deck.id == "main"))
        self.brightness = global_config.device.brightness
        self.device_poll_frequency = global_config.device.device_poll_frequency
        self.sleep_timeout = global_config.device.sleep_timeout
        self.device = device
        self.update_requested_event = Event()
        self.wake_lock = WakeLock(self.update_requested_event)
        self.sleeping = False
        self.last_action = time.monotonic()
        # StreamDeck library has incorrect type annotation for set_key_callback_async.
        # It expects KeyCallback (sync) but actually accepts async callbacks and wraps them internally.
        device.set_key_callback_async(self.key_callback)  # type: ignore[arg-type]

    async def run(self) -> None:
        self.device.set_brightness(self.brightness)
        self.device.set_poll_frequency(self.device_poll_frequency)
        self.last_action = time.monotonic()
        await self.active_deck.activate(self.device, self.update_requested_event, self.wake_lock)

        while True:
            now = time.monotonic()
            if (
                self.sleep_timeout
                and not self.wake_lock.held()
                and not self.sleeping
                and now - self.last_action > self.sleep_timeout
            ):
                await self.sleep()

            if self.sleeping and self.wake_lock.held():
                await self.wake_up()

            if not self.sleeping:
                await self.active_deck.update(self.device)

            self.update_requested_event.clear()
            logger.debug("Waiting for update request")

            try:
                timeout = None
                if self.sleep_timeout and not self.sleeping and not self.wake_lock.held():
                    timeout = self.sleep_timeout - (now - self.last_action)
                await wait_for(self.update_requested_event.wait(), timeout)
            except TimeoutError:
                pass

    async def key_callback(self, device: StreamDeck, index: int, pressed: bool) -> None:
        logger.debug(f"Key {index} {'pressed' if pressed else 'released'}")

        self.last_action = time.monotonic()

        if self.sleeping:
            if not pressed:
                await self.wake_up()
                self.update_requested_event.set()
            return

        try:
            action = await self.active_deck.handle_key(index, pressed)
            if action:
                if action.action_type == WidgetActionType.SWITCH_DECK:
                    switch_action = cast(SwitchDeckAction, action)
                    try:
                        await self.switch_deck(switch_action.target_deck)
                    except Exception as e:
                        logger.error(str(e))
        except Exception as e:
            logger.error(str(e))

    async def switch_deck(self, new_deck: str) -> None:
        logger.debug(f"Switching to deck {new_deck}")
        for deck in self.decks:
            if deck.id == new_deck:
                await self.active_deck.deactivate(self.device)
                self.active_deck = deck
                await self.active_deck.activate(self.device, self.update_requested_event, self.wake_lock)
                break
        else:
            raise RuntimeError(f"No deck with id {new_deck}")

    async def sleep(self) -> None:
        logger.debug("Going to sleep")
        with self.device:
            for i in range(self.brightness - 10, -10, -10):
                self.device.set_brightness(i)
                await sleep(0.1)
        self.sleeping = True

    async def wake_up(self) -> None:
        logger.debug("Waking up")
        with self.device:
            self.device.set_brightness(self.brightness)
        self.sleeping = False

import time
from asyncio import Event, TimeoutError, sleep, wait_for
from typing import Any, Dict, List

from StreamDeck.Devices import StreamDeck

from knoepfe.deck import Deck, SwitchDeckException
from knoepfe.log import debug, error
from knoepfe.wakelock import WakeLock


class DeckManager:
    def __init__(
        self,
        active_deck: Deck,
        decks: List[Deck],
        global_config: Dict[str, Any],
        device: StreamDeck,
    ) -> None:
        self.active_deck = active_deck
        self.decks = decks
        device_config = global_config.get("knoepfe.config.device", {})
        self.brightness = device_config.get("brightness", 100)
        self.device_poll_frequency = device_config.get("device_poll_frequency", 5)
        self.sleep_timeout = device_config.get("sleep_timeout", None)
        self.device = device
        self.update_requested_event = Event()
        self.wake_lock = WakeLock(self.update_requested_event)
        self.sleeping = False
        self.last_action = time.monotonic()
        device.set_key_callback_async(self.key_callback)

    async def run(self) -> None:
        self.device.set_brightness(self.brightness)
        self.device.set_poll_frequency(self.device_poll_frequency)
        self.last_action = time.monotonic()
        await self.active_deck.activate(
            self.device, self.update_requested_event, self.wake_lock
        )

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
            debug("Waiting for update request")

            try:
                timeout = None
                if self.sleep_timeout and not self.sleeping:
                    timeout = self.sleep_timeout - (now - self.last_action)
                await wait_for(self.update_requested_event.wait(), timeout)
            except TimeoutError:
                pass

    async def key_callback(self, device: StreamDeck, index: int, pressed: bool) -> None:
        debug(f'Key {index} {"pressed" if pressed else "released"}')

        self.last_action = time.monotonic()

        if self.sleeping:
            if not pressed:
                await self.wake_up()
                self.update_requested_event.set()
            return

        try:
            await self.active_deck.handle_key(index, pressed)
        except SwitchDeckException as e:
            try:
                await self.switch_deck(e.new_deck)
            except Exception as e:
                error(str(e))
        except Exception as e:
            error(str(e))

    async def switch_deck(self, new_deck: str) -> None:
        debug(f"Switching to deck {new_deck}")
        for deck in self.decks:
            if deck.id == new_deck:
                await self.active_deck.deactivate(self.device)
                self.active_deck = deck
                await self.active_deck.activate(
                    self.device, self.update_requested_event, self.wake_lock
                )
                break
        else:
            raise RuntimeError(f"No deck with id {new_deck}")

    async def sleep(self) -> None:
        debug("Going to sleep")
        with self.device:
            for i in range(self.brightness - 10, -10, -10):
                self.device.set_brightness(i)
                await sleep(0.1)
        self.sleeping = True

    async def wake_up(self) -> None:
        debug("Waking up")
        with self.device:
            self.device.set_brightness(self.brightness)
        self.sleeping = False

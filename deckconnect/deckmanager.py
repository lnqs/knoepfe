import time
from asyncio import sleep
from typing import Any, Dict, List

from StreamDeck.Devices import StreamDeck

from deckconnect.deck import Deck, SwitchDeckException
from deckconnect.log import error


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
        self.brightness = global_config.get("brightness", 100)
        self.sleep_timeout = global_config.get("sleep_timeout", None)
        self.device = device

        self.sleeping = False
        self.last_action = time.monotonic()
        device.set_key_callback_async(self.key_callback)

    async def run(self) -> None:
        self.device.set_brightness(self.brightness)
        self.last_action = time.monotonic()
        await self.active_deck.activate(self.device)

        while True:
            if (
                self.sleep_timeout
                and not self.sleeping
                and time.monotonic() - self.last_action > self.sleep_timeout
            ):
                await self.sleep()

            if not self.sleeping:
                await self.active_deck.update(self.device)

            await sleep(1)

    async def key_callback(self, device: StreamDeck, index: int, pressed: bool) -> None:
        self.last_action = time.monotonic()

        if self.sleeping:
            await self.wake_up()
            return

        try:
            await self.active_deck.handle_key(index, pressed)
        except SwitchDeckException as e:
            await self.switch_deck(e.new_deck)
        except Exception as e:
            error(str(e))

    async def switch_deck(self, new_deck: str) -> None:
        for deck in self.decks:
            if deck.id == new_deck:
                self.active_deck = deck
                await self.active_deck.activate(self.device)
                await self.active_deck.update(self.device)
                break
        else:
            raise RuntimeError(f"No deck with id {new_deck}")

    async def sleep(self) -> None:
        with self.device:
            for i in range(self.brightness - 10, -10, -10):
                self.device.set_brightness(i)
                await sleep(0.1)
        self.sleeping = True

    async def wake_up(self) -> None:
        with self.device:
            self.device.set_brightness(self.brightness)
        self.sleeping = False

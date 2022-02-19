from asyncio import sleep
from typing import List

from StreamDeck.Devices import StreamDeck

from deckconnect.deck import Deck, SwitchDeckException
from deckconnect.log import error


class DeckManager:
    def __init__(
        self, active_deck: Deck, decks: List[Deck], device: StreamDeck
    ) -> None:
        self.active_deck = active_deck
        self.decks = decks
        self.device = device

        device.set_key_callback_async(self.key_callback)

    async def run(self) -> None:
        await self.active_deck.activate(self.device)

        while True:
            await self.active_deck.update(self.device)
            await sleep(1)

    async def key_callback(self, device: StreamDeck, index: int, pressed: bool) -> None:
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

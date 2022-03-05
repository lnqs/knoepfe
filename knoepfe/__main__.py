"""knoepfe

Connect and control Elgato Stream Decks

Usage:
  knoepfe [(-v | --verbose)] [--config=<path>] [--mock-device]
  knoepfe (-h | --help)
  knoepfe --version

Options:
  -h --help       Show this screen.
  -v --verbose    Print debug information.
  --config=<path> Config file to use.
  --mock-device   Don't connect to a real device. Mainly useful for debugging.
"""

from asyncio import sleep
from pathlib import Path
from textwrap import indent

from aiorun import run
from docopt import docopt
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices import StreamDeck
from StreamDeck.Transport.Transport import TransportError

from knoepfe import __version__, log
from knoepfe.config import process_config
from knoepfe.deckmanager import DeckManager
from knoepfe.log import debug, info
from knoepfe.mockdeck import MockDeck


class Knoepfe:
    def __init__(self) -> None:
        self.device = None

    async def run(self, config_path: Path | None, mock_device: bool = False) -> None:
        try:
            debug("Processing config")
            global_config, active_deck, decks = process_config(config_path)
        except Exception as e:
            raise RuntimeError(
                f'Failed to parse configuration:\n{indent(str(e), "  ")}'
            )

        while True:
            device = await self.connect_device() if not mock_device else MockDeck()

            try:
                deck_manager = DeckManager(active_deck, decks, global_config, device)
                await deck_manager.run()
            except TransportError:
                debug("Transport error, trying to reconnect")
                continue

    async def connect_device(self) -> StreamDeck:
        info("Searching for devices")
        device = None

        while True:
            devices = DeviceManager().enumerate()
            if len(devices):
                device = devices[0]
                break
            await sleep(1.0)

        device.open()
        device.reset()

        info(
            f"Connected to {device.deck_type()} {device.get_serial_number()} "
            f"(Firmware {device.get_firmware_version()}, {device.key_layout()[0]}x{device.key_layout()[1]} keys)"
        )

        return device

    def shutdown(self) -> None:
        if self.device:
            debug("Closing device")
            self.device.close()


def main() -> None:
    arguments = docopt(__doc__, version=__version__)

    config_path = Path(arguments["--config"]) if arguments["--config"] else None
    mock_device = arguments["--mock-device"]
    log.verbose = arguments["--verbose"]

    knoepfe = Knoepfe()

    run(
        knoepfe.run(config_path, mock_device),
        stop_on_unhandled_errors=True,
        shutdown_callback=lambda _: knoepfe.shutdown(),
    )

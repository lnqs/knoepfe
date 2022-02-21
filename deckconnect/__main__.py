"""deckconnect

Connect and control Elgato Stream Decks

Usage:
  deckconnect [(-v | --verbose)] [--config=<path>]
  deckconnect (-h | --help)
  deckconnect --version

Options:
  -h --help       Show this screen.
  -v --verbose    Print debug information.
  --config=<path> Config file to use.
"""

import asyncio
import sys
from asyncio import sleep
from pathlib import Path
from textwrap import indent

from docopt import docopt
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices import StreamDeck
from StreamDeck.Transport.Transport import TransportError

from deckconnect import __version__, log
from deckconnect.config import process_config
from deckconnect.deckmanager import DeckManager
from deckconnect.log import debug, error, info


async def connect_device() -> StreamDeck:
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


async def run(config_path: Path | None) -> None:
    try:
        debug("Processing config")
        global_config, active_deck, decks = process_config(config_path)
    except Exception as e:
        raise RuntimeError(f'Failed to parse configuration:\n{indent(str(e), "  ")}')

    while True:
        device = await connect_device()
        try:
            deck_manager = DeckManager(active_deck, decks, global_config, device)
            await deck_manager.run()
        except TransportError:
            debug("Transport error, trying to reconnect")
            continue
        finally:
            debug("Closing device")
            device.close()


def main() -> None:
    arguments = docopt(__doc__, version=__version__)

    config_path = Path(arguments["--config"]) if arguments["--config"] else None
    log.verbose = arguments["--verbose"]

    try:
        asyncio.run(run(config_path))
    except Exception as e:
        if log.verbose:
            raise
        error(f"{e}")
        sys.exit(2)

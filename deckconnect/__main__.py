"""deckconnect

Connect and control Elgato Stream Decks

Usage:
  deckconnect [(-v | --verbose)] [--config=<path>] [--deck=<path>]
  deckconnect (-h | --help)
  deckconnect --version

Options:
  -h --help       Show this screen.
  -v --verbose    Print debug information.
  --config=<path> Config file to use.
"""

import sys
from pathlib import Path
from textwrap import indent

from docopt import docopt

from deckconnect import __version__
from deckconnect.config import process_config
from deckconnect.log import error, info


def run(config_path: Path | None) -> None:
    try:
        active_deck, decks = process_config(config_path)
    except Exception as e:
        raise RuntimeError(f'Failed to parse configuration:\n{indent(str(e), "  ")}')

    info(f"active_deck = {active_deck}; decks = {decks}")


def main() -> None:
    arguments = docopt(__doc__, version=__version__)

    config_path = Path(arguments["--config"]) if arguments["--config"] else None
    verbose = arguments["--verbose"]

    try:
        run(config_path)
    except Exception as e:
        if verbose:
            raise
        error(f"{e}")
        sys.exit(2)

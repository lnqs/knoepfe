"""knoepfe.

Connect and control Elgato Stream Decks
"""

import logging
from asyncio import sleep
from pathlib import Path

import click
from aiorun import run
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices.StreamDeck import StreamDeck
from StreamDeck.Transport.Transport import TransportError

from knoepfe import __version__
from knoepfe.config import process_config
from knoepfe.deckmanager import DeckManager
from knoepfe.log import configure_logging
from knoepfe.plugin_manager import plugin_manager

logger = logging.getLogger(__name__)


class Knoepfe:
    def __init__(self) -> None:
        self.device = None

    async def run(self, config_path: Path | None, mock_device: bool = False) -> None:
        try:
            logger.debug("Processing config")
            global_config, active_deck, decks = process_config(config_path)
        except Exception as e:
            raise RuntimeError("Failed to parse configuration") from e

        while True:
            device = await self.connect_device(mock_device)

            try:
                deck_manager = DeckManager(active_deck, decks, global_config, device)
                await deck_manager.run()
            except TransportError:
                logger.debug("Transport error, trying to reconnect")
                continue

    async def connect_device(self, mock_device: bool = False) -> StreamDeck:
        if mock_device:
            logger.info("Using mock device with dummy transport")
            device_manager = DeviceManager(transport="dummy")
            devices = device_manager.enumerate()
            device = devices[0]  # Use the first dummy device
        else:
            logger.info("Searching for devices")
            device = None

            while True:
                devices = DeviceManager().enumerate()
                if len(devices):
                    device = devices[0]
                    break
                await sleep(1.0)

        device.open()
        device.reset()

        logger.info(
            f"Connected to {device.deck_type()} {device.get_serial_number()} "
            f"(Firmware {device.get_firmware_version()}, {device.key_layout()[0]}x{device.key_layout()[1]} keys)"
        )

        return device

    def shutdown(self) -> None:
        if self.device:
            logger.debug("Closing device")
            self.device.reset()
            self.device.close()


@click.group(invoke_without_command=True)
@click.option("-v", "--verbose", is_flag=True, help="Print debug information.")
@click.option("--config", type=click.Path(exists=True, path_type=Path), help="Config file to use.")
@click.option("--mock-device", is_flag=True, help="Don't connect to a real device. Mainly useful for debugging.")
@click.version_option(version=__version__)
@click.pass_context
def main(ctx: click.Context, verbose: bool, config: Path | None, mock_device: bool) -> None:
    """Connect and control Elgato Stream Decks."""
    # Configure logging based on verbose flag
    configure_logging(verbose=verbose)

    # Store options in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config"] = config
    ctx.obj["mock_device"] = mock_device

    # If no subcommand is provided, run the main application
    if ctx.invoked_subcommand is None:
        knoepfe = Knoepfe()

        run(
            knoepfe.run(config, mock_device),
            stop_on_unhandled_errors=True,
            shutdown_callback=lambda _: knoepfe.shutdown(),
        )


@main.command("list-widgets")
def list_widgets() -> None:
    """List all available widgets."""
    widgets = plugin_manager.list_widgets()
    if not widgets:
        logger.info("No widgets available. Install widget packages like 'knoepfe[obs]'")
        return

    logger.info("Available widgets:")
    for widget_name in sorted(widgets):
        try:
            widget_class = plugin_manager.get_widget(widget_name)
            doc = widget_class.__doc__ or "No description available"
            logger.info(f"  {widget_name}: {doc}")
        except Exception as e:
            logger.error(f"  {widget_name}: Error getting info - {e}")


@main.command("widget-info")
@click.argument("widget_name")
def widget_info(widget_name: str) -> None:
    """Show detailed information about a widget."""
    try:
        widget_class = plugin_manager.get_widget(widget_name)
        logger.info(f"Name: {widget_name}")
        logger.info(f"Class: {widget_class.__name__}")
        logger.info(f"Module: {widget_class.__module__}")
        logger.info(f"Description: {widget_class.__doc__ or 'No description available'}")

        # Get configuration schema if available
        if hasattr(widget_class, "get_config_schema"):
            try:
                schema = widget_class.get_config_schema()
                logger.info("\nConfiguration Schema:")
                logger.info(f"  {schema}")
            except Exception as e:
                logger.error(f"Configuration schema error: {e}")
        else:
            logger.info("No configuration schema available")
    except ValueError as e:
        logger.error(f"Error: {e}")
        logger.info("Try 'knoepfe list-widgets' to see available widgets")


if __name__ == "__main__":
    main()

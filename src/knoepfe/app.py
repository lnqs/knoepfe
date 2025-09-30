"""Main application class for knoepfe."""

import logging
from asyncio import sleep
from pathlib import Path

from aiorun import run
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices.StreamDeck import StreamDeck
from StreamDeck.Transport.Transport import TransportError

from knoepfe.config import process_config
from knoepfe.deckmanager import DeckManager
from knoepfe.plugin_manager import PluginManager, WidgetNotFoundError

logger = logging.getLogger(__name__)


class Knoepfe:
    """Main application class for Knoepfe Stream Deck control."""

    def __init__(self) -> None:
        self.device = None
        self.plugin_manager = PluginManager()

    async def run(self, config_path: Path | None, mock_device: bool = False) -> None:
        """Run the main application loop.

        Args:
            config_path: Path to configuration file, or None to use default
            mock_device: If True, use a mock device instead of real hardware
        """
        try:
            logger.debug("Processing config")
            global_config, active_deck, decks = process_config(config_path, self.plugin_manager)
        except WidgetNotFoundError as e:
            raise e
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
        """Connect to a Stream Deck device.

        Args:
            mock_device: If True, use a mock device instead of real hardware

        Returns:
            Connected StreamDeck device
        """
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
        """Shutdown the application and clean up resources."""
        if self.device:
            logger.debug("Closing device")
            self.device.reset()
            self.device.close()

        # Shutdown all plugins
        logger.debug("Shutting down plugins")
        self.plugin_manager.shutdown_all()

    def run_sync(self, config_path: Path | None, mock_device: bool = False) -> None:
        """Synchronous wrapper for running the application.

        Args:
            config_path: Path to configuration file, or None to use default
            mock_device: If True, use a mock device instead of real hardware
        """
        run(
            self.run(config_path, mock_device),
            stop_on_unhandled_errors=True,
            shutdown_callback=lambda _: self.shutdown(),
        )

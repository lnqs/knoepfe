"""CLI commands and main entry point for knoepfe."""

import logging
from pathlib import Path

import click

from knoepfe import __version__
from knoepfe.app import Knoepfe
from knoepfe.logging import configure_logging
from knoepfe.plugin_manager import PluginManager

logger = logging.getLogger(__name__)


@click.group(invoke_without_command=True)
@click.option("-v", "--verbose", is_flag=True, help="Print debug information.")
@click.option("--config", type=click.Path(exists=True, path_type=Path), help="Config file to use.")
@click.option("--mock-device", is_flag=True, help="Don't connect to a real device. Mainly useful for debugging.")
@click.option("--no-cython-hid", is_flag=True, help="Disable experimental CythonHIDAPI transport.")
@click.version_option(version=__version__)
@click.pass_context
def main(ctx: click.Context, verbose: bool, config: Path | None, mock_device: bool, no_cython_hid: bool) -> None:
    """Connect and control Elgato Stream Decks."""
    # Apply CythonHIDAPI transport monkey patch if not disabled
    if not no_cython_hid:
        import StreamDeck.Transport.LibUSBHIDAPI as LibUSBHIDAPI_module

        from knoepfe.transport import CythonHIDAPI

        LibUSBHIDAPI_module.LibUSBHIDAPI = CythonHIDAPI

    # Configure logging based on verbose flag
    configure_logging(verbose=verbose)

    # Store options in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config"] = config
    ctx.obj["mock_device"] = mock_device
    ctx.obj["no_cython_hid"] = no_cython_hid

    # If no subcommand is provided, run the main application
    if ctx.invoked_subcommand is None:
        knoepfe = Knoepfe()
        knoepfe.run_sync(config, mock_device)


@main.command("list-widgets")
def list_widgets() -> None:
    """List all available widgets."""
    # Create managers for CLI commands
    # Create plugin manager for CLI commands
    plugin_manager = PluginManager()

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
    # Create managers for CLI commands
    plugin_manager = PluginManager()

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

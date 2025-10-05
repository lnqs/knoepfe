"""CLI commands and main entry point for knoepfe."""

import json
import logging
from pathlib import Path

import click

from . import __version__
from .core.app import Knoepfe
from .plugins import PluginManager
from .transport import apply_transport_patches
from .utils.logging import configure_logging

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
    # Apply transport patches and optionally enable CythonHIDAPI
    apply_transport_patches(enable_cython_hid=not no_cython_hid)

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


@main.group()
def widgets() -> None:
    """Manage and inspect widgets."""
    pass


@widgets.command("list")
def widgets_list() -> None:
    """List all available widgets."""
    plugin_manager = PluginManager()

    if not plugin_manager.widgets:
        click.echo("No widgets available. Install widget packages like 'knoepfe[obs]'")
        return

    click.echo("Available widgets:")
    for widget_info in sorted(plugin_manager.widgets.values(), key=lambda w: w.name):
        try:
            doc = widget_info.description or widget_info.widget_class.__doc__ or "No description"
            click.echo(f"  {widget_info.name}: {doc}")
        except Exception as e:
            click.echo(f"  {widget_info.name}: Error getting info - {e}", err=True)


@widgets.command("info")
@click.argument("widget_name")
def widgets_info(widget_name: str) -> None:
    """Show detailed information about a widget."""
    plugin_manager = PluginManager()

    if widget_name not in plugin_manager.widgets:
        click.echo(f"Error: Widget '{widget_name}' not found", err=True)
        click.echo("Try 'knoepfe widgets list' to see available widgets")
        return

    widget = plugin_manager.widgets[widget_name]
    click.echo(f"Name: {widget.name}")
    click.echo(f"Class: {widget.widget_class.__name__}")
    click.echo(f"Module: {widget.widget_class.__module__}")
    click.echo(f"Description: {widget.description or widget.widget_class.__doc__ or 'No description available'}")
    click.echo(f"Plugin: {widget.plugin_info.name} v{widget.plugin_info.version}")

    # Get configuration schema from the widget's config type
    try:
        schema = widget.config_type.model_json_schema()
        click.echo("\nConfiguration Schema:")
        click.echo(json.dumps(schema, indent=2))
    except Exception as e:
        click.echo(f"Error getting configuration schema: {e}", err=True)


@main.group()
def plugins() -> None:
    """Manage and inspect plugins."""
    pass


@plugins.command("list")
def plugins_list() -> None:
    """List all available plugins."""
    plugin_manager = PluginManager()

    # Filter out builtin plugin
    plugins = {name: info for name, info in plugin_manager.plugins.items() if name != "builtin"}

    if not plugins:
        click.echo("No plugins available.")
        return

    click.echo("Available plugins:")
    for plugin_info in sorted(plugins.values(), key=lambda p: p.name):
        widget_count = len(plugin_info.widgets)
        click.echo(f"  {plugin_info.name} v{plugin_info.version}: {plugin_info.description} ({widget_count} widgets)")


@plugins.command("info")
@click.argument("plugin_name")
def plugins_info(plugin_name: str) -> None:
    """Show detailed information about a plugin."""
    plugin_manager = PluginManager()

    if plugin_name not in plugin_manager.plugins:
        click.echo(f"Error: Plugin '{plugin_name}' not found", err=True)
        click.echo("Try 'knoepfe plugins list' to see available plugins")
        return

    plugin = plugin_manager.plugins[plugin_name]
    click.echo(f"Name: {plugin.name}")
    click.echo(f"Version: {plugin.version}")
    click.echo(f"Description: {plugin.description}")
    click.echo(f"Class: {plugin.plugin_class.__name__}")
    click.echo(f"Module: {plugin.plugin_class.__module__}")

    click.echo(f"\nWidgets ({len(plugin.widgets)}):")
    if plugin.widgets:
        for widget in sorted(plugin.widgets, key=lambda w: w.name):
            desc = widget.description or "No description"
            click.echo(f"  {widget.name}: {desc}")
    else:
        click.echo("  No widgets provided")

    # Show configuration schema
    try:
        schema = plugin.config.model_json_schema()
        click.echo("\nConfiguration Schema:")
        click.echo(json.dumps(schema, indent=2))
    except Exception as e:
        click.echo(f"Error getting configuration schema: {e}", err=True)

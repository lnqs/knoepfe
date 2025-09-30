import logging
from pathlib import Path
from typing import Any

import platformdirs
from schema import And, Optional, Schema

from knoepfe.deck import Deck
from knoepfe.plugin_manager import PluginManager
from knoepfe.widgets.base import Widget

logger = logging.getLogger(__name__)


device = Schema(
    {
        Optional("brightness"): And(int, lambda b: 0 <= b <= 100),
        Optional("sleep_timeout"): And(float, lambda b: b > 0.0),
        Optional("device_poll_frequency"): And(int, lambda v: 1 <= v <= 1000),
    }
)


def get_config_path(path: Path | None = None) -> Path:
    if path:
        return path

    path = Path(platformdirs.user_config_dir(__package__), "knoepfe.cfg")
    if path.exists():
        return path

    default_config = Path(__file__).parent.joinpath("default.cfg")
    logger.info(
        f"No configuration file found at `{path}`. Consider copying the default "
        f"config from `{default_config}` to this place and adjust it to your needs."
    )

    return default_config


def exec_config(config: str, plugin_manager: PluginManager) -> tuple[dict[str, Any], Deck, list[Deck]]:
    global_config: dict[str, Any] = {}
    decks = []
    main_deck = None

    def config_(plugin_name: str, config_data: dict[str, Any]) -> None:
        # Handle device config specially (built-in)
        if plugin_name == "device":
            # Validate device config
            device.validate(config_data)
            global_config["knoepfe.config.device"] = config_data
        else:
            # Store plugin config for plugin manager
            plugin_manager.set_plugin_config(plugin_name, config_data)
            # Also store in global config
            global_config[plugin_name] = config_data

    def deck_(deck_name: str, widgets: list[Widget | None]) -> Deck:
        nonlocal main_deck

        d = Deck(deck_name, widgets, global_config)
        decks.append(d)

        # Track the main deck
        if deck_name == "main":
            if main_deck:
                raise RuntimeError("Main deck already defined")
            main_deck = d

        return d

    def widget_(widget_name: str, widget_config: dict[str, Any] | None = None) -> Widget:
        if widget_config is None:
            widget_config = {}
        return create_widget(widget_name, widget_config, global_config, plugin_manager)

    exec(
        config,
        {
            "config": config_,
            "deck": deck_,
            "widget": widget_,
        },
    )

    if not main_deck:
        raise RuntimeError("No 'main' deck specified - a deck named 'main' is required")

    return global_config, main_deck, decks


def process_config(path: Path | None, plugin_manager: PluginManager) -> tuple[dict[str, Any], Deck, list[Deck]]:
    path = get_config_path(path)
    with open(path) as f:
        config = f.read()

    return exec_config(config, plugin_manager)


def create_widget(
    widget_name: str, widget_config: dict[str, Any], global_config: dict[str, Any], plugin_manager: PluginManager
) -> Widget:
    # Use plugin manager to get widget class
    widget_class = plugin_manager.get_widget(widget_name)

    # Get the plugin that provides this widget
    plugin = plugin_manager.get_plugin_for_widget(widget_name)

    # Validate config against widget schema
    schema = widget_class.get_config_schema()
    schema.validate(widget_config)

    # Pass the plugin's state, not the plugin itself
    return widget_class(widget_config, global_config, plugin.state)

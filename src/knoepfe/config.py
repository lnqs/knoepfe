import logging
from importlib import import_module
from pathlib import Path
from typing import Any, TypedDict

import platformdirs
from schema import And, Optional, Schema

from knoepfe.deck import Deck
from knoepfe.plugin_manager import plugin_manager
from knoepfe.widgets.base import Widget

logger = logging.getLogger(__name__)

DeckConfig = TypedDict("DeckConfig", {"id": str, "widgets": list[Widget | None]})

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


def exec_config(config: str) -> tuple[dict[str, Any], Deck, list[Deck]]:
    global_config: dict[str, Any] = {}
    decks = []
    default = None

    def config_(c: dict[str, Any]) -> None:
        type_, conf = create_config(c)
        if type_ in global_config:
            raise RuntimeError(f"Config {type_} already set")
        global_config[type_] = conf

    def deck(c: DeckConfig) -> Deck:
        d = create_deck(c)
        decks.append(d)
        return d

    def default_deck(c: DeckConfig) -> Deck:
        nonlocal default
        if default:
            raise RuntimeError("default deck already set")
        d = deck(c)
        default = d
        return d

    def widget(c: dict[str, Any]) -> Widget:
        return create_widget(c, global_config)

    exec(
        config,
        {
            "config": config_,
            "deck": deck,
            "default_deck": default_deck,
            "widget": widget,
        },
    )

    if not default:
        raise RuntimeError("No default deck specified")

    return global_config, default, decks


def process_config(path: Path | None = None) -> tuple[dict[str, Any], Deck, list[Deck]]:
    path = get_config_path(path)
    with open(path) as f:
        config = f.read()

    return exec_config(config)


def create_config(config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    type_ = config["type"]
    parts = type_.rsplit(".", 1)
    module = import_module(parts[0])
    schema: Schema = getattr(module, parts[-1])

    if not isinstance(schema, Schema):
        raise RuntimeError(f"{schema} isn't a Schema")

    config = config.copy()
    del config["type"]
    schema.validate(config)

    return type_, config


def create_deck(config: DeckConfig) -> Deck:
    return Deck(**config)


def create_widget(config: dict[str, Any], global_config: dict[str, Any]) -> Widget:
    widget_type = config["type"]

    # Use plugin manager to get widget class
    widget_class = plugin_manager.get_widget(widget_type)

    config = config.copy()
    del config["type"]

    # Validate config against widget schema
    schema = widget_class.get_config_schema()
    schema.validate(config)

    return widget_class(config, global_config)

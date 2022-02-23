from importlib import import_module
from pathlib import Path
from typing import Any, Dict, List, Tuple, Type, TypedDict

import appdirs
from schema import And, Optional, Schema

from knoepfe.deck import Deck
from knoepfe.log import info
from knoepfe.widgets.base import Widget

DeckConfig = TypedDict("DeckConfig", {"id": str, "widgets": List[Widget | None]})

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

    path = Path(appdirs.user_config_dir(__package__), "knoepfe.cfg")
    if path.exists():
        return path

    default_config = Path(__file__).parent.joinpath("default.cfg")
    info(
        f"No configuration file found at `{path}`. Consider copying the default"
        f"config from `{default_config}` to this place and adjust it to your needs."
    )

    return default_config


def exec_config(config: str) -> Tuple[Dict[str, Any], Deck, List[Deck]]:
    global_config: Dict[str, Any] = {}
    decks = []
    default = None

    def config_(c: Dict[str, Any]) -> None:
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

    def widget(c: Dict[str, Any]) -> Widget:
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


def process_config(path: Path | None = None) -> Tuple[Dict[str, Any], Deck, List[Deck]]:
    path = get_config_path(path)
    with open(path) as f:
        config = f.read()

    return exec_config(config)


def create_config(config: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
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


def create_widget(config: Dict[str, Any], global_config: Dict[str, Any]) -> Widget:
    parts = config["type"].rsplit(".", 1)
    module = import_module(parts[0])
    class_: Type[Widget] = getattr(module, parts[-1])

    if not issubclass(class_, Widget):
        raise RuntimeError(f"{class_} isn't a subclass of Widget")

    config = config.copy()
    del config["type"]
    schema = class_.get_config_schema()

    schema.validate(config)

    return class_(config, global_config)

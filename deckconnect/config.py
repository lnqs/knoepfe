from importlib import import_module
from pathlib import Path
from typing import Any, Dict, List, Tuple, Type, TypedDict

import appdirs

from deckconnect.deck import Deck
from deckconnect.widgets.base import Widget

DeckConfig = TypedDict("DeckConfig", {"id": str, "widgets": List[Widget | None]})


def get_config_path(path: Path | None = None) -> Path:
    if path:
        return path

    path = Path(appdirs.user_config_dir(__package__), "default.cfg")
    if path.exists():
        return path

    return Path(__file__).parent.joinpath("default.cfg")


def exec_config(config: str) -> Tuple[Deck, List[Deck]]:
    decks = []
    default = None

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
        return create_widget(c)

    exec(config, {"deck": deck, "default_deck": default_deck, "widget": widget})

    if not default:
        raise RuntimeError("No default deck specified")

    return (default, decks)


def process_config(path: Path | None = None) -> Tuple[Deck, List[Deck]]:
    path = get_config_path(path)
    with open(path) as f:
        config = f.read()

    default, decks = exec_config(config)
    return default, decks


def create_deck(config: DeckConfig) -> Deck:
    return Deck(**config)


def create_widget(config: Dict[str, Any]) -> Widget:
    parts = config["type"].rsplit(".", 1)
    module = import_module(parts[0])
    class_: Type[Widget] = getattr(module, parts[-1])

    if not issubclass(class_, Widget):
        raise RuntimeError(f"{class_} isn't a subclass of Widget")

    config = config.copy()
    del config["type"]
    schema = class_.get_config_schema()
    schema.validate(config)

    return class_(config)

from typing import Any, Dict

from schema import Schema

from deckconnect.widgets.base import Widget


class Text(Widget):
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    @staticmethod
    def get_config_schema() -> Schema:
        return Schema({"text": str})

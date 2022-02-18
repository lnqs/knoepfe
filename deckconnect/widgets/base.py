from typing import Any, Dict

from schema import Schema


class Widget:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    @staticmethod
    def get_config_schema() -> Schema:
        return Schema({})

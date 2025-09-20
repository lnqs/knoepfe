class SwitchDeckException(BaseException):
    def __init__(self, new_deck: str) -> None:
        self.new_deck = new_deck

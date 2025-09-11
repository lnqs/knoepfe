from typing import List

from StreamDeck.Devices.StreamDeck import StreamDeck
from StreamDeck.Transport.Dummy import Dummy


class MockDeck(StreamDeck):  # type: ignore
    KEY_COUNT = 16
    KEY_COLS = 4
    KEY_ROWS = 4

    KEY_PIXEL_WIDTH = 80
    KEY_PIXEL_HEIGHT = 80
    KEY_IMAGE_FORMAT = "BMP"
    KEY_FLIP = (True, True)
    KEY_ROTATION = 0

    DECK_TYPE = None

    def __init__(self) -> None:
        super().__init__(Dummy.Device("0000", "0000"))

    def _read_key_states(self) -> List[bool]:
        return self.KEY_COUNT * [False]

    def _reset_key_stream(self) -> None:
        pass

    def reset(self) -> None:
        pass

    def set_brightness(self, percent: int) -> None:
        pass

    def get_serial_number(self) -> str:
        return "MOCK"

    def get_firmware_version(self) -> str:
        return "1.0.0"

    def set_key_image(self, key: int, image: str) -> None:
        pass

    def _read_control_states(self) -> None:
        pass

    def set_touchscreen_image(
        self,
        image: bytes,
        x_pos: int = 0,
        y_pos: int = 0,
        width: int = 0,
        height: int = 0,
    ) -> None:
        pass

    def set_key_color(self, key: int, r: int, g: int, b: int) -> None:
        pass

    def set_screen_image(self, image: bytes) -> None:
        pass

from contextlib import contextmanager
from typing import Iterator, Literal

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.Devices import StreamDeck
from StreamDeck.ImageHelpers import PILHelper

Align = Literal["left", "center", "right"]
VAlign = Literal["top", "middle", "bottom"]


class Renderer:
    def __init__(self) -> None:
        self.image = Image.new("RGB", (512, 512))

    def text(
        self,
        text: str,
        x: int = 0,
        y: int = 0,
        align: Align = "center",
        valign: VAlign = "middle",
        font_size: int = 96,
    ) -> "Renderer":
        font = ImageFont.truetype("Roboto-Regular.ttf", font_size)
        draw = ImageDraw.Draw(self.image)
        text_width, text_height = draw.textsize(text, font=font)

        if align == "center":
            x = x + self.image.width // 2 - text_width // 2
        elif align == "right":
            x = x + self.image.width - text_width

        if valign == "middle":
            y = y + self.image.height // 2 - text_height // 2
        elif valign == "bottom":
            y = y + self.image.height - text_height

        draw.text((x, y), text=text, font=font)
        return self


class Key:
    def __init__(self, device: StreamDeck, index: int) -> None:
        self.device = device
        self.index = index

    @contextmanager
    def renderer(self) -> Iterator[Renderer]:
        r = Renderer()
        yield r

        image = PILHelper.to_native_format(self.device, r.image)
        with self.device:
            self.device.set_key_image(self.index, image)

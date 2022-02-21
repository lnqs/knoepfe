from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Literal, Tuple

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.Devices import StreamDeck
from StreamDeck.ImageHelpers import PILHelper

Align = Literal["left", "center", "right"]
VAlign = Literal["top", "middle", "bottom"]


ICONS = dict(
    line.split(" ")
    for line in Path(__file__)
    .parent.joinpath("MaterialIcons-Regular.codepoints")
    .read_text()
    .split("\n")
    if line
)


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
        color: str | None = None,
    ) -> "Renderer":
        return self._draw_text(
            "Roboto-Regular.ttf", text, x, y, align, valign, font_size, color
        )

    def icon(
        self,
        icon: str,
        x: int = 0,
        y: int = 0,
        align: Align = "center",
        valign: VAlign = "middle",
        font_size: int = 512,
        color: str | None = None,
    ) -> "Renderer":
        text = chr(int(ICONS[icon], 16))
        return self._draw_text(
            "MaterialIcons-Regular.ttf", text, x, y, align, valign, font_size, color
        )

    def _draw_text(
        self,
        font_file: str,
        text: str,
        x: int,
        y: int,
        align: Align,
        valign: VAlign,
        font_size: int,
        color: str | None,
    ) -> "Renderer":
        font_path = Path(__file__).parent.joinpath(font_file)
        font = ImageFont.truetype(str(font_path), font_size)
        draw = ImageDraw.Draw(self.image)
        text_width, text_height = draw.textsize(text, font=font)
        x, y = self._aligned(x, y, text_width, text_height, align, valign)
        draw.text((x, y), text=text, font=font, fill=color)
        return self

    def _aligned(
        self, x: int, y: int, w: int, h: int, align: Align, valign: VAlign
    ) -> Tuple[int, int]:
        if align == "center":
            x = x + self.image.width // 2 - w // 2
        elif align == "right":
            x = x + self.image.width - w

        if valign == "middle":
            y = y + self.image.height // 2 - h // 2
        elif valign == "bottom":
            y = y + self.image.height - h

        return x, y


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

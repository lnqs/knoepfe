from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Literal, Tuple

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont
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
        self.image = Image.new("RGB", (96, 96))

    def text(self, text: str, size: int = 24, color: str | None = None) -> "Renderer":
        return self._render_text("text", text, size, color)

    def icon(self, text: str, color: str | None = None) -> "Renderer":
        return self._render_text("icon", text, 86, color)

    def icon_and_text(
        self, icon: str, text: str, color: str | None = None
    ) -> "Renderer":
        self._render_text("icon", icon, 86, color, "top")
        self._render_text("text", text, 16, color, "bottom")
        return self

    def _render_text(
        self,
        type: Literal["text", "icon"],
        text: str,
        size: int,
        color: str | None,
        valign: VAlign = "middle",
    ) -> "Renderer":
        font = self._get_font(type, size)
        draw = ImageDraw.Draw(self.image)
        text_width, text_height = draw.textsize(text, font=font)
        x, y = self._aligned(text_width, text_height, "center", valign)
        draw.text((x, y), text=text, font=font, fill=color, align="center")
        return self

    def _aligned(self, w: int, h: int, align: Align, valign: VAlign) -> Tuple[int, int]:
        x, y = 0, 0

        if align == "center":
            x = self.image.width // 2 - w // 2
        elif align == "right":
            x = self.image.width - w

        if valign == "middle":
            y = self.image.height // 2 - h // 2
        elif valign == "bottom":
            y = self.image.height - h - 6

        return x, y

    def _get_font(self, type: Literal["text", "icon"], size: int) -> FreeTypeFont:
        font_file = (
            "Roboto-Regular.ttf" if type == "text" else "MaterialIcons-Regular.ttf"
        )
        font_path = Path(__file__).parent.joinpath(font_file)
        return ImageFont.truetype(str(font_path), size)


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

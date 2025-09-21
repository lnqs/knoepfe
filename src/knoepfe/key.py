from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Literal

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont
from StreamDeck.Devices.StreamDeck import StreamDeck
from StreamDeck.ImageHelpers import PILHelper

from .font_manager import FontManager

Align = Literal["left", "center", "right"]
VAlign = Literal["top", "middle", "bottom"]


ICONS = dict(
    line.split(" ")
    for line in Path(__file__).parent.joinpath("MaterialIcons-Regular.codepoints").read_text().split("\n")
    if line
)


class Renderer:
    def __init__(self) -> None:
        self.image = Image.new("RGB", (96, 96))

        self.font_manager = FontManager()

    def text(
        self, text: str, size: int = 24, color: str | None = None, font: str | None = None, anchor: str | None = None
    ) -> "Renderer":
        """Render text with fontconfig pattern and anchor support."""
        if anchor is None:
            anchor = "ms"  # middle-baseline (centered)

        return self._render_text("text", text, size, color, font_pattern=font, anchor=anchor, xy=(48, 48))

    def text_at(
        self,
        xy: tuple[int, int],
        text: str,
        size: int = 24,
        color: str | None = None,
        font: str | None = None,
        anchor: str = "la",
    ) -> "Renderer":
        """Draw text at specific position with fontconfig pattern."""
        return self._render_text("text", text, size, color, font_pattern=font, anchor=anchor, xy=xy)

    def icon(self, text: str, color: str | None = None) -> "Renderer":
        return self._render_text("icon", text, 86, color)

    def icon_and_text(self, icon: str, text: str, color: str | None = None) -> "Renderer":
        self._render_text("icon", icon, 86, color, "top")
        self._render_text("text", text, 16, color, "bottom")
        return self

    def _render_text(
        self,
        type: Literal["text", "icon"],
        text: str,
        size: int,
        color: str | None,
        valign: VAlign | None = None,  # Deprecated
        font_pattern: str | None = None,
        anchor: str | None = None,
        xy: tuple[int, int] | None = None,
    ) -> "Renderer":
        # Get font
        if type == "icon":
            # Icons still use bundled MaterialIcons font
            font = self._get_font("icon", size)
            anchor = anchor or "ms"
        else:
            # Use fontconfig pattern
            pattern = font_pattern or "Roboto"
            font = FontManager.get_font(pattern, size)

        # Handle legacy valign parameter for backward compatibility
        if xy is None and valign is not None:
            # Legacy behavior - calculate position based on text size and valign
            draw = ImageDraw.Draw(self.image)
            if "\n" in text:
                lines = text.split("\n")
                text_width = max(int(draw.textlength(line, font=font)) for line in lines)
            else:
                text_width = int(draw.textlength(text, font=font))
            text_height = int(font.size * (text.strip().count("\n") + 1))
            x, y = self._aligned(text_width, text_height, "center", valign)
            xy = (x, y)
            anchor = "la"  # left-ascender for legacy positioning
        elif xy is None:
            # Default position
            xy = (48, 48)

        # Default anchor
        if anchor is None:
            anchor = "la"

        # Draw text with Pillow anchor
        draw = ImageDraw.Draw(self.image)
        draw.text(xy, text=text, font=font, fill=color or "white", anchor=anchor, align="center")
        return self

    def _aligned(self, w: int, h: int, align: Align, valign: VAlign) -> tuple[int, int]:
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
        font_file = "Roboto-Regular.ttf" if type == "text" else "MaterialIcons-Regular.ttf"
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

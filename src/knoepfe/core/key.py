import textwrap
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Union

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.Devices.StreamDeck import StreamDeck
from StreamDeck.ImageHelpers import PILHelper

from ..config.models import GlobalConfig
from ..rendering.font_manager import FontManager


class Renderer:
    """Renderer with both primitive operations and convenience methods."""

    def __init__(self, config: GlobalConfig) -> None:
        self.canvas = Image.new("RGB", (96, 96), color="black")
        self._draw = ImageDraw.Draw(self.canvas)
        self.config = config

        # Get default font from config (Nerd Font contains both text and icons)
        self.default_text_font = config.device.default_text_font

    # ========== Primitive Operations ==========

    def text(
        self,
        position: tuple[int, int],
        text: str,
        font: Union[ImageFont.FreeTypeFont, str] | None = None,
        size: int = 24,
        color: str = "white",
        anchor: str = "la",
    ) -> "Renderer":
        """Draw text at specific position.

        Args:
            position: (x, y) coordinates
            text: Text to draw
            font: Font name/pattern or ImageFont instance (defaults to config default_text_font)
            size: Font size (ignored if font is ImageFont instance)
            color: Text color
            anchor: Text anchor (e.g., "mm" for middle-middle)
        """
        if font is None:
            font = self.default_text_font
        if isinstance(font, str):
            font = FontManager.get_font(font, size)
        self._draw.text(position, text, font=font, fill=color, anchor=anchor)
        return self

    def draw_image(
        self,
        img: Union[Image.Image, str, Path],
        position: tuple[int, int] = (0, 0),
        size: tuple[int, int] | None = None,
    ) -> "Renderer":
        """Draw an image at position, optionally resizing.

        Args:
            img: PIL Image, file path, or Path object
            position: (x, y) coordinates for top-left corner
            size: Optional (width, height) to resize to
        """
        if isinstance(img, (str, Path)):
            img = Image.open(img)

        if size:
            img = img.resize(size, Image.Resampling.LANCZOS)

        if img.mode in ("RGBA", "LA"):
            self.canvas.paste(img, position, img)
        else:
            self.canvas.paste(img, position)
        return self

    @property
    def draw(self) -> ImageDraw.ImageDraw:
        """Direct access to PIL ImageDraw for custom drawing."""
        return self._draw

    def clear(self, color: str = "black") -> "Renderer":
        """Clear canvas with solid color."""
        self._draw.rectangle([0, 0, 96, 96], fill=color)
        return self

    def measure_text(
        self, text: str, font: Union[ImageFont.FreeTypeFont, str] | None = None, size: int = 24
    ) -> tuple[int, int]:
        """Get text dimensions without drawing.

        Returns:
            (width, height) of the text
        """
        if font is None:
            font = self.default_text_font
        if isinstance(font, str):
            font = FontManager.get_font(font, size)
        bbox = self._draw.textbbox((0, 0), text, font=font)
        return int(bbox[2] - bbox[0]), int(bbox[3] - bbox[1])

    # ========== Convenience Methods ==========

    def icon(
        self,
        icon: str,
        size: int = 64,
        color: str = "white",
        position: tuple[int, int] | None = None,
        font: str | None = None,
    ) -> "Renderer":
        """Render an icon (Unicode character) centered or at position.

        Args:
            icon: Unicode character (e.g., "\ue029" or "🎤")
            size: Icon size
            color: Icon color
            position: Optional (x, y) position, defaults to center
            font: Font to use for icon (defaults to config default_text_font)
        """
        if font is None:
            font = self.default_text_font
        if position is None:
            position = (48, 48)
        return self.text(position, icon, font=font, size=size, color=color, anchor="mm")

    def image_centered(
        self, image_path: Union[str, Path, Image.Image], size: Union[int, tuple[int, int]] = 72, padding: int = 12
    ) -> "Renderer":
        """Render an image centered with optional padding.

        Args:
            image_path: Path to image or PIL Image
            size: Target size (int for square, tuple for width/height)
            padding: Padding from edges
        """
        # Load image if needed
        if isinstance(image_path, (str, Path)):
            img = Image.open(image_path)
        else:
            img = image_path

        # Calculate size with padding
        canvas_size = 96 - 2 * padding

        if isinstance(size, int):
            target_size = min(size, canvas_size)
            img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
        else:
            img = img.resize(size, Image.Resampling.LANCZOS)

        # Center image
        x = (96 - img.width) // 2
        y = (96 - img.height) // 2

        return self.draw_image(img, (x, y))

    def icon_and_text(
        self,
        icon: str,
        text: str,
        icon_size: int = 64,
        text_size: int = 16,
        icon_color: str = "white",
        text_color: str = "white",
        icon_font: str | None = None,
        text_font: str | None = None,
        spacing: int = 8,
    ) -> "Renderer":
        """Render icon with text below it.

        Args:
            icon: Unicode character for icon
            text: Text to display below icon
            icon_size: Size of icon
            text_size: Size of text
            icon_color: Color of icon
            text_color: Color of text
            icon_font: Font for icon (defaults to config default_text_font)
            text_font: Font for text (defaults to config default_text_font)
            spacing: Pixels between icon and text
        """
        if icon_font is None:
            icon_font = self.default_text_font
        if text_font is None:
            text_font = self.default_text_font

        # Calculate vertical positions
        total_height = icon_size + spacing + text_size
        start_y = (96 - total_height) // 2

        icon_y = start_y + icon_size // 2
        text_y = start_y + icon_size + spacing

        # Render icon
        self.icon(icon, icon_size, icon_color, (48, icon_y), icon_font)

        # Render text
        return self.text((48, text_y), text, font=text_font, size=text_size, color=text_color, anchor="mt")

    def image_and_text(
        self,
        image_path: Union[str, Path, Image.Image],
        text: str,
        image_size: int = 64,
        text_size: int = 16,
        text_color: str = "white",
        text_font: str | None = None,
        spacing: int = 8,
    ) -> "Renderer":
        """Render image with text below it.

        Args:
            image_path: Path to image or PIL Image
            text: Text to display below image
            image_size: Maximum size for image
            text_size: Size of text
            text_color: Color of text
            text_font: Font for text (defaults to config default_text_font)
            spacing: Pixels between image and text
        """
        if text_font is None:
            text_font = self.default_text_font

        # Load and prepare image
        if isinstance(image_path, (str, Path)):
            img = Image.open(image_path)
        else:
            img = image_path

        img.thumbnail((image_size, image_size), Image.Resampling.LANCZOS)

        # Calculate layout
        total_height = img.height + spacing + text_size
        start_y = (96 - total_height) // 2

        # Render image
        self.draw_image(img, ((96 - img.width) // 2, start_y))

        # Render text
        text_y = start_y + img.height + spacing
        return self.text((48, text_y), text, font=text_font, size=text_size, color=text_color, anchor="mt")

    def text_wrapped(
        self,
        text: str,
        size: int = 16,
        color: str = "white",
        font: str | None = None,
        max_width: int = 80,
        line_spacing: int = 4,
    ) -> "Renderer":
        """Render text with automatic word wrapping, centered.

        Args:
            text: Text to wrap and display
            size: Font size
            color: Text color
            font: Font name/pattern (defaults to config default_text_font)
            max_width: Maximum width in pixels before wrapping
            line_spacing: Pixels between lines
        """
        if font is None:
            font = self.default_text_font

        # Simple character-based wrapping (could be improved with actual width measurement)
        chars_per_line = max_width // (size // 2)  # Rough estimate
        lines = textwrap.wrap(text, width=chars_per_line)

        # Calculate starting position
        total_height = len(lines) * size + (len(lines) - 1) * line_spacing
        y = (96 - total_height) // 2

        # Render each line
        for i, line in enumerate(lines):
            line_y = y + i * (size + line_spacing)
            self.text((48, line_y), line, font=font, size=size, color=color, anchor="mt")

        return self


class Key:
    def __init__(self, device: StreamDeck, index: int, config: GlobalConfig) -> None:
        self.device = device
        self.index = index
        self.config = config

    @contextmanager
    def renderer(self) -> Iterator[Renderer]:
        r = Renderer(self.config)
        yield r

        image = PILHelper.to_native_format(self.device, r.canvas)
        with self.device:
            self.device.set_key_image(self.index, image)

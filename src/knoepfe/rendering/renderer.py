"""Renderer for Stream Deck key displays."""

import textwrap
from pathlib import Path
from typing import Union

from PIL import Image, ImageDraw, ImageFont

from .font_manager import FontManager


class Renderer:
    """Renderer with both primitive operations and convenience methods."""

    def __init__(self, default_text_font: str) -> None:
        """Initialize renderer with default font.

        Args:
            default_text_font: Default font pattern for text and icons (e.g., "RobotoMono Nerd Font")
        """
        self.canvas = Image.new("RGB", (96, 96), color="black")
        self._draw = ImageDraw.Draw(self.canvas)
        self.default_text_font = default_text_font

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

        # Handle palette mode images with transparency
        if img.mode == "P" and "transparency" in img.info:
            img = img.convert("RGBA")

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

    def _text_centered_visual(
        self,
        text: str,
        font: ImageFont.FreeTypeFont,
        center: tuple[int, int],
        color: str = "white",
    ) -> "Renderer":
        """Draw text centered based on visual glyph bounds.

        This helper ensures text is truly centered by calculating the actual glyph
        bounds, which is important for monospace fonts where glyphs may not be
        centered within their character cell.

        Args:
            text: Text to draw
            font: PIL ImageFont instance (must be loaded)
            center: (x, y) coordinates for the visual center
            color: Text color
        """
        # Get bounding box to measure actual glyph dimensions
        # Use anchor='lt' (left-top) at origin to get true glyph bounds
        bbox = self._draw.textbbox((0, 0), text, font=font, anchor="lt")
        glyph_width = bbox[2] - bbox[0]
        glyph_height = bbox[3] - bbox[1]

        # Calculate position to center the glyph visually
        # Account for glyph offset from anchor point
        glyph_left_offset = bbox[0]
        glyph_top_offset = bbox[1]

        # Adjust position so glyph center aligns with target center
        adjusted_x = center[0] - glyph_left_offset - glyph_width / 2
        adjusted_y = center[1] - glyph_top_offset - glyph_height / 2

        # Draw with 'lt' anchor at calculated position
        self._draw.text((adjusted_x, adjusted_y), text, font=font, fill=color, anchor="lt")
        return self

    # ========== Convenience Methods ==========

    def icon(
        self,
        icon: str,
        size: int = 86,
        color: str = "white",
        position: tuple[int, int] | None = None,
        font: str | None = None,
    ) -> "Renderer":
        """Render an icon (Unicode character) centered or at position.

        This method ensures the icon is visually centered by calculating the actual
        glyph bounds, which is important for monospace fonts where glyphs may not
        be centered within their character cell.

        Args:
            icon: Unicode character (e.g., "\ue029" or "🎤")
            size: Icon size
            color: Icon color
            position: Optional (x, y) position, defaults to center (48, 48)
            font: Font to use for icon (defaults to config default_text_font)
        """
        if font is None:
            font = self.default_text_font
        if position is None:
            position = (48, 48)

        # Load font if it's a string pattern
        if isinstance(font, str):
            font_obj = FontManager.get_font(font, size)
        else:
            font_obj = font

        # Use visual centering helper for accurate positioning
        return self._text_centered_visual(icon, font_obj, position, color)

    def image(
        self,
        image_path: Union[str, Path, Image.Image],
        size: int = 86,
        position: tuple[int, int] | None = None,
    ) -> "Renderer":
        """Render an image at a centered position with automatic sizing.

        Displays an image at the specified size, centered at the given position.
        By default, renders an 86x86 image centered on the key (matching typical
        icon sizes). The image is resized to fit within the specified dimensions
        while maintaining its aspect ratio.

        Args:
            image_path: Path to image file or PIL Image object
            size: Target size in pixels (image scaled to fit within size×size)
            position: Center point (x, y) for the image, defaults to (48, 48)
        """
        if position is None:
            position = (48, 48)

        # Calculate top-left position to center the image at the target position
        x = position[0] - size // 2
        y = position[1] - size // 2

        return self.draw_image(image_path, (x, y), (size, size))

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

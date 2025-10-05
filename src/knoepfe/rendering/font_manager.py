"""Font management using python-fontconfig for system font access."""

from functools import lru_cache

import fontconfig
from PIL import ImageFont


class FontManager:
    """Manages system fonts using python-fontconfig."""

    @classmethod
    @lru_cache()
    def get_font(cls, pattern: str = "Roboto", size: int = 24) -> ImageFont.FreeTypeFont:
        """Get a font from a fontconfig pattern string.

        Examples:
            "Ubuntu" - Ubuntu family
            "Ubuntu:style=Bold" - Ubuntu Bold
            "Roboto" - default Roboto font
            "DejaVu Sans" - DejaVu Sans font
            "monospace" - default monospace font
        """
        # Query fontconfig directly with the pattern
        fonts = fontconfig.query(pattern)

        if not fonts:
            raise ValueError(f"No font found for pattern: {pattern}")

        # Use the first matching font
        font_path = fonts[0]

        # Load font
        return ImageFont.truetype(font_path, size)

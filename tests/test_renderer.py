from contextlib import contextmanager
from unittest.mock import Mock, patch

from knoepfe.rendering import Renderer
from knoepfe.rendering.font_manager import FontManager


@contextmanager
def mock_fontconfig_system():
    """Context manager to mock the fontconfig system with common setup."""
    with patch("knoepfe.rendering.font_manager.fontconfig") as mock_fontconfig:
        mock_fontconfig.query.return_value = ["/path/to/font.ttf"]

        with patch("knoepfe.rendering.font_manager.ImageFont.truetype") as mock_truetype:
            mock_font = Mock()
            mock_font.size = 12  # Default size for tests
            # Mock the getmask2 method that PIL uses internally
            mock_font.getmask2.return_value = (Mock(), (0, 0))
            mock_truetype.return_value = mock_font

            yield {"fontconfig": mock_fontconfig, "truetype": mock_truetype, "font": mock_font}


def test_renderer_text() -> None:
    renderer = Renderer("Roboto", "RobotoMono Nerd Font")
    with patch.object(renderer, "_draw") as mock_draw:
        with mock_fontconfig_system():
            renderer.text((48, 48), "Blubb")
            mock_draw.text.assert_called_once()


def test_renderer_draw_text() -> None:
    with mock_fontconfig_system():
        renderer = Renderer("Roboto", "RobotoMono Nerd Font")

        with patch.object(renderer, "_draw") as mock_draw:
            # Test basic text rendering
            renderer.text((10, 20), "Test Text", size=12)

            # Check that text was called with correct parameters
            mock_draw.text.assert_called_once()
            call_args = mock_draw.text.call_args
            assert call_args[0][0] == (10, 20)  # position
            assert call_args[0][1] == "Test Text"  # text is positional arg


def test_renderer_convenience_methods() -> None:
    with mock_fontconfig_system() as mocks:
        # Mock getmetrics for text_multiline (ascent, descent)
        mocks["font"].getmetrics.return_value = (12, 4)  # Total height = 16

        renderer = Renderer("Roboto", "RobotoMono Nerd Font")

        with patch.object(renderer, "_draw") as mock_draw:
            # Test icon method
            renderer.icon("test_icon", size=64)
            mock_draw.text.assert_called()

            # Test text_multiline method
            renderer.text_multiline("Test multiline text")
            assert mock_draw.text.call_count >= 1


def test_renderer_image_method() -> None:
    """Test the image convenience method."""
    with mock_fontconfig_system():
        renderer = Renderer("Roboto", "RobotoMono Nerd Font")

        # Mock the draw_image method to verify it's called correctly
        with patch.object(renderer, "draw_image") as mock_draw_image:
            mock_draw_image.return_value = renderer  # For method chaining

            # Test with default parameters (centered, 86px)
            result = renderer.image("test.png")

            # Verify draw_image was called with correct parameters
            # Default: size=86, position=(48,48)
            # Calculated position: (48 - 86//2, 48 - 86//2) = (5, 5)
            # Size passed to draw_image: (86, 86)
            mock_draw_image.assert_called_once_with("test.png", (5, 5), (86, 86))

            # Verify method chaining works
            assert result is renderer


def test_renderer_image_method_custom_size() -> None:
    """Test image method with custom size."""
    with mock_fontconfig_system():
        renderer = Renderer("Roboto", "RobotoMono Nerd Font")

        with patch.object(renderer, "draw_image") as mock_draw_image:
            mock_draw_image.return_value = renderer

            # Test with custom size
            renderer.image("test.png", size=64)

            # Verify draw_image was called with correct position for 64px image
            # Position: (48 - 64//2, 48 - 64//2) = (16, 16)
            mock_draw_image.assert_called_once_with("test.png", (16, 16), (64, 64))


def test_renderer_image_method_custom_position() -> None:
    """Test image method with custom position."""
    with mock_fontconfig_system():
        renderer = Renderer("Roboto", "RobotoMono Nerd Font")

        with patch.object(renderer, "draw_image") as mock_draw_image:
            mock_draw_image.return_value = renderer

            # Test with custom position
            renderer.image("test.png", position=(30, 40))

            # Verify draw_image was called with position adjusted for centering
            # Position: (30 - 86//2, 40 - 86//2) = (-13, -3)
            mock_draw_image.assert_called_once_with("test.png", (-13, -3), (86, 86))


def test_renderer_image_method_with_pil_image() -> None:
    """Test image method with PIL Image object instead of path."""
    with mock_fontconfig_system():
        renderer = Renderer("Roboto", "RobotoMono Nerd Font")

        # Create a mock PIL Image object
        from PIL import Image

        mock_img = Mock(spec=Image.Image)

        with patch.object(renderer, "draw_image") as mock_draw_image:
            mock_draw_image.return_value = renderer

            # Pass PIL Image directly
            renderer.image(mock_img)

            # Verify draw_image was called with the PIL Image object
            mock_draw_image.assert_called_once_with(mock_img, (5, 5), (86, 86))


def test_font_manager_get_font() -> None:
    """Test FontManager font loading with mocked fontconfig."""
    # Clear the cache first to ensure clean test
    FontManager.get_font.cache_clear()

    with mock_fontconfig_system() as mocks:
        font = FontManager.get_font("Roboto", 24)

        assert font == mocks["font"]
        mocks["fontconfig"].query.assert_called_with("Roboto")
        mocks["truetype"].assert_called_with("/path/to/font.ttf", 24)


def test_font_manager_caching() -> None:
    """Test FontManager font caching."""
    # Clear the cache first to ensure clean test
    FontManager.get_font.cache_clear()

    with mock_fontconfig_system() as mocks:
        font1 = FontManager.get_font("Roboto", 24)
        font2 = FontManager.get_font("Roboto", 24)

        # Should be the same cached font
        assert font1 is font2
        # truetype should only be called once due to caching
        assert mocks["truetype"].call_count == 1

        # Check cache info
        cache_info = FontManager.get_font.cache_info()
        assert cache_info.hits == 1  # Second call was a cache hit
        assert cache_info.misses == 1  # First call was a cache miss


def test_font_manager_error_handling() -> None:
    """Test FontManager error handling when pattern not found."""
    with mock_fontconfig_system() as mocks:
        # Override to return empty list (no fonts found)
        mocks["fontconfig"].query.return_value = []

        # Should raise ValueError when no fonts found
        try:
            FontManager.get_font("nonexistent", 24)
            raise AssertionError("Expected ValueError to be raised")
        except ValueError as e:
            assert "No font found for pattern: nonexistent" in str(e)

        mocks["fontconfig"].query.assert_called_with("nonexistent")


def test_renderer_fontconfig_integration() -> None:
    """Test Renderer integration with FontManager."""
    with mock_fontconfig_system() as mocks:
        # Override for Ubuntu font
        mocks["fontconfig"].query.return_value = ["/path/to/ubuntu.ttf"]

        renderer = Renderer("Roboto", "RobotoMono Nerd Font")

        with patch.object(renderer, "_draw") as mock_draw:
            # Test text with fontconfig pattern
            renderer.text((48, 48), "Hello", font="Ubuntu", size=24)

            # Should have queried fontconfig for Ubuntu
            mocks["fontconfig"].query.assert_called_with("Ubuntu")
            mocks["truetype"].assert_called_with("/path/to/ubuntu.ttf", 24)

            # Should have drawn text
            mock_draw.text.assert_called_once()


def test_renderer_text_at() -> None:
    """Test Renderer text_at method."""
    with mock_fontconfig_system():
        renderer = Renderer("Roboto", "RobotoMono Nerd Font")

        with patch.object(renderer, "_draw") as mock_draw:
            renderer.text((10, 20), "Positioned", font="monospace", anchor="la")

            mock_draw.text.assert_called_once()
            call_args = mock_draw.text.call_args
            assert call_args[0][0] == (10, 20)
            assert call_args[0][1] == "Positioned"  # text is positional arg


def test_renderer_backward_compatibility() -> None:
    """Test that existing code without font parameter still works."""
    with mock_fontconfig_system():
        renderer = Renderer("Roboto", "RobotoMono Nerd Font")

        with patch.object(renderer, "_draw") as mock_draw:
            # Test with default font (should use Roboto)
            renderer.text((48, 48), "Legacy Text", size=20, color="#ffffff")

            mock_draw.text.assert_called_once()
            call_args = mock_draw.text.call_args
            assert call_args[0][1] == "Legacy Text"  # text is positional arg
            assert call_args[1]["fill"] == "#ffffff"


def test_renderer_unicode_icons() -> None:
    """Test that Unicode icons work with fontconfig patterns."""
    with mock_fontconfig_system() as mocks:
        # Override for Material Icons font
        mocks["fontconfig"].query.return_value = ["/path/to/materialicons.ttf"]

        renderer = Renderer("Roboto", "RobotoMono Nerd Font")

        with patch.object(renderer, "_draw"):
            # Test Unicode icon with Nerd Font
            renderer.text((48, 48), "🎤", font="RobotoMono Nerd Font", size=86)

            # Should have queried fontconfig for RobotoMono Nerd Font
            mocks["fontconfig"].query.assert_called_with("RobotoMono Nerd Font")
            mocks["truetype"].assert_called_with("/path/to/materialicons.ttf", 86)

            # Should have drawn the Unicode character


def test_renderer_text_multiline_with_newlines() -> None:
    """Test that text_multiline preserves explicit newlines."""
    with mock_fontconfig_system() as mocks:
        # Mock getmetrics to return font metrics (ascent, descent)
        mocks["font"].getmetrics.return_value = (12, 4)  # Total height = 16

        renderer = Renderer("Roboto", "RobotoMono Nerd Font")

        with patch.object(renderer, "_draw") as mock_draw:
            # Test text with explicit newlines
            renderer.text_multiline("Hello\nWorld", size=16)

            # Should have called text twice (once per line)
            assert mock_draw.text.call_count == 2

            # Verify the text content of each call
            calls = mock_draw.text.call_args_list
            assert calls[0][0][1] == "Hello"  # First line
            assert calls[1][0][1] == "World"  # Second line


def test_renderer_text_multiline_with_multiple_newlines() -> None:
    """Test that text_multiline handles multiple consecutive newlines."""
    with mock_fontconfig_system() as mocks:
        # Mock getmetrics to return font metrics (ascent, descent)
        mocks["font"].getmetrics.return_value = (12, 4)  # Total height = 16

        renderer = Renderer("Roboto", "RobotoMono Nerd Font")

        with patch.object(renderer, "_draw") as mock_draw:
            # Test text with multiple newlines (creates empty line)
            renderer.text_multiline("Line1\n\nLine3", size=16)

            # Should have called text three times (including empty line)
            assert mock_draw.text.call_count == 3

            # Verify the text content
            calls = mock_draw.text.call_args_list
            assert calls[0][0][1] == "Line1"  # First line
            assert calls[1][0][1] == ""  # Empty line
            assert calls[2][0][1] == "Line3"  # Third line


def test_renderer_text_multiline_preserves_spacing() -> None:
    """Test that text_multiline maintains proper line spacing with newlines."""
    with mock_fontconfig_system() as mocks:
        # Mock getmetrics to return font metrics (ascent, descent)
        mocks["font"].getmetrics.return_value = (12, 4)  # Total height = 16

        renderer = Renderer("Roboto", "RobotoMono Nerd Font")

        with patch.object(renderer, "_draw") as mock_draw:
            # Test with custom line spacing
            renderer.text_multiline("Line1\nLine2\nLine3", size=16, line_spacing=8)

            # Should have three calls
            assert mock_draw.text.call_count == 3

            # Verify y-coordinates increase by (line_height + line_spacing)
            calls = mock_draw.text.call_args_list
            y1 = calls[0][0][0][1]  # y-coordinate of first line
            y2 = calls[1][0][0][1]  # y-coordinate of second line
            y3 = calls[2][0][0][1]  # y-coordinate of third line

            # Each line should be (16 + 8) = 24 pixels apart (line_height from getmetrics + spacing)
            assert y2 - y1 == 24
            assert y3 - y2 == 24

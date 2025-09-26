from contextlib import contextmanager
from unittest.mock import DEFAULT, MagicMock, Mock, patch

from knoepfe.font_manager import FontManager
from knoepfe.key import Key, Renderer


@contextmanager
def mock_fontconfig_system():
    """Context manager to mock the fontconfig system with common setup."""
    with patch("knoepfe.font_manager.fontconfig") as mock_fontconfig:
        mock_fontconfig.query.return_value = ["/path/to/font.ttf"]

        with patch("knoepfe.font_manager.ImageFont.truetype") as mock_truetype:
            mock_font = Mock()
            mock_font.size = 12  # Default size for tests
            # Mock the getmask2 method that PIL uses internally
            mock_font.getmask2.return_value = (Mock(), (0, 0))
            mock_truetype.return_value = mock_font

            yield {"fontconfig": mock_fontconfig, "truetype": mock_truetype, "font": mock_font}


def test_renderer_text() -> None:
    renderer = Renderer()
    with patch.object(renderer, "_draw") as mock_draw:
        with mock_fontconfig_system():
            renderer.text((48, 48), "Blubb")
            mock_draw.text.assert_called_once()


def test_renderer_draw_text() -> None:
    with mock_fontconfig_system():
        renderer = Renderer()

        with patch.object(renderer, "_draw") as mock_draw:
            # Test basic text rendering
            renderer.text((10, 20), "Test Text", size=12)

            # Check that text was called with correct parameters
            mock_draw.text.assert_called_once()
            call_args = mock_draw.text.call_args
            assert call_args[0][0] == (10, 20)  # position
            assert call_args[0][1] == "Test Text"  # text is positional arg


def test_key_render() -> None:
    key = Key(MagicMock(), 0, {})

    with patch.multiple("knoepfe.key", PILHelper=DEFAULT, Renderer=DEFAULT):
        with key.renderer():
            pass

    assert key.device.set_key_image.called  # type: ignore[attr-defined]


def test_renderer_convenience_methods() -> None:
    with mock_fontconfig_system():
        renderer = Renderer()

        with patch.object(renderer, "_draw") as mock_draw:
            # Test icon method
            renderer.icon("test_icon", size=64)
            mock_draw.text.assert_called()

            # Test text_wrapped method
            renderer.text_wrapped("Test wrapped text")
            assert mock_draw.text.call_count >= 1


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

        renderer = Renderer()

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
        renderer = Renderer()

        with patch.object(renderer, "_draw") as mock_draw:
            renderer.text((10, 20), "Positioned", font="monospace", anchor="la")

            mock_draw.text.assert_called_once()
            call_args = mock_draw.text.call_args
            assert call_args[0][0] == (10, 20)
            assert call_args[0][1] == "Positioned"  # text is positional arg


def test_renderer_backward_compatibility() -> None:
    """Test that existing code without font parameter still works."""
    with mock_fontconfig_system():
        renderer = Renderer()

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

        renderer = Renderer()

        with patch.object(renderer, "_draw") as mock_draw:
            # Test Unicode icon with Material Icons font
            renderer.text((48, 48), "🎤", font="Material Icons", size=86)

            # Should have queried fontconfig for Material Icons
            mocks["fontconfig"].query.assert_called_with("Material Icons")
            mocks["truetype"].assert_called_with("/path/to/materialicons.ttf", 86)

            # Should have drawn the Unicode character
            mock_draw.text.assert_called_once()
            call_args = mock_draw.text.call_args
            # Check the 'text' keyword argument
            assert call_args[0][1] == "🎤"  # Unicode character

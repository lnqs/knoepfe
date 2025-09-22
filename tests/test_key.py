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
            mock_truetype.return_value = mock_font

            yield {"fontconfig": mock_fontconfig, "truetype": mock_truetype, "font": mock_font}


def test_renderer_text() -> None:
    renderer = Renderer()
    with patch.object(renderer, "_render_text") as draw_text:
        renderer.text("Blubb")
        assert draw_text.called


def test_renderer_draw_text() -> None:
    with mock_fontconfig_system():
        renderer = Renderer()

        with patch(
            "knoepfe.key.ImageDraw.Draw",
            return_value=Mock(textlength=Mock(return_value=0)),
        ) as draw:
            renderer._render_text("Text", size=12, color=None, valign="top")
            assert draw.return_value.text.call_args[0][0] == (48, 0)

        with patch(
            "knoepfe.key.ImageDraw.Draw",
            return_value=Mock(textlength=Mock(return_value=0)),
        ) as draw:
            renderer._render_text("Text", size=12, color=None, valign="middle")
            assert draw.return_value.text.call_args[0][0] == (48, 42)

        with patch(
            "knoepfe.key.ImageDraw.Draw",
            return_value=Mock(textlength=Mock(return_value=0)),
        ) as draw:
            renderer._render_text("Text", size=12, color=None, valign="bottom")
            assert draw.return_value.text.call_args[0][0] == (48, 78)


def test_key_render() -> None:
    key = Key(MagicMock(), 0)

    with patch.multiple("knoepfe.key", PILHelper=DEFAULT, Renderer=DEFAULT):
        with key.renderer():
            pass

    assert key.device.set_key_image.called  # type: ignore[attr-defined]


def test_key_aligned() -> None:
    renderer = Renderer()
    assert renderer._aligned(10, 10, "left", "top") == (0, 0)
    assert renderer._aligned(10, 10, "center", "middle") == (43, 43)
    assert renderer._aligned(10, 10, "right", "bottom") == (86, 80)


def test_font_manager_get_font() -> None:
    """Test FontManager font loading with mocked fontconfig."""
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

        with patch("knoepfe.key.ImageDraw.Draw") as mock_draw:
            mock_draw_instance = Mock()
            mock_draw.return_value = mock_draw_instance

            # Test text with fontconfig pattern
            renderer.text("Hello", font="Ubuntu", size=24)

            # Should have queried fontconfig for Ubuntu
            mocks["fontconfig"].query.assert_called_with("Ubuntu")
            mocks["truetype"].assert_called_with("/path/to/ubuntu.ttf", 24)

            # Should have drawn text with the returned font
            mock_draw_instance.text.assert_called_once()
            call_args = mock_draw_instance.text.call_args
            assert call_args[1]["font"] == mocks["font"]


def test_renderer_text_at() -> None:
    """Test Renderer text_at method."""
    with mock_fontconfig_system():
        renderer = Renderer()

        with patch.object(renderer, "_render_text") as mock_render_text:
            renderer.text_at((10, 20), "Positioned", font="monospace", anchor="la")

            mock_render_text.assert_called_once_with(
                "Positioned", 24, None, font_pattern="monospace", anchor="la", xy=(10, 20)
            )


def test_renderer_backward_compatibility() -> None:
    """Test that existing code without font parameter still works."""
    with mock_fontconfig_system():
        renderer = Renderer()

        with patch.object(renderer, "_render_text") as mock_render_text:
            # Old-style call without font parameter
            renderer.text("Legacy Text", size=20, color="#ffffff")

            # Should use default "Roboto" pattern
            mock_render_text.assert_called_once_with(
                "Legacy Text", 20, "#ffffff", font_pattern=None, anchor="ms", xy=(48, 48)
            )


def test_renderer_unicode_icons() -> None:
    """Test that Unicode icons work with fontconfig patterns."""
    with mock_fontconfig_system() as mocks:
        # Override for Material Icons font
        mocks["fontconfig"].query.return_value = ["/path/to/materialicons.ttf"]

        renderer = Renderer()

        with patch("knoepfe.key.ImageDraw.Draw") as mock_draw:
            mock_draw_instance = Mock()
            mock_draw.return_value = mock_draw_instance

            # Test Unicode icon with Material Icons font
            renderer.text("🎤", font="Material Icons", size=86)

            # Should have queried fontconfig for Material Icons
            mocks["fontconfig"].query.assert_called_with("Material Icons")
            mocks["truetype"].assert_called_with("/path/to/materialicons.ttf", 86)

            # Should have drawn the Unicode character
            mock_draw_instance.text.assert_called_once()
            call_args = mock_draw_instance.text.call_args
            # Check the 'text' keyword argument
            assert call_args[1]["text"] == "🎤"  # Unicode character

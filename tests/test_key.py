from unittest.mock import DEFAULT, MagicMock, Mock, patch

from deckconnect.key import Key, Renderer


def test_renderer_text() -> None:
    renderer = Renderer()
    with patch.object(renderer, "_render_text") as draw_text:
        renderer.text("Blubb")
        assert draw_text.called


def test_renderer_icon() -> None:
    renderer = Renderer()
    with patch.object(renderer, "_render_text") as draw_text:
        renderer.icon("mic")
        assert draw_text.called


def test_renderer_icon_and_text() -> None:
    renderer = Renderer()
    with patch.object(renderer, "_render_text") as draw_text:
        renderer.icon_and_text("mic", "text")
        assert draw_text.call_count == 2


def test_renderer_draw_text() -> None:
    renderer = Renderer()

    with patch(
        "deckconnect.key.ImageDraw.Draw",
        return_value=Mock(textsize=Mock(return_value=(0, 0))),
    ) as draw:
        renderer._render_text("text", "Text", size=12, color=None, valign="top")
        assert draw.return_value.text.call_args[0][0] == (48, 0)

    with patch(
        "deckconnect.key.ImageDraw.Draw",
        return_value=Mock(textsize=Mock(return_value=(0, 0))),
    ) as draw:
        renderer._render_text("text", "Text", size=12, color=None, valign="middle")
        assert draw.return_value.text.call_args[0][0] == (48, 48)

    with patch(
        "deckconnect.key.ImageDraw.Draw",
        return_value=Mock(textsize=Mock(return_value=(0, 0))),
    ) as draw:
        renderer._render_text("text", "Text", size=12, color=None, valign="bottom")
        assert draw.return_value.text.call_args[0][0] == (48, 90)


def test_key_render() -> None:
    key = Key(MagicMock(), 0)

    with patch.multiple("deckconnect.key", PILHelper=DEFAULT, Renderer=DEFAULT):
        with key.renderer():
            pass

    assert key.device.set_key_image.called

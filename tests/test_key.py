from unittest.mock import DEFAULT, MagicMock, Mock, patch

from deckconnect.key import Key, Renderer


def test_renderer_text() -> None:
    renderer = Renderer()
    with patch.object(renderer, "_draw_text") as draw_text:
        renderer.text("Blubb")
        assert draw_text.called


def test_renderer_icon() -> None:
    renderer = Renderer()
    with patch.object(renderer, "_draw_text") as draw_text:
        renderer.icon("mic")
        assert draw_text.called


def test_renderer_draw_text() -> None:
    renderer = Renderer()

    with patch(
        "deckconnect.key.ImageDraw.Draw",
        return_value=Mock(textsize=Mock(return_value=(0, 0))),
    ) as draw:
        renderer._draw_text(
            "Roboto-Regular.ttf",
            "Text",
            x=0,
            y=0,
            align="left",
            valign="top",
            font_size=42,
            color=None,
        )
        assert draw.return_value.text.call_args[0][0] == (0, 0)

    with patch(
        "deckconnect.key.ImageDraw.Draw",
        return_value=Mock(textsize=Mock(return_value=(0, 0))),
    ) as draw:
        renderer._draw_text(
            "Roboto-Regular.ttf",
            "Text",
            x=0,
            y=0,
            align="center",
            valign="middle",
            font_size=42,
            color=None,
        )
        assert draw.return_value.text.call_args[0][0] == (256, 256)

    with patch(
        "deckconnect.key.ImageDraw.Draw",
        return_value=Mock(textsize=Mock(return_value=(0, 0))),
    ) as draw:
        renderer._draw_text(
            "Roboto-Regular.ttf",
            "Text",
            x=0,
            y=0,
            align="right",
            valign="bottom",
            font_size=42,
            color=None,
        )
        assert draw.return_value.text.call_args[0][0] == (512, 512)


def test_key_render() -> None:
    key = Key(MagicMock(), 0)

    with patch.multiple("deckconnect.key", PILHelper=DEFAULT, Renderer=DEFAULT):
        with key.renderer():
            pass

    assert key.device.set_key_image.called

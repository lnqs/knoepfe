from unittest.mock import DEFAULT, MagicMock, Mock, patch

from deckconnect.key import Key, Renderer


def test_renderer_text() -> None:
    renderer = Renderer()

    with patch(
        "deckconnect.key.ImageDraw.Draw",
        return_value=Mock(textsize=Mock(return_value=(0, 0))),
    ) as draw:
        renderer.text("Text", align="left", valign="top")
        assert draw.return_value.text.call_args[0][0] == (0, 0)

    with patch(
        "deckconnect.key.ImageDraw.Draw",
        return_value=Mock(textsize=Mock(return_value=(0, 0))),
    ) as draw:
        renderer.text("Text", align="center", valign="middle")
        assert draw.return_value.text.call_args[0][0] == (256, 256)

    with patch(
        "deckconnect.key.ImageDraw.Draw",
        return_value=Mock(textsize=Mock(return_value=(0, 0))),
    ) as draw:
        renderer.text("Text", align="right", valign="bottom")
        assert draw.return_value.text.call_args[0][0] == (512, 512)


def test_key_render() -> None:
    key = Key(MagicMock(), 0)

    with patch.multiple("deckconnect.key", PILHelper=DEFAULT, Renderer=DEFAULT):
        with key.renderer():
            pass

    assert key.device.set_key_image.called

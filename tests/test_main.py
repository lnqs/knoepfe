from pathlib import Path
from unittest.mock import Mock, patch

from pytest import raises

from deckconnect.__main__ import main, run


def test_main_success() -> None:
    with patch("deckconnect.__main__.run") as run:
        main()
    assert run.call_args[0][0] is None


def test_main_error() -> None:
    with patch("deckconnect.__main__.run", side_effect=Exception("Error!")):
        with raises(SystemExit):
            main()

    with patch("deckconnect.__main__.run", side_effect=Exception("Error!")), patch(
        "sys.argv", ["deckconnect", "--verbose"]
    ):
        with raises(Exception):
            main()


def test_run_success() -> None:
    with patch(
        "deckconnect.__main__.process_config", return_value=(Mock(), [Mock()])
    ) as process_config:
        run(Path("path"))
    assert process_config.called


def test_run_error() -> None:
    with patch("deckconnect.__main__.process_config", side_effect=Exception("Error!")):
        with raises(Exception):
            run(Path("path"))

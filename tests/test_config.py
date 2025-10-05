from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
from pydantic import ValidationError

from knoepfe.config.loader import ConfigError, load_config
from knoepfe.config.models import DeckConfig, DeviceConfig, GlobalConfig


def test_load_config_valid():
    """Test loading a valid configuration."""
    config_content = """
device(brightness=80, sleep_timeout=30.0)

plugin.obs(host='localhost', port=4455)

deck.main([
    widget.Clock(format='%H:%M'),
    widget.Text(text='Hello'),
])
"""

    mock_file = mock_open(read_data=config_content)
    with patch("builtins.open", mock_file):
        config = load_config(Path("test.cfg"))

    assert isinstance(config, GlobalConfig)
    assert config.device.brightness == 80
    assert config.device.sleep_timeout == 30.0
    assert "obs" in config.plugins
    assert config.plugins["obs"]["host"] == "localhost"
    assert "main" in config.decks
    assert len(config.decks["main"].widgets) == 2


def test_load_config_validation_error():
    """Test that invalid config raises ConfigError."""
    config_content = """
device(brightness=150)  # Invalid: > 100

deck.main([widget.Clock()])
"""

    mock_file = mock_open(read_data=config_content)
    with patch("builtins.open", mock_file):
        with pytest.raises(ConfigError, match="validation failed"):
            load_config(Path("test.cfg"))


def test_load_config_no_main_deck():
    """Test that missing main deck raises ConfigError."""
    config_content = """
deck.other([widget.Clock()])
"""

    mock_file = mock_open(read_data=config_content)
    with patch("builtins.open", mock_file):
        with pytest.raises(ConfigError, match="validation failed"):
            load_config(Path("test.cfg"))


def test_load_config_file_not_found():
    """Test that missing file raises FileNotFoundError (not wrapped in ConfigError for explicit paths)."""
    with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
        with pytest.raises(FileNotFoundError):
            load_config(Path("nonexistent.cfg"))


def test_global_config_device_defaults():
    """Test that device config has proper defaults."""
    config = GlobalConfig(decks={"main": DeckConfig(name="main", widgets=[])})

    assert config.device.brightness == 100
    assert config.device.sleep_timeout == 10.0
    assert config.device.device_poll_frequency == 5


def test_global_config_validation():
    """Test GlobalConfig validation."""
    # Valid config
    config = GlobalConfig(
        device=DeviceConfig(brightness=50),
        decks={"main": DeckConfig(name="main", widgets=[])},
    )
    assert config.device.brightness == 50

    # Invalid brightness
    with pytest.raises(ValidationError):
        GlobalConfig(
            device=DeviceConfig(brightness=150),
            decks={"main": DeckConfig(name="main", widgets=[])},
        )

    # Missing main deck
    with pytest.raises(ValidationError):
        GlobalConfig(decks={"other": DeckConfig(name="other", widgets=[])})

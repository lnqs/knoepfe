from pathlib import Path

import pytest
from pydantic import ValidationError

from knoepfe.config.loader import ConfigError, load_config
from knoepfe.config.models import DeviceConfig, GlobalConfig


def test_load_config_valid(tmp_path):
    """Test loading a valid configuration."""
    config_content = """
[device]
brightness = 80
sleep_timeout = 30.0

[plugins.obs]
host = "localhost"
port = 4455

[[deck.main]]
type = "Clock"
[[deck.main.segments]]
format = "%H:%M"
x = 0
y = 0
width = 96
height = 96

[[deck.main]]
type = "Text"
text = "Hello"
"""

    config_file = tmp_path / "test.toml"
    config_file.write_text(config_content)

    config = load_config(config_file)

    assert isinstance(config, GlobalConfig)
    assert config.device.brightness == 80
    assert config.device.sleep_timeout == 30.0
    assert "obs" in config.plugins
    assert config.plugins["obs"]["host"] == "localhost"
    assert len(config.decks) == 1
    assert config.decks[0].name == "main"
    assert len(config.decks[0].widgets) == 2


def test_load_config_validation_error(tmp_path):
    """Test that invalid config raises ConfigError."""
    config_content = """
[device]
brightness = 150

[[deck.main]]
type = "Clock"
[[deck.main.segments]]
format = "%H:%M"
x = 0
y = 0
width = 96
height = 96
"""

    config_file = tmp_path / "test.toml"
    config_file.write_text(config_content)

    with pytest.raises(ConfigError, match="validation failed"):
        load_config(config_file)


def test_load_config_no_main_deck(tmp_path):
    """Test that missing main deck raises ConfigError."""
    config_content = """
[[deck.other]]
type = "Clock"
[[deck.other.segments]]
format = "%H:%M"
x = 0
y = 0
width = 96
height = 96
"""

    config_file = tmp_path / "test.toml"
    config_file.write_text(config_content)

    with pytest.raises(ConfigError, match="validation failed"):
        load_config(config_file)


def test_load_config_file_not_found():
    """Test that missing file raises ConfigError."""
    with pytest.raises(ConfigError, match="not found"):
        load_config(Path("nonexistent.toml"))


def test_global_config_device_defaults():
    """Test that device config has proper defaults."""
    config = GlobalConfig(deck={"main": []})

    assert config.device.brightness == 100
    assert config.device.sleep_timeout == 10.0
    assert config.device.device_poll_frequency == 5
    assert config.device.serial_number is None


def test_device_config_with_serial_number():
    """Test that device config accepts serial number."""
    config = GlobalConfig(
        device=DeviceConfig(serial_number="ABC123"),
        deck={"main": []},
    )
    assert config.device.serial_number == "ABC123"


def test_global_config_validation():
    """Test GlobalConfig validation."""
    # Valid config
    config = GlobalConfig(
        device=DeviceConfig(brightness=50),
        deck={"main": []},
    )
    assert config.device.brightness == 50

    # Invalid brightness
    with pytest.raises(ValidationError):
        GlobalConfig(
            device=DeviceConfig(brightness=150),
            deck={"main": []},
        )

    # Missing main deck
    with pytest.raises(ValidationError):
        GlobalConfig(deck={"other": []})

"""Tests for environment variable support in configuration."""

from knoepfe.config.loader import load_config


def test_env_var_overrides_toml(tmp_path, monkeypatch):
    """Test that environment variables override TOML values."""
    config_content = """
[device]
brightness = 80
sleep_timeout = 30.0

[[deck.main]]
type = "Clock"
"""

    config_file = tmp_path / "test.toml"
    config_file.write_text(config_content)

    # Set environment variable to override brightness
    monkeypatch.setenv("KNOEPFE_DEVICE__BRIGHTNESS", "50")

    config = load_config(config_file)

    # Environment variable should override TOML value
    assert config.device.brightness == 50
    # Other values should remain from TOML
    assert config.device.sleep_timeout == 30.0


def test_env_var_nested_delimiter(tmp_path, monkeypatch):
    """Test that nested environment variables work with __ delimiter."""
    config_content = """
[[deck.main]]
type = "Clock"
"""

    config_file = tmp_path / "test.toml"
    config_file.write_text(config_content)

    # Set nested environment variable
    monkeypatch.setenv("KNOEPFE_DEVICE__SLEEP_TIMEOUT", "60.0")

    config = load_config(config_file)

    # Environment variable should set the nested value
    assert config.device.sleep_timeout == 60.0


def test_env_var_without_toml_value(tmp_path, monkeypatch):
    """Test that environment variables can set values not in TOML."""
    config_content = """
[[deck.main]]
type = "Clock"
"""

    config_file = tmp_path / "test.toml"
    config_file.write_text(config_content)

    # Set environment variable for a value not in TOML
    monkeypatch.setenv("KNOEPFE_DEVICE__SERIAL_NUMBER", "ABC123")

    config = load_config(config_file)

    # Environment variable should set the value
    assert config.device.serial_number == "ABC123"


def test_no_env_vars_uses_toml_defaults(tmp_path):
    """Test that without env vars, TOML values are used."""
    config_content = """
[device]
brightness = 75

[[deck.main]]
type = "Clock"
"""

    config_file = tmp_path / "test.toml"
    config_file.write_text(config_content)

    config = load_config(config_file)

    # Should use TOML value
    assert config.device.brightness == 75
    # Should use default value for unspecified fields
    assert config.device.sleep_timeout == 10.0

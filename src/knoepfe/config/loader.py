"""Configuration loading and processing functions."""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import platformdirs
from pydantic import ValidationError
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, TomlConfigSettingsSource

from ..config.models import GlobalConfig, WidgetSpec
from ..utils.exceptions import WidgetNotFoundError

if TYPE_CHECKING:
    from ..core.deck import Deck
    from ..plugins.manager import PluginManager
    from ..widgets.base import Widget

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Configuration-related errors."""

    pass


def _create_config_with_file(config_path: Path) -> GlobalConfig:
    """Create GlobalConfig with explicit file path.

    This creates a custom settings source that loads from the specified file path.
    """

    class ConfigWithFile(GlobalConfig):
        """GlobalConfig with custom file path."""

        @classmethod
        def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
        ) -> tuple[PydanticBaseSettingsSource, ...]:
            """Customize settings sources with explicit file path."""
            # Return sources in priority order: env vars > TOML file > init
            return (
                env_settings,
                TomlConfigSettingsSource(settings_cls, config_path),
                init_settings,
            )

    return ConfigWithFile()


def load_config(path: Path | None = None) -> GlobalConfig:
    """Load configuration from TOML file with environment variable support.

    Args:
        path: Optional path to config file. If None, uses default locations.

    Returns:
        Loaded and validated GlobalConfig

    Raises:
        ConfigError: If configuration is invalid or cannot be loaded
    """
    # Resolve config file path
    if path:
        logger.info(f"Using config file: {path}")
        config_path = path
    else:
        # Check user config directory
        config_dir = Path(platformdirs.user_config_dir("knoepfe"))
        user_config = config_dir / "knoepfe.toml"

        if user_config.exists():
            logger.info(f"Using user config: {user_config}")
            config_path = user_config
        else:
            # No default config - user must create one
            raise ConfigError(
                f"No configuration file found. Please create a config file at {user_config}\n"
                "See the documentation for examples."
            )

    # Check if file exists before attempting to load
    if not config_path.exists():
        raise ConfigError(f"Configuration file not found: {config_path}")

    try:
        # Create GlobalConfig instance with explicit file path
        # The custom settings_customise_sources method will:
        # 1. Load from TOML file via TomlConfigSettingsSource with explicit path
        # 2. Override with environment variables (KNOEPFE_ prefix)
        config = _create_config_with_file(config_path)
        return config

    except ValidationError as e:
        raise ConfigError("Configuration validation failed") from e
    except Exception as e:
        raise ConfigError(f"Failed to load configuration: {e}") from e


def create_decks(config: GlobalConfig, plugin_manager: "PluginManager") -> list["Deck"]:
    """Create deck instances from configuration.

    Args:
        config: Global configuration
        plugin_manager: Plugin manager for widget creation

    Returns:
        List of all decks

    Raises:
        ConfigError: If deck creation fails
    """
    # Late import to avoid circular dependency
    from ..core.deck import Deck

    decks = []

    for deck_config in config.decks:
        widgets = []

        for widget_spec in deck_config.widgets:
            try:
                widget = create_widget(widget_spec, plugin_manager)
                widgets.append(widget)
            except ValidationError as e:
                raise ConfigError(f"Invalid config for widget {widget_spec.type} in deck {deck_config.name}") from e
            except Exception as e:
                raise ConfigError(f"Failed to create widget {widget_spec.type} in deck {deck_config.name}") from e

        deck = Deck(deck_config.name, widgets, config)
        decks.append(deck)

    return decks


def create_widget(spec: WidgetSpec, plugin_manager: "PluginManager") -> "Widget":
    """Create a single widget instance.

    Args:
        spec: Widget specification from config
        plugin_manager: Plugin manager for widget lookup

    Returns:
        Instantiated widget

    Raises:
        WidgetNotFoundError: If widget type is not found
        ValidationError: If widget config is invalid
    """
    if spec.type not in plugin_manager.widgets:
        raise WidgetNotFoundError(spec.type)

    widget_info = plugin_manager.widgets[spec.type]

    # Create and validate typed config from spec
    config = widget_info.config_type(**spec.config)

    # Instantiate widget with validated config and plugin instance
    return widget_info.widget_class(config, widget_info.plugin_info.plugin)

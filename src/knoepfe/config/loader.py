"""Configuration loading and processing functions."""

import logging
from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING

import platformdirs
from pydantic import ValidationError

from ..config.dsl import ConfigBuilder
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


def load_config(path: Path | None = None) -> GlobalConfig:
    """Load configuration from file.

    Args:
        path: Optional path to config file. If None, uses default locations.

    Returns:
        Loaded and validated GlobalConfig

    Raises:
        ConfigError: If configuration is invalid or cannot be loaded
    """
    # Resolve config file
    if path:
        logger.info(f"Using config file: {path}")
        config_file = open(path, "r")
        config_name = str(path)
    else:
        # Check user config directory
        config_dir = Path(platformdirs.user_config_dir("knoepfe"))
        user_config = config_dir / "knoepfe.cfg"

        if user_config.exists():
            logger.info(f"Using user config: {user_config}")
            config_file = open(user_config, "r")
            config_name = str(user_config)
        else:
            # Fall back to default config from package resources
            logger.info("No user config found, using default configuration")
            logger.info(f"Consider creating your own config file at {user_config}")
            default_resource = files("knoepfe").joinpath("data/default.cfg")
            config_file = default_resource.open("r")
            config_name = "knoepfe/data/default.cfg"

    try:
        # Create builder and namespace
        builder = ConfigBuilder()
        namespace = {
            "device": builder.device,
            "plugin": builder.plugin,
            "deck": builder.deck,
            "widget": builder.widget,
        }

        # Execute config file in namespace
        config_content = config_file.read()
        exec(compile(config_content, config_name, "exec"), namespace)

        # Build and return configuration
        return builder.build()

    except ValidationError as e:
        raise ConfigError("Configuration validation failed") from e
    except Exception as e:
        raise ConfigError("Failed to load configuration") from e
    finally:
        config_file.close()


def create_decks(config: GlobalConfig, plugin_manager: "PluginManager") -> list["Deck"]:
    """Create deck instances from configuration.

    Args:
        config: Global configuration
        plugin_manager: Plugin manager for widget creation

    Returns:
        List of all decks

    Raises:
        ConfigError: If deck creation fails or no main deck defined
    """
    # Late import to avoid circular dependency
    from ..core.deck import Deck

    decks = []
    has_main_deck = False

    for deck_name, deck_config in config.decks.items():
        widgets = []

        for widget_spec in deck_config.widgets:
            try:
                widget = create_widget(widget_spec, plugin_manager)
                widgets.append(widget)
            except ValidationError as e:
                raise ConfigError(f"Invalid config for widget {widget_spec.type} in deck {deck_name}") from e
            except Exception as e:
                raise ConfigError(f"Failed to create widget {widget_spec.type} in deck {deck_name}") from e

        deck = Deck(deck_name, widgets, config)
        decks.append(deck)

        if deck_name == "main":
            has_main_deck = True

    if not has_main_deck:
        raise ConfigError("No 'main' deck defined in configuration")

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

    # Instantiate widget with validated config and context
    return widget_info.widget_class(config, widget_info.plugin_info.context)

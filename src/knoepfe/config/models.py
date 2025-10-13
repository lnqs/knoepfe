"""Core configuration models for knoepfe."""

from typing import Any

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

from knoepfe.config.base import BaseConfig


class DeviceConfig(BaseConfig):
    """Stream Deck device configuration."""

    brightness: int = Field(default=100, ge=0, le=100, description="Display brightness percentage")
    sleep_timeout: float | None = Field(default=10.0, ge=0, description="Seconds until sleep, 0 or None to disable")
    device_poll_frequency: int = Field(default=5, ge=1, le=1000, description="Hardware polling rate in Hz")
    default_text_font: str = Field(default="Roboto", description="Default font for text rendering")
    default_icons_font: str = Field(default="RobotoMono Nerd Font", description="Default font for icons rendering")
    serial_number: str | None = Field(
        default=None, description="Device serial number to connect to, None for first available"
    )


class WidgetSpec(BaseConfig):
    """Specification for a widget instance.

    Supports flattened configuration where widget properties can be specified
    at the top level alongside 'type', making TOML configs more concise.

    Example TOML (flattened):
        [[decks.widgets]]
        type = "Clock"
        font = "Roboto"
        color = "#fefefe"

    This is automatically converted to:
        type = "Clock"
        config = { font = "Roboto", color = "#fefefe" }
    """

    model_config = {"extra": "allow"}  # Allow extra fields for flattening

    type: str = Field(..., description="Widget type name")
    config: dict[str, Any] = Field(default_factory=dict, description="Widget-specific configuration")

    @model_validator(mode="before")
    @classmethod
    def flatten_config(cls, data: Any) -> Any:
        """Move all non-'type' fields into the 'config' dict for cleaner TOML syntax.

        This allows users to write:
            [[decks.widgets]]
            type = "Clock"
            font = "Roboto"

        Instead of:
            [[decks.widgets]]
            type = "Clock"
            [decks.widgets.config]
            font = "Roboto"
        """
        if not isinstance(data, dict):
            return data

        # If 'config' key already exists, merge with top-level fields
        existing_config = data.get("config", {})

        # Extract 'type' field
        widget_type = data.get("type")
        if not widget_type:
            return data

        # Move all other fields into config
        flattened_config = {}
        for key, value in data.items():
            if key not in ("type", "config"):
                flattened_config[key] = value

        # Merge with existing config (existing config takes precedence)
        flattened_config.update(existing_config)

        return {"type": widget_type, "config": flattened_config}


class DeckConfig(BaseConfig):
    """Configuration for a deck of widgets."""

    name: str = Field(..., description="Unique deck identifier")
    widgets: list[WidgetSpec] = Field(default_factory=list, description="Widgets in this deck")


class GlobalConfig(BaseSettings):
    """Root configuration object using pydantic-settings for TOML support.

    This class loads configuration from TOML files and supports environment variable
    overrides with the KNOEPFE_ prefix.

    Decks are specified using table syntax: [deck.main], [deck.scenes], etc.
    """

    model_config = SettingsConfigDict(
        env_prefix="KNOEPFE_",
        env_nested_delimiter="__",
        extra="forbid",
        validate_assignment=True,
    )

    device: DeviceConfig = Field(default_factory=DeviceConfig)
    plugins: dict[str, dict[str, Any]] = Field(default_factory=dict, description="Raw plugin configs")
    deck: dict[str, list[WidgetSpec]] = Field(default_factory=dict, description="Deck configurations by name")

    @model_validator(mode="after")
    def validate_and_convert_decks(self) -> "GlobalConfig":
        """Ensure a 'main' deck is defined and convert deck dict to list format."""
        if "main" not in self.deck:
            raise ValueError("A 'main' deck is required")
        return self

    @property
    def decks(self) -> list[DeckConfig]:
        """Convert deck dictionary to list of DeckConfig objects."""
        return [DeckConfig(name=name, widgets=widgets) for name, widgets in self.deck.items()]

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customize settings sources to load TOML file with env var overrides."""
        from pydantic_settings import TomlConfigSettingsSource

        # Return sources in priority order: env vars > TOML file > init
        return (
            env_settings,
            TomlConfigSettingsSource(settings_cls),
            init_settings,
        )

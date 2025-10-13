"""Core configuration models for knoepfe."""

from typing import Any

from pydantic import Field, field_validator

from knoepfe.config.base import BaseConfig


class DeviceConfig(BaseConfig):
    """Stream Deck device configuration."""

    brightness: int = Field(default=100, ge=0, le=100, description="Display brightness percentage")
    sleep_timeout: float | None = Field(default=10.0, gt=0, description="Seconds until sleep, None to disable")
    device_poll_frequency: int = Field(default=5, ge=1, le=1000, description="Hardware polling rate in Hz")
    default_text_font: str = Field(default="Roboto", description="Default font for text rendering")
    default_icons_font: str = Field(default="RobotoMono Nerd Font", description="Default font for icons rendering")
    serial_number: str | None = Field(
        default=None, description="Device serial number to connect to, None for first available"
    )


class WidgetSpec(BaseConfig):
    """Specification for a widget instance."""

    type: str = Field(..., description="Widget type name")
    config: dict[str, Any] = Field(default_factory=dict, description="Widget-specific configuration")


class DeckConfig(BaseConfig):
    """Configuration for a deck of widgets."""

    name: str = Field(..., description="Unique deck identifier")
    widgets: list[WidgetSpec] = Field(default_factory=list, description="Widgets in this deck")


class GlobalConfig(BaseConfig):
    """Root configuration object - pure data container."""

    device: DeviceConfig = Field(default_factory=DeviceConfig)
    plugins: dict[str, dict[str, Any]] = Field(default_factory=dict, description="Raw plugin configs")
    decks: dict[str, DeckConfig] = Field(default_factory=dict, description="Deck configurations")

    @field_validator("decks")
    @classmethod
    def validate_main_deck(cls, v: dict[str, DeckConfig]) -> dict[str, DeckConfig]:
        """Ensure a 'main' deck is defined."""
        if "main" not in v:
            raise ValueError("A 'main' deck is required")
        return v

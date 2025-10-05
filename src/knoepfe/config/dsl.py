"""DSL for configuration files."""

from typing import Any

from knoepfe.config.models import DeckConfig, DeviceConfig, GlobalConfig, WidgetSpec


class ConfigBuilder:
    """Builder for creating typed configuration."""

    def __init__(self):
        self._device_config = DeviceConfig()
        self._plugin_configs: dict[str, dict[str, Any]] = {}
        self._decks: dict[str, DeckConfig] = {}

    @property
    def device(self) -> "DeviceBuilder":
        """Access device configuration builder."""
        return DeviceBuilder(self._device_config)

    @property
    def plugin(self) -> "DynamicPluginRegistry":
        """Access plugin configuration registry."""
        return DynamicPluginRegistry(self._plugin_configs)

    @property
    def deck(self) -> "DeckBuilder":
        """Access deck builder."""
        return DeckBuilder(self)

    @property
    def widget(self) -> "DynamicWidgetFactory":
        """Access widget factory."""
        return DynamicWidgetFactory()

    def build(self) -> GlobalConfig:
        """Build the final configuration."""
        return GlobalConfig(device=self._device_config, plugins=self._plugin_configs, decks=self._decks)


class DeviceBuilder:
    """Builder for device configuration."""

    def __init__(self, config: DeviceConfig):
        self._config = config

    def __call__(self, **kwargs) -> "DeviceBuilder":
        """Configure device settings."""
        for key, value in kwargs.items():
            setattr(self._config, key, value)
        return self


class DynamicPluginRegistry:
    """Dynamic registry for plugin configurations."""

    def __init__(self, configs: dict[str, dict[str, Any]]):
        self._configs = configs

    def __getattr__(self, plugin_name: str) -> "PluginConfigBuilder":
        """Dynamically create plugin config builder for any plugin."""
        return PluginConfigBuilder(plugin_name, self._configs)


class PluginConfigBuilder:
    """Builder for a specific plugin's configuration."""

    def __init__(self, plugin_name: str, configs: dict[str, dict[str, Any]]):
        self._plugin_name = plugin_name
        self._configs = configs

    def __call__(self, **kwargs) -> None:
        """Set plugin configuration."""
        self._configs[self._plugin_name] = kwargs


class DeckBuilder:
    """Builder for deck configurations."""

    def __init__(self, builder: ConfigBuilder):
        self._builder = builder

    def __getattr__(self, name: str) -> "DeckContext":
        """Create or access a deck by name."""
        return DeckContext(self._builder, name)


class DeckContext:
    """Context for building a deck."""

    def __init__(self, builder: ConfigBuilder, name: str):
        self._builder = builder
        self._name = name

    def __call__(self, widgets: list[WidgetSpec], **kwargs) -> DeckConfig:
        """Define deck with widgets."""
        deck = DeckConfig(name=self._name, widgets=widgets, **kwargs)
        self._builder._decks[self._name] = deck
        return deck


class DynamicWidgetFactory:
    """Dynamic factory for creating widget specifications."""

    def __getattr__(self, widget_type: str) -> "WidgetBuilder":
        """Dynamically create widget builder for any widget type."""
        return WidgetBuilder(widget_type)


class WidgetBuilder:
    """Builder for a specific widget type."""

    def __init__(self, widget_type: str):
        self._widget_type = widget_type

    def __call__(self, **kwargs) -> WidgetSpec:
        """Create widget specification with config."""
        return WidgetSpec(type=self._widget_type, config=kwargs)

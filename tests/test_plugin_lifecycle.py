"""Tests for plugin context lifecycle hooks."""

from unittest.mock import AsyncMock, Mock

from StreamDeck.Devices.StreamDeck import StreamDeck

from knoepfe.config.models import GlobalConfig
from knoepfe.config.plugin import PluginConfig
from knoepfe.config.widget import WidgetConfig
from knoepfe.core.deck import Deck
from knoepfe.plugins.context import PluginContext
from knoepfe.widgets.base import Widget


class MockPluginConfig(PluginConfig):
    """Test plugin configuration."""

    pass


class MockPluginContext(PluginContext):
    """Test plugin context with lifecycle tracking."""

    def __init__(self, config: MockPluginConfig):
        super().__init__(config)
        self.activated_widgets = []
        self.deactivated_widgets = []

    async def on_widget_activate(self, widget: Widget) -> None:
        """Track widget activation."""
        await super().on_widget_activate(widget)
        self.activated_widgets.append(widget)

    async def on_widget_deactivate(self, widget: Widget) -> None:
        """Track widget deactivation."""
        self.deactivated_widgets.append(widget)
        await super().on_widget_deactivate(widget)


class MockWidget(Widget[WidgetConfig, MockPluginContext]):
    """Test widget implementation."""

    name = "MockWidget"

    async def update(self, key) -> None:
        """Dummy update implementation."""
        pass


async def test_plugin_context_receives_widget_reference():
    """Test that plugin context receives the correct widget reference."""
    config = MockPluginConfig()
    context = MockPluginContext(config)
    widget_config = WidgetConfig()
    widget = MockWidget(widget_config, context)

    # Activate widget
    await context.on_widget_activate(widget)
    assert len(context.activated_widgets) == 1
    assert context.activated_widgets[0] is widget

    # Deactivate widget
    await context.on_widget_deactivate(widget)
    assert len(context.deactivated_widgets) == 1
    assert context.deactivated_widgets[0] is widget


async def test_deck_calls_lifecycle_hooks_on_activate():
    """Test that Deck calls plugin context lifecycle hooks on activation."""
    # Create mock context with lifecycle methods
    context = Mock(spec=PluginContext)
    context.on_widget_activate = AsyncMock()
    context.on_widget_deactivate = AsyncMock()

    # Create mock widget
    widget = Mock(spec=Widget)
    widget.context = context
    widget.config = Mock()
    widget.config.index = None
    widget.activate = AsyncMock()
    widget.update = AsyncMock()
    widget.needs_update = False

    # Create deck and activate
    deck = Deck("test", [widget], GlobalConfig())
    device = Mock(spec=StreamDeck)
    device.key_count = Mock(return_value=4)
    device.__enter__ = Mock(return_value=device)
    device.__exit__ = Mock(return_value=None)
    device.set_key_image = Mock()

    await deck.activate(device, Mock(), Mock())

    # Verify lifecycle hook was called before widget activation
    context.on_widget_activate.assert_called_once_with(widget)
    widget.activate.assert_called_once()


async def test_deck_calls_lifecycle_hooks_on_deactivate():
    """Test that Deck calls plugin context lifecycle hooks on deactivation."""
    # Create mock context with lifecycle methods
    context = Mock(spec=PluginContext)
    context.on_widget_activate = AsyncMock()
    context.on_widget_deactivate = AsyncMock()

    # Create mock widget
    widget = Mock(spec=Widget)
    widget.context = context
    widget.config = Mock()
    widget.config.index = None
    widget.deactivate = AsyncMock()
    widget.tasks = Mock()
    widget.tasks.cleanup = Mock()

    # Create deck and deactivate
    deck = Deck("test", [widget], GlobalConfig())
    device = Mock(spec=StreamDeck)

    await deck.deactivate(device)

    # Verify lifecycle hook was called after widget deactivation
    widget.deactivate.assert_called_once()
    context.on_widget_deactivate.assert_called_once_with(widget)


async def test_deck_calls_lifecycle_hooks_for_all_widgets():
    """Test that Deck calls lifecycle hooks for all widgets."""
    # Create shared context
    context = Mock(spec=PluginContext)
    context.on_widget_activate = AsyncMock()
    context.on_widget_deactivate = AsyncMock()

    # Create multiple widgets
    widgets = []
    for _ in range(3):
        widget = Mock(spec=Widget)
        widget.context = context
        widget.config = Mock()
        widget.config.index = None
        widget.activate = AsyncMock()
        widget.deactivate = AsyncMock()
        widget.update = AsyncMock()
        widget.needs_update = False
        widget.tasks = Mock()
        widget.tasks.cleanup = Mock()
        widgets.append(widget)

    # Create deck
    deck = Deck("test", widgets, GlobalConfig())
    device = Mock(spec=StreamDeck)
    device.key_count = Mock(return_value=4)
    device.__enter__ = Mock(return_value=device)
    device.__exit__ = Mock(return_value=None)
    device.set_key_image = Mock()

    # Activate deck
    await deck.activate(device, Mock(), Mock())
    assert context.on_widget_activate.call_count == 3

    # Deactivate deck
    await deck.deactivate(device)
    assert context.on_widget_deactivate.call_count == 3


async def test_lifecycle_hooks_called_in_correct_order():
    """Test that lifecycle hooks are called in the correct order relative to widget methods."""
    call_order = []

    # Create context that tracks call order
    context = Mock(spec=PluginContext)

    async def track_activate(widget):
        call_order.append("context.on_widget_activate")

    async def track_deactivate(widget):
        call_order.append("context.on_widget_deactivate")

    context.on_widget_activate = AsyncMock(side_effect=track_activate)
    context.on_widget_deactivate = AsyncMock(side_effect=track_deactivate)

    # Create widget that tracks call order
    widget = Mock(spec=Widget)
    widget.context = context
    widget.config = Mock()
    widget.config.index = None
    widget.update = AsyncMock()
    widget.needs_update = False
    widget.tasks = Mock()
    widget.tasks.cleanup = Mock()

    async def track_widget_activate():
        call_order.append("widget.activate")

    async def track_widget_deactivate():
        call_order.append("widget.deactivate")

    widget.activate = AsyncMock(side_effect=track_widget_activate)
    widget.deactivate = AsyncMock(side_effect=track_widget_deactivate)

    # Create deck
    deck = Deck("test", [widget], GlobalConfig())
    device = Mock(spec=StreamDeck)
    device.key_count = Mock(return_value=4)
    device.__enter__ = Mock(return_value=device)
    device.__exit__ = Mock(return_value=None)
    device.set_key_image = Mock()

    # Activate and verify order
    await deck.activate(device, Mock(), Mock())
    assert call_order[0] == "context.on_widget_activate"
    assert call_order[1] == "widget.activate"

    # Deactivate and verify order
    call_order.clear()
    await deck.deactivate(device)
    assert call_order[0] == "widget.deactivate"
    assert call_order[1] == "context.on_widget_deactivate"

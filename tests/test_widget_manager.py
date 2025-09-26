"""Tests for widget manager functionality."""

import pytest
from schema import Schema

from knoepfe.widget_manager import WidgetManager, WidgetNotFoundError
from knoepfe.widgets.base import Widget


class MockWidget(Widget):
    name = "MockWidget"

    @classmethod
    def get_config_schema(cls) -> Schema:
        return Schema({"test": str})


class MockWidgetNoSchema(Widget):
    name = "MockWidgetNoSchema"


def test_widget_manager_init():
    """Test WidgetManager initialization with built-in widgets."""
    wm = WidgetManager()

    # Check that built-in widgets are registered
    widgets = wm.list_widgets()
    assert "Clock" in widgets
    assert "Text" in widgets
    assert "Timer" in widgets


def test_widget_manager_register_widget():
    """Test registering a widget."""
    wm = WidgetManager()
    wm.register_widget(MockWidget)

    assert "MockWidget" in wm.list_widgets()
    assert wm.get_widget("MockWidget") == MockWidget


def test_widget_manager_register_duplicate_widget():
    """Test registering a widget with duplicate name raises error."""
    wm = WidgetManager()
    wm.register_widget(MockWidget)

    with pytest.raises(ValueError, match="Widget name 'MockWidget' already in use"):
        wm.register_widget(MockWidget)


def test_widget_manager_get_widget():
    """Test getting a widget successfully."""
    wm = WidgetManager()
    wm.register_widget(MockWidget)

    widget_class = wm.get_widget("MockWidget")
    assert widget_class == MockWidget


def test_widget_manager_get_nonexistent_widget():
    """Test getting a non-existent widget raises WidgetNotFoundError."""
    wm = WidgetManager()

    with pytest.raises(WidgetNotFoundError):
        wm.get_widget("NonExistentWidget")


def test_widget_manager_has_widget():
    """Test checking if widget exists."""
    wm = WidgetManager()
    wm.register_widget(MockWidget)

    assert wm.has_widget("MockWidget")
    assert not wm.has_widget("NonExistentWidget")


def test_widget_manager_list_widgets():
    """Test listing all available widgets."""
    wm = WidgetManager()
    wm.register_widget(MockWidget)
    wm.register_widget(MockWidgetNoSchema)

    widgets = wm.list_widgets()
    assert "MockWidget" in widgets
    assert "MockWidgetNoSchema" in widgets
    # Built-in widgets should also be present
    assert "Clock" in widgets
    assert "Text" in widgets
    assert "Timer" in widgets


def test_widget_manager_builtin_widgets():
    """Test that built-in widgets are properly registered."""
    wm = WidgetManager()

    # Should be able to get built-in widgets
    try:
        clock_class = wm.get_widget("Clock")
        text_class = wm.get_widget("Text")
        timer_class = wm.get_widget("Timer")

        assert clock_class is not None
        assert text_class is not None
        assert timer_class is not None
    except WidgetNotFoundError:
        pytest.fail("Built-in widgets should be available")


def test_widget_manager_register_widget_without_name():
    """Test registering a widget without name attribute raises error."""
    wm = WidgetManager()

    # Create a widget class without name attribute
    class WidgetWithoutName(Widget):
        pass

    with pytest.raises(ValueError, match="Widget class 'WidgetWithoutName' must have a 'name' attribute"):
        wm.register_widget(WidgetWithoutName)

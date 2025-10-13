# Knoepfe Example Plugin

A minimal example plugin demonstrating how to create custom widgets for [knoepfe](https://github.com/lnqs/knoepfe).

This plugin serves as a template and learning resource for developers who want to create their own knoepfe widgets.

## Installation

This example plugin is not published to PyPI. To install it for development:

```bash
# Install in development mode from the knoepfe monorepo
uv pip install -e plugins/example

# Or if you're working outside the monorepo
pip install -e /path/to/knoepfe/plugins/example
```

## Widget: ExampleWidget

A simple interactive widget that demonstrates the basic structure and functionality of a knoepfe widget.

### Configuration

```python
# Basic usage with defaults
widget("ExampleWidget")

# Customized configuration
widget("ExampleWidget", {
    'message': 'Hello World'
})
```

### Parameters

- `message` (optional, default: 'Example'): The text message to display on the widget

### Features

- **Interactive Display**: Shows a customizable message with click counter
- **Click Tracking**: Counts and displays the number of times the widget has been clicked
- **State Management**: Demonstrates how to maintain widget state between updates

### Behavior

1. **Initial State**: Shows the configured message with "Click me!" text
2. **After Clicking**: Displays click count

## Development Guide

This example demonstrates the essential components of a knoepfe widget:

### 1. Plugin Descriptor

Define a plugin descriptor that declares your plugin's configuration and widgets:

```python
from knoepfe.plugins import PluginDescriptor

class ExamplePluginDescriptor(PluginDescriptor[ExamplePluginConfig, ExamplePlugin]):
    """Brief description of your plugin (used as plugin description)."""

    @classmethod
    def widgets(cls) -> list[Type[Widget]]:
        return [ExampleWidget]
```

### 2. Widget Class Structure

```python
from knoepfe.widgets import Widget

class ExampleWidget(Widget[ExampleWidgetConfig, ExamplePlugin]):
    """Brief description of your widget (used as widget description)."""
    
    name = "ExampleWidget"
    
    def __init__(self, config: ExampleWidgetConfig, plugin: ExamplePlugin) -> None:
        super().__init__(config, plugin)
        # Initialize widget state
        
    async def activate(self) -> None:
        # Called when widget becomes active
        
    async def deactivate(self) -> None:
        # Called when widget becomes inactive
        
    async def update(self, key: Key) -> None:
        # Render the widget display
        
    async def pressed(self) -> None:
        # Handle key press events
        
    async def released(self) -> WidgetAction | None:
        # Handle key release events
        return None
```

**Important**: Widget and plugin descriptions are automatically extracted from class docstrings. Do not use a separate `description` attribute.

### 3. Entry Point Registration

In `pyproject.toml`:

```toml
[project.entry-points."knoepfe.plugins"]
example = "knoepfe_example_plugin:ExamplePluginDescriptor"
```

### 4. Configuration with Pydantic

Use Pydantic models to define and validate configuration:

```python
from pydantic import Field
from knoepfe.config.widget import WidgetConfig

class ExampleWidgetConfig(WidgetConfig):
    """Configuration for ExampleWidget."""
    
    message: str = Field(default="Example", description="The text message to display")
```

### 5. Rendering with Key Renderer

Use the key renderer context manager to draw the widget:

```python
async def update(self, key: Key) -> None:
    with key.renderer() as renderer:
        renderer.text('Hello World')
```

### 6. State Management

Widgets can maintain both internal state and shared plugin state:

```python
def __init__(self, config: ExampleWidgetConfig, plugin: ExamplePlugin) -> None:
    super().__init__(config, plugin)
    self._click_count = 0  # Internal widget state
```

#### Plugin Instance vs Widget State

- **Widget State**: Private to each widget instance (e.g., `self._click_count`)
- **Plugin Instance**: Shared between all widgets of the same plugin (e.g., `self.plugin`)

The plugin instance is useful for:
- Sharing connections (like OBS WebSocket)
- Coordinating between multiple widget instances
- Maintaining plugin-wide configuration
- Managing shared resources and background tasks

### 7. Event Handling

Handle user interactions:

```python
async def pressed(self) -> None:
    # Called when key is pressed
    pass

async def released(self) -> WidgetAction | None:
    # Called when key is released
    self._click_count += 1
    self.request_update()  # Trigger re-render
    return None
```

## Plugin Structure

```
plugins/example/
├── README.md                          # This file
├── pyproject.toml                     # Package configuration
├── src/
│   └── knoepfe_example_plugin/
│       ├── __init__.py               # Package initialization & plugin descriptor
│       ├── plugin.py                 # Plugin instance with state management
│       └── example_widget.py        # Widget implementation
└── tests/
    └── test_example_widget.py       # Unit tests (optional)
```

### Creating Custom Plugin Instances

For plugins that need to share data or resources between widgets, create a custom plugin class:

```python
# plugin.py
from knoepfe.plugins import Plugin

class ExamplePlugin(Plugin):
    def __init__(self, config: ExamplePluginConfig):
        super().__init__(config)
        self.shared_counter = 0
        self.widget_instances = []
    
    def increment_counter(self):
        self.shared_counter += 1
        return self.shared_counter
    
    def shutdown(self):
        """Called when the plugin is being shut down."""
        # Clean up resources here
        pass
```

For simple plugins that don't need shared state, use the base `Plugin` class directly in your descriptor.

## Key Concepts

### Plugin Lifecycle

1. **Discovery**: Plugin descriptors are discovered via entry points
2. **Instantiation**: Plugin instance is created with validated configuration
3. **Widget Registration**: Widgets from the plugin are registered with the system
4. **Runtime**: Plugin instance is shared across all widget instances
5. **Shutdown**: `shutdown()` method is called for cleanup when knoepfe exits

### Widget Lifecycle

1. **Initialization**: `__init__()` - Set up initial state and configuration
2. **Activation**: `activate()` - Start background tasks, initialize resources
3. **Updates**: `update()` - Render the widget display (called frequently)
4. **Events**: `pressed()`, `released()`, `triggered()` - Handle user interactions
5. **Deactivation**: `deactivate()` - Clean up resources, stop tasks

### Configuration Management

- Use `self.config` to access widget-specific configuration (typed as your WidgetConfig subclass)
- Define configuration with Pydantic models for validation and type safety
- Use `Field()` with defaults and descriptions for configuration parameters

### Rendering

- Use `key.renderer()` context manager for drawing
- Use `renderer.text()` for text display
- Call `self.request_update()` to trigger re-rendering

## Testing

```bash
# Run tests (if implemented)
pytest plugins/example/tests/

# Test widget discovery
uv run python -m knoepfe list-widgets

# Test widget info
uv run python -m knoepfe widget-info ExampleWidget
```

## Next Steps

To create your own widget:

1. Copy this example plugin structure
2. Rename the package and widget class
3. Implement your custom logic in the widget methods
4. Update the configuration schema for your parameters
5. Add your widget to the entry points in `pyproject.toml`
6. Install and test your plugin

## Resources

- [Knoepfe Documentation](https://github.com/lnqs/knoepfe)
- [Schema Library Documentation](https://github.com/keleshev/schema)
- [Stream Deck SDK](https://developer.elgato.com/documentation/stream-deck/)

## License

GPL-3.0-or-later
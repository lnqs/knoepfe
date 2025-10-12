"""Utilities for extracting generic type parameters at runtime."""

from typing import Type, TypeVar, get_args

T = TypeVar("T")


def extract_generic_arg(cls: type, base_class: Type[T], arg_index: int = 0) -> Type[T]:
    """Extract a generic type argument from a class's base classes.

    Args:
        cls: The class to extract the type from
        base_class: The base class type to match against
        arg_index: Which generic argument to extract (0-based)

    Returns:
        The extracted type argument

    Raises:
        TypeError: If the type argument cannot be found or is invalid

    Example:
        class MyWidget(Widget[TextConfig, Plugin]):
            pass

        config_type = extract_generic_arg(MyWidget, WidgetConfig, 0)  # Returns TextConfig
        plugin_type = extract_generic_arg(MyWidget, Plugin, 1)   # Returns Plugin
    """
    if hasattr(cls, "__orig_bases__"):
        for base in cls.__orig_bases__:  # type: ignore
            args = get_args(base)
            if args and len(args) > arg_index:
                try:
                    if issubclass(args[arg_index], base_class):
                        return args[arg_index]  # type: ignore
                except TypeError:
                    pass

    raise TypeError(
        f"Class {cls.__name__} must specify a {base_class.__name__} type as generic parameter at index {arg_index}"
    )

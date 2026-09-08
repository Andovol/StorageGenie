"""Plugin contracts and the built-in StorageGenie plugins."""

from app.plugins.registry import PluginError, get_plugin, register_plugin

__all__ = ["PluginError", "get_plugin", "register_plugin"]

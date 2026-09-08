"""Small, explicit registry for versioned domain plugins."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class PluginError(ValueError):
    """A caller requested an unavailable plugin or unsupported version."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


@dataclass(frozen=True)
class RegisteredPlugin:
    plugin_id: str
    version: str
    implementation: Any


_PLUGINS: dict[str, RegisteredPlugin] = {}


def register_plugin(plugin_id: str, version: str, implementation: Any) -> RegisteredPlugin:
    """Register one exact semantic-version implementation."""
    plugin = RegisteredPlugin(plugin_id=plugin_id, version=version, implementation=implementation)
    _PLUGINS[plugin_id] = plugin
    return plugin


def get_plugin(plugin_id: str, version: str | None = None) -> RegisteredPlugin:
    plugin = _PLUGINS.get(plugin_id)
    if plugin is None:
        raise PluginError(f"Unknown plugin id: {plugin_id}")
    if version is not None and version != plugin.version:
        raise PluginError(
            f"Plugin version mismatch for {plugin_id}: requested {version}, expected {plugin.version}"
        )
    return plugin


# Register built-ins when the registry is imported, independent of API wiring.
from app.plugins import expiry_tracker as _expiry_tracker  # noqa: E402

register_plugin(_expiry_tracker.PLUGIN_ID, _expiry_tracker.PLUGIN_VERSION, _expiry_tracker)

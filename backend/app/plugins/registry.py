"""Small, explicit registry for versioned domain plugins."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.plugins.descriptor import (
    DescriptorError,
    PluginTaxonomy,
    validate_taxonomy,
)


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
    taxonomy: PluginTaxonomy | None = None


_PLUGINS: dict[str, RegisteredPlugin] = {}


def register_plugin(
    plugin_id: str,
    version: str,
    implementation: Any,
    taxonomy: PluginTaxonomy | None = None,
) -> RegisteredPlugin:
    """Register one exact semantic-version implementation.

    A descriptor supplied here is validated BEFORE the plugin becomes
    reachable: an unknown notification/chat mode, a duplicate category id, or a
    category that redefines a core asset field raises ``DescriptorError`` and
    nothing is registered (blueprint §8). ``taxonomy`` stays optional so a
    plugin with no descriptor is still a valid registration.
    """
    if taxonomy is not None:
        validate_taxonomy(taxonomy)
        if taxonomy.plugin_id != plugin_id or taxonomy.version != version:
            raise DescriptorError(
                "taxonomy identity mismatch: "
                f"{taxonomy.plugin_id}@{taxonomy.version} != {plugin_id}@{version}"
            )
    plugin = RegisteredPlugin(
        plugin_id=plugin_id,
        version=version,
        implementation=implementation,
        taxonomy=taxonomy,
    )
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


def iter_plugins() -> tuple[RegisteredPlugin, ...]:
    """Every registered plugin, ordered by plugin_id (deterministic)."""
    return tuple(_PLUGINS[plugin_id] for plugin_id in sorted(_PLUGINS))


# Register built-ins when the registry is imported, independent of API wiring.
from app.plugins import expiry_tracker as _expiry_tracker  # noqa: E402
from app.plugins.descriptor import EXPIRY_TRACKER_TAXONOMY  # noqa: E402

register_plugin(
    _expiry_tracker.PLUGIN_ID,
    _expiry_tracker.PLUGIN_VERSION,
    _expiry_tracker,
    taxonomy=EXPIRY_TRACKER_TAXONOMY,
)

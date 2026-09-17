"""Immutable plugin taxonomy descriptors — the plugin contract made executable.

A plugin's taxonomy is DATA. It declares its categories (id/name) with a
behaviour profile, the domain's date-type enum and its default units. Every
descriptor is a frozen dataclass whose collection fields are tuples: no
mutation, no aliasing, one source. The registry validates each descriptor at
registration time, so a domain that tries to redefine a core field is rejected
before it can be served.

Nothing here reads or writes a core table. Defining a new domain is a
registration, never a migration (blueprint §8).
"""

from __future__ import annotations

from dataclasses import dataclass

# Core asset field names (``app.models.asset.Asset``). Blueprint §8: "Plugins
# cannot redefine core fields". Enforced on every descriptor by
# ``validate_taxonomy`` below. Kept as a literal so validation stays pure data
# with no ORM import in the contract module.
CORE_ASSET_FIELDS = frozenset(
    {
        "id",
        "household_id",
        "display_name",
        "asset_type",
        "status",
        "quantity",
        "unit",
        "condition",
        "version",
        "created_at",
        "updated_at",
    }
)

# Stable behaviour-profile vocabulary. The first five name the shipped tier
# windows exactly; ``none`` is the non-perishable case with no expiry concept.
NOTIFICATION_MODES = frozenset(
    {
        "tiered-30-7-1",
        "tiered-short",
        "tiered-90-30-7",
        "basic-expiry",
        "long-lead-60-30",
        "none",
    }
)

# ``category`` = a dedicated category chat agent handles it; ``fallback`` = the
# generic chat fallback, no dedicated agent; ``none`` = no chat path.
CHAT_MODES = frozenset({"category", "fallback", "none"})


class DescriptorError(ValueError):
    """A taxonomy descriptor is malformed or redefines a core field."""


@dataclass(frozen=True)
class BehaviorProfile:
    """The per-category behaviour a plugin enforces."""

    notification: str
    opened_date_tracking: bool
    chat: str


@dataclass(frozen=True)
class CategoryDescriptor:
    """One plugin category: a stable id, a display name and its behaviour."""

    id: str
    name: str
    active: bool
    behavior: BehaviorProfile


@dataclass(frozen=True)
class PluginTaxonomy:
    """A plugin's complete taxonomy descriptor (immutable, tuple collections)."""

    plugin_id: str
    version: str
    categories: tuple[CategoryDescriptor, ...]
    date_types: tuple[str, ...]
    units: tuple[str, ...]


def _validate_category(category: CategoryDescriptor, seen: set[str]) -> None:
    key = category.id.strip().lower()
    if not key:
        raise DescriptorError("category id must be non-empty")
    if key in seen:
        raise DescriptorError(f"duplicate category id: {category.id}")
    seen.add(key)
    for candidate in (category.id, category.name):
        if candidate.strip().lower() in CORE_ASSET_FIELDS:
            raise DescriptorError(f"category {candidate!r} redefines a core asset field")
    if category.behavior.notification not in NOTIFICATION_MODES:
        raise DescriptorError(f"unknown notification mode: {category.behavior.notification!r}")
    if category.behavior.chat not in CHAT_MODES:
        raise DescriptorError(f"unknown chat mode: {category.behavior.chat!r}")


def validate_taxonomy(taxonomy: PluginTaxonomy) -> PluginTaxonomy:
    """Validate one descriptor; raise ``DescriptorError`` on any violation.

    The enforcement mechanism for blueprint §8's "cannot redefine core fields"
    rail: a category id or name that collides with a core asset field is
    rejected at registration time. An empty category map is VALID (a plugin may
    legitimately expose no categories yet); the endpoint serves it as ``[]``.
    """
    if not taxonomy.plugin_id or not taxonomy.version:
        raise DescriptorError("taxonomy requires a plugin_id and a version")
    seen: set[str] = set()
    for category in taxonomy.categories:
        _validate_category(category, seen)
    for field_name, values in (("date_type", taxonomy.date_types), ("unit", taxonomy.units)):
        for value in values:
            if not isinstance(value, str) or not value.strip():
                raise DescriptorError(f"{field_name} entries must be non-empty strings")
    return taxonomy


# The shipped Expiry Tracker taxonomy. Food/Medicine/Cosmetics/Non-perishable
# mirror what ``expiry_tracker.CATEGORIES`` already enforces; Household
# chemicals and Documents/other carry the blueprint §9.1 pilot profiles (their
# shipped ``CATEGORIES`` rows are inactive Phase-3 placeholders — see
# F-SG065-2). ``date_types``/``units`` are enumerated from the shipped enums,
# never re-typed.
from app.plugins.expiry_tracker import DateType, Unit  # noqa: E402

EXPIRY_TRACKER_TAXONOMY = PluginTaxonomy(
    plugin_id="expiry-tracker",
    version="1.0.0",
    categories=(
        CategoryDescriptor(
            "food_beverages",
            "Food & beverages",
            True,
            BehaviorProfile("tiered-30-7-1", False, "category"),
        ),
        CategoryDescriptor(
            "medicine_pharma",
            "Medicine/pharma",
            True,
            BehaviorProfile("tiered-short", False, "category"),
        ),
        CategoryDescriptor(
            "cosmetics_personal_care",
            "Cosmetics/personal care",
            True,
            BehaviorProfile("tiered-90-30-7", True, "none"),
        ),
        CategoryDescriptor(
            "household_chemicals",
            "Household chemicals",
            False,
            BehaviorProfile("basic-expiry", False, "fallback"),
        ),
        CategoryDescriptor(
            "documents_other",
            "Documents/other",
            False,
            BehaviorProfile("long-lead-60-30", False, "fallback"),
        ),
        CategoryDescriptor(
            "non_perishable",
            "Non-perishable",
            True,
            BehaviorProfile("none", False, "none"),
        ),
    ),
    date_types=tuple(item.value for item in DateType),
    units=tuple(item.value for item in Unit),
)

"""SG-065: plugin taxonomy descriptors, the served taxonomy endpoint, and the
Phase-4 exit property ("a new plugin domain can be defined without modifying
core tables").

Every test here uses the REAL registry (``register_plugin``/``get_plugin``) and
the REAL HTTP path (``TestClient(app)``); no fake registry re-implements the
logic. The new domains are registered in TEST space and never shipped.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.db import Base
from app.main import app
from app.plugins.descriptor import (
    BehaviorProfile,
    CategoryDescriptor,
    DescriptorError,
    PluginTaxonomy,
)
from app.plugins.expiry_tracker import DateType, Unit
from app.plugins.registry import PluginError, get_plugin, register_plugin


def _served(client: TestClient) -> dict[str, dict[str, object]]:
    response = client.get("/v1/taxonomy")
    assert response.status_code == 200
    body = response.json()
    return {entry["plugin_id"]: entry for entry in body["plugins"]}


def test_expiry_descriptor_is_served_on_the_real_http_path() -> None:
    with TestClient(app) as client:
        served = _served(client)
    expiry = served["expiry-tracker"]
    categories = {category["id"]: category for category in expiry["categories"]}  # type: ignore[union-attr]
    household = categories["household_chemicals"]
    assert household["notification"] == "basic-expiry"
    assert household["opened_date_tracking"] is False
    assert household["chat"] == "fallback"
    documents = categories["documents_other"]
    assert documents["notification"] == "long-lead-60-30"
    assert documents["chat"] == "fallback"
    # Deterministic order is part of the contract.
    plugin_ids = [entry["plugin_id"] for entry in served.values()]
    assert plugin_ids == sorted(plugin_ids)


def test_descriptor_enumerates_the_shipped_enums_not_a_second_copy() -> None:
    taxonomy = get_plugin("expiry-tracker").taxonomy
    assert taxonomy is not None
    assert taxonomy.date_types == tuple(item.value for item in DateType)
    assert taxonomy.units == tuple(item.value for item in Unit)


def test_new_domain_registers_without_touching_core_tables() -> None:
    """The exit property: registration, not migration."""
    before = set(Base.metadata.tables)
    assert before, "no core tables registered — the app import did not run"

    taxonomy = PluginTaxonomy(
        plugin_id="documents-domain",
        version="0.1.0",
        categories=(
            CategoryDescriptor(
                "warranties",
                "Warranties",
                True,
                BehaviorProfile("long-lead-60-30", False, "fallback"),
            ),
        ),
        date_types=("expiry_date", "best_before"),
        units=("piece",),
    )
    registered = register_plugin("documents-domain", "0.1.0", object(), taxonomy=taxonomy)
    assert registered.taxonomy is taxonomy
    assert get_plugin("documents-domain", "0.1.0").taxonomy is taxonomy

    after = set(Base.metadata.tables)
    assert after == before, f"registration changed the table set: {after ^ before}"

    with TestClient(app) as client:
        served = _served(client)
    entry = served["documents-domain"]
    assert entry["categories"] == [  # type: ignore[comparison-overlap]
        {
            "id": "warranties",
            "name": "Warranties",
            "active": True,
            "notification": "long-lead-60-30",
            "opened_date_tracking": False,
            "chat": "fallback",
        }
    ]


def test_plugin_with_no_categories_serves_an_empty_list_gracefully() -> None:
    taxonomy = PluginTaxonomy(
        plugin_id="empty-domain",
        version="1.0.0",
        categories=(),
        date_types=("expiry_date",),
        units=("piece",),
    )
    register_plugin("empty-domain", "1.0.0", object(), taxonomy=taxonomy)
    with TestClient(app) as client:
        served = _served(client)
    assert served["empty-domain"]["categories"] == []


def test_valid_registration_still_succeeds_beside_the_rejection() -> None:
    """Guards against a vacuous rejection: a legal id registers fine."""
    legal = PluginTaxonomy(
        plugin_id="legal-domain",
        version="1.0.0",
        categories=(
            CategoryDescriptor(
                "manuals", "Manuals", True, BehaviorProfile("basic-expiry", False, "none")
            ),
        ),
        date_types=("expiry_date",),
        units=("piece",),
    )
    register_plugin("legal-domain", "1.0.0", object(), taxonomy=legal)
    assert get_plugin("legal-domain").taxonomy is legal


def test_descriptor_redefining_a_core_field_is_rejected() -> None:
    rogue = PluginTaxonomy(
        plugin_id="rogue-domain",
        version="1.0.0",
        categories=(
            CategoryDescriptor(
                "status",
                "Status",
                True,
                BehaviorProfile("basic-expiry", False, "none"),
            ),
        ),
        date_types=("expiry_date",),
        units=("piece",),
    )
    with pytest.raises(DescriptorError, match="core asset field"):
        register_plugin("rogue-domain", "1.0.0", object(), taxonomy=rogue)
    # Rejected means NOT registered: no partial write survived validation.
    with pytest.raises(PluginError, match="Unknown plugin id"):
        get_plugin("rogue-domain")


def test_descriptor_validation_rejects_unknown_modes_and_duplicates() -> None:
    bad_notification = PluginTaxonomy(
        "bad-notification",
        "1.0.0",
        (
            CategoryDescriptor(
                "widgets", "Widgets", True, BehaviorProfile("weekly", False, "none")
            ),
        ),
        ("expiry_date",),
        ("piece",),
    )
    with pytest.raises(DescriptorError, match="notification mode"):
        register_plugin("bad-notification", "1.0.0", object(), taxonomy=bad_notification)

    duplicate = PluginTaxonomy(
        "duplicate-category",
        "1.0.0",
        (
            CategoryDescriptor("widgets", "Widgets", True, BehaviorProfile("none", False, "none")),
            CategoryDescriptor("widgets", "Widgets again", True, BehaviorProfile("none", False, "none")),
        ),
        ("expiry_date",),
        ("piece",),
    )
    with pytest.raises(DescriptorError, match="duplicate category id"):
        register_plugin("duplicate-category", "1.0.0", object(), taxonomy=duplicate)

"""Namespaced endpoints for domain plugins."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.asset import Asset
from app.models.assertion import Assertion
from app.models.evidence import Evidence
from app.models.review_task import ReviewTask
from app.plugins import expiry_tracker
from app.plugins.expiry_tracker import ExpiryValidationError
from app.plugins.registry import PluginError, get_plugin
from app.services import audit_service

router = APIRouter(prefix="/plugins/expiry-tracker")


def _plugin(payload: dict[str, object]) -> None:
    plugin_id = payload.get("plugin_id", expiry_tracker.PLUGIN_ID)
    version = payload.get("version", expiry_tracker.PLUGIN_VERSION)
    if not isinstance(plugin_id, str) or not isinstance(version, str):
        raise HTTPException(status_code=422, detail="plugin_id and version must be strings")
    try:
        get_plugin(plugin_id, version)
    except PluginError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def _asset(db: Session, asset_id: str, household_id: str) -> Asset:
    asset = db.query(Asset).filter_by(id=asset_id).first()
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    if asset.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")
    return asset


def _assertion_view(assertion: Assertion | None) -> dict[str, object] | None:
    if assertion is None:
        return None
    return {
        "id": assertion.id,
        "field_path": assertion.field_path,
        "value": json.loads(assertion.value_json),
        "source_type": assertion.source_type,
        "review_state": assertion.review_state,
        "source_evidence_ids": json.loads(assertion.source_evidence_ids)
        if assertion.source_evidence_ids
        else [],
    }


def _error(exc: ExpiryValidationError) -> HTTPException:
    return HTTPException(status_code=422, detail=str(exc))


@router.post("/assets/{asset_id}/classification")
def classify(
    asset_id: str,
    payload: dict[str, object],
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    _plugin(payload)
    asset = _asset(db, asset_id, household_id)
    try:
        category = expiry_tracker.canonical_category(payload.get("category"))
        tier = payload.get("notification_tier")
        if tier is not None and not isinstance(tier, str):
            raise ExpiryValidationError("notification_tier must be a string")
        result = expiry_tracker.classify_asset(db, asset, category, tier)
    except ExpiryValidationError as exc:
        raise _error(exc) from exc
    db.commit()
    task = result["review_task"]
    expiry_assertion = result["expiry_assertion"]
    return {
        "plugin_id": expiry_tracker.PLUGIN_ID,
        "version": expiry_tracker.PLUGIN_VERSION,
        "classification": result["classification"],
        "expiry_assertion": _assertion_view(
            expiry_assertion if isinstance(expiry_assertion, Assertion) else None
        ),
        "review_task": task.id if isinstance(task, ReviewTask) else None,
    }


@router.get("/assets/{asset_id}/classification")
def read_classification(
    asset_id: str,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    asset = _asset(db, asset_id, household_id)
    assertion = expiry_tracker.get_classification(db, asset.id)
    if assertion is None:
        raise HTTPException(status_code=404, detail="Expiry Tracker classification not found")
    return {
        "plugin_id": expiry_tracker.PLUGIN_ID,
        "version": expiry_tracker.PLUGIN_VERSION,
        "asset_id": asset.id,
        "classification": json.loads(assertion.value_json),
        "assertion": _assertion_view(assertion),
    }


@router.post("/assets/{asset_id}/expiry")
def enter_expiry(
    asset_id: str,
    payload: dict[str, object],
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    _plugin(payload)
    asset = _asset(db, asset_id, household_id)
    try:
        entry = expiry_tracker.parse_manual_entry(payload)
        source_ids = payload.get("source_evidence_ids", payload.get("evidence_ids"))
        if source_ids is not None and (
            not isinstance(source_ids, list) or any(not isinstance(item, str) for item in source_ids)
        ):
            raise ExpiryValidationError("source_evidence_ids must be a list of strings")
        evidence_ids = [str(item) for item in source_ids] if source_ids is not None else None
        if evidence_ids:
            evidence = db.query(Evidence).filter(Evidence.id.in_(evidence_ids)).all()
            if len(evidence) != len(set(evidence_ids)):
                raise ExpiryValidationError("source evidence was not found")
            if any(item.household_id != household_id for item in evidence):
                raise HTTPException(status_code=403, detail="Evidence household mismatch")
        assertion, tasks = expiry_tracker.store_manual_expiry(db, asset, entry, evidence_ids)
    except ExpiryValidationError as exc:
        raise _error(exc) from exc
    audit_service.record(
        db,
        actor="user",
        action="expiry.manual_entry",
        entity_type="asset",
        entity_id=asset.id,
        before={"review_state": "needs_evidence"},
        after={"review_state": "accepted", "field_path": expiry_tracker.EXPIRY_FIELD},
        household_id=asset.household_id,
    )
    db.commit()
    return {
        "asset_id": asset.id,
        "assertion": _assertion_view(assertion),
        "resolved_review_task_ids": [task.id for task in tasks],
    }


@router.post("/assets/{asset_id}/extensions")
def write_extensions(
    asset_id: str,
    payload: dict[str, object],
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    _plugin(payload)
    asset = _asset(db, asset_id, household_id)
    attributes = payload.get("attributes", payload)
    try:
        validated = expiry_tracker.validate_extension_attributes(attributes)
    except ExpiryValidationError as exc:
        raise _error(exc) from exc
    rows = expiry_tracker.store_extensions(db, asset, validated)
    db.commit()
    return {
        "asset_id": asset.id,
        "attributes": validated,
        "assertions": [_assertion_view(row) for row in rows],
    }


@router.get("/assets/{asset_id}/extensions")
def read_extensions(
    asset_id: str,
    household_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    asset = _asset(db, asset_id, household_id)
    rows = (
        db.query(Assertion)
        .filter(
            Assertion.asset_id == asset.id,
            Assertion.field_path.like(f"{expiry_tracker.EXTENSION_PREFIX}%"),
            Assertion.review_state == "accepted",
        )
        .order_by(Assertion.field_path)
        .all()
    )
    return {
        "asset_id": asset.id,
        "attributes": {
            row.field_path.removeprefix(expiry_tracker.EXTENSION_PREFIX): json.loads(row.value_json)
            for row in rows
        },
        "assertions": [_assertion_view(row) for row in rows],
    }

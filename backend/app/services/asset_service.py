import json

from sqlalchemy.orm import Session

from app.models.assertion import Assertion
from app.models.asset import Asset
from app.models.evidence import asset_evidence
from app.services import audit_service, lifecycle
from app.services.assertion_service import upsert_assertion
from app.services.candidates import _deterministic_display_name


def resolve_display_name(
    db: Session,
    payload: dict,
    evidence_ids: list[str],
) -> tuple[str | None, str | None]:
    """Return ``(display_name, source_type)`` for a create payload.

    A non-blank supplied name wins (``source_type="user"``). An absent or
    whitespace-only name is server-resolved from the first attached evidence's
    filename stem (``source_type="deterministic"``, the existing verbatim
    namer). With neither name nor evidence the value is NULL and no
    ``display_name`` assertion is written -- honest, never fabricated.
    """
    raw_name = payload.get("display_name")
    if isinstance(raw_name, str) and raw_name.strip():
        return raw_name, "user"
    if evidence_ids:
        return _deterministic_display_name(db, evidence_ids), "deterministic"
    return None, None


def create_asset(
    db: Session,
    household_id: str,
    payload: dict,
    actor: str = "api",
) -> Asset:
    evidence_ids = payload.get("evidence_ids") or []
    display_name, name_source = resolve_display_name(db, payload, evidence_ids)
    asset = Asset(
        household_id=household_id,
        display_name=display_name,
        asset_type=payload.get("asset_type", "unknown"),
        status=payload.get("status", lifecycle.ACTIVE),
        quantity=payload.get("quantity"),
        unit=payload.get("unit"),
        condition=payload.get("condition"),
    )
    db.add(asset)
    db.flush()
    # Create assertions for each supplied field
    for field in ("asset_type", "quantity", "unit", "condition", "status"):
        if field in payload and payload[field] is not None:
            a = Assertion(
                asset_id=asset.id,
                field_path=field,
                value_json=json.dumps(payload[field]),
                source_type="user",
                review_state="accepted",
            )
            db.add(a)
    if name_source is not None:
        db.add(
            Assertion(
                asset_id=asset.id,
                field_path="display_name",
                value_json=json.dumps(display_name),
                source_type=name_source,
                review_state="accepted",
            )
        )
    # Link evidence
    for eid in evidence_ids:
        db.execute(asset_evidence.insert().values(asset_id=asset.id, evidence_id=eid))
    audit_service.record(
        db,
        actor=actor,
        action="asset.create",
        entity_type="asset",
        entity_id=asset.id,
        before=None,
        after=payload,
        household_id=household_id,
    )
    audit_service.record(
        db,
        actor=actor,
        action="asset.accepted",
        entity_type="asset",
        entity_id=asset.id,
        before=None,
        after={"review_state": "accepted"},
        household_id=household_id,
    )
    db.commit()
    db.refresh(asset)
    return asset


def update_asset(
    db: Session,
    asset: Asset,
    payload: dict,
    actor: str = "api",
) -> Asset:
    before = {"display_name": asset.display_name, "version": asset.version}
    # Optimistic concurrency handled at API layer; bump version
    for field in ("display_name", "asset_type", "quantity", "unit", "condition", "status"):
        if field in payload:
            setattr(asset, field, payload[field])
            # Assertion supersession
            upsert_assertion(db, asset.id, field, payload[field], asset.household_id)
    asset.version = (asset.version or 1) + 1
    audit_service.record(
        db,
        actor=actor,
        action="asset.update",
        entity_type="asset",
        entity_id=asset.id,
        before=before,
        after=payload,
        household_id=asset.household_id,
    )
    db.commit()
    db.refresh(asset)
    return asset


def attach_evidence(db: Session, asset: Asset, evidence_ids: list[str], actor: str = "api") -> None:
    for eid in evidence_ids:
        # Use INSERT OR IGNORE to avoid duplicate PK error
        try:
            db.execute(asset_evidence.insert().values(asset_id=asset.id, evidence_id=eid))
        except Exception:
            pass
    audit_service.record(
        db,
        actor=actor,
        action="asset.attach_evidence",
        entity_type="asset",
        entity_id=asset.id,
        before=None,
        after={"evidence_ids": evidence_ids},
        household_id=asset.household_id,
    )
    db.commit()


# SG-112: the one redirect assertion a MERGED duplicate carries. It lives in the
# `merge.*` namespace so a reader can name the winner with NO new table; the
# value object carries `merged_into` (the winning asset id). A MERGED asset with
# no redirect yet reads terminal, never dangling (`PG-SC-07`).
MERGE_REDIRECT_FIELD = "merge.merged_into"


class AssetMergeError(RuntimeError):
    """An asset merge the operation refuses; `status_code` is the HTTP mapping."""

    def __init__(self, message: str, status_code: int = 422) -> None:
        super().__init__(message)
        self.status_code = status_code


def merge_asset_redirect(
    db: Session,
    asset: Asset,
    winner_id: str,
    actor: str = "api",
) -> Asset:
    """Redirect a materialized duplicate asset to its winner (`ACTIVE -> MERGED`).

    Validate-first-then-write: the winner must exist, share the household and not
    itself be MERGED (no redirect chains), and the source transition is checked
    through the single lifecycle table -- never written as free text. The source
    then carries status `MERGED` plus a `merge.merged_into` assertion naming the
    winner, and an audit row. The caller commits.
    """
    winner = db.query(Asset).filter_by(id=winner_id).first()
    if winner is None:
        raise AssetMergeError("Merge target asset not found", status_code=404)
    if winner.household_id != asset.household_id:
        raise AssetMergeError("Merge target household mismatch", status_code=403)
    if winner.id == asset.id:
        raise AssetMergeError("an asset cannot merge into itself", status_code=422)
    if winner.status == lifecycle.MERGED:
        raise AssetMergeError("merge target is itself MERGED", status_code=422)
    if asset.status == lifecycle.MERGED:
        raise AssetMergeError("asset is already MERGED", status_code=409)
    lifecycle.validate_transition(asset.status, lifecycle.MERGED)

    before = {"status": asset.status, "version": asset.version}
    asset.status = lifecycle.MERGED
    upsert_assertion(db, asset.id, "status", lifecycle.MERGED, household_id=asset.household_id)
    upsert_assertion(
        db,
        asset.id,
        MERGE_REDIRECT_FIELD,
        {"merged_into": winner_id},
        household_id=asset.household_id,
    )
    asset.version = (asset.version or 1) + 1
    audit_service.record(
        db,
        actor=actor,
        action="asset.merge",
        entity_type="asset",
        entity_id=asset.id,
        before=before,
        after={"status": lifecycle.MERGED, "merged_into": winner_id},
        household_id=asset.household_id,
    )
    db.commit()
    db.refresh(asset)
    return asset

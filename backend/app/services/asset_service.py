import json
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.assertion import Assertion
from app.models.asset import Asset
from app.models.evidence import asset_evidence
from app.services import audit_service, lifecycle
from app.services.assertion_service import upsert_assertion
from app.services.candidates import _deterministic_display_name

logger = logging.getLogger(__name__)


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
    evidence_ids = list(dict.fromkeys(payload.get("evidence_ids") or []))
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
    # Link evidence via bulk insert
    if evidence_ids:
        db.execute(
            asset_evidence.insert(),
            [{"asset_id": asset.id, "evidence_id": eid} for eid in evidence_ids],
        )
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
    evidence_ids = list(dict.fromkeys(evidence_ids))
    if evidence_ids:
        existing_eids = set(
            db.scalars(
                select(asset_evidence.c.evidence_id).where(
                    asset_evidence.c.asset_id == asset.id,
                    asset_evidence.c.evidence_id.in_(evidence_ids),
                )
            ).all()
        )
        new_eids = [eid for eid in evidence_ids if eid not in existing_eids]
        if new_eids:
            try:
                db.execute(
                    asset_evidence.insert(),
                    [{"asset_id": asset.id, "evidence_id": eid} for eid in new_eids],
                )
            except Exception:
                # SG-151: a bulk insert is atomic, so one unwritable link takes
                # the whole batch down. Fall back to per-item inserts so the
                # good links still land and every failure is logged with both
                # ids -- the #34 failure visibility, repathed onto the bulk path.
                db.rollback()
                for eid in new_eids:
                    try:
                        db.execute(
                            asset_evidence.insert().values(asset_id=asset.id, evidence_id=eid)
                        )
                    except Exception as exc:
                        logger.warning(
                            "Failed to attach evidence_id=%s to asset_id=%s: %s",
                            eid,
                            asset.id,
                            exc,
                        )

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


# SG-272 G1: the one reason assertion a gone item carries. It lives in the
# `gone.*` namespace so a reader can name the reason with NO new table and NO
# migration; the value object carries `reason` (one of GONE_REASONS). The row
# is written by mark_gone, superseded by put_back, and read back by the
# catalog list serializer and the item screens through the assertions they
# already carry (`PG-SC-02`: writer -> assertion row -> serializer -> screen).
GONE_REASON_FIELD = "gone.reason"

# SG-272 G1 (Q22): the owner's three gone reasons. Stored as slugs; screens
# show only plain words (Used up, Thrown away, Given away), never these.
GONE_REASONS: tuple[str, ...] = ("used_up", "thrown_away", "given_away")


class AssetGoneError(RuntimeError):
    """A gone/put-back/quantity move the API refuses; `status_code` is the HTTP mapping."""

    def __init__(self, message: str, status_code: int = 422):
        super().__init__(message)
        self.status_code = status_code


def get_gone_reason(db: Session, asset_id: str) -> str | None:
    """The latest accepted gone reason for one asset, or None when live/never-gone."""
    row = (
        db.query(Assertion)
        .filter_by(asset_id=asset_id, field_path=GONE_REASON_FIELD, review_state="accepted")
        .order_by(Assertion.created_at.desc())
        .first()
    )
    if row is None:
        return None
    try:
        value = json.loads(row.value_json)
    except json.JSONDecodeError:
        return None
    if not isinstance(value, dict):
        return None
    reason = value.get("reason")
    return reason if isinstance(reason, str) and reason in GONE_REASONS else None


def mark_gone(
    db: Session,
    asset: Asset,
    reason: str,
    actor: str = "api",
) -> Asset:
    """Mark one ACTIVE item gone with a reason — one all-or-nothing action.

    Writes status `ARCHIVED` plus the `gone.reason` assertion plus an audit
    row in a single commit. A repeat with the same reason is a no-op success
    (double-tap safe); a different reason while gone is refused (put back
    first). Anything else (non-ACTIVE source, unknown reason) is refused and
    writes nothing.
    """
    if reason not in GONE_REASONS:
        raise AssetGoneError(
            f"unknown gone reason {reason!r}; expected one of {list(GONE_REASONS)}",
            status_code=422,
        )
    if asset.status == lifecycle.ARCHIVED:
        existing = get_gone_reason(db, asset.id)
        if existing == reason:
            return asset
        raise AssetGoneError(
            "item is already gone; put it back before marking it gone again",
            status_code=422,
        )
    try:
        lifecycle.validate_transition(asset.status, lifecycle.ARCHIVED)
    except lifecycle.LifecycleTransitionError as exc:
        raise AssetGoneError(str(exc), status_code=422) from None

    before = {"status": asset.status, "version": asset.version}
    asset.status = lifecycle.ARCHIVED
    upsert_assertion(db, asset.id, "status", lifecycle.ARCHIVED, household_id=asset.household_id)
    upsert_assertion(
        db,
        asset.id,
        GONE_REASON_FIELD,
        {"reason": reason},
        household_id=asset.household_id,
    )
    asset.version = (asset.version or 1) + 1
    audit_service.record(
        db,
        actor=actor,
        action="asset.gone",
        entity_type="asset",
        entity_id=asset.id,
        before=before,
        after={"status": lifecycle.ARCHIVED, "reason": reason},
        household_id=asset.household_id,
    )
    db.commit()
    db.refresh(asset)
    return asset


def put_back(
    db: Session,
    asset: Asset,
    actor: str = "api",
) -> Asset:
    """Put one gone item back to ACTIVE — the owner's approved undo (Q22).

    One all-or-nothing commit: status `ACTIVE`, the `gone.reason` assertion
    superseded (history kept, read-back cleared), plus an audit row. Review
    tasks and reminders are deliberately untouched: readers hide rows for
    non-ACTIVE assets, so a gone-and-back cycle restores the same visible
    state with no row replay. A repeat on an ACTIVE item is a no-op success.
    """
    if asset.status == lifecycle.ACTIVE:
        return asset
    try:
        lifecycle.validate_transition(asset.status, lifecycle.ACTIVE)
    except lifecycle.LifecycleTransitionError as exc:
        raise AssetGoneError(str(exc), status_code=422) from None

    before = {"status": asset.status, "version": asset.version}
    asset.status = lifecycle.ACTIVE
    upsert_assertion(db, asset.id, "status", lifecycle.ACTIVE, household_id=asset.household_id)
    # Supersede the reason so the list/detail read-back clears; the old row
    # stays as superseded history.
    upsert_assertion(db, asset.id, GONE_REASON_FIELD, {"reason": None}, household_id=asset.household_id)
    asset.version = (asset.version or 1) + 1
    audit_service.record(
        db,
        actor=actor,
        action="asset.put_back",
        entity_type="asset",
        entity_id=asset.id,
        before=before,
        after={"status": lifecycle.ACTIVE},
        household_id=asset.household_id,
    )
    db.commit()
    db.refresh(asset)
    return asset


def adjust_quantity(
    db: Session,
    asset: Asset,
    delta: int,
    actor: str = "api",
) -> Asset:
    """Tap +/-1 on a counted item, server-side (SG-272 G3).

    Reads the live row inside the transaction, never the screen's stale copy,
    so two quick taps cannot lose one. Refuses below 0 (422) and writes
    nothing then. At 0 the screens offer Mark gone instead of auto-archiving.
    """
    if delta not in (1, -1):
        raise AssetGoneError("quantity delta must be +1 or -1", status_code=422)
    if asset.status != lifecycle.ACTIVE:
        raise AssetGoneError("quantity can only change on a live item", status_code=422)
    current = asset.quantity if asset.quantity is not None else 0
    try:
        new_value = float(current) + delta
    except (TypeError, ValueError) as exc:
        raise AssetGoneError("quantity is not a number", status_code=422) from exc
    if new_value < 0:
        raise AssetGoneError("quantity cannot go below 0", status_code=422)
    before = {"quantity": asset.quantity, "version": asset.version}
    asset.quantity = new_value
    upsert_assertion(db, asset.id, "quantity", new_value, household_id=asset.household_id)
    asset.version = (asset.version or 1) + 1
    audit_service.record(
        db,
        actor=actor,
        action="asset.quantity_adjust",
        entity_type="asset",
        entity_id=asset.id,
        before=before,
        after={"quantity": new_value, "delta": delta},
        household_id=asset.household_id,
    )
    db.commit()
    db.refresh(asset)
    return asset


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

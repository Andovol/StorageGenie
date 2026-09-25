"""SG-098 manual Enrich trigger endpoint (D131).

This is the WIRING slice: one manual `POST` trigger that reads an asset's
brand+name/barcode TEXT only, runs the OFF-first -> Jina fallback decision
through the REAL SG-081/082 clients, and persists the web-sourced proposals as
a gated candidate row readable through the REAL `GET /v1/candidates/{id}` route.

Standing lines (packet SG-098):
- No synthesis prompt/caller and no persistence model/migration ride here. As of
  SG-102 the OFF/Jina snapshots ARE recorded to the SG-100 `enrich_snapshot`
  table through its append-only writer (`PG-SC-02` closed in-slice); they also
  still ride the in-memory decision record and the response body. The candidate
  proposal rides the EXISTING candidate table (no new table, no migration).
- Consent gates BEFORE any client touch: with `settings.sg_consent` false the
  request refuses with a named reason and ZERO invocations.
- The per-press cap is enforced server-side as a mirror of the frontend
  `enrichCapRefusal`; the ceiling is stated and uncalibrated (`G-A9`).
- No photo bytes, no GPS, no key value ever leaves here. The key is resolved by
  the real client through the settings/env seam and is added at send time only.
"""

from __future__ import annotations

import json
import math

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.assertion import Assertion
from app.models.asset import Asset
from app.models.job import Job
from app.services import candidates
from app.services.candidates import Candidate
from app.services.enrich import client as off_client
from app.services.enrich import jina as jina_mod
from app.services.enrich import snapshots as snapshots_mod

router = APIRouter()

# Mirror of the frontend `ENRICH_PER_PRESS_CAP_USD` (SG-082, `G-A9`: stated,
# uncalibrated ceiling). Kept in lockstep with `AssetDetailPage.tsx`.
ENRICH_PER_PRESS_CAP_USD = 0.05

# The assertion field paths that carry an asset's identifier TEXT. `brand` is
# read when a writer has produced one (none does on this tree yet, reported);
# `identifier` is the barcode written by the import commit path.
IDENTIFIER_FIELD_PATHS = ("brand", "identifier")
ENRICH_JOB_TYPE = "enrich"


def enrich_cap_refusal(
    projected_spend_usd: float,
    cap_usd: float = ENRICH_PER_PRESS_CAP_USD,
) -> str | None:
    """Server mirror of the frontend `enrichCapRefusal` (same message shape).

    `None` means allowed; a string is the named refusal. Non-finite spend is
    refused as unknown rather than treated as zero.
    """
    if not math.isfinite(projected_spend_usd):
        return "per_press_cap_unknown: spend is not a finite number — refusing to press"
    if projected_spend_usd > cap_usd:
        return (
            f"per_press_cap_exceeded: last press cost ${projected_spend_usd:.6f} "
            f"exceeds cap ${cap_usd:.2f}"
        )
    return None


def read_asset_identifiers(db: Session, asset: Asset) -> dict[str, str | None]:
    """Read the asset's brand+name/barcode TEXT only (never bytes or GPS).

    Returns `{"name", "brand", "barcode"}` with blank values collapsed to
    `None`. Only the real `Assertion` rows are read; a non-string or unparsable
    value is skipped, never guessed.
    """
    name = (asset.display_name or "").strip() or None
    brand: str | None = None
    barcode: str | None = None
    for row in db.query(Assertion).filter(Assertion.asset_id == asset.id).all():
        if row.field_path not in IDENTIFIER_FIELD_PATHS:
            continue
        try:
            value = json.loads(row.value_json)
        except (TypeError, ValueError):
            continue
        if not isinstance(value, str) or not value.strip():
            continue
        if row.field_path == "brand":
            brand = value.strip()
        else:
            barcode = value.strip()
    return {"name": name, "brand": brand, "barcode": barcode}


def label_existing_fields(db: Session, asset: Asset) -> dict[str, object]:
    """The asset's label-side facts, keyed by `merge_web_fields`' own field names.

    SG-103: the label-wins merge needs the asset's LABEL side as the `existing`
    half — merging web fields against the proposal's own web fields can never
    conflict (same source both sides). The asset's label facts live as its
    `Assertion` rows (the commit paths write a `display_name` assertion beside
    the denormalised column), so this reads those rows and keeps only the
    `field_path`s in the `LABEL_VISIBLE_FIELDS` vocabulary (SG-082, extended by
    SG-119). Each value is a provenance envelope (`{"value", "source_type"}`)
    so the REAL `merge_web_fields` reads it through `_field_parts`.

    SG-119: `brand` IS in that vocabulary and the OFF path emits one under the
    `web:OpenFoodFacts` provenance, so a label brand and a web brand both stay
    visible (the label wins the proposal, the web value becomes its alternate).
    Jina still emits no brand, and the OFF-miss population (`PG-SC-07`) still
    maps to nothing. A non-string/unparsable or blank value is skipped, never
    guessed.
    """
    existing: dict[str, object] = {}
    for row in db.query(Assertion).filter(Assertion.asset_id == asset.id).all():
        if row.field_path not in candidates.LABEL_VISIBLE_FIELDS:
            continue
        if row.field_path in existing:
            continue
        try:
            value = json.loads(row.value_json)
        except (TypeError, ValueError):
            continue
        if value is None or (isinstance(value, str) and not value.strip()):
            continue
        existing[row.field_path] = {"value": value, "source_type": row.source_type}
    return existing


def get_off_http_client() -> httpx.Client | None:
    """Injection seam for the OFF transport (tests override; production None)."""
    return None


def get_jina_http_client() -> httpx.Client | None:
    """Injection seam for the Jina transport (tests override; production None)."""
    return None


@router.post("/enrich/{asset_id}")
def trigger_enrich(
    asset_id: str,
    household_id: str = Query(...),
    last_spend_usd: float = Query(default=0.0),
    db: Session = Depends(get_db),
    off_http_client: httpx.Client | None = Depends(get_off_http_client),
    jina_http_client: httpx.Client | None = Depends(get_jina_http_client),
) -> dict[str, object]:
    """Run one manual Enrich decision for one asset and land its gated proposals.

    The asset id travels in the PATH (the REST shape the other asset routes
    use); `household_id` and the cap input travel as query params.
    """
    asset = db.query(Asset).filter_by(id=asset_id).first()
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    if asset.household_id != household_id:
        raise HTTPException(status_code=403, detail="Household mismatch")

    # Consent gate BEFORE any client touch: refuse by name with zero sends.
    if not settings.sg_consent:
        raise HTTPException(
            status_code=403,
            detail=(
                "consent_disabled: Enrich requires sg_consent=true before any "
                "source is contacted"
            ),
        )

    refusal = enrich_cap_refusal(last_spend_usd)
    if refusal is not None:
        raise HTTPException(status_code=402, detail=refusal)

    identifiers = read_asset_identifiers(db, asset)
    query_name = identifiers["name"] or identifiers["barcode"]
    if not query_name:
        raise HTTPException(
            status_code=422,
            detail=(
                "missing_identifiers: asset has no brand+name/barcode text to "
                "search; refusing to guess a query"
            ),
        )
    brand = identifiers["brand"] or ""

    record = jina_mod.fetch_with_fallback(
        query_name,
        brand,
        category=None,
        http_client=off_http_client,
        jina_http_client=jina_http_client,
    )

    # SG-102: persist the raw snapshots through the SG-100 append-only writer
    # BEFORE the candidate commit. OFF is always recorded; Jina is recorded iff
    # the fallback fired. The query is the exact brand+name TEXT the Jina client
    # searched (`build_jina_query`) — never a photo, a coordinate or a key.
    query_text = jina_mod.build_jina_query(brand, query_name)
    snapshots_mod.record_off_snapshot(db, record.primary, query=query_text)
    if record.fallback is not None:
        snapshots_mod.record_jina_snapshot(db, record.fallback, query=query_text)

    web = candidates.build_enrich_fields(record, category=None)
    web_fields = web["fields"]
    sources = web["sources"]
    if not isinstance(web_fields, dict):
        web_fields = {}

    # SG-103 label-wins-visible (spec §4): the asset's own label-visible facts
    # are the `existing` half, so a label/web conflict keeps the label value in
    # the proposal and surfaces the web value as an alternate with its source.
    # The REAL merge rule runs; it is never re-implemented here.
    label_existing = label_existing_fields(db, asset)
    fields, alternates = candidates.merge_web_fields(label_existing, web_fields)

    proposal: dict[str, object] = {
        "kind": "new_asset",
        "asset_id": None,
        "enrich_asset_id": asset.id,
        "fields": fields,
        "dedup_matches": [],
        "review_task_ids": [],
        "web_sources": sources,
        "web_alternates": alternates,
    }
    job = Job(
        household_id=asset.household_id,
        job_type=ENRICH_JOB_TYPE,
        state="COMPLETED",
        config_snapshot=json.dumps({"asset_id": asset.id}),
    )
    db.add(job)
    db.flush()
    candidate = Candidate(
        job_id=job.id,
        evidence_ids_json=json.dumps([]),
        proposed_fields_json=json.dumps(proposal, ensure_ascii=False),
        state="proposed",
        household_id=asset.household_id,
    )
    db.add(candidate)
    db.commit()

    return {
        "asset_id": asset.id,
        "candidate_id": candidate.id,
        "state": candidate.state,
        "fields": fields,
        "web_sources": sources,
        "web_alternates": alternates,
        "off_accepted": record.off_decision.accepted,
        "off_reason": record.off_decision.reason,
        "fallback_fired": record.fallback_fired,
        "fallback_reason": record.fallback_reason,
        "primary": json.loads(off_client.snapshot_to_json(record.primary)),
        "fallback": (
            json.loads(jina_mod.snapshot_to_json(record.fallback))
            if record.fallback is not None
            else None
        ),
        "snapshots_recorded": True,
    }

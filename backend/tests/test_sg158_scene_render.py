"""SG-158 T1b — scene send path: consent/guard refusals, POST, download,
Evidence + ledger persistence (offline, $0; `PG-EV-04`).

Scope: every HTTP leg is an `httpx.MockTransport` injected through the real
`render_scene` seam — no network, no key crosses a wire, no metered call. The
live renders are recorded in `docs/worklogs/SG-158_*`, never here.

What this file proves:
- the consent predicate is the explicit `SceneSpendAuthority`; `sg_consent` is
  never consulted (a flipped settings flag cannot authorize a send);
- the cap guard refuses `over_cap` BEFORE any send, counting unknown-cost rows
  at the worst case again (fail closed);
- a missing key refuses before any send;
- a successful render appends exactly one `provider_call` row (cost from the
  response `usage.cost`) and one `Evidence` row whose stored bytes are the
  downloaded image, `source_kind="scene_render"`;
- the temporary `imageUrl` is downloaded immediately, over HTTP as well as from
  a `data:` URL;
- a billed failure (HTTP 200, no image / download failure) still ledgers its
  cost — never billed-but-unledgered;
- a transport failure ledgers with `cost=None` (never a substituted zero);
- `Authorization` is added at SEND time only and the key value never appears in
  the builder output, the ledger row or the Evidence provenance.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401  (registers every table for create_all)
from app.config import settings
from app.db import Base
from app.models.audit_event import AuditEvent
from app.models.evidence import Evidence
from app.models.household import Household
from app.models.provider_call import ProviderCall
from app.services.scene import openrouter as scene

BRIEF = "restage this labeled packet on a clean kitchen counter in warm daylight"
IMAGE_MODEL = "openai/gpt-5-image"
ORCHESTRATOR = "inclusionai/ling-3.0-flash-vl"
PHOTO = "data:image/png;base64,QUJD"
KEY = "test-key-value-never-stored"
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
PNG_DATA_URL = "data:image/png;base64," + base64.b64encode(PNG_BYTES).decode()
AUTHORITY = scene.SceneSpendAuthority(grant_id="D-1009-4 + L3 (D-1009-7)", cap_usd=1.0)
WORST_CASE = 0.05
HOUSEHOLD_ID = "hhhhhhhh-1111-4111-8111-hhhhhhhhhhhh"


@pytest.fixture()
def db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Session:
    monkeypatch.setattr(settings, "storage_root", str(tmp_path / "storage"))
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add(Household(id=HOUSEHOLD_ID, name="Test Household"))
    session.commit()
    try:
        yield session
    finally:
        session.close()


def _payload(*, image_url: str | None, cost: float | None = 0.0003) -> dict[str, Any]:
    content: list[dict[str, Any]] = [{"type": "text", "text": "done"}]
    if image_url is not None:
        content.append({"type": "image_url", "image_url": {"url": image_url}})
    usage: dict[str, Any] = {"prompt_tokens": 10, "completion_tokens": 5}
    if cost is not None:
        usage["cost"] = cost
    return {
        "id": "gen-test-1",
        "choices": [{"message": {"role": "assistant", "content": content}}],
        "usage": usage,
    }


def _client(
    payload: dict[str, Any] | None = None,
    *,
    post_status: int = 200,
    post_exc: Exception | None = None,
    get_bytes: bytes | None = None,
    get_status: int = 200,
    get_exc: Exception | None = None,
) -> tuple[httpx.Client, list[httpx.Request]]:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.method == "POST":
            if post_exc is not None:
                raise post_exc
            return httpx.Response(post_status, json=payload, request=request)
        if get_exc is not None:
            raise get_exc
        return httpx.Response(
            get_status,
            content=get_bytes or b"",
            headers={"Content-Type": "image/png"},
            request=request,
        )

    return httpx.Client(transport=httpx.MockTransport(handler)), seen


def _call(db: Session, client: httpx.Client, **overrides: Any) -> scene.SceneRenderOutcome:
    kwargs: dict[str, Any] = {
        "db": db,
        "household_id": HOUSEHOLD_ID,
        "photo_ref": PHOTO,
        "brief": BRIEF,
        "image_model": IMAGE_MODEL,
        "orchestrator": ORCHESTRATOR,
        "worst_case_usd": WORST_CASE,
        "authority": AUTHORITY,
        "key": KEY,
        "http_client": client,
    }
    kwargs.update(overrides)
    return scene.render_scene(**kwargs)


# --------------------------------------------------------------------------- #
# refusal paths — nothing may be sent, nothing written
# --------------------------------------------------------------------------- #
def test_missing_authority_refuses_consent_without_send(db: Session) -> None:
    client, seen = _client(_payload(image_url=PNG_DATA_URL))
    outcome = _call(db, client, authority=None)
    assert outcome.status == "refused"
    assert outcome.refusal is not None and outcome.refusal.code == "refused_consent"
    assert seen == []
    assert db.query(ProviderCall).count() == 0
    assert db.query(Evidence).count() == 0


def test_sg_consent_true_is_not_the_predicate(db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "sg_consent", True)
    client, seen = _client(_payload(image_url=PNG_DATA_URL))
    outcome = _call(db, client, authority=None)
    assert outcome.status == "refused"
    assert outcome.refusal is not None and outcome.refusal.code == "refused_consent"
    assert seen == []


def test_over_cap_refuses_before_send(db: Session) -> None:
    db.add(
        ProviderCall(
            provider=scene.SCENE_LEDGER_PROVIDER,
            model=ORCHESTRATOR,
            prompt_template_version=scene.SCENE_LEDGER_TEMPLATE_VERSION,
            cost=0.9995,
        )
    )
    db.commit()
    client, seen = _client(_payload(image_url=PNG_DATA_URL))
    outcome = _call(db, client)
    assert outcome.status == "refused"
    assert outcome.refusal is not None and outcome.refusal.code == "over_cap"
    assert seen == []
    assert db.query(ProviderCall).count() == 1  # the pre-existing row only


def test_unknown_cost_rows_are_charged_the_worst_case(db: Session) -> None:
    for _ in range(2):
        db.add(
            ProviderCall(
                provider=scene.SCENE_LEDGER_PROVIDER,
                model=ORCHESTRATOR,
                prompt_template_version=scene.SCENE_LEDGER_TEMPLATE_VERSION,
                cost=None,
            )
        )
    db.commit()
    client, seen = _client(_payload(image_url=PNG_DATA_URL))
    outcome = _call(db, client, worst_case_usd=0.4)
    # 2 x 0.4 (unknown) + 0.4 (this render) = 1.2 > 1.0 -> refuse
    assert outcome.status == "refused"
    assert outcome.refusal is not None and outcome.refusal.code == "over_cap"
    assert seen == []


def test_missing_key_refuses_before_send(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "openrouter_api_key", None)
    monkeypatch.delenv(scene.OPENROUTER_API_KEY_ENV, raising=False)
    client, seen = _client(_payload(image_url=PNG_DATA_URL))
    outcome = _call(db, client, key=None)
    assert outcome.status == "refused"
    assert outcome.refusal is not None and outcome.refusal.code == "missing_key"
    assert seen == []
    assert db.query(ProviderCall).count() == 0


# --------------------------------------------------------------------------- #
# success — exactly one ledger row + one Evidence row, bytes = downloaded image
# --------------------------------------------------------------------------- #
def test_successful_render_writes_evidence_and_ledger(db: Session) -> None:
    client, seen = _client(_payload(image_url=PNG_DATA_URL))
    outcome = _call(db, client)
    assert outcome.status == "rendered"
    assert outcome.status_code == 200
    assert outcome.cost_usd == 0.0003
    assert outcome.error_state is None

    evidence = db.query(Evidence).all()
    assert len(evidence) == 1
    row = evidence[0]
    assert row.id == outcome.evidence_id
    assert row.source_kind == "scene_render"
    assert row.media_type == "image/png"
    assert row.sha256 == outcome.image_sha256
    stored = (Path(settings.storage_root) / row.storage_key).read_bytes()
    assert stored == PNG_BYTES

    ledgers = db.query(ProviderCall).all()
    assert len(ledgers) == 1
    entry = ledgers[0]
    assert entry.id == outcome.ledger_id
    assert entry.provider == "openrouter"
    assert entry.model == ORCHESTRATOR
    assert entry.cost == 0.0003
    assert entry.error_state is None
    payload = json.loads(entry.output_payload or "{}")
    assert payload["image_model"] == IMAGE_MODEL
    assert payload["orchestrator"] == ORCHESTRATOR
    assert payload["evidence_id"] == outcome.evidence_id
    assert payload["prompt"] == BRIEF

    # probe: response provenance is committed beside the Evidence row
    audits = db.query(AuditEvent).filter_by(entity_id=row.id).all()
    assert len(audits) == 1
    after = json.loads(audits[0].after_json or "{}")
    assert after["provider"] == "openrouter"
    assert after["image_model"] == IMAGE_MODEL
    assert after["orchestrator"] == ORCHESTRATOR
    assert after["cost_usd"] == 0.0003


def test_temporary_image_url_is_downloaded_over_http(db: Session) -> None:
    client, seen = _client(
        _payload(image_url="https://openrouter.ai/tmp/render-1.png"),
        get_bytes=PNG_BYTES,
    )
    outcome = _call(db, client)
    assert outcome.status == "rendered"
    assert outcome.image_url == "https://openrouter.ai/tmp/render-1.png"
    methods = [request.method for request in seen]
    assert methods == ["POST", "GET"]
    row = db.query(Evidence).one()
    assert (Path(settings.storage_root) / row.storage_key).read_bytes() == PNG_BYTES


def test_authorization_header_added_at_send_time_only(db: Session) -> None:
    client, seen = _client(_payload(image_url=PNG_DATA_URL))
    outcome = _call(db, client)
    assert outcome.status == "rendered"

    post = next(request for request in seen if request.method == "POST")
    assert post.headers.get("Authorization") == f"Bearer {KEY}"

    built = scene.build_scene_request(
        PHOTO, BRIEF, IMAGE_MODEL, ORCHESTRATOR, spend_cap_usd=WORST_CASE
    )
    assert "Authorization" not in built["headers"]

    entry = db.query(ProviderCall).one()
    row_text = json.dumps(
        {
            "output_payload": entry.output_payload,
            "usage_json": entry.usage_json,
            "input_hashes": entry.input_hashes,
            "error_state": entry.error_state,
        }
    )
    assert KEY not in row_text
    audit = db.query(AuditEvent).one()
    assert KEY not in (audit.after_json or "")


# --------------------------------------------------------------------------- #
# billed failures — still exactly one ledger row each, cost never invented
# --------------------------------------------------------------------------- #
def test_billed_failure_without_image_still_ledgers_the_cost(db: Session) -> None:
    client, seen = _client(_payload(image_url=None, cost=0.0004))
    outcome = _call(db, client)
    assert outcome.status == "failed"
    assert outcome.error_state == "image_url_missing"
    assert db.query(Evidence).count() == 0
    entry = db.query(ProviderCall).one()
    assert entry.id == outcome.ledger_id
    assert entry.cost == 0.0004
    assert entry.error_state == "image_url_missing"
    assert [r.method for r in seen] == ["POST"]


def test_failed_image_download_still_ledgers_the_cost(db: Session) -> None:
    client, _ = _client(
        _payload(image_url="https://openrouter.ai/tmp/gone.png", cost=0.0004),
        get_status=500,
    )
    outcome = _call(db, client)
    assert outcome.status == "failed"
    assert outcome.error_state == "image_download_failed: http_status:500"
    entry = db.query(ProviderCall).one()
    assert entry.cost == 0.0004
    assert db.query(Evidence).count() == 0


def test_transport_failure_ledgers_unknown_cost_not_zero(db: Session) -> None:
    client, seen = _client(post_exc=httpx.ConnectError("boom"))
    outcome = _call(db, client)
    assert outcome.status == "failed"
    assert outcome.status_code is None
    assert outcome.error_state == "transport: ConnectError"
    entry = db.query(ProviderCall).one()
    assert entry.cost is None  # never a substituted zero
    assert entry.error_state == "transport: ConnectError"
    assert [r.method for r in seen] == ["POST"]


def test_http_error_status_still_ledgers(db: Session) -> None:
    client, _ = _client({"error": {"message": "rate limited"}}, post_status=429)
    outcome = _call(db, client)
    assert outcome.status == "failed"
    assert outcome.error_state == "http_status:429"
    entry = db.query(ProviderCall).one()
    assert entry.cost is None
    payload = json.loads(entry.output_payload or "{}")
    assert payload["status_code"] == 429
    assert "rate limited" in payload["error_body"]


def test_extract_image_url_handles_data_and_walks_nested_shapes() -> None:
    assert scene.extract_image_url(_payload(image_url=PNG_DATA_URL)) == PNG_DATA_URL
    nested = {"choices": [{"message": {"content": [{"image_url": {"url": "https://x/y.png"}}]}}]}
    assert scene.extract_image_url(nested) == "https://x/y.png"
    assert scene.extract_image_url({"choices": []}) is None


def test_evidence_write_failure_still_ledgers(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _explode(*args: Any, **kwargs: Any) -> Evidence:
        raise RuntimeError("disk full")

    monkeypatch.setattr(scene, "store_scene_render_evidence", _explode)
    client, _ = _client(_payload(image_url=PNG_DATA_URL, cost=0.0002))
    outcome = _call(db, client)
    assert outcome.status == "failed"
    assert outcome.error_state == "evidence_write_failed"
    entry = db.query(ProviderCall).one()
    assert entry.cost == 0.0002
    assert entry.error_state == "evidence_write_failed"


def test_scene_spend_so_far_sums_known_and_counts_unknown(db: Session) -> None:
    db.add(
        ProviderCall(
            provider="openrouter",
            model=ORCHESTRATOR,
            prompt_template_version=scene.SCENE_LEDGER_TEMPLATE_VERSION,
            cost=0.1,
        )
    )
    db.add(
        ProviderCall(
            provider="openrouter",
            model=ORCHESTRATOR,
            prompt_template_version=scene.SCENE_LEDGER_TEMPLATE_VERSION,
            cost=None,
        )
    )
    db.add(
        ProviderCall(
            provider="opencode-go",
            model="other",
            prompt_template_version="x",
            cost=99.0,
        )
    )
    db.commit()
    known, unknown = scene.scene_spend_so_far(db)
    assert known == 0.1
    assert unknown == 1

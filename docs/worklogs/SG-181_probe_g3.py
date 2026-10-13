"""SG-181 G3 probe — grounded readers: planning, chat, analytics, enrichment.

Real FastAPI routes against a disposable SQLite DB + storage root. Scripted
in-process providers and httpx.MockTransport only; zero network, zero spend.

Run:
  cd /tmp/opencode && PYTHONPATH=<repo>/backend <repo>/backend/venv/bin/python \
      <repo>/docs/worklogs/SG-181_probe_g3.py
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

TEMP_ROOT = Path(tempfile.mkdtemp(prefix="sg181-g3-"))
TEMP_DB = TEMP_ROOT / "storagegenie.db"
TEMP_STORAGE = TEMP_ROOT / "storage"
TEMP_STORAGE.mkdir()
os.environ["DATABASE_URL"] = f"sqlite:///{TEMP_DB}"
os.environ["STORAGE_ROOT"] = str(TEMP_STORAGE)
os.environ.pop("OPENCODE_API_KEY", None)
os.environ.pop("JINA_API_KEY", None)

import httpx  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.api.v1.enrich import get_jina_http_client, get_off_http_client  # noqa: E402
from app.config import settings  # noqa: E402
from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Asset, EnrichSnapshot, GuardrailEvent, Household, PlanningSuggestion, ProviderCall  # noqa: E402
from app.services import audit_service  # noqa: E402
from app.services.chat import service as chat_service  # noqa: E402
from app.services.planning import service as planning_service  # noqa: E402
from app.services.providers import reader  # noqa: E402
from app.services.providers.fake import FakeProvider, ScriptedProvider  # noqa: E402

RESULTS: list[dict[str, object]] = []
EXP = "/v1/plugins/expiry-tracker"


def record(name: str, level: str, **detail: object) -> None:
    RESULTS.append({"check": name, "result": level, **detail})
    print(f"[{level}] {name} {json.dumps(detail, default=str)[:450]}", flush=True)


def expect(name: str, condition: bool, **detail: object) -> None:
    record(name, "PASS" if condition else "FAIL", **detail)


def observe(name: str, **detail: object) -> None:
    record(name, "OBSERVE", **detail)


def set_provider(provider) -> None:  # type: ignore[no-untyped-def]
    reader.provider_registry = lambda: {provider.provider_id: provider}  # type: ignore[assignment]
    settings.sg_provider_id = provider.provider_id


def classify(client: TestClient, hid: str, asset_id: str, category: str) -> dict:
    return client.post(f"{EXP}/assets/{asset_id}/classification", params={"household_id": hid}, json={"category": category}).json()


def main() -> int:
    opened = time.monotonic()
    cmd_start = int(time.time())
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = Session()
    house_a = Household(name="SG181 G3 House A")
    house_b = Household(name="SG181 G3 House B")
    session.add_all([house_a, house_b])
    session.commit()
    aid, bid = house_a.id, house_b.id
    record("isolation", "PASS", storage_root=settings.storage_root, engine_url=str(engine.url), temp_root=str(TEMP_ROOT))
    client = TestClient(app)

    def mk(hid: str, name: str) -> str:
        return client.post("/v1/assets", params={"household_id": hid}, json={"display_name": name}).json()["id"]

    # fixtures: classified + manual expiry, unknown-expiry, unclassified asset_type-only, archived, foreign
    a_food = mk(aid, "SG181 Olive Oil")
    classify(client, aid, a_food, "food")
    client.post(f"{EXP}/assets/{a_food}/expiry", params={"household_id": aid}, json={"expiry_date": "2026-11-30"})
    a_unknown = mk(aid, "SG181 Mystery Jar")
    classify(client, aid, a_unknown, "food")
    a_med = mk(aid, "SG181 Aspirin")
    classify(client, aid, a_med, "medicine")
    client.post(f"{EXP}/assets/{a_med}/expiry", params={"household_id": aid}, json={"expiry_date": "2026-10-20"})
    a_typeonly = mk(aid, "SG181 TypeOnly Food")
    client.patch(f"/v1/assets/{a_typeonly}", params={"household_id": aid}, json={"asset_type": "food_beverages"})
    a_archived = mk(aid, "SG181 Archived Food")
    classify(client, aid, a_archived, "food")
    client.delete(f"/v1/assets/{a_archived}", params={"household_id": aid})
    b_food = mk(bid, "SG181 Foreign Food")
    classify(client, bid, b_food, "food")
    observe("fixtures", a_food=a_food, a_unknown=a_unknown, a_med=a_med, a_typeonly=a_typeonly, a_archived=a_archived, b_food=b_food)

    # --- G3.A chat ---
    settings.sg_consent = False
    consent_off = client.post("/v1/chat/food", params={"household_id": aid}, json={"message": "What do I have?"}).json()
    expect("chat_consent_off_skipped", consent_off["status"] == "skipped" and consent_off["provider_call_id"] is None, body=consent_off)
    settings.sg_consent = True
    fake = FakeProvider(mode="valid", provider_id="fake-valid")
    set_provider(fake)
    answer = client.post("/v1/chat/food", params={"household_id": aid}, json={"message": "What do I have?"})
    a_body = answer.json()
    calls_after_answer = session.query(ProviderCall).count()
    expect("chat_grounded_answer", answer.status_code == 200 and a_body["status"] == "ok" and a_body["answer"] == "fake-text" and a_body["grounded"] is True and a_body["catalogue_size"] >= 2 and fake.invocations == 1 and calls_after_answer >= 1, status=answer.status_code, body=a_body, invocations=fake.invocations, ledger_rows=calls_after_answer)
    empty_docs = client.post("/v1/chat/documents", params={"household_id": aid}, json={"message": "Anything?"}).json()
    expect("chat_empty_category_refuses_to_guess", empty_docs["status"] == "ok" and empty_docs["empty_catalogue"] is True and empty_docs["answer"] and fake.invocations == 1, body=empty_docs, invocations=fake.invocations)
    unsupported = client.post("/v1/chat/spaceships", params={"household_id": aid}, json={"message": "hi"})
    expect("chat_unsupported_category_422", unsupported.status_code == 422, status=unsupported.status_code)
    # catalog scope: A vs B disjoint; asset_type-only and archived excluded
    cat_a = chat_service.build_catalog(session, aid, "food")
    cat_b = chat_service.build_catalog(session, bid, "food")
    ids_a = {row["id"] for row in cat_a}
    ids_b = {row["id"] for row in cat_b}
    expect("chat_catalog_scope", ids_a.isdisjoint(ids_b) and b_food not in ids_a and a_typeonly not in ids_a and a_archived not in ids_a and a_food in ids_a and a_unknown in ids_a, a_ids=sorted(ids_a), b_ids=sorted(ids_b), note="category grounding requires the classification assertion; asset_type alone and archived rows are excluded")
    g_before = session.query(GuardrailEvent).count()
    corr = client.post("/v1/chat/food/corrections", params={"household_id": aid}, json={"message": "Olive oil is in the pantry"})
    g_after = session.query(GuardrailEvent).count()
    row = session.query(GuardrailEvent).filter_by(id=corr.json()["id"]).one()
    expect("chat_correction_guardrail_persisted", corr.status_code == 200 and g_after == g_before + 1 and row.kind == "correction" and json.loads(row.detail_json)["source"] == "user", status=corr.status_code, kind=row.kind, detail=json.loads(row.detail_json))
    observe("guardrail_reader_absent", note="no API route reads GuardrailEvent (source grep); rows observable only via DB/fresh session")

    # --- G3.B planning ---
    settings.sg_consent = False
    poff = client.post("/v1/planning/run", params={"household_id": aid}).json()
    expect("planning_consent_off_skipped", poff["status"] == "skipped", body=poff)
    settings.sg_consent = True
    payload = {"items": [{"name": "Audit expiry soon", "expiry_date": "2026-11-01", "date_type": "expiry", "lot": a_food, "confidence": 0.9, "uncertainty_reasons": ["audit"]}], "unknowns": [], "needs_evidence": False}
    plan_provider = ScriptedProvider(provider_id="plan-scripted", payload=payload)
    set_provider(plan_provider)
    run = client.post("/v1/planning/run", params={"household_id": aid})
    r_body = run.json()
    suggestions = client.get("/v1/planning/suggestions", params={"household_id": aid}).json()
    s_item = suggestions["items"][0] if suggestions["items"] else None
    expect("planning_run_writes_pending_suggestion", run.status_code == 200 and r_body["status"] == "ok" and r_body["suggestion_count"] == 1 and s_item and s_item["status"] == "pending" and a_food in json.dumps(s_item["backing_refs"]), body=r_body, suggestion=s_item)
    sid = s_item["id"] if s_item else None
    asset_before = client.get(f"/v1/assets/{a_food}", params={"household_id": aid}).json()
    foreign_confirm = client.post(f"/v1/planning/suggestions/{sid}/confirm", params={"household_id": bid})
    expect("planning_confirm_foreign_403", foreign_confirm.status_code == 403, status=foreign_confirm.status_code)
    confirm = client.post(f"/v1/planning/suggestions/{sid}/confirm", params={"household_id": aid})
    again = client.post(f"/v1/planning/suggestions/{sid}/confirm", params={"household_id": aid})
    asset_after = client.get(f"/v1/assets/{a_food}", params={"household_id": aid}).json()
    expect("planning_confirm_transition", confirm.status_code == 200 and confirm.json()["status"] == "confirmed" and again.status_code == 422, confirm=confirm.status_code, again=again.status_code, detail=again.json().get("detail"))
    expect("planning_confirm_does_not_execute", json.dumps(asset_before["assertions"], sort_keys=True) == json.dumps(asset_after["assertions"], sort_keys=True) and asset_before["status"] == asset_after["status"], note="confirm records the suggestion only; no catalog write")
    payload2 = {"items": [{"name": "Second plan", "date_type": "expiry", "lot": a_med, "confidence": 0.8, "uncertainty_reasons": ["audit"]}], "unknowns": [], "needs_evidence": False}
    set_provider(ScriptedProvider(provider_id="plan-scripted2", payload=payload2))
    client.post("/v1/planning/run", params={"household_id": aid})
    pend = client.get("/v1/planning/suggestions", params={"household_id": aid, "status": "pending"}).json()["items"]
    dismiss = client.post(f"/v1/planning/suggestions/{pend[0]['id']}/dismiss", params={"household_id": aid}, json={"reason": "audit"})
    expect("planning_dismiss_transition", dismiss.status_code == 200 and dismiss.json()["status"] == "dismissed", status=dismiss.status_code)
    failing = ScriptedProvider(provider_id="plan-fail", payload=payload, fail_times=2)
    set_provider(failing)
    failed = client.post("/v1/planning/run", params={"household_id": aid})
    fail_body = failed.json()
    expect("planning_provider_failure_reported", failed.status_code == 200 and fail_body["status"] == "error" and failing.invocations == 2 and fail_body["suggestion_count"] == 0, body=fail_body, invocations=failing.invocations)
    foreign_payload = {"items": [{"name": "Foreign ref", "lot": b_food, "confidence": 0.5, "uncertainty_reasons": ["audit"]}], "unknowns": [], "needs_evidence": False}
    set_provider(ScriptedProvider(provider_id="plan-foreign", payload=foreign_payload))
    client.post("/v1/planning/run", params={"household_id": aid})
    latest = client.get("/v1/planning/suggestions", params={"household_id": aid}).json()["items"][0]
    observe("planning_foreign_backing_ref", backing_refs=latest["backing_refs"], note="fixture names a house-B asset id; observe whether it survives into a suggestion")

    # --- G3.C analytics ---
    summary = client.get("/v1/analytics/summary", params={"household_id": aid})
    stats = summary.json()
    by_id = {entry["id"]: entry for entry in stats["stats"]}
    db_total = session.query(Asset).filter_by(household_id=aid).count()
    db_active = session.query(Asset).filter_by(household_id=aid, status="ACTIVE").count()
    expect("analytics_counts_match_db", summary.status_code == 200 and by_id["assets.total"]["value"] == db_total and by_id["assets.active"]["value"] == db_active, total=by_id["assets.total"]["value"], active=by_id["assets.active"]["value"], db_total=db_total, db_active=db_active)
    empty_summary = client.get("/v1/analytics/summary", params={"household_id": bid}).json()
    uncat = by_id.get("uncategorized") or by_id.get("assets.uncategorized")
    observe("analytics_empty_and_uncategorized", empty_total={e["id"]: e["value"] for e in empty_summary["stats"] if e["id"].startswith("assets.")}, uncategorized_stat=uncat)
    settings.sg_consent = False
    ins_off = client.post("/v1/analytics/insights", params={"household_id": aid}).json()
    expect("insights_consent_off_skipped", ins_off["status"] == "skipped", body=ins_off)
    settings.sg_consent = True
    good = ScriptedProvider(provider_id="ins-good", payload={"items": [{"name": "You hold a measured catalog.", "lot": "assets.total", "confidence": 0.9, "uncertainty_reasons": ["none"]}], "unknowns": [], "needs_evidence": False})
    set_provider(good)
    ins = client.post("/v1/analytics/insights", params={"household_id": aid})
    ins_body = ins.json()
    expect("insights_grounded_citation", ins.status_code == 200 and ins_body["status"] == "ok" and ins_body["cited_stat_ids"] == ["assets.total"] and bool(ins_body["cited_stats"]) and "You hold a measured catalog." in str(ins_body.get("summary", "")), status=ins.status_code, body={k: ins_body.get(k) for k in ("status", "summary", "cited_stat_ids", "cited_stats")})
    bad = ScriptedProvider(provider_id="ins-bad", payload={"items": [{"name": "Unbacked claim.", "lot": "bogus.stat", "confidence": 0.9, "uncertainty_reasons": ["none"]}], "unknowns": [], "needs_evidence": False})
    set_provider(bad)
    ungrounded = client.post("/v1/analytics/insights", params={"household_id": aid})
    event_rows = session.query(GuardrailEvent).filter_by(kind="insight").all()
    expect("insights_ungrounded_rejected_502", ungrounded.status_code == 502 and "bogus.stat" in ungrounded.json().get("detail", "") and event_rows, status=ungrounded.status_code, detail=ungrounded.json().get("detail"), guardrail_events=[json.loads(e.detail_json)["outcome"] for e in event_rows])
    nocite = ScriptedProvider(provider_id="ins-nocite", payload={"items": [{"name": "No citation.", "confidence": 0.9, "uncertainty_reasons": ["none"]}], "unknowns": [], "needs_evidence": False})
    set_provider(nocite)
    no_cite = client.post("/v1/analytics/insights", params={"household_id": aid})
    expect("insights_no_citation_502", no_cite.status_code == 502, status=no_cite.status_code, detail=no_cite.json().get("detail"))

    # --- G3.D enrichment (scripted httpx transports only) ---
    e_asset = mk(aid, "SG181 Enrich Widget")
    from app.services.assertion_service import upsert_assertion as _upsert
    _upsert(session, e_asset, "brand", "AuditBrand", household_id=aid)
    session.commit()
    settings.sg_consent = False
    off_consent = client.post(f"/v1/enrich/{e_asset}", params={"household_id": aid})
    expect("enrich_consent_off_refused_before_client", off_consent.status_code == 403 and "consent_disabled" in off_consent.json().get("detail", ""), status=off_consent.status_code)
    settings.sg_consent = True
    transport_hits = {"off": 0, "jina": 0}

    def off_handler(request: httpx.Request) -> httpx.Response:
        transport_hits["off"] += 1
        body = {"count": 1, "page": 1, "products": [{"code": "1234567890123", "product_name": "SG181 Enrich Widget", "brands": "AuditBrand", "categories_tags": ["en:snacks"], "countries_tags": ["en:romania"], "quantity": "500 g", "ingredients_text": "audited fixture"}]}
        return httpx.Response(200, json=body)

    def jina_handler(request: httpx.Request) -> httpx.Response:
        transport_hits["jina"] += 1
        return httpx.Response(200, json={"data": []})

    app.dependency_overrides[get_off_http_client] = lambda: httpx.Client(transport=httpx.MockTransport(off_handler))
    app.dependency_overrides[get_jina_http_client] = lambda: httpx.Client(transport=httpx.MockTransport(jina_handler))
    enrich = client.post(f"/v1/enrich/{e_asset}", params={"household_id": aid, "last_spend_usd": 0.0})
    e_body = enrich.json()
    cand_state = session.query(EnrichSnapshot).count()
    observe("enrich_off_scripted", status=enrich.status_code, off_accepted=e_body.get("off_accepted"), off_reason=e_body.get("off_reason"), fallback_fired=e_body.get("fallback_fired"), fallback_reason=e_body.get("fallback_reason"), fields=e_body.get("fields"), web_alternates=e_body.get("web_alternates"), snapshot_rows=cand_state, candidate_state=e_body.get("state"), transport_hits=dict(transport_hits))
    expect("enrich_no_network_no_spend", transport_hits["off"] == 1, hits=dict(transport_hits), note="MockTransport only; no real provider call")
    foreign_enrich = client.post(f"/v1/enrich/{b_food}", params={"household_id": aid})
    expect("enrich_foreign_asset_403", foreign_enrich.status_code == 403, status=foreign_enrich.status_code)
    app.dependency_overrides.pop(get_off_http_client, None)
    app.dependency_overrides.pop(get_jina_http_client, None)

    session.close()
    print(json.dumps({"results": RESULTS}, indent=2))
    print(f"TEMP_ROOT={TEMP_ROOT}")
    print(f"elapsed_s={time.monotonic() - opened:.1f} start_epoch={cmd_start} end_epoch={int(time.time())}")
    return 1 if any(r["result"] == "FAIL" for r in RESULTS) else 0


if __name__ == "__main__":
    sys.exit(main())

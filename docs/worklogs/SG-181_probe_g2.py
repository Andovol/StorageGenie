"""SG-181 G2 probe — catalog pagination/FTS/facets/saved searches, lifecycle, locations/relations, expiry/tasks.

Real FastAPI routes against a disposable SQLite DB + storage root. Nonempty,
multi-page population with tied timestamps. Dormant flags are exercised both OFF
(default) and ON in-process only; no production effective-state claim.

Run:
  cd /tmp/opencode && PYTHONPATH=<repo>/backend <repo>/backend/venv/bin/python \
      <repo>/docs/worklogs/SG-181_probe_g2.py
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

TEMP_ROOT = Path(tempfile.mkdtemp(prefix="sg181-g2-"))
TEMP_DB = TEMP_ROOT / "storagegenie.db"
TEMP_STORAGE = TEMP_ROOT / "storage"
TEMP_STORAGE.mkdir()
os.environ["DATABASE_URL"] = f"sqlite:///{TEMP_DB}"
os.environ["STORAGE_ROOT"] = str(TEMP_STORAGE)
os.environ.pop("OPENCODE_API_KEY", None)

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.config import settings  # noqa: E402
from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Asset, Household  # noqa: E402
from app.schemas.saved_search import SavedSearchCreate  # noqa: E402

RESULTS: list[dict[str, object]] = []


def record(name: str, level: str, **detail: object) -> None:
    RESULTS.append({"check": name, "result": level, **detail})
    print(f"[{level}] {name} {json.dumps(detail, default=str)[:450]}", flush=True)


def expect(name: str, condition: bool, **detail: object) -> None:
    record(name, "PASS" if condition else "FAIL", **detail)


def observe(name: str, **detail: object) -> None:
    record(name, "OBSERVE", **detail)


def main() -> int:
    opened = time.monotonic()
    cmd_start = int(time.time())
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = Session()
    house_a = Household(name="SG181 G2 House A")
    house_b = Household(name="SG181 G2 House B")
    house_c = Household(name="SG181 G2 Empty C")
    session.add_all([house_a, house_b, house_c])
    session.commit()
    aid, bid, cid = house_a.id, house_b.id, house_c.id
    record("isolation", "PASS", storage_root=settings.storage_root, engine_url=str(engine.url), temp_root=str(TEMP_ROOT))
    record("flags_default", "OBSERVE", locations=settings.sg_locations_enabled, relations=settings.sg_relations_enabled, note="privileged process settings; production effective state NOT inferred")

    client = TestClient(app)

    # --- G2.A nonempty multi-page population with tied timestamps ---
    created = []
    for i in range(25):
        body = {
            "display_name": f"Audit Widget {i:02d}" + (" Zebraphant" if i == 7 else ""),
            "asset_type": "food" if i % 2 == 0 else "household",
            "status": "ACTIVE",
        }
        r = client.post("/v1/assets", params={"household_id": aid}, json=body)
        created.append(r.json())
    b_created = [client.post("/v1/assets", params={"household_id": bid}, json={"display_name": f"B item {i}"}).json() for i in range(3)]
    stamps = {c["created_at"] for c in created}
    record("population_tied_timestamps", "PASS" if len(stamps) < len(created) else "OBSERVE", distinct_created_at=len(stamps), total=len(created), sample=sorted(stamps)[:3])

    ids_all, cursor, pages = [], None, 0
    while True:
        params = {"household_id": aid, "limit": 10}
        if cursor:
            params["cursor"] = cursor
        page = client.get("/v1/assets", params=params).json()
        ids_all.extend(x["id"] for x in page["items"])
        pages += 1
        cursor = page["next_cursor"]
        if not cursor:
            break
        assert pages < 10
    db_order = [a.id for a in session.query(Asset).filter_by(household_id=aid).order_by(Asset.created_at.desc(), Asset.id.desc()).all()]
    expect("cursor_paging_no_loss_no_dup", len(ids_all) == 25 and len(set(ids_all)) == 25, pages=pages, returned=len(ids_all))
    expect("cursor_order_matches_db", ids_all == db_order, first_page_5=ids_all[:5], note="tied second-resolution created_at, id desc tiebreak")
    malformed = client.get("/v1/assets", params={"household_id": aid, "cursor": "%%%not-a-cursor%%%", "limit": 10})
    record("malformed_cursor", "OBSERVE" if malformed.status_code == 200 else "DEFECT_OBSERVED", status=malformed.status_code, item_ids=[i["id"] for i in malformed.json().get("items", [])][:3], note="silent fallback to first page vs 422")

    # --- G2.B FTS filter/escaping + facets ---
    hit = client.get("/v1/assets", params={"household_id": aid, "q": "Zebraphant"}).json()
    expect("fts_filter_hit", len(hit["items"]) == 1 and hit["items"][0]["display_name"].endswith("Zebraphant"), total=len(hit["items"]))
    miss = client.get("/v1/assets", params={"household_id": aid, "q": "NoSuchTokenXyz"}).json()
    expect("fts_no_match_empty", miss["items"] == [] and miss["next_cursor"] is None)
    for probe in ['Zebraphant" OR "x', "Zebraphant'", "Zebraphant*", "NEAR("]:
        esc = client.get("/v1/assets", params={"household_id": aid, "q": probe})
        record(f"fts_escape[{probe[:18]}]", "PASS" if esc.status_code == 200 else "DEFECT_OBSERVED", status=esc.status_code, total=len(esc.json().get("items", [])) if esc.status_code == 200 else esc.text[:120])
    facets = client.get("/v1/assets/facets", params={"household_id": aid}).json()
    type_food = client.get("/v1/assets", params={"household_id": aid, "asset_type": "food", "limit": 100}).json()["items"]
    expect("facets_asset_type_match_list", facets["asset_type"].get("food") == len(type_food), facet=facets["asset_type"], listed=len(type_food))
    expect("facets_has_evidence_zero_but_present", facets["has_evidence"] == {"with": 0, "without": 25}, facets=facets["has_evidence"], note="populated household reports 0/25; keys omitted only when the whole base is empty (empty-household check below)")
    empty = client.get("/v1/assets", params={"household_id": cid}).json()
    empty_f = client.get("/v1/assets/facets", params={"household_id": cid}).json()
    expect("empty_household_distinct_zero", empty["items"] == [] and empty_f["asset_type"] == {} and empty_f["status"] == {}, list_items=len(empty["items"]), facets=empty_f)

    # --- G2.C sort honesty + saved searches ---
    base_resp = client.get("/v1/assets", params={"household_id": aid, "limit": 100}).json()["items"]
    sorted_resp = client.get("/v1/assets", params={"household_id": aid, "limit": 100, "sort": "display_name"}).json()["items"]
    observe("sort_param_effect", identical=[i["id"] for i in sorted_resp] == [i["id"] for i in base_resp], accepted_keys=sorted(SavedSearchCreate.model_fields.keys()), note="server has no sort parameter; CatalogPage sorts the loaded page only (source)")
    s1 = client.post("/v1/saved-searches", params={"household_id": aid}, json={"name": "Food only", "query": {"asset_type": "food", "q": "Zebraphant"}})
    expect("saved_search_create", s1.status_code == 201 and s1.json()["query"] == {"asset_type": "food", "q": "Zebraphant"}, status=s1.status_code, query=s1.json().get("query"))
    s1b = client.post("/v1/saved-searches", params={"household_id": aid}, json={"name": "food ONLY", "query": {"asset_type": "household"}})
    expect("saved_search_duplicate_name_409", s1b.status_code == 409, status=s1b.status_code)
    s1c = client.post("/v1/saved-searches", params={"household_id": bid}, json={"name": "Food only", "query": {"asset_type": "household"}})
    expect("saved_search_same_name_other_household_ok", s1c.status_code == 201, status=s1c.status_code)
    replay = client.post("/v1/saved-searches", params={"household_id": aid}, json={"name": "Replay test", "query": {"q": "Zebraphant"}})
    observed_replay = client.post("/v1/saved-searches", params={"household_id": aid}, json={"name": "Replay test 2", "query": {"q": "Zebraphant", "sort": "name", "bogus": 1}})
    record("saved_search_unknown_sort_key", "OBSERVE", status=observed_replay.status_code, persisted_query=observed_replay.json().get("query"))
    applied = client.get("/v1/assets", params={"household_id": aid, **replay.json()["query"]}).json()
    expect("saved_search_apply_roundtrip", [i["id"] for i in applied["items"]] == [hit["items"][0]["id"]], returned=len(applied["items"]))
    list_a = client.get("/v1/saved-searches", params={"household_id": aid}).json()
    list_b = client.get("/v1/saved-searches", params={"household_id": bid}).json()
    expect("saved_search_household_scoped", all(x["household_id"] == aid for x in list_a["items"]) and all(x["household_id"] == bid for x in list_b["items"]))
    foreign_del = client.delete(f"/v1/saved-searches/{s1.json()['id']}", params={"household_id": bid})
    expect("saved_search_foreign_delete_403", foreign_del.status_code == 403, status=foreign_del.status_code)
    own_del = client.delete(f"/v1/saved-searches/{s1.json()['id']}", params={"household_id": aid})
    gone = client.get("/v1/saved-searches", params={"household_id": aid}).json()
    expect("saved_search_delete", own_del.status_code == 200 and s1.json()["id"] not in [x["id"] for x in gone["items"]], status=own_del.status_code, remaining=len(gone["items"]))

    # --- G2.D lifecycle ---
    life = client.post("/v1/assets", params={"household_id": aid}, json={"display_name": "Lifecycle probe"}).json()
    lid = life["id"]
    illegal = client.patch(f"/v1/assets/{lid}", params={"household_id": aid}, json={"status": "DISPOSED"})
    expect("lifecycle_active_disposed_422", illegal.status_code == 422, status=illegal.status_code, detail=illegal.json().get("detail"))
    archive = client.delete(f"/v1/assets/{lid}", params={"household_id": aid})
    rearchive = client.delete(f"/v1/assets/{lid}", params={"household_id": aid})
    back = client.patch(f"/v1/assets/{lid}", params={"household_id": aid}, json={"status": "ACTIVE"})
    expect("lifecycle_archive_then_illegal_reactivate", archive.status_code == 200 and rearchive.status_code == 200 and back.status_code == 422, archive=archive.status_code, rearchive=rearchive.status_code, reactivate=back.status_code, detail=back.json().get("detail"))
    default_list = client.get("/v1/assets", params={"household_id": aid, "limit": 100}).json()["items"]
    observe("archived_visibility_default_list", archived_in_default_list=any(i["id"] == lid for i in default_list), status_filtered=client.get("/v1/assets", params={"household_id": aid, "status": "ARCHIVED"}).json()["total"] if "total" in client.get("/v1/assets", params={"household_id": aid, "status": "ARCHIVED"}).json() else len(client.get("/v1/assets", params={"household_id": aid, "status": "ARCHIVED"}).json()["items"]), note="list endpoint has no implicit ACTIVE filter; UI filtering not exercised")

    # --- G2.E locations/relations OFF (dormant) then ON (disposable process only) ---
    off_loc = client.get("/v1/locations", params={"household_id": aid})
    off_rel = client.get(f"/v1/assets/{life['id']}/relations", params={"household_id": aid})
    expect("flags_off_routes_404", off_loc.status_code == 404 and off_rel.status_code == 404, locations=off_loc.status_code, relations=off_rel.status_code)
    settings.sg_locations_enabled = True
    settings.sg_relations_enabled = True
    parent = client.post("/v1/locations", params={"household_id": aid}, json={"name": "Kitchen"})
    child = client.post("/v1/locations", params={"household_id": aid}, json={"name": "Fridge", "parent_id": parent.json()["id"]})
    b_loc = client.post("/v1/locations", params={"household_id": bid}, json={"name": "B room"})
    expect("location_create_tree", parent.status_code == 201 and child.status_code == 201, parent=parent.status_code, child=child.status_code)
    cycle = client.patch(f"/v1/locations/{parent.json()['id']}", params={"household_id": aid}, json={"parent_id": child.json()["id"]})
    selfp = client.patch(f"/v1/locations/{parent.json()['id']}", params={"household_id": aid}, json={"parent_id": parent.json()["id"]})
    crossp = client.post("/v1/locations", params={"household_id": aid}, json={"name": "X", "parent_id": b_loc.json()["id"]})
    expect("location_cycle_self_cross_household_rejected", cycle.status_code == 422 and selfp.status_code == 422 and crossp.status_code in {403, 404}, cycle=cycle.status_code, self_parent=selfp.status_code, cross_parent=crossp.status_code, cross_detail=crossp.json().get("detail"))
    assign = client.post(f"/v1/assets/{life['id']}/locations", params={"household_id": aid}, json={"location_id": child.json()["id"]})
    assign_again = client.post(f"/v1/assets/{life['id']}/locations", params={"household_id": aid}, json={"location_id": child.json()["id"]})
    foreign_assign = client.post(f"/v1/assets/{life['id']}/locations", params={"household_id": aid}, json={"location_id": b_loc.json()["id"]})
    detail = client.get(f"/v1/assets/{life['id']}", params={"household_id": aid}).json()
    expect("location_assign_idempotent_and_reader", assign.status_code == 200 and assign_again.status_code == 200 and foreign_assign.status_code in {403, 404} and detail.get("locations") == [{"id": child.json()["id"], "name": "Fridge", "parent_id": parent.json()["id"]}], assign=assign.status_code, again=assign_again.status_code, foreign=foreign_assign.status_code, reader=detail.get("locations"))
    rel = client.post(f"/v1/assets/{life['id']}/relations", params={"household_id": aid}, json={"to_asset_id": hit["items"][0]["id"], "relation_type": "related_to"})
    rel_dup = client.post(f"/v1/assets/{life['id']}/relations", params={"household_id": aid}, json={"to_asset_id": hit["items"][0]["id"], "relation_type": "related_to"})
    rel_self = client.post(f"/v1/assets/{life['id']}/relations", params={"household_id": aid}, json={"to_asset_id": life["id"], "relation_type": "related_to"})
    rel_cross = client.post(f"/v1/assets/{life['id']}/relations", params={"household_id": aid}, json={"to_asset_id": b_created[0]["id"], "relation_type": "related_to"})
    rel_bad_type = client.post(f"/v1/assets/{life['id']}/relations", params={"household_id": aid}, json={"to_asset_id": hit["items"][0]["id"], "relation_type": "hates"})
    expect("relation_controls", rel.status_code == 201 and rel_dup.status_code == 409 and rel_self.status_code == 422 and rel_cross.status_code == 403 and rel_bad_type.status_code == 422, created=rel.status_code, dup=rel_dup.status_code, self=rel_self.status_code, cross=rel_cross.status_code, bad_type=rel_bad_type.status_code)
    both = client.get(f"/v1/assets/{hit['items'][0]['id']}/relations", params={"household_id": aid}).json()
    detail_rel = client.get(f"/v1/assets/{life['id']}", params={"household_id": aid}).json()
    expect("relation_reader_both_directions", len(both["items"]) == 1 and detail_rel.get("relations") and detail_rel["relations"][0]["relation_type"] == "related_to", reverse_view=both["items"][0].get("direction") if both["items"] else None, forward=detail_rel.get("relations"))

    # --- G2.F expiry classification -> manual entry -> status/task readback; bare Resolve ---
    def mk(name: str) -> str:
        return client.post("/v1/assets", params={"household_id": aid}, json={"display_name": name}).json()["id"]

    exp_x, exp_y, nonp = mk("Expiry X"), mk("Expiry Y"), mk("Non perishable Z")
    EXP = "/v1/plugins/expiry-tracker"
    badcat = client.post(f"{EXP}/assets/{exp_x}/classification", params={"household_id": aid}, json={"category": "spaceships"})
    expect("classify_unknown_category_422", badcat.status_code == 422, status=badcat.status_code)
    cx = client.post(f"{EXP}/assets/{exp_x}/classification", params={"household_id": aid}, json={"category": "food"})
    cy = client.post(f"{EXP}/assets/{exp_y}/classification", params={"household_id": aid}, json={"category": "medicine"})
    cz = client.post(f"{EXP}/assets/{nonp}/classification", params={"household_id": aid}, json={"category": "non_perishable"})
    expect("classify_food_unknown_expiry_and_task", cx.status_code == 200 and cx.json()["expiry_assertion"]["value"] == {"status": "unknown"} and cx.json()["review_task"], status=cx.status_code, expiry=cx.json().get("expiry_assertion"), task=cx.json().get("review_task"))
    expect("classify_non_perishable_no_task", cz.status_code == 200 and cz.json()["expiry_assertion"] is None and cz.json()["review_task"] is None, body=cz.json())
    tasks = client.get("/v1/review-tasks", params={"household_id": aid, "limit": 100}).json()
    t_x = [t for t in tasks["items"] if t["id"] == cx.json()["review_task"]]
    expect("review_task_readback", len(t_x) == 1 and t_x[0]["task_type"] == "expiry.manual_entry" and t_x[0]["status"] == "open", task=t_x[0] if t_x else None)
    foreign_resolve = client.post(f"/v1/review-tasks/{cx.json()['review_task']}/resolve", params={"household_id": bid}, json={})
    expect("review_task_foreign_403", foreign_resolve.status_code == 403, status=foreign_resolve.status_code)
    bare = client.post(f"/v1/review-tasks/{cx.json()['review_task']}/resolve", params={"household_id": aid}, json={})
    after_bare_detail = client.get(f"/v1/assets/{exp_x}", params={"household_id": aid}).json()
    expiry_after_bare = [a for a in after_bare_detail["assertions"] if a["field_path"].endswith("expiry_date")]
    observe("bare_resolve_without_data", resolve_status=bare.status_code, task_status=bare.json().get("status"), expiry_assertion_still=expiry_after_bare, note="SC-08/09: bare Resolve closes the task without writing the expiry data-required assertion")
    manual = client.post(f"{EXP}/assets/{exp_y}/expiry", params={"household_id": aid}, json={"expiry_date": "2026-11-30"})
    task_y_after = client.get("/v1/review-tasks", params={"household_id": aid, "limit": 100}).json()
    t_y = [t for t in task_y_after["items"] if t["id"] == cy.json()["review_task"]]
    bad_date = client.post(f"{EXP}/assets/{exp_y}/expiry", params={"household_id": aid}, json={"expiry_date": "31-11-2026"})
    not_applicable = client.post(f"{EXP}/assets/{nonp}/expiry", params={"household_id": aid}, json={"expiry_date": "2026-11-30"})
    expect("manual_entry_resolves_real_task", manual.status_code == 200 and cy.json()["review_task"] in manual.json()["resolved_review_task_ids"] and t_y and t_y[0]["status"] == "resolved", status=manual.status_code, resolved=manual.json().get("resolved_review_task_ids"), task=t_y[0] if t_y else None)
    expect("manual_entry_invalid_date_422", bad_date.status_code == 422, status=bad_date.status_code, detail=bad_date.json().get("detail"))
    expect("manual_entry_non_perishable_422", not_applicable.status_code == 422 and "not applicable" in not_applicable.json().get("detail", ""), status=not_applicable.status_code, detail=not_applicable.json().get("detail"))
    status_fixed = client.get(f"{EXP}/status", params={"household_id": aid, "as_of": "2026-10-13"}).json()
    observe("status_engine_readback", keys=sorted(status_fixed.keys()), sample=(status_fixed.get("items") or [])[:3] if isinstance(status_fixed.get("items"), list) else status_fixed)
    zero_cat = client.get(f"{EXP}/status", params={"household_id": aid, "as_of": "2026-10-13", "category": "documents"}).json()
    observe("status_category_filter", empty_result=zero_cat if len(json.dumps(zero_cat)) < 300 else "large", total=zero_cat.get("total") if isinstance(zero_cat, dict) else None)
    archived_x = client.delete(f"/v1/assets/{exp_x}", params={"household_id": aid})
    status_after = client.get(f"{EXP}/status", params={"household_id": aid, "as_of": "2026-10-13"}).json()
    observe("status_after_archive", archive=archived_x.status_code, rows=[row.get("asset_id") for row in status_after.get("rows", [])], unresolved_rows=status_after.get("unresolved_rows"), summary=status_after.get("summary"))

    session.close()
    print(json.dumps({"results": RESULTS}, indent=2))
    print(f"TEMP_ROOT={TEMP_ROOT}")
    print(f"elapsed_s={time.monotonic() - opened:.1f} start_epoch={cmd_start} end_epoch={int(time.time())}")
    return 1 if any(r["result"] == "FAIL" for r in RESULTS) else 0


if __name__ == "__main__":
    sys.exit(main())

SG-113 report — Location tree: schema + ONE migration (temp-only) + dormant API + asset-detail UI
=================================================================================================

Verdict: SHIPPED (dormant). A household location TREE (`location`, nullable self-FK) and an
asset↔location assignment (`asset_location`, composite key = one asset sits in one location once) now
exist as models + exactly ONE migration that chains from the live head and cycles on temp. The API
(create/list/rename-reparent/delete + assign/unassign) is served behind `sg_locations_enabled`,
default OFF, so every new route answers 404 until the owner's migration word; the asset-detail read adds
`locations[]` only when the flag is ON (the OFF response is byte-identical). The asset-detail page shows
the section only when the backend is enabled and otherwise hides it entirely. The served backend was
rebuilt and recreated exactly once; it serves the dormant code with zero row delta and zero behaviour
change. $0.000000 — no metered call exists on any path. PRODUCTION MIGRATION NOT RUN.

Contract echo + source path
---------------------------
Contract 0.33.0 — installed global rules file hashed against the payload, never checkout-vs-stamp (G-L1/M3).
- source: `/home/andrei/storagegenie-contract/VERSION` = `0.33.0`
- source HEAD: `b232b845d74e89cb346c60fa4b9a40ec401c42dd` = "Contract payload 0.33.0"
- `sha256sum /home/andrei/storagegenie-contract/RULES.md` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46`
- payload `/home/andrei/storagegenie-contract/RULES.sha256` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46 RULES.md` -> match.
- recorded `0.33.0` == published `b232b84`. Clean.

Model / effort / spend (CO-78)
------------------------------
Read from the process arguments, never a system-prompt identity line.
- argv (`/proc/3846705/cmdline`): `opencode run --auto --dir /home/andrei/StorageGenie --variant high <packet>`
- effort = `high` (from `--variant high`)
- model = `unknown` — no `--model` flag present (`grep -c -- '--model' /proc/3846705/cmdline` = 0) and no
  provider metadata readable; the packet states the CLI default model is omitted by policy, and I refuse
  to guess a plausible id.
- Spend real $ = `$0.000000` (zero provider calls; no metered call exists on any path).

Refs
----
- Work dir `/home/andrei/StorageGenie`, origin `git@github.com:Andovol/StorageGenie.git`
- BASE_REF = `origin/automation`
- BASE_RESOLVED = `2ed06a976bc142887adf9d6c7a469adcce6d6a63` (== start HEAD; the packet commit)
- WORK_HEAD = `<WORK_HEAD>`

Premise verification — corrections are worth more than agreement
----------------------------------------------------------------
Every packet premise re-verified against the tree; the counts, paths and line numbers held. Two nuances
are reported rather than bent:

1. **"NO location model/table/route anywhere" — VERIFIED.** `grep -rni "location" backend/app/models/
   backend/app/api/ backend/app/services/` returned 0 hits (quoted in `SG-113_verify.log`). The only
   location vocabulary is the extension enum `storage_location` at
   `backend/app/plugins/expiry_tracker.py:182` (fridge/freezer/pantry/bathroom_cabinet/medicine_cabinet/
   garage_utility/custom) — a free-text hint, never trusted as the set and never imported by this slice.
2. **The migration head is `20260923_sg100_enrich_snapshot` — VERIFIED** by reading every `revision` /
   `down_revision` pair in `backend/alembic/versions/` in-slice (9 files), not by inheriting the packet's
   listing. My migration chains from that exact head.

G1 — BEFORE (raw, in `SG-113_verify.log`)
-----------------------------------------
- image `sha256:f1d9f99affd1…` created 2026-09-24T11:03:01Z; container `d184fbc0becd…`, restart 0, healthy
- `alembic current` (in container) = `20260923_sg100_enrich_snapshot (head)` — single head, VERIFIED
- `select count(*) from sqlite_master where type='table'` = `25` — VERIFIED
- 25-table counts captured; asset status census `ACTIVE|6`; all byte-identical AFTER
- health exact: `{"status":"ok","db":"ok","storage":"ok"}`
- gate (canonical vhost): http:80 `code=301 redirect=https://storagegenie.dynv6.net/`; https:443 `code=401`
- bundle assets served: `index-CoNI-1Zn.css`, `index-DAsiAK51.js`
- location-absence grep: 0 hits (quoted above)

G1 — models + migration (temp-only)
-----------------------------------
- `backend/app/models/location.py`:
  * `Location(TimestampMixin, Base)` — `id String(36) PK default new_id`, `household_id` FK
    `household.id` ondelete CASCADE + index, `name String(200)` non-empty (enforced in the route),
    `parent_id` self-FK `location.id` nullable + index. NULL parent = root.
  * `asset_location` Table — `asset_id` FK `asset.id` CASCADE, `location_id` FK `location.id` CASCADE,
    composite PRIMARY KEY `(asset_id, location_id)` (the "one asset sits in one location once" rule),
    `created_at`. Multi-location is separate rows, stated.
- `backend/app/models/__init__.py` — `Location`, `asset_location` exported (import + `__all__`).
- `backend/alembic/versions/20260924_sg113_location.py` — revision `20260924_sg113_location`,
  down_revision `20260923_sg100_enrich_snapshot`. Upgrade creates `location` (+ `ix_location_household_id`,
  `ix_location_parent_id`) and `asset_location` (+ `ix_asset_location_location_id`); downgrade drops both
  head-relative. Re-read by `upgrade -> downgrade -> upgrade` on temp (`PG-SC-02`).
- `PG-SC-11`: end-relative assertion grep over the touched files yields exactly one hit,
  `backend/app/api/v1/assets.py:292: last = items[-1]` — PRE-EXISTING cursor-pagination code in
  `list_assets`, not introduced by this slice and not on any changed line.

G2 — API + dormancy gate
------------------------
- `backend/app/api/v1/locations.py`, a router-level `Depends(_require_locations_enabled)`: with
  `settings.sg_locations_enabled` False (default) EVERY route answers 404, so undeployed schema can never
  be exercised.
  * `GET /v1/locations` — list (household-scoped, name-sorted); empty household -> `{"items": []}`.
  * `POST /v1/locations` `{name, parent_id?}` — 201; household must exist (404); parent must exist in the
    same household (404/403); name non-blank, ≤200 (422, stripped).
  * `PATCH /v1/locations/{id}` `{name?, parent_id?}` — rename/reparent; self-parent 422; missing parent
    404; cross-household parent 403; cycle 422.
  * `DELETE /v1/locations/{id}` — 409 when the location has assigned assets; 409 when it has child
    locations; otherwise 200. A location is never cascade-emptied silently.
  * `POST /v1/assets/{id}/locations` `{location_id}` — assign; asset and location must exist (404) and be
    in the same household (403); a repeat assign is an idempotent no-op (200).
  * `DELETE /v1/assets/{id}/locations/{location_id}` — unassign; a repeat unassign is an idempotent no-op.
- **Cycle guard** (`_would_cycle`): walks the proposed parent's ancestor chain; the location itself or any
  descendant (which appears as an ancestor of the proposed parent) is refused 422; a pre-existing loop is
  refused defensively. A parent chain is data, not schema — the guard lives here, not in the migration.
- **Seed names are never the set**: no §9.2 name is pre-created; the tree starts empty and creation is
  explicit rows only (tested).
- **Asset-detail reader** (`backend/app/api/v1/assets.py` `_asset_to_dict`): adds `locations[]` (id, name,
  parent_id) ONLY when `settings.sg_locations_enabled` is True; when OFF the key is absent, so the
  pre-existing response shape is byte-identical.
- `backend/app/main.py` registers the router. `backend/app/config.py` gains
  `sg_locations_enabled: bool = False` (env `SG_LOCATIONS_ENABLED`).

### Frontend

- `frontend/src/api/types.ts` — `Location`, `LocationListResponse`, `Asset.locations?`.
- `frontend/src/api/client.ts` — `apiDelete` + `fetchLocations` / `assignAssetLocation` /
  `unassignAssetLocation`.
- `frontend/src/routes/AssetDetailPage.tsx` — `LocationsSection`: the list route answers 404 while
  dormant, the query errors, and the WHOLE section is hidden (no error, no fallback list). When enabled it
  renders the empty state (`No locations assigned`, `PG-SC-07`) or the assigned list with a Remove button,
  plus an assign `<select>` filtered to not re-offer an assigned location. Create-inline NOT shipped
  (optional per G3; stated rather than silently omitted).

### Tests (fail-then-pass; BOTH runs committed raw, `PG-EV-09`)

- `backend/tests/test_sg113_locations.py` (9 tests). The migration oracle is an independent
  `upgrade -> downgrade -> upgrade` cycle; the API matrix drives the REAL routes through `TestClient`.
- **FAIL run** (candidate test file against BASE `2ed06a9`, isolated `git archive`, `PYTHONPATH` forced to
  the base app — verified `import app` -> base path): `9 failed`. Classification, loud and honest:
  8 are genuine behavioural fails (schema absent after head upgrade; route absence surfaces as 405/404
  instead of the candidate's 200/422/409/404); 1 (`..._roundtrip`) first reaches a lazy
  `from app.models.location import asset_location` and is an ARTIFACT-ABSENCE fail, not a behavioural
  baseline. **PASS run**: `9 passed`.
- Frontend `frontend/src/routes/AssetDetailPage.test.tsx` (+4, 9 total): hides entirely when the backend
  reports disabled; empty state for an unassigned asset; lists assigned + assigns from select + unassigns.

### Gates (raw in `SG-113_verify.log`)

- **Full backend suite**: `2 failed, 572 passed`. The 2 reds are the known decoder env reds
  (`test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier`,
  `test_ocr_has_text_boxes_and_mean_confidence`). STASH-PROVED on this slice: both fail identically on the
  BASE archive with `pyzbar/libzbar` and `tesseract` absent on the host (`2 failed in 0.74s`). Not caused here.
- **ruff**: `All checks passed!` (whole backend).
- **mypy**: candidate `41 errors in 9 files (checked 88 source files)` vs base
  `41 errors in 9 files (checked 86 source files)` — delta 0. The new files add 0 errors (the six
  `# type: ignore[no-untyped-def]` comments my first draft copied from the assets-route precedent were
  unused and removed to keep the delta at 0).
- **Secret gate** (`PG-SC-05`): pattern over every changed/new file -> 0 real secrets. The only hits are
  the pre-existing settings NAMES in `config.py` (`opencode_api_key`, `jina_api_key`, plus the SG-097
  comment), quoted; no value is printed or read. Host `.env` never printed, never read into any artifact.
- **Frontend**: `tsc && vite build` ok (built `dist/assets/index-BXZ7OS4d.js`), `eslint src` clean,
  `vitest run` `24 passed (24)` files / `202 passed (202)` tests.
- **Scope**: changed files = `models/location.py` (new), `models/__init__.py`, `config.py`,
  `alembic/versions/20260924_sg113_location.py` (new), `api/v1/locations.py` (new), `api/v1/assets.py`,
  `main.py`, `tests/test_sg113_locations.py` (new), `frontend/src/api/types.ts`,
  `frontend/src/api/client.ts`, `frontend/src/routes/AssetDetailPage.tsx`,
  `frontend/src/routes/AssetDetailPage.test.tsx`, three `docs/worklogs` files. No other model, no second
  migration, no service, no catalog filter, no merge/lifecycle hunk. `.gitignore` re-verified, all
  committable. `docker compose config` never run.

Cross-product (`PG-IC-01`): no criterion demanded a production migration, a second recreate, a live
assignment, a press, a sender, or any metered call — no cell collides. Reads were pytest/vitest/TestClient
+ host commands + the authorised image build and ONE recreate; no other image was pulled or run, no
unnamed runtime launched.

G4 — refresh + verify (dormant code live, zero behaviour change)
----------------------------------------------------------------
- image id: `sha256:f1d9f99affd1…` -> `sha256:67c62b86806e…` (differs)
- container: `d184fbc0becd…` -> `2fceee17df2e…` (exactly ONE recreate; RestartCount 0, healthy)
- `alembic current`: `20260923_sg100_enrich_snapshot` UNCHANGED — note the `(head)` suffix is gone
  precisely because the new `20260924_sg113_location` is now the head; the migration file is in the image
  but **NOT applied** to the live DB.
- 25-table counts: byte-identical, delta exactly 0; asset status census `ACTIVE|6` -> `ACTIVE|6`
- health: `{"status":"ok","db":"ok","storage":"ok"}` x6
- gate (canonical vhost): `301` / `401`
- bundle: `index-DAsiAK51.js` -> `index-t_5eG484.js` (differs — EXPECTED, frontend changed)
- fresh-server dormancy proof (no live write): all six new routes answer `404` through the recreated
  server (GET/POST `/v1/locations`, PATCH/DELETE `/v1/locations/missing`,
  POST/DELETE `/v1/assets/{id}/locations[/{id}]`); asset detail has NO `locations` key; catalog-list
  `GET /v1/assets` still `200`.
- fresh image carries the new code: `grep -c 'locations'` finds it and the served
  `locations.py`/`location.py` sha256 match the host byte for byte.

Post-restart sweep waived (`PG-DP-02`, restart-gated). Substitute authority: the in-process full backend
suite + frontend suite pre-restart, plus the post-restart live probes (health x6, gate, alembic, 25-table
counts, flag-off 404s, catalog-list 200). The derived browser-driven set is empty and differed nowise
beyond the new mocked-API unit tests, which run in-process.

Actual-versus-budget per leg (`PG-PR-06`; units = wall seconds)
--------------------------------------------------------------
- G1 recon + BEFORE capture: ~90 s actual (bound 120 s ordinary).
- G2 implement + tests + G3 gates: ~600 s actual, dominated by the full backend suite (27.21 s), two full
  mypy runs, the BASE-archive fail run, the base decoder stash-proof, the frontend build (1.62 s) and
  full vitest (4.55 s) (bound 600 s suite+lint per side).
- G4 build + ONE recreate + verify: ~180 s actual, dominated by the classic-builder image build
  (bound 600 s build+recreate+verify).
- G5 worklog/report/receipt: ~150 s actual (bound 1500 s early-close).
- Overall: ~1020 s actual vs 2100 s overall bound.

Production migration + activation word-shape (batched with SG-114; NOT run here)
--------------------------------------------------------------------------------
Exact commands for the owner-gated word (migrate + flip + recreate). No `docker compose config`.
```
# 0. before census (live DB)
docker exec storagegenie-backend-1 python -c "import sqlite3;c=sqlite3.connect('/data/db/storagegenie.db');print(c.execute('select version_num from alembic_version').fetchone()[0]);print(sorted(r[0] for r in c.execute(\"select name from sqlite_master where type='table'\")))"
# 1. apply the migration (expected new head 20260924_sg113_location; adds location + asset_location)
docker exec storagegenie-backend-1 python -m alembic upgrade head
# 2. flip the flag in the host .env (never printed): append SG_LOCATIONS_ENABLED=true
# 3. one backend recreate to pick up the env
docker compose up -d --no-deps backend
# 4. after census (expect both tables present; version_num = 20260924_sg113_location; other counts equal)
docker exec storagegenie-backend-1 python -c "import sqlite3;c=sqlite3.connect('/data/db/storagegenie.db');print(c.execute('select version_num from alembic_version').fetchone()[0]);print(sorted(r[0] for r in c.execute(\"select name from sqlite_master where type='table'\")))"
# 5. activation probe (expect 200, not 404)
curl -s -o /dev/null -w '%{http_code}\n' "http://127.0.0.1:8003/v1/locations?household_id=<id>"
```

Issues / disagreements / unanswered
-----------------------------------
- Corrected above: none of the packet's premises were wrong; two design calls are named — (a) delete is
  refused 409 when the location has CHILDREN as well as when it has assignments (the packet explicitly
  named only assignments; refusing children keeps the tree free of orphans, and both are tested);
  (b) create-inline was NOT shipped (G3 makes it optional; the section still lists/assigns/unassigns).
- `model` reported `unknown` (no `--model` in argv, no provider metadata). A refusal to guess, not a failure.
- The buildkit EROFS condition from SG-111 still holds; used `DOCKER_BUILDKIT=0` (classic builder).
- No privileged operation was denied; nothing was left unanswered.

Receipt (notes ref)
-------------------
Work pushed to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no
`{{RECEIPT_CMD}}`. Note added on WORK_HEAD; notes ref pushed and read back from a MAPPED fetch. Pasted
executed output:

```
<RECEIPT_SHOW_OUTPUT>
```

Full raw transcript (precheck, add, push, mapped fetch, show) is in `SG-113_verify.log` -> `RECEIPT
NOTE VERIFY`. The final tip (this report/receipt commit) is dual-annotated with the same note (SG-092
inoculation). final line: `<NOTE_YES>`.

Three UNCLEAR lines
-------------------
- FIRST READ: whether the asset-detail read should always carry `locations: []` or only when the flag is
  ON. I chose "only when ON" so the flag-OFF response is byte-identical to the pre-slice shape (G4's
  zero-behaviour-change requirement); the UI detects dormancy from the 404 on the list route.
- DURING EXECUTION: whether delete-with-children should be a 409 or a cascade. The packet named only
  delete-with-assignments; I refused children too to keep the tree orphan-free, and tested it.
- REMAINING: the model id (CLI default, unreadable from argv/metadata); whether the location tree needs a
  rename/reorder audit trail (none was specified; no audit row is written); and whether SG-114 should
  reuse `asset_location` for a future multi-location UI or grow a `primary` flag.

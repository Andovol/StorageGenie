SG-114 report — Asset relations: typed links + ONE migration (temp-only) + dormant API + asset-detail UI
=========================================================================================================

Verdict: SHIPPED (dormant). An `asset_relation` table (typed, directed links between two assets of one
household; composite uniqueness `(from_asset_id, to_asset_id, relation_type)`) now exists as a model +
exactly ONE migration that chains from the live file head and cycles on temp. The relation API
(list-for-asset BOTH directions, create, delete) is served behind `sg_relations_enabled`, default OFF,
so every new route answers 404 until the owner's batched migration word; the asset-detail read adds
`relations[]` ONLY when the flag is ON (the OFF response is byte-identical). The detail page shows a
relations section only when the backend is enabled and hides it entirely otherwise. The served backend
was rebuilt and recreated exactly once; it serves the dormant code with zero row delta and zero behaviour
change. $0.000000 — no metered call exists on any path. PRODUCTION MIGRATION NOT RUN (batched word-shape
recorded below, together with SG-113's).

Contract echo + source path
---------------------------
Contract 0.33.0 — installed global rules file hashed against the payload, never checkout-vs-stamp (G-L1/M3).
- source: `/home/andrei/storagegenie-contract/VERSION` = `0.33.0`
- source HEAD: `b232b845d74e89cb346c60fa4b9a40ec401c42dd` = "Contract payload 0.33.0"; `git show
  FETCH_HEAD:VERSION` after `git fetch origin` = `0.33.0` (remote == local).
- `sha256sum /home/andrei/storagegenie-contract/RULES.md` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46`
- payload `/home/andrei/storagegenie-contract/RULES.sha256` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46 RULES.md` -> match.
- recorded `0.33.0` == published `b232b84`. Clean.

Model / effort / spend (CO-78)
------------------------------
Read from the process arguments, never a system-prompt identity line.
- argv (`/proc/3874953/cmdline`): `opencode run --auto --dir /home/andrei/StorageGenie --variant high <packet>`
- effort = `high` (from `--variant high`)
- model = `unknown` — no `--model` flag present (`tr '\0' '\n' < /proc/3874953/cmdline | grep -c -- '--model'` = 0)
  and no provider metadata readable; the packet states the CLI default model is omitted by policy, and I
  refuse to guess a plausible id.
- Spend real $ = `$0.000000` (zero provider calls; no metered call exists on any path).

Refs
----
- Work dir `/home/andrei/StorageGenie`, origin `git@github.com:Andovol/StorageGenie.git`
- BASE_REF = `origin/automation`
- BASE_RESOLVED = `8bed3f0bb8652ea3712980182accddd88ff8f8d1` (== start HEAD; the packet commit)
- WORK_HEAD = `7c16635e85197c436119121d409f6f86974855ed`

Premise verification — corrections are worth more than agreement
----------------------------------------------------------------
Every packet premise re-verified against the tree; the counts, paths and line numbers held. Two nuances
are reported rather than bent:

1. **"NO relation model/table/route anywhere" — VERIFIED.** `grep -rni "relation"` over
   `backend/app/{models,api,services}` against the BASE archive (`8bed3f0`) returned **0 hits** (quoted in
   `SG-114_verify.log` -> PREMISE). My in-slice working-tree grep necessarily finds the NEW slice files;
   it is labelled as such in the log and is NOT the absence proof.
2. **The migration file head is `20260924_sg113_location` — VERIFIED** by reading every `revision` /
   `down_revision` pair in `backend/alembic/versions/` in-slice (10 files before my addition), not by
   inheriting the packet's listing. My migration chains from that exact head.
3. **`duplicate_of` pre-exists as a dedup PROPOSAL kind, not a relation.** The token `duplicate_of_asset`
   already exists in `backend/app/services/dedup.py:117,133`, `candidates.py:920` and
   `frontend/src/components/CandidateCard.tsx:18` (SG-112 lineage). That is out of scope and untouched;
   the relation surface itself contains **0** occurrences of the token (grep-gate below).

G1 — BEFORE (raw, in `SG-114_verify.log`)
-----------------------------------------
- image `sha256:67c62b86806e…` created 2026-09-24T11:19:06Z; container `2fceee17df2e…`, restart 0, healthy
- `alembic current` (in container) = `20260923_sg100_enrich_snapshot` — single head (DB stamp), VERIFIED
- `select count(*)` over `sqlite_master where type='table'` = `25`; 25-table counts captured; asset
  status census `ACTIVE|6`; all byte-identical AFTER
- health exact: `{"status":"ok","db":"ok","storage":"ok"}`
- gate (canonical vhost): http:80 `code=301 redirect=https://storagegenie.dynv6.net/`; https:443 `code=401`
- bundle assets served: `index-CoNI-1Zn.css`, `index-t_5eG484.js` (js sha256 `9989a432…`)

G1 — model + migration (temp-only)
----------------------------------
- `backend/app/models/relation.py`:
  * `AssetRelation(TimestampMixin, Base)` — `id String(36) PK default new_id`, `household_id` FK
    `household.id` ondelete CASCADE + index, `from_asset_id` FK `asset.id` CASCADE + index,
    `to_asset_id` FK `asset.id` CASCADE + index, `relation_type String(50)` non-empty (the API vocabulary
    pins it), `created_at`/`updated_at` from the mixin.
  * `__table_args__` `UniqueConstraint("from_asset_id","to_asset_id","relation_type",
    name="uq_asset_relation_from_to_type")` — the same typed link twice is one row; `household_id` is
    carried so the household scope is readable without joining either asset.
- `backend/app/models/__init__.py` — `AssetRelation` exported (import + `__all__`).
- `backend/app/config.py` — `sg_relations_enabled: bool = False` (env `SG_RELATIONS_ENABLED`), deliberately
  SEPARATE from `sg_locations_enabled` so each batched word flips only its own surface.
- `backend/alembic/versions/20260924_sg114_relation.py` — revision `20260924_sg114_relation`,
  down_revision `20260924_sg113_location`. Upgrade creates `asset_relation` (+
  `ix_asset_relation_household_id`, `ix_asset_relation_from_asset_id`, `ix_asset_relation_to_asset_id`)
  and the unique constraint; downgrade drops indexes then table, head-relative. Re-read by
  `upgrade -> downgrade -> upgrade` on temp (`PG-SC-02`).
- `PG-SC-11`: end-relative assertion grep over the touched Python source yields exactly one hit,
  `backend/app/api/v1/assets.py:299: last = items[-1]` — PRE-EXISTING cursor-pagination code in
  `list_assets` (line moved by the one added import), not introduced by this slice and not on a changed line.

G2 — API + dormancy gate
------------------------
- `backend/app/api/v1/relations.py`, a router-level `Depends(_require_relations_enabled)`: with
  `settings.sg_relations_enabled` False (default) EVERY route answers 404, so the undeployed schema can
  never be exercised.
  * `GET /v1/assets/{asset_id}/relations` — list-for-asset. BOTH directions: outgoing (`from == asset`)
    and incoming (`to == asset`), each row labelled `direction` from THIS asset's perspective. Empty
    asset -> `{"items": []}`.
  * `POST /v1/assets/{asset_id}/relations` `{to_asset_id, relation_type}` — `asset_id` is the directed
    `from` end; 201. Both ends must be assets of the SAME household (missing 404 / foreign 403); a
    self-link is 422; an out-of-vocabulary type is 422 (request model); the exact typed link twice is 409.
  * `DELETE /v1/assets/{asset_id}/relations/{relation_id}` — idempotent: a missing link is a 200 no-op;
    a link owned by another household is 403; a link not touching the path asset is 404.
- **Vocabulary is EXACTLY two types** (`RELATION_TYPES = frozenset({"related_to", "contains"})`):
  `related_to` expresses symmetric intent but is STORED once as a directed row; `contains` is directed
  container -> content. Membership lives in the API, not a DB CHECK, so vocabulary can evolve with a
  decision rather than a migration; a third type is a new decision, never invented here.
- **Duplicate ownership is not a relation**: SG-112 already redirects a materialized duplicate through the
  lifecycle `MERGED` status + the `merge.merged_into` assertion. The relation surface contains **0**
  occurrences of `duplicate_of` (grep-gate below).
- **Asset-detail reader** (`backend/app/api/v1/assets.py` `_asset_to_dict`): adds `relations[]` (via the
  shared `relations_for_asset` helper) ONLY when `settings.sg_relations_enabled` is True; when OFF the key
  is absent, so the pre-existing response shape is byte-identical.
- `backend/app/main.py` registers the router.

### Frontend

- `frontend/src/api/types.ts` — `AssetRelation`, `RelationListResponse`, `Asset.relations?`.
- `frontend/src/api/client.ts` — `fetchRelations` / `createRelation` / `deleteRelation` +
  `fetchHouseholdAssets` (the always-on catalog list, used as the target picker and id->name map).
- `frontend/src/routes/AssetDetailPage.tsx` — `RelationsSection`: the list route answers 404 while
  dormant, the query errors, and the WHOLE section is hidden (no error, no fallback list). When enabled it
  renders the empty state (`No related assets`, `PG-SC-07`) or the both-direction list (other asset named
  from the catalog list, labelled `(relation_type, direction)`) with a Remove button, plus target/type
  selects and a Link button.

### Tests (fail-then-pass; BOTH runs committed raw, `PG-EV-09`)

- `backend/tests/test_sg114_relations.py` (9 tests). The migration oracle is an independent
  `upgrade -> downgrade -> upgrade` cycle; the API matrix drives the REAL routes through `TestClient`;
  refusals are proven to write NOTHING by a before==after row count (`PG-EV-02`).
- **FAIL run** (candidate test file against BASE `8bed3f0`, isolated `git archive`, `PYTHONPATH` forced to
  the base app — verified `import app` -> base path): `9 failed`. All 9 are genuine absence fails (the
  table does not exist after `upgrade head`; the routes are absent; `app.models.relation` /
  `app.api.v1.relations` do not exist). **PASS run**: `9 passed`.
- Frontend `frontend/src/routes/AssetDetailPage.test.tsx` (+3, 12 total): hides entirely when the backend
  reports disabled; empty state for an unlinked asset; lists both directions, creates a link, deletes one.

### Gates (raw in `SG-114_verify.log`)

- **Full backend suite**: `2 failed, 581 passed`. The 2 reds are the known decoder env reds
  (`test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier`,
  `test_ocr_has_text_boxes_and_mean_confidence`). STASH-PROVED on this slice: both fail identically on the
  BASE archive with `pyzbar/libzbar` and `tesseract` absent on the host (`2 failed in 0.67s`). Not caused here.
- **ruff**: `All checks passed!` (whole backend).
- **mypy**: candidate `41 errors in 9 files (checked 90 source files)` vs base
  `41 errors in 9 files (checked 88 source files)` — delta 0. The new files add 0 errors.
- **Secret gate** (`PG-SC-05`): pattern over every changed/new source file -> 0 real secrets. The only
  hits are the pre-existing settings NAMES in `config.py` (`opencode_api_key`, `jina_api_key`), quoted; no
  value is printed or read. Host `.env` never printed, never read into any artifact.
- **Frontend**: `tsc && vite build` ok (built `dist/assets/index-DyQr8w8_.js`), `eslint src` clean
  (exit 0), `vitest run` `24 passed (24)` files / `205 passed (205)` tests.
- **no-`duplicate_of` grep-gate**: 0 hits in the relation surface
  (`backend/app/models/relation.py`, `backend/app/api/v1/relations.py`,
  `backend/alembic/versions/20260924_sg114_relation.py`); the pre-existing dedup `duplicate_of_asset` kind
  is out of scope and quoted.
- **Scope**: changed files = `models/relation.py` (new), `models/__init__.py`, `config.py`,
  `alembic/versions/20260924_sg114_relation.py` (new), `api/v1/relations.py` (new), `api/v1/assets.py`,
  `main.py`, `tests/test_sg114_relations.py` (new), `frontend/src/api/types.ts`, `frontend/src/api/client.ts`,
  `frontend/src/routes/AssetDetailPage.tsx`, `frontend/src/routes/AssetDetailPage.test.tsx`, three
  `docs/worklogs` files. No other model, no second migration, no third relation type, no
  lifecycle/merge/location hunk. `.gitignore` re-verified, all committable. `docker compose config` never run.

Cross-product (`PG-IC-01`): no criterion demanded a production migration, a second recreate, a live link,
a press, a sender, or any metered call — no cell collides. Reads were pytest/vitest/TestClient +
host commands + the authorised image build and ONE recreate; no other image was pulled or run, no unnamed
runtime launched.

G4 — refresh + verify (dormant code live, zero behaviour change)
----------------------------------------------------------------
- image id: `sha256:67c62b86806e…` -> `sha256:b4bec08d9bcb…` (differs)
- container: `2fceee17df2e…` -> `1a0588c7d944…` (exactly ONE recreate; RestartCount 0, healthy)
- `alembic current`: `20260923_sg100_enrich_snapshot` UNCHANGED — the `(head)` suffix is gone precisely
  because the new `20260924_sg114_relation` is now the file head; 12 migration files are in the image but
  the new one is **NOT applied** to the live DB.
- 25-table counts: byte-identical, delta exactly 0; asset status census `ACTIVE|6` -> `ACTIVE|6`;
  `asset_relation` is absent from the live DB.
- health: `{"status":"ok","db":"ok","storage":"ok"}` x6
- gate (canonical vhost): `301` / `401`
- bundle: `index-t_5eG484.js` (sha `9989a432…`) -> `index-XGj8xV3t.js` (sha `65736eec…`) — differs,
  EXPECTED because the frontend changed; the CSS bundle is unchanged.
- fresh-server dormancy proof (no live write): GET/POST `/v1/assets/{id}/relations` and
  DELETE `/v1/assets/{id}/relations/missing` all answer `404` through the recreated server; asset detail
  has NO `relations` key; catalog-list `GET /v1/assets` still `200`.
- fresh image carries the new code: `/app/alembic/versions/20260924_sg114_relation.py` ships; served
  `relations.py`/`relation.py` sha256 match the host byte for byte
  (`4ef350ea…` / `a910610d…`).

Post-restart sweep waived (`PG-DP-02`, restart-gated). Substitute authority: the in-process full backend
suite + frontend suite pre-restart, plus the post-restart live probes (health x6, gate, alembic, 25-table
counts, flag-off 404s, catalog-list 200, in-image sha match). The derived browser-driven set is empty and
differed nowise beyond the new mocked-API unit tests, which run in-process.

Question each criterion answers (`PG-SC-09`): schema — links hold BOTH directions without orphans (FK
cascade + both-direction reader + temp migration cycle); dormancy — the undeployed schema's code serves
safely (flag-off 404 on every route, byte-identical detail read); UI — the detail page shows truth
(both directions, named, labelled) and hides cleanly (404 -> null section).

Actual-versus-budget per leg (`PG-PR-06`; units = wall seconds)
--------------------------------------------------------------
- G1 recon + G1/G2 implementation + G3 tests/gates (candidate fail/pass, BASE archive, full suite, two
  mypy runs, frontend build+vitest+eslint): ~450 s actual (each ordinary command <=120 s; suite+lint under
  the 600 s per-side bound).
- G4 build + ONE recreate + verify: ~130 s actual (bound 600 s build+recreate+verify).
- G5 worklog/report/receipt/push: ~250 s actual (bound 1500 s early-close).
- Overall: process elapsed ~502 s at the start of G5, well under the 2100 s overall bound.

Production migration + activation word-shape (BOTH batched migrations; NOT run here)
------------------------------------------------------------------------------------
Exact commands for the owner-gated word (apply SG-113 + SG-114, flip BOTH flags, recreate once). No
`docker compose config`.
```
# 0. before census (live DB): stamp + table set
docker exec storagegenie-backend-1 python -c "import sqlite3;c=sqlite3.connect('/data/db/storagegenie.db');print(c.execute('select version_num from alembic_version').fetchone()[0]);print(sorted(r[0] for r in c.execute(\"select name from sqlite_master where type='table'\")))"
# 1. apply BOTH migrations (head moves 20260923_sg100_enrich_snapshot -> 20260924_sg113_location -> 20260924_sg114_relation; adds location, asset_location, asset_relation)
docker exec storagegenie-backend-1 python -m alembic upgrade head
# 2. flip BOTH flags in the host .env (never printed/read into any artifact):
#    append SG_LOCATIONS_ENABLED=true and SG_RELATIONS_ENABLED=true
# 3. one backend recreate to pick up the env
docker compose up -d --no-deps backend
# 4. after census (expect version_num = 20260924_sg114_relation; location/asset_location/asset_relation present; other counts equal)
docker exec storagegenie-backend-1 python -c "import sqlite3;c=sqlite3.connect('/data/db/storagegenie.db');print(c.execute('select version_num from alembic_version').fetchone()[0]);print(sorted(r[0] for r in c.execute(\"select name from sqlite_master where type='table'\")))"
# 5. activation probes (expect 200, not 404) — one household id
curl -s -o /dev/null -w '%{http_code}\n' "http://127.0.0.1:8003/v1/locations?household_id=<id>"
curl -s -o /dev/null -w '%{http_code}\n' "http://127.0.0.1:8003/v1/assets/<asset_id>/relations?household_id=<id>"
```

Issues / disagreements / unanswered
-----------------------------------
- Corrected above: no packet premise was wrong. Design calls named: (a) the duplicate check is the EXACT
  composite `(from, to, type)` the packet specifies, so `A->B related_to` and `B->A related_to` are two
  rows (symmetric INTENT, stored once directed per create); I did NOT add a reverse-dedup, and state it.
  (b) delete scoping: a link not touching the path asset is 404, a foreign-household link is 403 — the
  packet named only the idempotent missing case.
- `model` reported `unknown` (no `--model` in argv, no provider metadata). A refusal to guess, not a failure.
- The buildkit EROFS condition from SG-111 still holds; used `DOCKER_BUILDKIT=0` (classic builder).
- No privileged operation was denied; nothing was left unanswered.

Receipt (notes ref)
-------------------
Work pushed to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no
`{{RECEIPT_CMD}}`. Note added on WORK_HEAD; notes ref pushed and read back from a MAPPED fetch. Pasted
executed output:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports-sg114-fetched show 7c16635e85197c436119121d409f6f86974855ed
Dispatch-ID: SG-114 | Report: docs/worklogs/SG-114_report.md | Work-HEAD: 7c16635e85197c436119121d409f6f86974855ed
```

Full raw transcript (precheck, add, push, mapped fetch, show) is in `SG-114_verify.log` -> `RECEIPT NOTE
VERIFY`. The final tip (this report/receipt commit) is dual-annotated with the same note (SG-092
inoculation). final line: `note=yes`.

Three UNCLEAR lines
-------------------
- FIRST READ: whether the UI should read the relation list from the flag-gated list route (mirroring
  SG-113's LocationsSection, which is how the section detects dormancy) or from the asset-detail
  `relations[]` key. I chose the list route as the data source and kept the asset-detail `relations[]` as
  the independently-tested reader half (`PG-SC-02`); both are in acceptance.
- DURING EXECUTION: whether `related_to`, though symmetric in intent, should dedupe the reverse pair
  `B->A` against `A->B`. The packet fixes composite uniqueness as `(from, to, type)`, so I stored exactly
  that and did not dedupe the reverse; stated rather than silently widened.
- REMAINING: the model id (CLI default, unreadable from argv/metadata); whether relation types need an
  audit trail (none specified; no audit row is written); and whether a future slice should expose
  `related_to` as a single symmetric edge in the UI rather than two directed rows.

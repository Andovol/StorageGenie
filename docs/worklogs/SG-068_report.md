# SG-068 report — saved searches: named filter sets persisted per household

- **Dispatch-ID:** SG-068 — `opencode`, effort `medium` (`--variant medium` on the process argv).
- **Contract echo:** recorded `0.28.2` == published `0.28.2`. Source path (read in-slice):
  `/home/andrei/storagegenie-contract/VERSION` = `0.28.2`; `/home/andrei/storagegenie-contract/RULES.sha256`
  = `a66aa4313d62cebff8b44f10299928288e05dc4d7c45f4f4e83e0bbd954c131d  RULES.md`; contract git `b495b59`
  ("Contract payload 0.28.2"). This matches the AGENTS.md recorded echo.
- **BASE:** packet requested `origin/automation`; the ref resolved to `ee78d3072e0422ca6c8e613ce2bcf531745bd699`.
- **WORK_HEAD:** `8747cd24abe59ecf60a46c6faa34f63ddc8c92e5` (the work commit; this report's
  docs-only follow-up sits on top, so the final pushed `automation` tip is one commit later).
- **Model:** `unknown` — no model id appears in the process argv (`opencode run --auto --dir
  /home/andrei/StorageGenie --variant medium …`); the CLI default is the model per `CODERS.md`.
  Effort `medium` is read from that same argv. Not read from any identity line.
- **Spend:** real `$0.000000` (zero provider calls).
- **Autonomy:** L3 stage (D83). **No deploy** (`PG-PR-04`). **Production migrate executed** under D85.

## 1. Starting tree and premises (quoted reads)

- `git status` clean, branch `automation` tracking `origin/automation`, remote
  `git@github.com:Andovol/StorageGenie.git`. HEAD `ee78d3072e0422ca6c8e613ce2bcf531745bd699`
  (`D85/D86 + decision-labeling directive; SG-068 authorized + dispatch-ready`).
- Filter surface the saved search must capture — `backend/app/api/v1/assets.py:192-200`:
  `def list_assets(household_id, q, asset_type, status, has_evidence, cursor, limit)` and the shared
  `_apply_asset_filters` (`:120-154`) applying `q` (FTS MATCH), `asset_type`, `status`, `has_evidence`.
  Mirrored exactly: the whitelist is those four keys.
- Catalog state to set on apply — `frontend/src/routes/CatalogPage.tsx:28-33`
  (`qRaw`, `q` debounced, `category`, `cursor`) and the reset effect `:81-85`
  (`useEffect(() => { setAllItems([]); setCursor(undefined); }, [effectiveHousehold, q, category])`).
  Applying a saved search sets `qRaw` + `category`, so the existing single `GET /v1/assets` path re-queries —
  no second query language.
- `hooks/useAssets.ts:5-25` (post-SG-064 shape: household/q/asset_type/status/cursor) — unchanged by this
  slice except for the three new saved-search hooks.
- **D85 present** (`STATE.md:214`): "SG-068 production migration AUTHORISED on its packet alone (G-K3) —
  one new `saved_search` table, `alembic upgrade head` on the production SQLite, no data writes". The packet
  (`docs/packets/SG-068-saved-searches.md:43`) carries the same. **Word present → migrate GO.**
- `EXPECTED_TABLES` static registry read live (`backend/tests/test_postgres_dialect.py:34-52`); extended
  with `saved_search`, giving 18 tables:
  `asset, asset_evidence, assertion, audit_event, candidate, evidence, guardrail_event, household,
  idempotency_key, job, job_step, observation, planning_suggestion, provider_call, review_task,
  saved_search, source_attribution, user`.

**Premise correction (a finding, not an obstacle):** the packet's standing line said "head-relative
downgrade assertions must be updated". The mandated grep (`downgrade` across `backend/tests` and
`backend/alembic`) found every downgrade target **explicitly named** (`test_candidates.py:163`
`20260908_sg013_observation`; `test_foundations.py:81` `20260912_sg025_provider_call`; `test_search.py:247`
`20260908_sg014_candidate`; `test_signals.py:229` `20260908_sg013_observation`; `test_sg048_name_optional.py:22`
`PREVIOUS_REVISION=20260914_sg035_foundations`), and the one head lookup is dynamic
(`test_export.py:114` `ScriptDirectory(...).get_current_head()`; `exports.py:29` `ALEMBIC_HEAD = _alembic_head()`).
The single candidate, `test_sg048_name_optional.py:101`, asserts the version stays at **the blocked
revision** (`20260916_sg048_name_optional`), which is still correct after appending a newer head — I verified
this by first "fixing" it to the new head and watching it FAIL (`1 failed, 19 passed`), then reverting it.
No head-relative assertion needed updating; `test_sg048_name_optional.py` is byte-unchanged in the diff.

## 2. What shipped

### G1 — backend table + API
- `backend/app/models/saved_search.py` (new): `saved_search(id, household_id FK→household.id ON DELETE
  CASCADE indexed, name String(80), query_json Text, created_at, updated_at)` (the two timestamps come from
  the project's `TimestampMixin`; the packet named `created_at`, the mixin's `updated_at` is the established
  table shape).
- `backend/alembic/versions/20260917_sg068_saved_search.py` (new): revision
  `20260917_sg068_saved_search`, `down_revision = 20260916_sg048_name_optional` (date-prefix `max+1` per the
  existing convention `20260908_* → … → 20260916_* → 20260917_*`), **idempotent-add**
  (`if inspector.has_table("saved_search"): return`), **NO ownership statements** — `AGENTS.md` names no
  owning role for the SQLite path, and the 0.28.2 `lang/python.md` rule says such a migration adds none.
- `backend/app/api/v1/assets.py`: `POST /v1/saved-searches` (`household_id` query, body `{name, query}`),
  `GET /v1/saved-searches?household_id=` (newest first), `DELETE /v1/saved-searches/{id}?household_id=`
  (missing 404, cross-household 403). `PATCH` rename SKIP (noted future).
  - **Router decision:** appended to `assets.py`, *not* a new `saved_searches.py` router: mounting a new
    router requires `backend/app/main.py`, which is outside the scope ceiling. `assets.py` is explicitly allowed.
- `backend/app/schemas/saved_search.py` (new): `SavedSearchQuery` with `extra="forbid"` (unknown key → 422,
  named), `SavedSearchCreate` with the named caps `SAVED_SEARCH_NAME_MAX_LENGTH = 80` and
  `SAVED_SEARCH_QUERY_MAX_BYTES = 2048` (named settings with a visible 422, not silent — `G-A8`/`PG-SC-06`).
  The schema split earns its place by holding the caps without touching `config.py` (off-ceiling).
  `has_evidence: bool | None` and `status: str | None` mirror exactly what `list_assets` accepts today
  (FastAPI bool coercion; free status string) — an invalid stored filter fails loudly at **save** time.
  - **Duplicate-name decision:** a pre-check on `lower(name)` scoped to the household → **409**
    (case-insensitive). Chosen over a functional unique index; the only cost is a race window between read
    and insert, reported rather than hidden.
- `backend/tests/test_postgres_dialect.py`: `SavedSearch` imported and `"saved_search"` added to
  `EXPECTED_TABLES` (registry walked live).
- `backend/tests/test_saved_searches.py` (new): 10 tests — CRUD round-trip, **PG-SC-02 working round-trip**
  (manual URL vs read-back URL, bodies equal), **household isolation** (invisible + undeletable), whitelist
  unknown key + invalid bool type 422, name/query caps 422, case-insensitive duplicate 409 + cross-household
  same-name 201, empty-state 200, DELETE missing 404, Alembic upgrade/downgrade/upgrade, stored JSON parsed.

### G2 — frontend save + apply
- `frontend/src/api/types.ts`: `SavedSearchQuery`, `SavedSearch`, `SavedSearchListResponse`.
- `frontend/src/hooks/useAssets.ts`: `useSavedSearches`, `useSaveSearch`, `useDeleteSavedSearch`. POST uses
  `apiPost`; DELETE is issued with raw `fetch` + `buildUrl` because `api/client.ts` has no `apiDelete` and
  `client.ts` is **off-ceiling** (reason recorded in a code comment).
- `frontend/src/components/shell/CatalogToolbar.tsx`: "Save search" button (disabled while
  `activeFilters.length === 0`), "Saved searches" `<select>` (auto-selected option = name), a "Delete" button
  for the selected set, filter labels for the selected set (`q: …`, `type: …`, `status: …`, `evidence: …`),
  and a muted `None yet` span for the empty list.
- `frontend/src/routes/CatalogPage.tsx`: selection state, `window.prompt` → `POST` (name trimmed; only the
  active `q`/`category` are captured), apply sets `qRaw` + `category` (reuses the existing reset effect →
  the one and only `GET /v1/assets` path), delete clears selection, household change resets selection.
- `frontend/src/components/shell/shell.test.tsx`: mock extended (`apiPost`, `buildUrl`,
  `/v1/saved-searches` branch) and 6 new tests: save gating + POST payload, dropdown apply sets the same
  state and re-queries with `q`/`asset_type`, a name `O'Brien <derp>` round-trips and renders as TEXT
  (`document.querySelector("derp") === null`), muted `None yet`, DELETE with method and id, household switch
  clears selection. Suite 14 → 20 tests in the file.

## 3. Migration and production database

- **New head named:** `20260917_sg068_saved_search`.
- **Scratch proof (raw in `SG-068_verify.log`):** before upgrade `select from saved_search` → `FAIL
  (expected): OperationalError: no such table: saved_search`; `upgrade head` → rows 0, version
  `20260917_sg068_saved_search`; `downgrade 20260916_sg048_name_optional` → table gone, version
  `20260916_sg048_name_optional`; re-`upgrade head` → rows 0, version back.
- **Production (D85, live SQLite `/home/andrei/StorageGenie/data/db/storagegenie.db`):**
  `PRE  version 20260916_sg048_name_optional, has saved_search: False` →
  `alembic upgrade head` logged `Running upgrade 20260916_sg048_name_optional -> 20260917_sg068_saved_search` →
  `POST version 20260917_sg068_saved_search (head), has saved_search: True, saved_search count: 0`,
  columns `[id, household_id, name, query_json, created_at, updated_at]`, index
  `ix_saved_search_household_id`. Row counts unchanged: `household 1, asset 1, evidence 2, assertion 3,
  provider_call 6` (no data writes). Health after: `{"status":"ok","db":"ok","storage":"ok"}`.
- **Restart: none. Deploy: none.** The running container serves the pre-SG-068 image; the new table is inert
  until the next owner-gated deploy slice.

## 4. Acceptance criteria

- Starting tree quoted, clean. Premises re-verified with quoted reads (§1).
- Migration: new head named; upgrade+downgrade proven on scratch; **no head-relative assertion update was
  needed** (grep + reproduced failure of the unnecessary "fix", §1); production migrated on the D85 word.
- Round-trip: save → the dropdown lists it (name verbatim, filter labels) → selecting it issues the same
  request state and re-queries (`q`/`asset_type` asserted) → DELETE works. Backend proof: applied URL has
  the same parameter multiset as the manual URL and identical response body; isolation 403/absent.
  *(Raw URL strings differ only in parameter order — `q,asset_type,status` vs sorted `asset_type,q,status`;
  the multisets and bodies are equal, and in the UI both paths go through `useAssets`, so the order is
  identical by construction. Reported rather than papered over.)*
- Whitelist + caps: unknown key → 422 naming `bogus_key` (quoted); name 81 chars → 422; query 3000 bytes →
  422 containing `2048` (quoted); duplicate → 409 (quoted), cross-household same name → 201.
- Suite + lint + build green (only the 2 base reds); no-deploy reason stated; dep list unchanged; no ignored
  file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass (each test invokes the real endpoint
  / real migration; see §5).

## 5. Gates (derived set)

| Gate | Result | Base |
|---|---|---|
| backend `pytest` | **264 passed**, 2 failed = the same base decoder-env reds (`test_signals::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier`, `test_signals::test_ocr_has_text_boxes_and_mean_confidence`) | 254 passed + 2 reds |
| backend `ruff check .` | `All checks passed!` | clean |
| backend `mypy app` | `Found 41 errors in 9 files (checked 71)` — **delta 0**; the 16 `assets.py` lines are the same pre-existing errors shifted by the insertion offset (diff shows only `→` line moves, `+0 added, -0 removed`); new files 0 errors | 41 / 9 files (69) |
| frontend `vitest` | **158 passed / 21 files** | 152 / 21 |
| frontend `tsc && vite build` | green (`✓ built`) | green |
| frontend `eslint src` | green | green |
| derived hit files | backend `test_saved_searches.py` 10, `test_postgres_dialect.py` 1; frontend `shell.test.tsx` 20 | — |
| intuition extra | `catalog.test.tsx` (renders `CatalogPage`; not a symbol hit) 32 — green | — |

All commands ran under timeouts (suite 600s class, build 450s, ordinary 120s); none was killed or hung.

## 6. Findings, corrections, and reported scope

1. **Head-relative premise did not hold** — see §1; corrected with evidence, no source change needed.
2. **Out-of-ceiling plumbing edits (reported, minimal, reason each):**
   - `backend/app/models/__init__.py` — register `SavedSearch`; without it `Base.metadata` (and therefore
     `test_postgres_dialect` and every `Base.metadata.create_all` test) never sees the table.
   - `frontend/src/components/shell/AppShell.tsx` — 5 prop pass-throughs; the ceiling names
     `CatalogToolbar.tsx`, but `CatalogToolbar` is rendered *by* `AppShell`, so the named edit cannot reach
     the toolbar without this. No logic changed.
3. **Router decision** (§2): endpoints live in `assets.py` to avoid touching the off-ceiling mount point.
4. **Duplicate-name race window** reported (pre-check, not a DB constraint). `PATCH` rename skipped as
   instructed.
5. **Transport observation (outside the slice):** the on-host dispatch wrapper
   `/opt/storagegenie-dispatch/dispatch_coder.sh` whitelists only `grok|codex` (`parse`/`model`/`effort`
   reject anything else), so it cannot launch the SELECTED `opencode` coder; this session was launched
   directly as `opencode run --auto --dir /home/andrei/StorageGenie --variant medium …`, not through the
   `job_spawn` lane. Reported, not acted on.
6. **`query_json` size cap** is byte-length of the stored JSON text (2048) — a named setting in
   `schemas/saved_search.py` (config.py is off-ceiling).
7. No new dependencies (`pyproject.toml`, `requirements.lock`, `package.json`, `package-lock.json` all
   untouched). Secret scan on all touched/new files: no key/password/private-key patterns. No ignored file
   staged. Nothing pushed to `storagegenie-evidence`.

## 7. Receipt (notes ref `refs/notes/storagegenie-coder-reports`)

Note added on `WORK_HEAD = 8747cd24abe59ecf60a46c6faa34f63ddc8c92e5`, pushed, then fetched into a MAPPED
local ref and verified. Executed output pasted verbatim:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-068 | Report: docs/worklogs/SG-068_report.md | Work-HEAD: 8747cd24abe59ecf60a46c6faa34f63ddc8c92e5" 8747cd24abe59ecf60a46c6faa34f63ddc8c92e5
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   f3966ee..cd21654  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-verify
From github.com:Andovol/StorageGenie
   8fbbc0b..cd21654  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-verify

$ git notes --ref=refs/notes/storagegenie-coder-reports-verify list | grep 8747cd24abe59ecf60a46c6faa34f63ddc8c92e5
621a11628e02b5a7d2e6f70e5c6deebf9ea64537 8747cd24abe59ecf60a46c6faa34f63ddc8c92e5

$ git notes --ref=refs/notes/storagegenie-coder-reports-verify show 8747cd24abe59ecf60a46c6faa34f63ddc8c92e5
Dispatch-ID: SG-068 | Report: docs/worklogs/SG-068_report.md | Work-HEAD: 8747cd24abe59ecf60a46c6faa34f63ddc8c92e5

$ git notes --ref=refs/notes/storagegenie-coder-reports-verify show 8747cd24abe59ecf60a46c6faa34f63ddc8c92e5 | grep -c "Dispatch-ID: SG-068"
1
```

The fetched ref (not the local write) is what proves the push landed; first line carries both
`Dispatch-ID:` and `Report:`. `note=yes`.

## 8. UNCLEAR

- **FIRST READ:** I read "PRODUCTION MIGRATE AUTHORIZED … one new table, no data writes" as authorizing the
  real `alembic upgrade head` on `/home/andrei/StorageGenie/data/db/storagegenie.db` from the host (the
  container image predates this migration, so `docker compose exec … alembic` would not see it) — I executed
  that and verified no other row counts changed.
- **DURING EXECUTION:** the applied-vs-manual raw query strings differ only in parameter order while the
  parameter multisets and bodies are identical; I treated that as satisfying "the SAME query" and said so
  explicitly rather than reordering to make the demo look cleaner.
- **REMAINING:** the saved-search UI is not reachable on the live public entry until an owner-gated
  rebuild/deploy rider runs (no deploy in this packet); the duplicate-name race window and the off-ceiling
  `AppShell.tsx`/`models/__init__.py` plumbing are recorded for the next slice.

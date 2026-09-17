SG-064 report — catalog facets + server-side category filter + evidence-badge truth

coder: opencode · effort: **medium** (process args `--variant medium`) · MODEL: **unknown** (no `--model` on
argv; CLI default omitted per policy — never read from a system-prompt identity line)
contract echo: **0.28.2** · source path: `/home/andrei/storagegenie-contract/VERSION` (repo `.rules-cache/`
is absent on this box) · spend **real $0.000000** vs $0 bound (zero provider calls)

Work dir: `/home/andrei/StorageGenie` · origin: `git@github.com:Andovol/StorageGenie.git`
`BASE` ref requested: `origin/automation` · `BASE` resolved: `146b7b56098e70fdbb65fe184574015daea08278`
`WORK_HEAD`: `4060bb00fcb70a79b7c9db879112085d27834cf4`
final branch head after integrating the Architect's `5f95810` (D84): merge `1e3603f` (no rebase — keeps
`WORK_HEAD` and its receipt note reachable).

Starting tree: clean (`git status --porcelain` empty) — dirt would have been a STOP; none.

## G0 — THINK-TAG repair (SG-062 audit finding)

`backend/app/services/providers/opencode_go.py` `strip_single_think` had three SG-062-mangled lines (docstring,
guard, raise message) with **no bytes 60/62**. Repaired with a char-code-constructed routine
(`chr(96)+chr(32)+'thinking'` → `` ` ``+`chr(60)`+`think`+`chr(62)`+`` ` ``, and the `" thinking"` / `stray  thinking`
variants), asserting replacement count == 1 per pattern. Post-edit char-code probe: lines 92/95/96 each
`60_present=True 62_present=True`. `git log` confirms the mangle entered at `c71bad2` (correct at `c71bad2~1`).

New mangler-immune pin `tests/test_opencode_go.py::test_guard_stray_think_raises_and_single_block_strips_charcode_built`
builds the payload from `chr(60)+"think"+chr(62)`. Raw FAIL→PASS in the verify log: on the mangled source the
stray-tag leg **DID NOT RAISE ProviderError**; on the repaired source it passes (16 passed in the file).

## G1 — facets endpoint

New `GET /v1/assets/facets` (`backend/app/api/v1/assets.py`), declared before `/assets/{asset_id}`.
Response shape:
```
{"asset_type": {..sorted keys..}, "status": {..}, "has_evidence": {"with": N, "without": M}}
```
Each dimension omits its OWN filter; keys sorted deterministically; counts are `int`s. Shared base filters are
factored into `_apply_asset_filters` (also used by `list_assets`), so the facet base equals the list base
(same `ensure_asset_fts` + `sanitize_fts_query` for `q`). `has_evidence` uses an `Asset.id.in_(asset_evidence)`
subquery, mirroring the list path.

- `PG-SC-09` discriminator: `test_facets_counts_each_dimension_without_its_own_filter` asserts that requesting
  `asset_type=appliance` leaves the `asset_type` map **unchanged** (`{"appliance":2,"furniture":2,"storage":1}`)
  and `!= {"appliance":2}` — the with-all-filters world is named and excluded.
- `q` narrowing: `test_facets_q_narrows_the_shared_base` (`q=Kitchen` → 2 total).
- `PG-SC-07` zero-population: `test_facets_empty_household_is_empty_maps_not_error` → `200` and
  `{"asset_type":{},"status":{},"has_evidence":{}}`. `has_evidence` carries `with`/`without` only when at
  least one row is reachable (fixed binary axis otherwise meaningless) — this is the design call behind the
  packet's "empty maps" phrasing.
- Smallest real population: seed household `01a0a029-1477-7ca0-b200-bce78a96c679` → 2 users + `Toothpaste`
  (`asset_type='unknown'`, `PG-SC-12` real record path via the SG-048 verify log).
- Dialect: `test_facets_aggregate_statements_compile_for_postgresql` compiles the real facet statements
  (`count(*)` + `group_by`, and the `asset_evidence` subquery) under the PostgreSQL offline dialect and asserts
  no `strftime`. **F-SG064-1:** `test_postgres_dialect.py` is metadata-DDL-only — verified and quoted; it was
  run green and cannot assert endpoint SQL, so the endpoint assertion lives in the new facets test.

## G2 — server-side category filter + pills

- `useAssets` now receives `asset_type` (the raw facet KEY) for any non-`All` pill; `CatalogPage` passes
  `category === "All" ? undefined : category`.
- Pills are derived from the real `asset_type` facet map: `All (N)` + `key (N)` per key, with `All` = sum of
  the asset_type map (unfiltered-with-`q`). Empty household → `All (0)`. No `types/product.ts` change and no
  `AppShell.tsx` change (labels are built in `CatalogPage` and ride the existing `categories: string[]` prop).
- `filterAndSortCatalog` was replaced by `sortCatalog` (ordering only). The client `q` needle re-filter was
  **REMOVED** — the FTS index covers `display_name` (`asset_fts(asset_id UNINDEXED, display_name,
  household_id UNINDEXED)` from `fts.py`), the same field `item.name` came from, so there is no divergence.
  The client category item-match was **REMOVED** too; keeping it would have dropped `asset_type='unknown'`
  rows (mapped to `Uncategorized`). Server is the single authority.
- Reset effect now includes `category` alongside `effectiveHousehold` and `q`; accumulation otherwise
  unchanged.
- Test edits (allowed by the ceiling, each with reason): `shell.test.tsx` — import/describe renamed to
  `sortCatalog`, mock honors `asset_type`/`q`, pill selectors use counted labels, added the server-param
  assertion; `catalog.test.tsx` — added the planned `/v1/assets/facets` mock shape (its 482-era mock shapes
  are expectations) and the badge test.

## G3 — evidence-badge establishment

Verdict: **never served**. Pre-change trace (quoted): list serializer (`assets.py:172-189` pre-edit) sent
`id/household/display_name/asset_type/status/quantity/unit/condition/version/created_at` — no `evidence`;
`CatalogPage.tsx:83` `const firstEvidence = asset.evidence?.[0];` therefore always `undefined`; `ProductCard`
`cardMedia` (`ProductCard.tsx:60-65`) only builds a thumbnail from `cutoutUrl`/`sceneUrl`/`evidenceId`, so the
evidence-backed thumbnail could NEVER render on the list path.

Fix: list serializer now sends **`evidence_ids`** (the field the card reads), batched in one query per page.
Readback trace (`PG-SC-02`): backend `GET /v1/assets` row → `CatalogPage.visibleItems` reads
`asset.evidence_ids?.[0]` → `ProductCard` renders `thumbUrl` (`/v1/evidence/{id}/thumb/256`). Raw FAIL→PASS:
on the base serializer the new real-HTTP test fails with `KeyError: 'evidence_ids'`; on the fixed serializer it
passes. Frontend end-to-end readback test added in `catalog.test.tsx`.

Scope note: `frontend/src/api/types.ts` was touched only to add `evidence_ids?: string[]` (G3-required), and
`frontend/src/components/catalog/ProductGrid.tsx` was NOT touched (not needed).

## G4 — suite + lint + build (NO deploy)

Derived test set (a hit is a FILE; grep of the HIT-tree for the touched symbols/fields `/v1/assets`,
`evidence_ids`, `facets`, `strip_single_think`, `CatalogPage`, `CatalogToolbar`, `sortCatalog`, `useFacets`):
- backend: `test_assets_crud.py`, `test_asset_facets.py` (new), `test_search.py`, `test_postgres_dialect.py`,
  `test_opencode_go.py`, plus the e2e files that hit the list endpoint (`test_phase0/1/3_e2e.py`,
  `test_export.py`).
- frontend: `shell.test.tsx`, `catalog.test.tsx`.
Intuition superset (run anyway): the full backend + frontend suites, so every hit node ran.

Results (BASE `146b7b5` → work):
| Gate | BASE | Work | Notes |
|---|---|---|---|
| backend pytest | 2 failed / **248 passed** (16.77s) | 2 failed / **254 passed** (16.88s) | same 2 `test_signals.py` decoder env reds (`test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier`, `test_ocr_has_text_boxes_and_mean_confidence`) — base-proven |
| ruff | All checks passed | All checks passed | |
| mypy | 41 errors / 9 files | **41 errors / 9 files** | delta **0** |
| frontend vitest | 21 files / **152 passed** | 21 files / **152 passed** | |
| eslint | clean | clean | |
| frontend build | built | built | `tsc && vite build` |

**NO DEPLOY (`PG-PR-04`):** the change is user-visible in the API/UI, but proving it needs a rebuild; deploy is
a separate owner-gated slice after this returns green. Nothing production-effect is claimed beyond the gates.
Full-sweep WAIVED per `PG-DP-02`; substitutes named: backend/frontend suites + lint + build + the new endpoint
tests on the real HTTP path (TestClient + temp SQLite).

Safety: secret scan zero; no ignored file staged; nothing pushed to `storagegenie-evidence`; prod DB untouched
(scratch temp SQLite only); no migration (`alembic/` clean); dep list unchanged
(`package.json`/`pyproject.toml`/`requirements.lock` untouched); no vacuous pass (every gate invokes the real
function/endpoint and the new tests are seen failing before passing).

## Findings / disagreements (not hidden)

- F-SG064-1: `test_postgres_dialect.py` is metadata-DDL-only; the endpoint dialect assertion had to live in the
  new facets test (real aggregate SQL compiled for PostgreSQL).
- F-SG064-2: the seed household's real `asset_type` is `unknown`, so "UI follows the data" shows an `unknown`
  pill, not a DQ1 label.
- F-SG064-3: the packet's line cites matched the live pre-edit file.
- Design call: zero-population `has_evidence` is `{}` (not `{"with":0,"without":0}`) to satisfy the literal
  "empty maps" acceptance; flagged here in case the reviewer intended the fixed axis to persist.

## Receipt (executed; output pasted verbatim)

Note added on `WORK_HEAD` (`refs/notes/storagegenie-coder-reports`), first line carries both `Dispatch-ID:`
and `Report:` (`CO-97`):

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-064 | Report: docs/worklogs/SG-064_report.md | Work-HEAD: 4060bb00fcb70a79b7c9db879112085d27834cf4" 4060bb0
$ git notes --ref=refs/notes/storagegenie-coder-reports show 4060bb0
Dispatch-ID: SG-064 | Report: docs/worklogs/SG-064_report.md | Work-HEAD: 4060bb00fcb70a79b7c9db879112085d27834cf4
```

Pushed (300s bound) and fetched into the MAPPED local name (a bare refspec fetch only rewrites `FETCH_HEAD`):

```
$ git push origin refs/notes/storagegenie-coder-reports
   362bf0d..8fbbc0b  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-verify
   9a641c0..8fbbc0b  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-verify
```

Content grep on the FETCHED ref (log `--grep` does not match note bodies; the list is `note-blob` then
annotated-commit):

```
4060bb00fcb70a79b7c9db879112085d27834cf4 -> Dispatch-ID: SG-064 | Report: docs/worklogs/SG-064_report.md | Work-HEAD: 4060bb00fcb70a79b7c9db879112085d27834cf4
```

`git notes show` on `WORK_HEAD`, fetched ref:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports-verify show 4060bb00fcb70a79b7c9db879112085d27834cf4
Dispatch-ID: SG-064 | Report: docs/worklogs/SG-064_report.md | Work-HEAD: 4060bb00fcb70a79b7c9db879112085d27834cf4
```

`automation` push: `5f95810..1e3603f` (fast-forward of the integration merge). No push to
`storagegenie-evidence`; no `{{RECEIPT_CMD}}` (out of scope this slice).

**note=yes**

## UNCLEAR

- FIRST READ: whether "pills render `Label (N)`" meant the DQ1 labels or the raw `asset_type` keys; F-SG064-2
  (`unknown` in the seed) and the packet's own "static pills do not match the real type population" point to
  the raw keys, so the raw keys are used.
- DURING EXECUTION: the zero-population `has_evidence` shape — "empty maps" vs the fixed `with`/`without` axis;
  chose all-empty maps for the empty base and documented it.
- REMAINING: `test_postgres_dialect.py` does not assert endpoint SQL (F-SG064-1); a future dialect slice may
  want to register the facets statements there, but that file was outside the "as-is" intent. No deploy was
  performed (owner-gated follow-on).

# SG-048 — name-optional capture: nullable `display_name` + photo-derived default + form

**Dispatch-ID:** SG-048 · **Coder:** opencode · **Effort:** medium (read from process args: `/proc/888531: opencode run --auto --dir /home/andrei/StorageGenie --variant medium …`) · **Model:** `unknown` (no model id on argv; CLI default per policy — not guessed from any identity line).
**Contract:** 0.27.0. **Spend:** `$0` metered (AI OFF, no provider calls).
**Work dir:** `/home/andrei/StorageGenie` · **origin:** `git@github.com:Andovol/StorageGenie.git`.
**DATABASE:** production SQLite `sqlite:////data/db/storagegenie.db` on the host for the MIGRATION ONLY (authority D72); scratch temp SQLite for every test. No prod credentials in the test layer.

- **BASE REF requested:** `origin/automation`; **resolved commit:** `2a0c572212c91cbd2c98f0bf386bb8f3af977140` (`SG-048 packet (S2 name-optional migration, L3/D74 chain)`).
- **WORK_HEAD:** the commit carrying these three worklogs — stated in the delivery message (it cannot be stated inside a file that is itself part of that commit, same as SG-053/SG-054). The receipt note is attached to it LAST; no commit follows.
- **Slice wall-clock:** start `2026-09-16T19:48:09Z` (live clock); report frozen `2026-09-16T19:59Z` (~660 s vs 1500 s early-close / 2400 s overall cap).

## 1. Starting tree (clean expected; dirt = STOP first)

```
$ git status --porcelain=v1 -b
## automation...origin/automation
$ git rev-parse HEAD ; git rev-parse origin/automation
2a0c572212c91cbd2c98f0bf386bb8f3af977140
2a0c572212c91cbd2c98f0bf386bb8f3af977140
```
Clean and level: no STOP. Final tree = 11 modified product/test files + 1 new migration + 1 new backend test file + 3 worklogs. **Nothing pushed to `storagegenie-evidence`.**

## 2. Premises re-verified in-slice (quoted reads, `PG-IC-09`)

- **`models/asset.py:15`** — `display_name: Mapped[str] = mapped_column(String(300), nullable=False)`. **Matches.**
- **`schemas/asset.py:6-13`** — `AssetCreate.display_name: str`; `:36-49` `AssetOut.display_name: str`. **Matches.**
- **`asset_service.py:18-39`** — `Asset(..., display_name=payload["display_name"], ...)` → `KeyError` when absent; assertion loop `source_type="user"`, `review_state="accepted"` for supplied fields. **Matches.**
- **`candidates.py:159-165`** — `_deterministic_display_name` = `Path(evidence.original_filename).stem or evidence.original_filename`, `"Imported item"` when the list is empty / the row is missing. Reused by import (no hunk). **Matches.**
- **`AssetForm.tsx:66-71`** refusal + **`:110-121`** `required` input, label `Display name *`. **Matches.**
- **`0201cf10c56c:41`** — `sa.Column('display_name', sa.String(length=300), nullable=False)`. **Matches.**
- **Head revision** `20260914_sg035_foundations`; `down_revision` `20260912_sg025_provider_call`. Verified by the revision chain, `alembic current` on the scratch DB, and the live DB. **Matches.**
- **`api/types.ts:29-44`** — `Asset.display_name: string`. **Matches.**

## 3. Reader enumeration (`PG-SC-02`) — write path + ALL readers, with the diff vs the packet

**Writers:** `asset_service.create_asset` (the API create path), `update_asset` (PATCH), `candidates._create_asset_for_candidate` (import path, untouched, still supplies a name). **New migration** changes the schema.

**Production readers of `asset.display_name` / `AssetOut.display_name`:**

| Reader | Null-safe? | Evidence |
|---|---|---|
| `api/v1/assets.py:104` `_asset_to_dict` | yes — passes through | returns `asset.display_name`; the API test GETs a NULL and reads `null` |
| `api/v1/assets.py:177` list serializer | yes — passes through | same shape as above |
| `api/v1/exports.py:58` manifest value | yes — JSON `null` | read-only context, no hunk |
| `fts.py:34-74` FTS5 triggers over the external-content view | yes — SQLite FTS5 stores NULL, indexes no tokens, neighbours intact | `test_nameless_asset_neither_errors_nor_corrupts_fts` |
| `planning/service.py:114,153` (`order_by`, `"label": display_name`) | **packet omitted** — no crash, NULL passes through | `test_catalog_builders_tolerate_null_name`; see **F-SG048-2** |
| `chat/service.py:147,179` (`order_by`, `"label": display_name`) | **packet omitted** — no crash, NULL passes through | same test; see **F-SG048-2** |
| `types/product.ts:79` `assetToProductItem` name | fixed → `UNTITLED_ASSET_NAME` | `product.test.ts` |
| `api/types.ts:32` `Asset.display_name` | fixed → `string \| null` | typecheck/build |
| `components/AssetCard.tsx:32,55` alt + text | fixed → constant | `AssetCard.test.tsx` |
| `routes/AssetDetailPage.tsx:65` h1, `:68` edit-name init | fixed → constant / `""` | build + typecheck |
| `components/shell/ItemInspectorDrawer.tsx:59,85,90,170,176,254` | fixed → constant / `""` | `drawer.test.tsx` |

**Not readers of `Asset.display_name`:** `dedup.py:95` `_display_name` reads `Evidence.original_filename`; `mockProducts.ts:113` builds fixture objects; `ReviewPage.tsx:10` reads a `Candidate` field. Named so they are excluded by rule, not by omission.

**Diff vs the packet's G3 expectation:** the packet listed the frontend readers, `exports.py`, and the FTS triggers. It **did not list** `planning/service.py` and `chat/service.py`, both of which read `asset.display_name` into an AI prompt catalog (`"label"`). Because those files are **outside the scope ceiling**, no hunk was made; they are proven pass-through/no-crash and reported as **F-SG048-2** with a destination.

## 4. G1 — migration `backend/alembic/versions/20260916_sg048_name_optional.py` (new)

`down_revision = "20260914_sg035_foundations"`. SQLite has no `ALTER COLUMN`, so the change is a `batch_alter_table` recreate (the repo's first SQLite alter; there was no prior pattern — `grep batch_alter_table` = 0 hits). Two tree-forced additions:

1. **FTS objects must be dropped/reinstalled (F-SG048-1).** The external-content view `asset_fts_content` names `asset`; SQLite validates every view when the batch rename runs, so `upgrade head` otherwise fails with `sqlite3.OperationalError: error in view asset_fts_content: no such table: main.asset`. The migration drops the three triggers + virtual table + view, recreates the table, then `install_asset_fts(..., rebuild=True)` (existing helper, same pattern as `20260908_sg017_fts.py`).
2. **Downgrade fails closed.** A nameless row present at downgrade time raises `RuntimeError` (`unable to restore NOT NULL … no silent data drop`) **before** any DDL; `alembic_version` stays at head and the row survives (proven).

Nullability is observed with `PRAGMA table_info(asset)` both directions; one nameless row is inserted after a full-chain upgrade and read back `NULL`; the downgrade refusal is asserted. **`PG-SC-11` grep named hits:** `test_search.py:239,252`, `test_signals.py:227,233`, `test_candidates.py:161,165`, `test_foundations.py:65,85` use `"head"` (dynamic); `test_export.py:114` + `exports.py:23` use `get_current_head()` (dynamic); `test_foundations.py:81` downgrades to `20260912_sg025_provider_call` (intentionally not head); `[-1]` hits are list indexing. **Zero head-relative assertions needed a hunk** — the diff from the packet's implied expectation is reported.

## 5. G2 — write path (`schemas/asset.py`, `models/asset.py`, `asset_service.py`)

- `AssetCreate.display_name: str | None = None`; `AssetOut.display_name: str | None`; `models/asset.py:15` `nullable=True`.
- New `resolve_display_name(db, payload, evidence_ids) -> (name, source)`: non-blank supplied name → `("…", "user")`; blank/whitespace-only or absent + evidence → `(_deterministic_display_name(...), "deterministic")`; neither → `(None, None)`.
- Reuses `candidates._deterministic_display_name` **by import** (no cycle: `candidates` does not import `asset_service`). No duplicated namer; **no hunk in `candidates.py`**.
- Assertion rows: user name → `source_type="user"`/`review_state="accepted"` (unchanged); server name → `"deterministic"`/`"accepted"`; NULL → **no** `display_name` assertion row. Import path (`_create_asset_for_candidate`) untouched.
- `_asset_to_dict` passes `null` through (proved by test, not asserted by reading).

## 6. G3 — read path (null-safe readers, `PG-SC-02`)

Backend passthroughs unchanged (enumerated in §3). Frontend: a single display constant `UNTITLED_ASSET_NAME = "Untitled asset"` in `types/product.ts`, used by `assetToProductItem`, `AssetCard`, `AssetDetailPage`, `ItemInspectorDrawer`; editable fields init to `""` (not `null`). The constant is **display-only** — never written to the DB, never promised as AI naming (no user-facing AI text). **F-SG048-3:** the old `ItemInspectorDrawer` threw `Cannot read properties of null (reading 'trim')` on a NULL name; the fail run proves the crash and the fix removes it.

## 7. G4 — form (`AssetForm.tsx`)

- Label `Display name (optional)` + hint `Left blank, we use the photo's filename` (plain, no AI promise). `required` and the `"Display name required"` refusal removed.
- A blank name is **omitted** from the POST payload; the client never fabricates a name.
- New junk-row guard (both directions tested): nameless + photo → creates (no `display_name` key in the asserted payload); nameless + photoless → refused with `Add a photo or a display name` and no request sent; name + photo → unchanged payload shape.
- **SG-042 listener verdict:** `grep AssetForm` mounts = `routes/CapturePage.tsx:46` + tests **only**; the import modal is a separate component. The window `paste` listener stays as-is.

## 8. G5 — tests, FAIL-then-PASS, mutations (`PG-EV-01/09`)

- **Pre-change (implementation stashed, migration moved):** backend `10 failed / 187 passed` (8 new + 2 pre-existing) ; frontend `6 failed / 137 passed`. All failures are the new assertions.
- **Green:** backend `195 passed` + the same 2 pre-existing decoder reds; frontend `143 passed` / 21 files; `ruff` 0; `eslint` 0; `tsc && vite build` 0.
- **Mutations caught singly:** M1 name-resolution branch (`if evidence_ids` → `if False and evidence_ids`) → 2 failures; M2 fallback branch (`product.ts ||` → `&&`) → 2 failures; M3 migration nullability (`nullable=True` → `False` in `upgrade`) → 3 failures. All reverted; tree verified.
- **Pre-existing failures (base-cited):** at base `2a0c572`, `../venv/bin/python -m pytest -q` → `2 failed, 186 passed`; the two are `tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` and `::test_ocr_has_text_boxes_and_mean_confidence` (the documented decoder env reds). Unchanged by this slice.
- **No vacuous pass:** the full-chain test upgrades a scratch DB from base through every revision and runs the real `create_asset` for both a nameless and a named row — the same path production runs, never a hand-made schema.

## 9. G6 — live migration + deploy (authority D72; `PG-PR-04`, `PG-PR-10`)

| Fact | BEFORE | AFTER |
|---|---|---|
| `alembic_version` | `20260914_sg035_foundations` | `20260916_sg048_name_optional` |
| `display_name` notnull | `1` | `0` |
| blessed counts (household/user/asset/evidence/assertion/audit) | `1/2/1/1/3/3` | `1/2/1/1/3/3` (EQUAL) |
| Toothpaste `display_name` | `"Toothpaste"` | `"Toothpaste"` (EQUAL) |
| FTS triggers | 3 present | 3 present |
| health | `{"status":"ok","db":"ok","storage":"ok"}` | same (exact) |
| served bundle | `index-CuxlcH9v.js` | `index-GQSnPT8t.js` (CHANGED) |
| port | `127.0.0.1:8003` only | `127.0.0.1:8003` only |
| gate | `http=301` / `https=401` | `http=301` / `https=401` |

- **Zero new production rows** (`PG-EV-06`): counts are byte-identical before/after; the nameless-create path is proven only on scratch SQLite. The DB was safety-copied to `/tmp/opencode/storagegenie-before-sg048.db` (outside the repo) before the migration.
- **Sequence:** build the new image (cached base layers, no registry pulls) → `docker compose stop backend` → `docker compose run --rm --no-deps backend python -m alembic upgrade head` (the running image did not carry the new revision — see UNCLEAR) → `docker compose up -d` → idempotent re-`up -d` left the same container, `RestartCount=0`.
- **Full e2e sweep WAIVED** per `PG-DP-02` (restart-gated); substitute = the targeted checks in the table above, named here.

## 10. Guards invoked (0.27.0)

| Guard | Status |
|---|---|
| `PG-EV-01` gate-seen-failing | MET — new tests fail pre-change, pass green (raw). |
| `PG-EV-02` artifact-exists | MET — pragma output, rendered DOM, committed verify log. |
| `PG-EV-05` property-not-command | MET — "nameless+photo creates with the photo's filename", "nameless+photoless stores NULL and displays Untitled", "Toothpaste keeps its name" as test properties. |
| `PG-EV-06` live-rows | MET — zero new prod rows; nameless path on a full-chain scratch DB. |
| `PG-EV-08` before-capture | MET — before state read-only before any write. |
| `PG-EV-09` both-runs-committed | MET — pre-change + green + mutations raw in `SG-048_verify.log`. |
| `PG-SC-01` write-and-read-paths | MET — writer + all readers traced (§3). |
| `PG-SC-02` field-traced | MET — every reader enumerated; diff reported. |
| `PG-SC-05` exclude-by-rule | MET — non-readers named as excluded, not omitted. |
| `PG-SC-10` no-ignored-commit | MET — only intended files; `data/`, `.env`, caches stay ignored. |
| `PG-SC-11` end-relative-assertions | MET — every hit named (§4); zero hunks. |
| `PG-IC-01` cross-product | MET — no blanket exclusion; migration shares no condition with remediation. |
| `PG-IC-03` stop-wins | MET — downgrade-with-nameless raises before DDL; version/row intact. |
| `PG-IC-07` no-fixed-dates | MET — live clock; authoring date is metadata only. |
| `PG-IC-08` blast-radius-is-stop | MET — before counts/name matched exactly; otherwise STOP. |
| `PG-IC-09` premises-live | MET — every premise re-read live (§2). |
| `PG-PR-03` denied-is-stop | MET — no denied privileged action; build used the writable `BUILDX_CONFIG`. |
| `PG-PR-04` code-becomes-live | MET — compose rebuild+up; bundle changed. |
| `PG-PR-06` runtime-vs-budget | MET — per-leg actuals in §12. |
| `PG-PR-10` which-database-plus-grant | MET — prod SQLite migration only (D72); scratch SQLite for tests. |
| `PG-DP-02` no-sweep-in-restart-slice | MET — sweep waived; targeted checks named. |

## 11. Acceptance criteria

- [x] Starting tree quoted clean; premises re-verified with quoted reads.
- [x] Reader enumeration reported with the diff vs expectation either way; every reader null-safe by test (planning/chat no-crash; F-SG048-2).
- [x] FAIL-then-PASS honest: pre-change + green + 3 mutations raw committed; live before/after raw committed.
- [x] Suite (backend + frontend) + lint + build green; blessed counts + Toothpaste name equal; zero new prod rows; no ignored file staged; nothing to `storagegenie-evidence`; no vacuous pass.
- [ ] Secret scan: see delivery message (searched the diff for key/secret patterns; none).

## 12. Budget (actual vs cap, per leg, units)

| Leg | Actual | Cap |
|---|---|---|
| Recon + baseline | ~60 s | 120 s (ordinary) |
| Pre-change suite (backend + frontend) | 14 s + 5 s | 600 s |
| Green suite + ruff + lint + build | 13 s + 5 s + 1 s + 2 s | 600 s |
| Mutations (3) | 1.2 s / 0.6 s / 1.4 s | — |
| Host build / stop+run+up / verify | ~35 s / ~15 s / ~20 s | 900 s |
| Overall wall-clock | ~660 s | 1500 s early-close / 2400 s overall |

## 13. Receipt note

Work is pushed to `automation` with the worktree clean (`CO-55`). **No** push to `storagegenie-evidence`, **no** `{{RECEIPT_CMD}}` (this packet's M20-corrected block). A note is added on WORK_HEAD under `refs/notes/storagegenie-coder-reports`, pushed, then verified against the explicitly fetched refspec (`git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports` then `git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>`). Per the SG-053/SG-054 convention, that `show` output is pasted verbatim **in the delivery message** — it cannot live inside this file, which is itself the noted commit. `note=yes`.

## Findings

- **F-SG048-1** — SQLite batch recreate is blocked by the FTS5 external-content view `asset_fts_content`; the migration must drop and reinstall the FTS objects. Without it `upgrade head` fails (`error in view asset_fts_content`). Implemented and tested both directions.
- **F-SG048-2** — `planning/service.py:153` and `chat/service.py:179` read `asset.display_name` into `"label"`; the packet's G3 enumeration omitted them and they are outside the scope ceiling, so no hunk was made. Proven no-crash/pass-through on NULL, but a NULL label is a display-quality gap for the AI prompt catalogs. **Destination:** S3/SG-049 or a future consistency slice.
- **F-SG048-3** — the old `ItemInspectorDrawer` crashed on a NULL `display_name` (`title.trim()`); now fixed and regression-tested. The G3 reader sweep was load-bearing, not cosmetic.

## UNCLEAR

- **FIRST READ:** whether the `planning`/`chat` `"label": asset.display_name` readers are in-scope (G3 says "EVERY production reader") or out-of-scope (the ceiling says those files are a STOP). I judged them a finding rather than a STOP because they do not crash and the acceptance still holds; a ruling either way is owed.
- **DURING EXECUTION:** which image runs the migration. The packet's order ("`alembic upgrade head` … rebuild + up") implies the running container runs it, but the running image did not contain the new revision, so I built first and ran `docker compose run --rm --no-deps backend python -m alembic upgrade head`. That is a sequencing decision, not a route around a denial.
- **REMAINING:** whether the Architect wants the AI-catalog labels made null-safe (an amendment to the ceiling for `planning/service.py` + `chat/service.py`), or the gap left for a later slice.

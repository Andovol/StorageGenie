# SG-065 report — plugin-contract taxonomy: Household chemicals pilot + served taxonomy + exit-proof

- **Dispatch-ID:** SG-065 — `opencode`, effort `medium` (`--variant medium` on the process argv).
- **Model:** `unknown` — no `--model` appears in the process argv
  (`opencode run --auto --dir /home/andrei/StorageGenie --variant medium …`); the CLI default is
  the model per `CODERS.md`. Not read from any identity line.
- **Contract echo:** recorded `0.28.2` == published `0.28.2`. Source path (read in-slice):
  `/home/andrei/storagegenie-contract/VERSION` = `0.28.2`; `RULES.sha256` =
  `a66aa4313d62cebff8b44f10299928288e05dc4d7c45f4f4e83e0bbd954c131d  RULES.md`; contract git
  `b495b59`. Matches the `AGENTS.md` recorded echo.
- **Work dir:** `/home/andrei/StorageGenie` · **origin:** `git@github.com:Andovol/StorageGenie.git`
- **BASE ref:** packet requested `origin/automation`; resolved at start to
  `f999df953da54b3df778f70d8cfc63cdee1f1381`.
- **WORK_HEAD:** `3f2fd6bd95f8988316abca7ce7eafc3af1baa85d` (the work commit, rebased onto
  `c849088` after the remote advanced mid-slice; this report's docs-only follow-up sits on top).
- **Spend:** real `$0.000000` (zero provider calls).
- **Autonomy:** L3 stage (D83). **No deploy** (`PG-PR-04`). No migration. No restart.

---

## Outcome (one line)

The plugin contract is now an explicit immutable descriptor (frozen dataclasses), the Expiry
Tracker taxonomy — including the blueprint's Household chemicals pilot and Documents/other
entries — is served read-only at `GET /v1/taxonomy` and consumed by the inspector's category
dropdown, and a test-space `documents-domain` registration plus a `Base.metadata` vs
`EXPECTED_TABLES` diff prove a new domain registers with **zero new tables**; a descriptor
redefining the core field `status` is **rejected** (FAIL-then-PASS).

---

## Legs — actual vs budget (units per leg)

| Leg | Actual | Bound | Margin |
|---|---|---|---|
| Recon + premise verification (quoted reads, grep) | ~110 s | 120 s | under |
| G1–G3 backend build + new tests | ~130 s | 120 s ordinary (suite 600 s) | under |
| G2 frontend swap + test | ~60 s | 120 s | under |
| G4 backend suite + ruff + mypy | ~35 s | 600 s | under |
| G4 frontend suite + build + eslint | ~10 s | 600 s | under |
| Rebase + re-run backend gates + push/notes | ~90 s | — | under |
| **Overall** | **~7.5 min** | 1800 s | under |

No command was killed; no interactive command was run.

---

## 1. Starting tree and premises (quoted reads)

- `git status` clean, branch `automation` tracking `origin/automation`, remote
  `git@github.com:Andovol/StorageGenie.git`. Start HEAD `f999df953da54b3df778f70d8cfc63cdee1f1381`
  (`SG-069 rated 98; SG-065 packet`).
- **Registry shape confirmed** — `backend/app/plugins/registry.py` (48 lines):
  `register_plugin(plugin_id, version, implementation)` at `:27`, `get_plugin` at `:34`, built-in
  registered at import at `:46-48` with `_expiry_tracker.PLUGIN_ID`/`PLUGIN_VERSION`.
- **Expiry plugin constants confirmed** — `backend/app/plugins/expiry_tracker.py:27-28`
  `PLUGIN_ID = "expiry-tracker"`, `PLUGIN_VERSION = "1.0.0"`; `DateType` `:35-41`, `Unit` `:44-52`,
  `CATEGORIES` `:111-134`, `EXTENSION_SCHEMA` `:154-165`, `_CATEGORY_ALIASES` `:136-152`.
- **Blueprint §8/§9.1/§9.2 quoted** — `inception/…blueprint.md`: "A plugin defines: A category
  taxonomy … A behavior profile per category: notification defaults, whether opened-date tracking
  applies, whether disposal guidance applies, which chat agent (if any) handles it … **Plugins cannot
  redefine core fields** or bypass assertion/review-state validation."; Household chemicals =
  "Basic expiry only — Minimal special logic"; Documents/other = "Long-lead windows (60/30 day) …
  reminder-only".
- **Frontend category consumers enumerated** (grep `CANONICAL_CATEGORIES|toProductCategory`):
  `frontend/src/types/product.ts:7-14` (the constant), `product.ts:80-86` (`toProductCategory` map),
  `frontend/src/types/product.test.ts` (expectations), and **one live component**,
  `frontend/src/components/shell/ItemInspectorDrawer.tsx:6,137,289` (datalist + save
  canonicalisation). `CatalogToolbar.tsx` does **not** import it (see F-SG065-3).
- **Chat supported-category set found** (recorded stage limit, not restated): backend
  `backend/app/services/chat/service.py:53-56` `SUPPORTED_CATEGORIES = {"food": "food_beverages",
  "medicine": "medicine_pharma"}` (enforced 422 via `resolve_category` `:87-91`); frontend
  `frontend/src/routes/ChatPage.tsx:9-12` `CATEGORIES = [{value:"food"},{value:"medicine"}]`.
- **Import/capture forms** — `AssetImportModal.tsx` carries no category list; `AssetForm.tsx:125-134`
  has an `asset_type` `<select>` of the **8 core asset types** (`unknown/equipment/product/component/
  consumable/container/document/collection`) — a different taxonomy, untouched.
- **Router mount** — `backend/app/main.py:61` already mounts `assets_router` at `/v1`, and
  `assets.py:34` `router = APIRouter()` has no prefix. A route added there serves `/v1/taxonomy`
  **without editing `main.py`** (off-ceiling). This is the SG-068 router decision pattern.
- `EXPECTED_TABLES` read live (`backend/tests/test_postgres_dialect.py:35-54`): 18 tables.

---

## 2. What shipped

### G1 — plugin taxonomy descriptor (contract made real)
- **New `backend/app/plugins/descriptor.py`** — frozen dataclasses `BehaviorProfile(notification,
  opened_date_tracking, chat)`, `CategoryDescriptor(id, name, active, behavior)`,
  `PluginTaxonomy(plugin_id, version, categories, date_types, units)`; all collection fields are
  tuples (immutability, single source). `CORE_ASSET_FIELDS` (the 11 `Asset` columns),
  `NOTIFICATION_MODES`, `CHAT_MODES`; `validate_taxonomy` (enforcement); `DescriptorError`;
  and `EXPIRY_TRACKER_TAXONOMY` (the shipped data). `date_types`/`units` are enumerated from the
  live `DateType`/`Unit` enums, never re-typed. **Data only — no core-table or schema change.**
- **Registry wiring** — `backend/app/plugins/registry.py`: `RegisteredPlugin` gains
  `taxonomy: PluginTaxonomy | None`; `register_plugin(..., taxonomy=None)` validates the descriptor
  and its identity **before** registering (a bad descriptor raises and nothing is registered);
  `iter_plugins()` returns registrations in deterministic `plugin_id` order. The built-in expiry
  registration at import passes `EXPIRY_TRACKER_TAXONOMY` — same shape as before, extended.
  `get_plugin` remains the access route.
- **Household chemicals pilot (quoted data):** `CategoryDescriptor("household_chemicals",
  "Household chemicals", False, BehaviorProfile("basic-expiry", False, "fallback"))` — basic expiry,
  **no** opened-date tracking, **no** dedicated chat agent (generic fallback). Documents:
  `BehaviorProfile("long-lead-60-30", False, "fallback")`.

### G2 — taxonomy served + consumed
- **`GET /v1/taxonomy`** added to `backend/app/api/v1/assets.py` (read-only): iterates the real
  registry, skips plugins without a descriptor, serves each plugin's categories (`id/name/active/
  notification/opened_date_tracking/chat`), `date_types`, `units`. Deterministic order.
- **Frontend swap** — `frontend/src/api/types.ts` gains `TaxonomyCategory/TaxonomyPlugin/
  TaxonomyResponse`; `frontend/src/hooks/useAssets.ts` gains `useTaxonomy` (`staleTime: Infinity`);
  `frontend/src/components/shell/ItemInspectorDrawer.tsx` sources the `<datalist>` and the save
  canonicalisation from the served names and **no longer imports `CANONICAL_CATEGORIES`**.
  `frontend/src/types/product.ts` keeps the constant (display normalisation + grid/mock expectations)
  with a doc note that the live dropdown source moved; `toProductCategory` passthrough is unchanged.
- **Empty/absent descriptor (`PG-SC-07`):** a descriptor with zero categories serves `categories: []`
  (backend test); the UI degrades to an empty `<datalist>` — the input stays free text and the typed
  value passes through on save (explicit frontend test). Absent taxonomy (query unresolved) is the
  same `?? []` path, never a crash.

### G3 — the exit property, proven
- **New `backend/tests/test_plugin_taxonomy.py`** (7 tests, runs the real registry + real HTTP path):
  1. `GET /v1/taxonomy` serves the expiry descriptor with Household = `basic-expiry`/
     `opened_date_tracking false`/`chat fallback`, Documents = `long-lead-60-30`; deterministic order.
  2. Descriptor `date_types`/`units` equal the live `DateType`/`Unit` enums (no second copy).
  3. **Exit proof:** register `documents-domain` via real `register_plugin`; `get_plugin` returns it;
     `set(Base.metadata.tables)` equals `EXPECTED_TABLES` **before and after**; the new domain then
     answers through `GET /v1/taxonomy`.
  4. Empty category map serves `[]`.
  5. A legal id registers fine beside the rejection (guards against a vacuous rejection).
  6. **Core-field redefinition rejected:** `CategoryDescriptor("status", …)` → `DescriptorError`
     and `get_plugin("rogue-domain")` still raises `PluginError` (no partial write).
  7. Unknown notification mode and duplicate category id rejected.
- **FAIL-then-PASS raw (PG-EV-09):** enforcement active → PASS; `validate_taxonomy` disabled →
  FAIL; restored → PASS. All three runs pasted in `SG-065_verify.log` §3.

### Enforcement mechanism named
**Descriptor schema validation on registration** (`validate_taxonomy`, called by
`register_plugin`). It checks, in stdlib dataclasses only (no new dependency): core-field collision
on category id/name, duplicate ids, empty ids, unknown notification/chat modes, and non-empty
string date-types/units. The core-field probe lives entirely in the descriptor contract — no schema
is touched.

---

## 3. Findings, corrections, and reported scope

1. **F-SG065-1 (packet enum insufficient — extended by one value, reported).** The packet's
   notification enum is `tiered-30-7-1 | tiered-short | basic-expiry | long-lead-60-30 | none`, but
   the **shipped** Cosmetics profile (`expiry_tracker.py:105-109` `COSMETICS_TIERS`) is 90/30/7.
   Forcing it into `tiered-short` would misdescribe the live data, and G1 says reflect the shipped
   profile. I added `"tiered-90-30-7"` to `NOTIFICATION_MODES` and report the divergence rather than
   bending the data. Also, the packet's Documents line writes `"chat": "generic-fallback"` while its
   own enum says `fallback`; resolved to the enum value `"fallback"` for Household **and** Documents
   (identical semantics — no dedicated agent, generic fallback).
2. **F-SG065-2 (shipped vs blueprint divergence — reported, not hidden).** Shipped
   `expiry_tracker.CATEGORIES:127-132` marks `household_chemicals` and `documents_other` as
   `active=False, phase="Phase 3"` with **empty tier defaults** (their `profile()` returns
   `notification_tier: None`), which contradicts blueprint §9.1 (Household = basic expiry; Documents =
   long-lead 60/30). The descriptor carries the **blueprint pilot profiles as DATA** and mirrors the
   shipped activation state with `"active": false`. Enabling the classify path would require editing
   `expiry_tracker.CATEGORIES`, which the scope explicitly bars (`expiry_tracker.py` descriptors only
   if the shared-shape refactor earns it — it did not; the refactor lives in the new module), so it
   was **not** done. Reported for the next slice.
3. **F-SG065-3 (stale premise corrected).** The packet said `CatalogToolbar.tsx:21` pills derive from
   `CANONICAL_CATEGORIES`. They do **not** — since SG-064 the pills are data-driven from `asset_type`
   facet keys (`CatalogPage.tsx:77-87` → `AppShell` → `CatalogToolbar`); `CatalogToolbar` never
   imports the constant. The **only** live consumer of `CANONICAL_CATEGORIES` was
   `ItemInspectorDrawer` (datalist + save canonicalisation), which is what this slice swapped. The
   import modal and capture form carry no DQ1 list (F-SG065-3 in §1).
4. **F-SG065-4 (chat gate enumerated, intentionally not swapped).** The chat supported set is
   `SUPPORTED_CATEGORIES` (`chat/service.py:53-56`) mirrored by `ChatPage.tsx:9-12`. Its route values
   are `food`/`medicine`, while the plugin taxonomy ids are `food_beverages`/`medicine_pharma`; wiring
   the chat dropdown to taxonomy would change the enforced chat gate (a behavior change beyond a
   data-only pilot, and this packet adds no agent). Enumerated and left as-is, per G-A7 simplicity.
5. **F-SG065-5 (descriptor shape follows G1).** The shipped `Category.profile` also carries
   `disposal_guidance` (blueprint §8 names it), but the packet's G1 field list names only
   `notification`/`opened_date_tracking`/`chat`, so the descriptor does not include it. Reported.
6. **Integration during the slice (reported).** `origin/automation` advanced after my first commit
   (two Bolt PRs merged: `df184e5` exports N+1 fix, `c849088` asset-evidence JOIN fix); the first
   `git push` was rejected. I rebased onto `origin/automation` (**no force-push**), re-ran backend
   gates, and pushed `c849088..3f2fd6b`. `WORK_HEAD` is the rebased `3f2fd6b`.
7. **No new dependencies; no migration; no prompt/template change; no provider call; no deploy.**
   `pyproject.toml`, `requirements.lock`, `package.json`, `package-lock.json` untouched. Secret scan
   on all touched/new files: zero matches. No ignored file staged. Nothing pushed to
   `storagegenie-evidence`; `{{RECEIPT_CMD}}` not invoked. Production DB untouched.

## 4. Vacuity audit

- The endpoint tests call the **real** `TestClient(app).get("/v1/taxonomy")` — not a direct function
  call, so the route/mount is exercised.
- The exit proof registers through the **real** `register_plugin` and asserts a **before/after**
  `Base.metadata` diff against the live `EXPECTED_TABLES` — a fake registry or a vacuous empty set
  would fail the `== EXPECTED_TABLES` equality.
- The FAIL-then-PASS run proves the rejection test is load-bearing (disabling validation turns it RED).
- The frontend test asserts a served option value is present **and** a retired DQ1 label is absent —
  an empty render cannot satisfy both.
- The `date_types`/`units` test compares against the live enums, so a second hand-typed copy would be
  caught.

## 5. Acceptance criteria

- [x] Starting tree quoted clean; premises re-verified with quoted reads (registry shape, expiry
  constants, live chat-supported set, category-list consumers) — §1.
- [x] Descriptor immutable (frozen dataclasses, tuple fields) + registered via the existing
  `register_plugin` mechanism; `GET /v1/taxonomy` answers with the descriptor (quoted test on the
  real HTTP path); the inspector dropdown consumes it, and a derived-set test proves the old hardcoded
  DQ1 list is gone from the live path.
- [x] Exit proof: `documents-domain` registration exercises the real registry + taxonomy path with
  zero new tables (inspector diff quoted: 18 → 18, `new tables added: []`); core-field redefinition
  (`status`) rejected (FAIL-then-PASS raw ×3 pasted).
- [x] Household chemicals pilot complete per blueprint (basic expiry, no opened-date, no chat agent),
  its behaviour profile is DATA and quoted in §2 G1.
- [x] Suite + lint + build green (only the 2 base decoder reds); no-deploy stated; prod DB untouched;
  no migration; no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## 6. Gates (derived set)

| Gate | Result | Base |
|---|---|---|
| backend `pytest` | **271 passed**, 2 failed = the same base decoder-env reds (`test_signals::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier`, `test_signals::test_ocr_has_text_boxes_and_mean_confidence`) | 264 passed + 2 reds |
| backend `ruff check .` | `All checks passed!` | clean |
| backend `mypy app` | `Found 41 errors in 9 files (checked 72)` — **delta 0**; new `descriptor.py` 0 errors, only the checked-file count moved 71 → 72 | 41 / 9 files (71) |
| frontend `vitest` | **160 passed / 21 files** | 158 / 21 |
| frontend `tsc && vite build` | green (`✓ built`) | green |
| frontend `eslint src` | green | green |
| derived backend files | `test_plugin_taxonomy.py` (7) + `test_plugin_expiry.py` + `test_postgres_dialect.py` = **17 passed** | — |
| derived frontend files | `product.test.ts` (12) + `drawer.test.tsx` (15) = **27** | — |
| intuition extra | `catalog.test.tsx` renders `CatalogPage` (not a symbol hit) — green in the full suite | — |

Full sweep **WAIVED** (`PG-PR-04` shape); substitutes named: the suites above, lint/build, and the new
endpoint/registration tests on the real HTTP path. **No deploy** — the user-visible change (served
taxonomy + dropdown) rides the next owner-gated deploy slice, as SG-064/068; nothing
production-effect is claimed beyond gates.

## 7. Receipt (notes ref `refs/notes/storagegenie-coder-reports`)

Work pushed to `automation` (`c849088..3f2fd6b`), worktree clean. Note added on
`WORK_HEAD = 3f2fd6bd95f8988316abca7ce7eafc3af1baa85d`, pushed, fetched into a MAPPED local ref, and
verified. Executed output pasted verbatim:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports show 3f2fd6bd95f8988316abca7ce7eafc3af1baa85d
error: no note found for object 3f2fd6bd95f8988316abca7ce7eafc3af1baa85d.   (pre-add refusal guard)
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-065 | Report: docs/worklogs/SG-065_report.md | Work-HEAD: 3f2fd6bd95f8988316abca7ce7eafc3af1baa85d" 3f2fd6bd95f8988316abca7ce7eafc3af1baa85d
notes add rc=0
$ git push origin refs/notes/storagegenie-coder-reports
   50041a8..214f8d8  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
notes push rc=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-sg065-verify
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-sg065-verify
fetch rc=0
$ git rev-parse refs/notes/storagegenie-coder-reports-sg065-verify
214f8d809e7ff2e606e851dcce3778363b6be545
$ git notes --ref=refs/notes/storagegenie-coder-reports-sg065-verify list | grep 3f2fd6bd95f8988316abca7ce7eafc3af1baa85d
fbc12d2ce8d6023d05493d620e7214a095fe9eb9 3f2fd6bd95f8988316abca7ce7eafc3af1baa85d
list-grep rc=0
$ git notes --ref=refs/notes/storagegenie-coder-reports-sg065-verify show 3f2fd6bd95f8988316abca7ce7eafc3af1baa85d
Dispatch-ID: SG-065 | Report: docs/worklogs/SG-065_report.md | Work-HEAD: 3f2fd6bd95f8988316abca7ce7eafc3af1baa85d
show rc=0
$ git notes --ref=refs/notes/storagegenie-coder-reports-sg065-verify show 3f2fd6bd95f8988316abca7ce7eafc3af1baa85d | grep -c "Dispatch-ID: SG-065"
1
```

The fetched ref (not the local write) is what proves the push landed; the first line carries both
`Dispatch-ID:` and `Report:`. `note=yes`.

## 8. UNCLEAR

- **FIRST READ:** whether the packet's notification enum was meant to be exhaustive. The shipped
  Cosmetics profile (90/30/7) has no matching value, so I treated the enum as a starting vocabulary
  and added `tiered-90-30-7` rather than mislabel live data (F-SG065-1).
- **DURING EXECUTION:** whether the Household chemicals pilot entry should be `active: true`.
  Enabling classification lives in `expiry_tracker.CATEGORIES` (scope-barred), so the descriptor
  carries the blueprint behaviour profile as DATA and mirrors the shipped `active: false`
  (F-SG065-2). Flagged rather than guessed.
- **REMAINING:** the served taxonomy + dropdown are not reachable on the live public entry until an
  owner-gated deploy rider runs (no deploy in this packet); the chat dropdown remains hardcoded
  `food`/`medicine` by design (F-SG065-4); and `disposal_guidance` from blueprint §8 is not yet part
  of the descriptor shape (F-SG065-5).

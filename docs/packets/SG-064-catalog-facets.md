# SG-064 — catalog facets + server-side category filter + evidence-badge truth (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** Phase 4 arc slice 3 (stage approved 2026-09-17 minus the second-provider slice). Purpose: blueprint:536 "advanced filters" opening — make the catalog's category pills REAL (server-faceted counts + server-side filtering) and establish whether the evidence badge can ever be true from server data. **This slice carries the SG-062 token-mangle repair as its G0** (product correctness found by the Architect's byte-probe — the repair cannot wait for the plugin/saved-search slices that follow, so it rides FIRST here). Recorded facts, all re-verify in-slice (quoted reads):
- `backend/app/api/v1/assets.py:119-189` — `GET /assets`: filters `q` (FTS MATCH via `ensure_asset_fts` + `sanitize_fts_query`, :131-142), `asset_type`, `status`, `has_evidence`; cursor envelope `(created_at, id)` desc with the strftime microsecond shim; serializer `:172-189` sends id/household/display_name/asset_type/status/quantity/unit/condition/version/created_at — **no `evidence` field**.
- `frontend/src/routes/CatalogPage.tsx` — pills state `category` (`:30`), the server `q` via `useDebounced` (`:28-29`), page accumulation + client-side `filterAndSortCatalog` (`:80-87`) which re-filters by `qRaw` substring AND category, on top of the server's MATCH narrowing — **double filtering with divergent semantics**; comment `:78-79` records "no per-category counts / no aggregation endpoint yet".
- `frontend/src/components/shell/CatalogToolbar.tsx:21` — pills `["All", ...CANONICAL_CATEGORIES]`; `frontend/src/types/product.ts:7-14` `CANONICAL_CATEGORIES` = Hardware & Tools / Electronics & Gadgets / Apparel & Textiles / Home & Decor / Packaging & Materials / Uncategorized (DQ1 generic taxonomy) and `toProductCategory` `:80-86` passes non-canonical asset_types (food/medicine/cosmetics/…) through UNCHANGED — so the static pills do not match the real type population.
- `frontend/src/routes/CatalogPage.tsx:81-84` reads `asset.evidence?.[0]` for the badge; the list serializer never sends `evidence` — **establish whether the badge can EVER be true from the live API, and fix if it cannot (the usual construction: server sends the data, or the badge cannot render — no fake path).**
- THINK-TAG token: `backend/app/services/providers/opencode_go.py` `strip_single_think` `:91-101` currently carries the SG-062 mangle (the unbalanced-guard condition queries the literal space-thinking string; the message lost its angle tokens). RESTORE plans in G0 with char-code payloads — **DO NOT try to type the angle token through your editing tooling: that is exactly what corrupted it** (byte probe of the committed file shows the guard condition is `" thinking"` with NO codes 60/62 anywhere).
**Authoring date (metadata, never a gate):** 2026-09-17. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published (`b495b59`); the on-box copy at `/home/andrei/storagegenie-contract/` was readable for SG-062 — echo verbatim + name the source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** no new dependencies; no prompt/template changes; no provider calls ($0 — a metered call is a STOP-and-report); results from deterministic scripted-provider/scratch-SQLite tests; NETWORK: loopback + container-runtime only.
**Standing line (SG-062 recurrence guard, this slice):** any in-scope file expected to contain an angle-bracket token (think-tag) is re-probed BY CHAR CODES after every edit; tests exercising such strings construct them from `chr(60)`/`chr(62)` — never a typed escape.
**Money posture:** $0.000000 actual vs $0 bound.
**Guards invoked (0.28.2 — Architect copies these to the rating row):** `PG-EV-01` gates-seen-failing · `PG-EV-02` artifact-not-command · `PG-EV-03` stop-not-disclosure · `PG-EV-05` property-not-command · `PG-EV-08` capture-before-change · `PG-EV-09` fail-then-pass-committed · `PG-SC-02` recorded-field-reaches-readback · `PG-SC-05` exclude-by-rule · `PG-SC-07` eliminated-every-candidate · `PG-SC-09` name-the-world · `PG-SC-12` proof-on-the-real-thing · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03` denied-is-stop · `PG-PR-04` live-proof-scoped · `PG-PR-06` runtime-vs-budget · `PG-DP-02` no-sweep-waiver.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint+build, 1200s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none for proofs** (scratch temp SQLite / `{reversed}` FTS tables); **Restart: none; Deploy: none** (explicitly — the change is user-visible in the API/UI but proving it needs a rebuild; deploy is a separate owner-gated slice after this returns).

## G0 — THINK-TAG repair (SG-062 audit finding; byte-precise)

- Restore the three corrupted lines in `backend/app/services/providers/opencode_go.py` `strip_single_think` — docstring ("Strip ONE leading `&lt;think&gt;` block"), guard condition `if "&lt;think&gt;" in text:`, raise message ("unbalanced or stray `&lt;think&gt;` block in content") — **the angle token is bytes 60,116,104,105,110,107,62 between the quotes**. Because your editing channel is what mangled it last time, apply this with a routine that CONSTRUCTS the literal from character codes (e.g. a one-line Python `s.replace(chr(34)+chr(32)+'thinking'+chr(34), chr(34)+chr(60)+'think'+chr(62)+chr(34))` per line) and asserts the replacement count per line — never by typing the token.
- Re-probe after the edit: print the char codes of the three lines; the codes MUST include 60 and 62 inside the quoted strings.
- New pin test (mangler-immune): build the payload via `chr(60)+"think"+chr(62)` and assert `strip_single_think` — the unbalanced leg RAISES ("unbalanced" in the message) and the balanced-single-block leg STRIPS once. FAIL-then-PASS raw, both runs into the verify log (`PG-EV-09`).

## G1 — facets endpoint (backend, countable, dialect-safe)

- New `GET /v1/assets/facets` — same base filters as `list_assets` (`household_id` required; `q`, `asset_type`, `status`, `has_evidence` optional). Response: one map per ANALYZED dimension — `asset_type`, `status`, `has_evidence` — where **each dimension's counts are computed WITHOUT that dimension's own filter** (a pill must show the counts reachable by selecting it, never only-the-selected-zero). Keys sorted deterministically; `has_evidence` keys `"with"`/`"without"`; counts are INTEGERs.
- `q` semantics shared with `list_assets`: same `ensure_asset_fts` + `sanitize_fts_query` call — the facet base equals the list base; reuse the shared filtering code or factor it — design call, report it (behavior-preservation rail: identical filter semantics per dimension pair, divergence is a STOP; consolidation is refactoring only because the behaviours already match).
- Dialect: aggregate SQL stays dialect-neutral (`count(*)` + group_by / an exists-style subquery for `has_evidence` — the same `asset_evidence` join the list path uses at `:147-151`); `test_postgres_dialect.py` run with the new endpoint asserted (M13 family: the dialect test file is named by its registry — verify its live shape, quote it).
- `PG-SC-07`: state the zero-population behavior (household with zero assets = empty maps, not an error); name the smallest real population (seed household `01a0a029…` has 2 users and at least the Toothpaste rows).
- `PG-SC-09` named world where this is wrong: counts computed WITH all filters would show only-selected-type; packet chose MINUS-OWN-DIMENSION — your tests must discriminate the two (selecting a type must NOT zero the other pills' counts).

## G2 — server-side category filter wired into the pills (UI follows the data)

- `useAssets`/`CatalogPage`: the active NON-"All" pill passes `asset_type=<category>` (the facet KEY, the raw string — not the DQ1 label) to the list query; the client-side category item-match in `filterAndSortCatalog` (`CatalogToolbar.tsx:29`) therefore becomes redundant — remove the category-term filter from that client path or keep it provably inert, decide and report (behavior-preservation: `catalog.test.tsx:482`-era mock shapes are expectations).
- Pills render their count next to the label: `Label (N)` from the facets map; the "All" pill count = unfiltered-with-q count. Empty-household pills render `(0)`.
- **q double-filter unified:** the debounced server `q` REMAINS the source (`MATCH`); the client-side `needle` re-filter (`CatalogToolbar.tsx:30`) is REMOVED only if you verify the server MATCH covers the same field the client filter touched (name) — where different (e.g. MATCH is broader), the client filter DROPPED and the divergence documented as intended behavior (server is the authority; never silently narrower client-side). State which you did and quote the field list the FTS covers (`ensure_asset_fts` schema).
- Cursor/reset behaviour preserved: change the reset-on-query-change effect (`CatalogPage.tsx:50-54`) to include the category dimension; loaded-accumulation otherwise unchanged.

## G3 — evidence-badge establishment (probe, then fix only if confirmed)

- Probe: from the committed code, trace the LIST path field-by-field (serializer `:172-189` → frontend `Asset.evidence` consumers: `CatalogPage.tsx:83`, `ProductGrid` badge render) and state whether a list row can EVER satisfy the badge. Quote consumer lines.
- Only if confirmed never-served: extend the list serializer with the minimal evidence payload (e.g. `evidence_ids` or the first evidence id — pick the one the badge reads; `PG-SC-02` trace: name the screen/query that READS it back) + the test proving a seeded asset's badge signals true end-to-end on the real HTTP path (TestClient + temp SQLite; `PG-SC-12` real record path). If already served (premise wrong), say so with the quoted line instead.
- FALSE-then-PASS rule: if a fix lands in this leg, capture the pre-change assertion visibly red on base and green after (`PG-EV-09`, committed verify log, both raw).

## G4 — suite + lint + build (NO deploy)

- Derived test set (0.28.2 test-set rule): **a hit is a FILE** — grep HIT-tree for assertions naming the touched symbols/markup/fields; run every node in each hit file. Report derived-vs-intuition sets.
- Backend suite + `ruff` + mypy delta-0 + frontend `tsc && vite build` + eslint + frontend suite green; only base-proven reds (2 decoder env reds; cite base commit + recorded base-run).
- **NO DEPLOY (`PG-PR-04` stated):** user-visible change requires rebuild; deploy is a separate owner-gated slice after this returns green — nothing production-effect is claimed this slice beyond gates. Full-sweep WAIVED per `PG-DP-02`; substitutes named here: backend/frontend suites + lint + build + the new endpoint tests on the real HTTP path (TestClient) — the externally-observed contract is what those tests assert.
- Secret scan zero; no ignored-file staged; nothing pushed to `storagegenie-evidence`; prod DB untouched; no migration; dep list unchanged; no vacuous pass.

## G5 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-064.log`, `SG-064_report.md`, `SG-064_verify.log` (facet-line table + char-code probes + both runs of every FAIL-then-PASS). First token `SG-064`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `backend/app/services/providers/opencode_go.py` (G0 hunks only) · `backend/app/api/v1/assets.py` (facets endpoint + filters + serializer) · backend tests (extend/new: facets + dialect + think-tag pin) · `frontend/src/hooks/useAssets.ts` · `frontend/src/routes/CatalogPage.tsx` · `frontend/src/components/shell/CatalogToolbar.tsx` (+ its test file if the derived set hits) · **frontend test files the derived set names may be EDITED to match the new behaviour, each edit reported with its reason** (`M9` counter-rule — test registries are in the ceiling, not beside it) · `frontend/src/components/catalog/ProductGrid.tsx` + `frontend/src/api/types.ts` only if G3's fix requires them · `docs/worklogs` (3 files). **Anything else is a STOP** — including `types/product.ts` CANONICAL_CATEGORIES values, `router.py`, `.env`, `docker-compose.yml`, `AGENTS.md`, migrations, prompts, saved-searches (future slice), asset-relations.
- Every requirement above names a file the ceiling enables; if one does not, STOP and say which.
- Cross-product (`PG-IC-01`): the ONLY live-external surface is the facets/list endpoints and the Catalog UI against the local API — no criterion touches provider code except G0's three lines. Reads MAY pull/run the already-built local images only (dev server via Vite allowed for a UI check, not required).
- Budget (uncalibrated per `G-A9`; back-end+front-end feature slices on this lane measured within 1800s historically): 120s ordinary · 600s suite+lint+build · 1200s early-close · 1800s overall — actual-vs-budget per leg with units.
- Simplicity (`G-A7`): three corrupted-line restores + one endpoint + wiring; no framework introduction, no search-param library, no new table.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Saved searches are EXPLICITLY OUT OF SCOPE (they become a follow-on slice — the packet's why-this-exists names them only as future scope).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); premises re-verified with quoted reads (list endpoint, catalog page, toolbar, product types, the three corrupted lines' current bytes).
- G0: char-code probes show codes 60/62 restored in all three lines; think-tag pin red→green raw (both runs in the verify log).
- Facets endpoint live: quoted test proves (a) each dimension counts WITHOUT its own filter (selecting a type does not zero other pills), (b) `q` narrows the facet base, (c) empty household → empty maps (200, no error), (d) dialect test green.
- Pills render real counts; non-"All" pill passes `asset_type` to the server; the client-side category match is provably inert or removed; q divergence decision recorded with the FTS field list quoted.
- Evidence badge: establishment verdict quoted (served-never / fixed with end-to-end true test); no fix without the failed pre-change capture.
- Suite + lint + build green (only base-proven reds); no-deploy reason stated; prod DB untouched; no migration; no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-064 | Report: docs/worklogs/SG-064_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), LIST the note contents and grep for this ID (log `--grep` does not match note bodies — proven twice), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint+build · 1200s early-close · 1800s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.

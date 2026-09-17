# SG-068 — saved searches: named filter sets persisted per household (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** Phase 4 arc slice 5 — the saved-searches leg of blueprint:536's "advanced filters" (split out of SG-064's approved line when that slice landed facets; announced at D83-era planning, so this IS approved arc scope). SG-064 shipped facets + server-side category filter (`4060bb0`, audited 98) and the deploy rider SG-067 brought them live. This slice adds NAMED FILTER SETS: a user saves the current search (q + active category) under a name and re-applies it later with one click. Recorded facts, verify each in-slice with quoted reads:
- The filter surface it must capture is EXACTLY what the catalog URL/query sends today: `q` (FTS MATCH), `asset_type` (server-side since SG-064), `status`, `has_evidence` (backend `list_assets` filters) — the pill/toolbar state in `frontend/src/routes/CatalogPage.tsx` (`qRaw`, `category`, `cursor`) and `hooks/useAssets.ts` (post-SG-064 shape: household/q/asset_type/cursor).
- Backend assets/list endpoints live at `backend/app/api/v1/assets.py` (list + facets + shared `_apply_asset_filters`); the catalog UI already resets accumulation on filter changes (`CatalogPage.tsx` reset effect) — a saved search applies by setting the SAME state, never by inventing a second query language.
- Migration: SQLite live DB; `max(+1)` naming per `lang/python.md`; **head-relative downgrade assertions must be updated by the grep the packet mandates (standing line); ownership statements: NONE — `AGENTS.md` names no owning role for the SQLite path, and the 0.28.2 language rule says a migration adds none and the report says so.**
- `EXPECTED_TABLES` static registry (backend test, SG-025-era): a new table extends it (M4/M9 family — the registry file is IN the ceiling, walk it live).
**Authoring date (metadata, never a gate):** 2026-09-17. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published (`b495b59`); echo verbatim + name the source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** no new dependencies; no prompt/template changes; no provider calls ($0 — a metered call is a STOP-and-report); NETWORK: loopback + container-runtime only. THINK-TAG standing line: any in-scope file expected to carry an angle-bracket token is re-probed by char codes after editing; tests build such strings from `chr()` codes.
**Money posture:** $0.000000 actual vs $0 bound.
**Guards invoked (0.28.2 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-03` · `PG-EV-05` · `PG-EV-08` · `PG-EV-09` · `PG-SC-02` (recorded field reaches read-back: the saved name/filter must round-trip to a working query) · `PG-SC-05` (exclude by rule: the query whitelist) · `PG-SC-06` (name the caps: name length, payload size, list count) · `PG-SC-07` (zero-saved-state renders nothing, not an error) · `PG-SC-09` · `PG-SC-11` (head-relative assertions) · `PG-SC-12` · `PG-IC-01` · `PG-IC-03` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06` · `PG-DP-02`.

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

**DATABASE: test-only migrations + scratch temp SQLite for proofs; PRODUCTION MIGRATE AUTHORIZED — owner decision D85 (2026-09-17, "Both approved") covers the live `alembic upgrade head` on the production SQLite for THIS packet alone (one new table, no data writes; the G-K3 surface decision rides this packet). If you read this packet and cannot find a decision record citing it, STOP and report the word as absent.** **Restart: none.** **Deploy: none** (rebuild rider is a separate slice as before).

## Why this exists

Blueprint:536 names "advanced filters"; facets landed (SG-064); the natural completion is persistence — a household's recurring searches ("my unreviewed photos", "toothpaste restock") should not be retyped. Scope: named, per-household, round-trip filters; nothing more.

## G1 — backend saved-searches (table + API)

- New table `saved_search`: `id` (uuid pk), `household_id` (fk, indexed), `name` (String 80, not null), `query_json` (Text, not null — the WHITELISTED filter set), `created_at`. Migration numbered `max+1`, idempotent-add; NO ownership statements (say so in the report per the 0.28.2 language rule).
- Endpoints: `POST /v1/saved-searches` `{name, query}`; `GET /v1/saved-searches?household_id=` (ordered `created_at desc`, no cursor needed — small); `DELETE /v1/saved-searches/{id}` (household mismatch = 403, missing = 404). `PATCH` rename: SKIP (not needed; noted as future).
- **`query` whitelist (`PG-SC-05`, exclude by rule):** accepted keys EXACTLY `q`, `asset_type`, `status`, `has_evidence` — anything else in the payload is a 422 with the offending keys named (visible reject, never silently dropped). Sizes: `name` ≤ 80 chars; `query_json` serialized ≤ 2 KiB (cap is a named setting with a visible 413/422, not silent — `G-A8`). Duplicate name per household = 409 (case-insensitive compare; the unique index or a pre-check — decide, report).
- `status`/`has_evidence` values validated against the same enums the list endpoint accepts today (read `list_assets`' handling and mirror; an invalid stored filter must FAIL LOUDLY at save time, never at apply time).
- Backend tests: CRUD + household isolation (another household's saved search is invisible AND undeletable) + whitelist 422s + size-cap rejections + empty-state 200 (`PG-SC-07`). `test_postgres_dialect.py` extended with the new table's schema + the registry assertion named (M13: read the registry live, quote it).

## G2 — frontend: save + apply (CatalogToolbar + CatalogPage)

- A "Save search" affordance in the toolbar (only when a filter is actually active — the `activeFilters` list is non-empty; click → name prompt → POST). A "Saved searches" dropdown listing the household's sets; selecting one SETS the same state the pills/search box use (`qRaw`, `category`) and re-queries; deleting from the dropdown DELETEs. Empty list renders a muted "None yet" (never an error).
- Apply semantics: the saved query maps onto the EXISTING state variables — no second query path; changing household resets the dropdown state (scope discipline: saved searches are per-household; switching households shows THAT household's set).
- Names render verbatim (no HTML interpretation of a user-supplied name — the existing text-node rendering already does this; a test asserts a name like `O'Brien <derp>` round-trips and renders as TEXT (constructed in the test from plain literals — no angle-token typing needed here, but if your fixture ever embeds the THINK-TAG token, build it from `chr()` codes).

## G3 — suite + lint + build (NO deploy)

- Derived test set (0.28.2: a hit is a FILE): grep for the touched symbols/fields; run every node in each hit file. Report derived-vs-intuition.
- Backend suite + `ruff` + mypy delta-0 + frontend suite + `tsc && vite build` + eslint green; only base-proven reds (2 decoder env reds).
- **NO DEPLOY, stated (`PG-PR-04`):** same shape as SG-064 — the live proof rides the next owner-gated deploy slice; nothing production-effect is claimed beyond gates. Full sweep WAIVED per `PG-DP-02`; substitutes named: backend/frontend suites + lint + build + the new endpoint tests on the real HTTP path (TestClient + temp SQLite; the migration runs there).
- Secret scan zero; no ignored file staged; nothing pushed to `storagegenie-evidence`; prod DB untouched EXCEPT the authorized `alembic upgrade head` (G1 scope above — if the packet lacks the owner word per your reading, STOP); dep list unchanged; no vacuous pass.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-068.log`, `SG-068_report.md`, `SG-068_verify.log` (round-trip + FAIL-then-PASS raws). First token `SG-068`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `backend/app/api/v1/assets.py` OR a new `backend/app/api/v1/saved_searches.py` router (decide + report where the router mounts; both allowed) · `backend/app/models/saved_search.py` (new) · `backend/app/schemas/saved_search.py` (new, if the schema split earns it) · one migration file + `backend/tests/test_postgres_dialect.py` + the static table registry it names + `backend/tests/test_saved_searches.py` (new) · `frontend/src/routes/CatalogPage.tsx` + `frontend/src/components/shell/CatalogToolbar.tsx` + `frontend/src/api/types.ts` (+ `hooks/useAssets.ts` if a hook splits) + frontend test files the derived set names (each edit reported with reason) · `docs/worklogs` (3 files). **Anything else is a STOP** — `router.py`, provider code, `.env`, `docker-compose.yml`, `AGENTS.md`, prompts.
- Cross-product (`PG-IC-01`): the ONLY new persisted state is `saved_search`; no criterion touches provider/ledger code; the whitelist rule and the round-trip criterion cannot collide (the whitelist is what the round-trip sends). Reads MAY pull/run the already-built local images only.
- Budget (uncalibrated per `G-A9`): 120s ordinary · 600s suite+lint+build · 1200s early-close · 1800s overall — actual-vs-budget per leg with units.
- Simplicity (`G-A7`): one small table, three endpoints, one save affordance + one dropdown; no query-language invention (the saved `query` is exactly today's filter set).
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Out of scope: sharing saved searches across households, scheduled/rerunning saved searches, relevance ranking (SG-017's recorded constraint stands).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); premises re-verified with quoted reads.
- Migration: new head named; upgrade+downgrade on scratch DB proven (head-relative assertions updated where the appended table breaks tail-relative checks — grep required, `PG-SC-11`); production head checked and EITHER migrated on the owner word or left untouched with the word absent reported loudly.
- Round-trip: save a named filter set → the dropdown lists it (with its counts-visible filters rendered as labels) → selecting it issues the SAME query the manual state did (quoted request URLs) → delete works. Household isolation: second household cannot see/delete the first's rows (quoted test).
- Whitelist + caps: unknown filter key → 422 (quoted); oversize → visible 413/422 (quoted); duplicate name → 409 or the decided behavior (quoted).
- Suite + lint + build green (only base-proven reds); no-deploy reason stated; dep list unchanged; no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-068 | Report: docs/worklogs/SG-068_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), LIST the note contents and grep for this ID (log `--grep` does not match note bodies — proven twice), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint+build · 1200s early-close · 1800s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.

# SG-048 — name-optional capture: nullable display_name migration + photo-derived default + form (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** Stage D60/D74 (photo-first capture, L3) slice S2 of 3: S1 (SG-042) staged photo bytes (paste + camera) and left the name required; THIS slice makes the name optional with a photo-derived server default; S3 derives quantity/unit/type via AI (needs D62, out of this slice). Live-DB migration authority: D72 (banked `docs/decisions/2026-09-16-feedback-approvals.md`). SG-042 REMAINING listener question answered here: `AssetForm` mounts ONLY in `CapturePage.tsx:46` (plus tests) — the import modal is a separate component — so the window paste listener stays as-is; report the re-enumeration either way. **Authoring date (metadata, never a gate):** 2026-09-16. Transport: the standard job_spawn lane. Contract 0.27.0 (recorded == published payload == SG-054 receipt echo; packet states it).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **AI stays OFF**: no provider calls, **$0 metered**; no new dependencies; NETWORK: none except loopback reads on the box (no registry pulls; base layers from the local builder cache).
**Guards invoked (0.27.0 — Architect copies these to the rating row):** `PG-EV-01` gate-seen-failing · `PG-EV-02` artifact-exists · `PG-EV-05` property-not-command · `PG-EV-06` live-rows · `PG-EV-08` before-capture · `PG-EV-09` both-runs-committed · `PG-SC-01` write-and-read-paths · `PG-SC-02` field-traced · `PG-SC-05` exclude-by-rule · `PG-SC-10` no-ignored-commit · `PG-SC-11` end-relative-assertions · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-08` blast-radius-is-stop · `PG-IC-09` premises-live · `PG-PR-03` denied-is-stop · `PG-PR-04` code-becomes-live · `PG-PR-06` runtime-vs-budget · `PG-PR-10` which-database-plus-grant · `PG-DP-02` no-sweep-in-restart-slice. (`PG-DP-03`/`PG-DP-04` do not fire: planned stage work, no reported failure, no new entry point.)

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint+build, 900s host build/up/migrate leg. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: production SQLite `sqlite:////data/db/storagegenie.db` on the host for the MIGRATION ONLY (authority D72, `PG-PR-10`) — plus scratch temp SQLite for all tests (never prod credentials in the test layer). Restart: backend container via compose rebuild+up (`PG-PR-04`). NETWORK: none except loopback reads on the box.**

## Why this exists

The owner-approved photo-first flow (D60/S1→S2→S3): S1 stages photo bytes, but capture still forces a typed name — `AssetForm.tsx:66-71` refuses nameless submit ("Display name required") with a `required` input (`:113-121`), `AssetCreate.display_name: str` (`schemas/asset.py:7`) rejects a missing name with 422, and `create_asset` does `payload["display_name"]` (`asset_service.py:20`, KeyError when absent) against a `nullable=False` column (`models/asset.py:15`, migration `0201cf10c56c:41`). Expected-state premises (re-verify in-slice per `PG-IC-09`, quote what you read): the six cites above plus `_deterministic_display_name` (`candidates.py:159-165`: first-evidence filename stem, `"Imported item"` when no evidence — the existing verbatim photo-derived namer this slice reuses, NO AI), assertion creation on supplied fields (`asset_service.py:30-39`, `source_type="user"`, `review_state="accepted"`), FTS external-content projection over `display_name` (`fts.py:34-74`), head revision `20260914_sg035_foundations`.

## G1 — migration: `display_name` nullable (new `backend/alembic/versions/20260916_sg048_name_optional.py`)

- `down_revision = "20260914_sg035_foundations"` (the current head — verify, never inherit). Data-preserving nullability change ONLY (SQLite batch mode as the repo's SQLite target requires — check how the tree handles SQLite alters before choosing the op; production is SQLite).
- Downgrade restores `nullable=False` (fail-closed on rows that would violate it: a nameless row present at downgrade time is a STOP-and-report, never a silent data drop — `PG-IC-03`: stops win).
- Round-trip test in the slice (repo pattern `test_foundations.py:58-81`: tmp DB, upgrade→downgrade-to-`20260914_sg035_foundations`→upgrade): nullability observed via `pragma table_info` both directions, one nameless row survives upgrade-wrap. `PG-SC-11`: grep every head-relative assertion (`head`, `latest`, `[-1]`, expected-head strings) and update each hit in this slice — name the hits.

## G2 — write path: missing/blank name resolves server-side, never 422s, never KeyErrors

- `AssetCreate.display_name: str | None = None`. Missing OR blank/whitespace-only counts as absent (one rule, tested both ways).
- `create_asset`: absent name + evidence present → `_deterministic_display_name` value (first-evidence filename stem verbatim; `"Imported item"` only when evidence is absent too — reuse the existing helper by import; if the import is genuinely unworkable, duplicate its 5 lines WITH the reason stated, never a third namer). Absent name + no evidence → store NULL (honest, not fabricated).
- Assertion row: user-supplied name → `source_type="user"`, `review_state="accepted"` (unchanged). Server-filled name → `source_type="deterministic"`, `review_state="accepted"` (EXACT states per M11 — the name is shown as fact and renamable; S3 supersedes through the same upsert path). NULL name → NO `display_name` assertion row.
- `AssetOut.display_name: str | None`. `_asset_to_dict` passes null through (no change expected — prove it, don't assert it).

## G3 — read path: every `display_name` reader is null-safe (`PG-SC-02`: writer + ALL readers in the ceiling or the gap is named)

- Criterion (sets are facts — enumerate on the target, my expectation follows, report the diff either way): EVERY production reader of `asset.display_name` / `AssetOut.display_name` handles NULL. My expectation: `frontend/src/types/product.ts` (`assetToProductItem` name → `"Untitled asset"` fallback constant), `frontend/src/api/types.ts:32` (`Asset.display_name: string | null`), `AssetCard.tsx:32,55`, `AssetDetailPage.tsx:65` (+ edit-name init `:68`), `ItemInspectorDrawer.tsx:59,176` (title state + render), `exports.py:58` manifest value, FTS triggers (null flows into the index — establish what SQLite FTS5 does with it and TEST that nameless-asset search neither errors nor corrupts neighboring rows).
- "Untitled asset" is a DISPLAY fallback only — never written to the DB, never promised as AI naming in any user-facing text (`PG-SC-02` last clause).

## G4 — form: name optional, photo-first honest (`AssetForm.tsx` + test)

- `required` + the `"Display name required"` refusal go; label reads `Display name (optional)` with hint `Left blank, we use the photo's filename` (plain, no AI promise). Blank names are OMITTED from the POST payload (server resolves; the client never fabricates).
- New rule, tested both directions: nameless + photo → creates (mocked `uploadEvidence`, no `display_name` key in the asserted payload); nameless + photoless → refused with a named error (junk-row guard); name + photo → unchanged payload shape.
- SG-042 listener verdict: re-grep `AssetForm` mounts; expectation = `CapturePage` only (+ tests) → window listener stays, one line in the report.

## G5 — tests: FAIL-then-PASS both runs committed, mutation proof

- Backend (temp SQLite via the repo's `tmp_path` pattern, NEVER prod): migration round-trip (G1); nameless+evidence create → filename-stem name + deterministic/accepted assertion; nameless+photoless create → NULL + no assertion row; blank-string ≡ missing; update AssetOut null round-trip; FTS null-safety; full backend suite green.
- Frontend: G4 rule tests + `"Untitled asset"` fallback render test(s) on the touched readers; full frontend suite + lint + build green.
- Pre-change failing run + green run + 2–3 post-change mutations caught singly (name-resolution branch, fallback branch, migration nullability), ALL raw committed to `{{WORKLOG_DIR}}/SG-048_verify.log` (`PG-EV-01`, `PG-EV-09`).

## G6 — live migration + deploy (authority D72; `PG-PR-04` code becomes live via compose rebuild+up)

- BEFORE (read-only): `alembic_version == 20260914_sg035_foundations`, `pragma table_info(asset)` nullability quoted, health exact, blessed counts EXACTLY `household=1, user=2, asset=1, evidence=1, assertion=3, audit_event=3` AND Toothpaste `display_name == "Toothpaste"` — **`PG-IC-08`: differ in EITHER direction (or a renamed Toothpaste) = STOP and report before writing anything.**
- `alembic upgrade head` (900s bound) + pragma re-read (nullable now) + counts + Toothpaste name re-read EQUAL. Rebuild + up, idempotent re-`up -d` (same container, RestartCount=0), health exact, served asset hash changed, 8003 loopback-only, gate 301/401 (loopback Host-header form per F-SG053-2).
- **NO test rows in production** (`PG-EV-06` primary rule — the nameless-create path is proven on scratch SQLite upgraded through the FULL migration chain from base, which is the real path, not a hand-made schema). Report any prod-created rows with identifiers (expect zero new); removal is my decision, never yours. Full e2e sweep WAIVED per `PG-DP-02` (restart-gated); substitute = the targeted checks in this goal, named here.

## G7 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-048.log`, `{{WORKLOG_DIR}}/SG-048_report.md`, `{{WORKLOG_DIR}}/SG-048_verify.log` (G5 both runs + mutations raw, G6 before/after raw). First token `SG-048`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line (`$0`); three UNCLEAR lines. Runtime-vs-budget per `PG-PR-06` (units inside every claim; 80% warning threshold uncalibrated per `G-A9`).

## Constraints

- **Scope ceiling:** `backend/alembic/versions/20260916_sg048_name_optional.py` (new) · `backend/app/models/asset.py` (nullability hunk) · `backend/app/schemas/asset.py` (Create/Out hunks) · `backend/app/services/asset_service.py` (resolution hunk) · `backend/tests/test_assets_crud.py` + `backend/tests/test_sg048_name_optional.py` (new) + head-relative-assertion hunks wherever the G1 grep lands · `frontend/src/components/AssetForm.tsx` + `AssetForm.test.tsx` · `frontend/src/types/product.ts` (+ test) · `frontend/src/api/types.ts` (Asset hunk) · `frontend/src/components/AssetCard.tsx` · `frontend/src/routes/AssetDetailPage.tsx` · `frontend/src/components/shell/ItemInspectorDrawer.tsx` · `docs/worklogs` (3 files). **Anything else is a STOP** — including `candidates.py` (import-from ONLY, zero hunks; any needed change there is a STOP), `user.py` display_name (a different field), provider/ledger/pricing code, and any new dependency. `exports.py` + `fts.py`: read-only context, no hunks expected — a needed hunk there is a STOP-first finding (report, ship the rest only if the acceptance still holds).
- Every requirement above names a file the ceiling enables it; if you find one that does not, STOP and say which.
- Cross-product (`PG-IC-01`): no blanket exclusion is issued. G6's migration shares no condition with any remediation step — stops win (`PG-IC-03`). Reads MAY pull/run the already-built local images only.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. `PG-EV-02`: migrated pragma output / rendered DOM / committed logs, never exits. `PG-EV-05`: properties ("nameless+photo creates with the photo's filename", "nameless+photoless stores NULL and displays Untitled", "Toothpaste keeps its name across the live migration").
- Budget (uncalibrated per `G-A9`): 120s ordinary · 600s suite+lint+build · 900s host build/up/migrate leg · **1500s early-close** · **2400s overall** — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): nullability + server default + reader fallbacks + form rule; nothing else.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); premises re-verified in-slice with quoted reads — in particular `asset.py:15`, `schemas/asset.py:6-13 + :36-49`, `asset_service.py:18-39`, `candidates.py:159-165`, `AssetForm.tsx:66-108 + :110-121`, `0201cf10c56c:41`, head revision id, `api/types.ts:29-44`, every reader file the enumeration lands on.
- Reader enumeration reported with the diff vs my expectation either way; every production reader null-safe by test.
- **FAIL-then-PASS honestly (`PG-EV-09`):** pre-change failing run + green run + mutations caught-singly, all raw committed. Live before/after raw committed (`PG-EV-08`).
- Suite (backend + frontend) + lint + build green; secret scan 0; no provider calls; dep list unchanged; blessed counts + Toothpaste name equal across the live migration; zero new prod rows; no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: migration applied (D72), blessed counts before/after, Toothpaste name before/after, any prod-created rows with identifiers (expect none), live spend `$0`, no network beyond loopback.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-048 | Report: docs/worklogs/SG-048_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly (a default fetch never carries notes), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint+build · 900s host build/up/migrate · 1500s early-close · 2400s overall; $0 metered; actual-versus-budget per leg with units.

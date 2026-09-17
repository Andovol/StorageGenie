# SG-058 — consistency: unify Untitled label + per-item quantity/unit/asset_type on split (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** L3 stage D80 slice 2 of 4 (SG-057 GO). Two consistency advisories, one slice: (1) backend `UNTITLED_LABEL = "Untitled"` (`app/models/asset.py:8`) vs frontend `UNTITLED_ASSET_NAME = "Untitled asset"` (`frontend/src/types/product.ts:25`) — DECIDED by the Architect (not delegated): unify on **"Untitled asset"** everywhere (single user-visible vocabulary beats prompt brevity; the one-word delta does not move extraction behaviour, and the suite guards it); (2) `_split_child_fields` (`candidates.py:528-596`) replaces per-item `display_name`/`expiry_date`/`opened_date`/`lot` but shares origin `quantity`/`unit`/`asset_type` unchanged — every split child inherits the origin's values instead of its item's. Owner-visible expectation (re-verify per `PG-IC-09`): frontend `AssetCard`/drawer/product tests assert `"Untitled asset"`; backend `test_sg049_v2_extraction.py:295` asserts `UNTITLED_LABEL == "Untitled"`; split coverage lives in `test_review_split.py:185`, `test_ai_pipeline.py:305,428`, `test_phase3_e2e.py:434`. **Authoring date (metadata, never a gate):** 2026-09-17. Transport: the standard job_spawn lane. Contract 0.27.0 (recorded == published payload == SG-057 receipt echo; packet states it).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** no migration (labels are constants, split fields are JSON); no new dependencies; no provider calls ($0 — a metered call is a STOP-and-report); NETWORK: loopback + container-runtime only, nothing else.
**Money posture (F2):** spend UNCAPPED-but-ledgered with re-evaluation owed; this slice makes zero provider calls so the spend line reads $0.000000 actual vs $0 bound.
**Guards invoked (0.27.0 — Architect copies these to the rating row):** `PG-EV-01` gate-seen-failing · `PG-EV-02` artifact-not-command · `PG-EV-05` property-not-command · `PG-EV-09` both-runs-committed · `PG-SC-09` name-the-world · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03` denied-is-stop · `PG-PR-04` code-becomes-live · `PG-DP-02` no-sweep-waiver.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint+build, 900s host build/up. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none.** All tests use scratch temp SQLite; no live import runs; the production SQLite is touched by nothing.

## Why this exists

Two user-visible inconsistencies, both cheap, both guarded: nameless assets read "Untitled" in AI-built labels but "Untitled asset" on screen; split children of a multi-item candidate all show the origin's quantity/unit/asset_type instead of their own item's. Neither blocks the pipeline; both erode trust in exactly the review UI the Stage-0 posture depends on.

## G1 — label unification (constant + its tests only)

- `app/models/asset.py` `UNTITLED_LABEL` → `"Untitled asset"`. `planning/service.py:153` + `chat/service.py:179` need NO hunk (they read the constant — verify, not silently added). Frontend needs NO hunk (already `"Untitled asset"` — verify served/built value, not silently added).
- Enumerate EVERY `Untitled` occurrence in backend tests + docstrings on the target and report the diff vs this expectation (constant assertion + fallback-behaviour tests + one docstring line); update exactly those, keeping every assertion they make.
- `PG-SC-09`: name the world where unifying the label is wrong (a prompt-sensitivity regression where "Untitled asset" changes extraction behaviour) and why the slice still ships (no prompt text changes — only the fallback label for nameless assets — and the extraction suite guards behaviour).

## G2 — split propagation (one function + its tests, FAIL-then-PASS `PG-EV-09`)

- `_split_child_fields`: `quantity`/`unit`/`asset_type` become item-derived with the same `_provenance` pattern as `lot` (extraction source, item confidence, call provenance); null/absent → omitted like `expiry_date`/`lot`, never guessed, never inherited. Docstring updated (it currently promises only name/expiry/lot replacement).
- FAIL-then-PASS honestly: a split test with per-item quantities/units/types DIFFERING from the origin's (and one null-valued item field) FAILS pre-hunk (children share origin's) and PASSES post-hunk (each child carries its own + null omitted); BOTH runs raw committed. Extend the existing split tests (`test_review_split.py`, `test_ai_pipeline.py:305`) rather than duplicating their scaffolding — say what was extended vs added.

## G3 — suite + lint + deploy + hygiene

- Backend suite + frontend suite + `ruff`/`eslint` + `tsc && vite build` green; only base-proven pre-existing reds permitted (cite base commit + base-run command and output, or they are new findings with destinations). Gates name files checked with counts+elapsed; silent gates FAIL.
- Deploy (backend code changed — `PG-PR-04`): rebuild + up, idempotent re-`up -d` (same container, RestartCount=0), health exact, 8003 loopback-only. Property: served frontend bundle hash UNCHANGED (no frontend hunk — distinguishes this deploy from SG-049's). Full sweep WAIVED per `PG-DP-02` (substitute = G2 red→green + targeted checks, named here).
- Prod DB untouched (no import, no writes — state the construction); no migration; dep list unchanged; secret scan n/a (no secrets touched — state it); no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-058.log`, `{{WORKLOG_DIR}}/SG-058_report.md`, `{{WORKLOG_DIR}}/SG-058_verify.log` (G2 both runs + deploy raw). First token `SG-058`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend line (**real $** $0.000000 actual vs $0 bound); three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `backend/app/models/asset.py` (label hunk) · `backend/app/services/candidates.py` (split hunk only) · `backend/tests/test_sg049_v2_extraction.py` + `backend/tests/test_review_split.py` + `backend/tests/test_ai_pipeline.py` (test hunks) + ONE new test file if needed (`backend/tests/test_sg058_*`, only if existing scaffolding cannot host the case — say why) · `docs/worklogs` (3 files). **Anything else is a STOP** — including `planning/service.py`, `chat/service.py`, any frontend file, prompts, migrations, and any new dependency.
- Every requirement above names a file the ceiling enables it; if you find one that does not, STOP and say which.
- Cross-product (`PG-IC-01`): no blanket exclusion is issued. G-hunks share no condition with any remediation step — stops win (`PG-IC-03`). Reads MAY pull/run the already-built local images only.
- Budget (uncalibrated per `G-A9`): 120s ordinary · 600s suite+lint+build · 900s host build/up · **1500s early-close** · **2400s overall** — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): one constant, one function, their tests; nothing else.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); premises re-verified in-slice with quoted reads — in particular `asset.py:8`, `product.ts:25`, `candidates.py:528-596`, the six split/label test sites.
- `Untitled` enumeration with diff vs expectation either way; frontend value verified unchanged; no hunk outside the ceiling.
- **FAIL-then-PASS honestly (`PG-EV-09`):** pre-hunk RED (children share origin quantity quoted) + post-hunk GREEN (per-item values + null omitted quoted), both raw committed.
- Suite + lint + build green (only base-proven reds); deploy targeted checks quoted (same container, RestartCount=0, bundle UNCHANGED, health exact, loopback-only); prod DB untouched; no migration; dep list unchanged; no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-058 | Report: docs/worklogs/SG-058_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), LIST the note contents and grep for this ID (log `--grep` does not match note bodies — proven twice), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint+build · 900s host build/up · 1500s early-close · 2400s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.

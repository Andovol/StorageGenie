# SG-047 — import modal: staged queue, auto-detect, real pipeline (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** Wardrobe track (D63, L3) step 5 of 5, closing the track: DQ9 import modal. Prompt 4 + DQ answers are the spec; the pipeline below is EMBEDDED from verified reads (M19 — `docs/design/DQ-answers.md` committed). **Authoring date (metadata, never a gate):** 2026-09-16. Transport: the standard job_spawn lane. Contract 0.27.0 (receipt echoes it).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no file under `backend/` is touched** (frontend-only; a needed backend change is a STOP); **no migration** (an alembic diff is a STOP); **AI stays OFF in this slice**: the modal CREATES + RUNS import jobs through the existing deterministic-first pipeline (AI legs stay consent-gated server-side as today — the slice triggers nothing model-side itself), **$0 metered** by the slice; no new dependencies; NETWORK: app API only (no npm, no registry).
**Guards invoked (0.27.0 — Architect copies these to the rating row):** `PG-EV-01` gate-seen-failing · `PG-EV-02` artifact-exists · `PG-EV-05` property-not-command · `PG-EV-09` both-runs-committed · `PG-SC-02` omission-traced · `PG-SC-05` exclude-by-rule · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live. (`PG-EV-06`/`PG-EV-08`/`PG-DP-02..04` do not fire: no live writes beyond the modal's own user-confirmed import (see G2 ledger rule), no delivery change, no entry point, no reported failure.)

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine, investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a test that never invokes the function, a grep scoped so narrowly it could not have matched — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata, never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint+build. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean. Report every issue and disagreement, including ones outside this slice's scope. End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: via the import API only (user-confirmed Process action — a live write the modal exists for; report every created job id per `PG-EV-06`, leave jobs in place). Restart: none. NETWORK: app API only.**

## Why this exists

"Import Asset" (header) and "Import New Item" (empty state) currently route to `/capture` (manual create). DQ9 gives them a real staged import: dropzone + paste + review queue + `Process N Items` driving the EXISTING import pipeline. Verified trigger shape: `POST /v1/imports` takes `{evidence_ids[], config{}}`, 201, idempotent via `Idempotency-Key` (`jobs.py:18-20,32-75`); `POST /v1/imports/{job_id}/run` executes (`jobs.py:78-85`); jobs list at `GET /v1/jobs` and the Inbox screen renders them (`InboxPage.tsx:16-26`).

## G1 — `AssetImportModal.tsx` (new, `frontend/src/components/shell/`)

- Dialog (accessible role + label, `Esc` closes, focus in/out): dropzone accepting drag-drop + file select + window paste (`Ctrl+V`/`⌘V`, same clipboard-files path SG-042 proved), client-side filter PNG/JPG/WebP with rejected files named + skipped (never silently dropped); the 25 MB figure is NAMED as the gate target (server enforces 20 MB today — the modal never promises more than the server allows, `PG-SC-02`).
- `Automatically detect items and isolate cutouts` checkbox, default ON: checked = create import AND run it; unchecked = upload evidence + create the job WITHOUT running (it sits visible in Inbox, runnable there). Both paths stated in the UI in plain words.
- Pending queue: staged files with Ready state + Remove; Cancel discards staged bytes (nothing uploaded is deleted — uploaded evidence rows stay, reported); `Process N Items` (disabled at 0, count live) uploads each via `uploadEvidence` (`client.ts:105-120`), creates ONE import with one `Idempotency-Key`, runs it iff checked, then closes and navigates to `/inbox` where the job is visible.

## G2 — open the modal from both CTAs (two gated hunks)

- Header `Import Asset` button + empty-state `Import New Item` CTA open the modal instead of routing to `/capture` (the route stays for direct navigation). Byte-diff both hunks, quote them.

## G3 — tests: new `frontend/src/components/shell/import-modal.test.tsx`, mutation proof, both runs committed

- Dropzone staging (drop + select + paste incl. rejection naming), Remove, checkbox both paths (run called / not called, job visible), `Process N Items` posts evidence_ids + idempotency key then routes to `/inbox`, Cancel discards staging, Esc closes.
- Mock the transport boundary only (`../api/client` + fetch where the component calls it); assert request SHAPES (`PG-EV-04`: the slice builds requests for an external system — here the app API — so one test asserts the exact create/run payload shape).
- **Pre-change honesty (class 8):** new module fails on unresolvable imports — quote + label hollow, never evidence. Discriminating proof is a post-change mutation run (2–3: the checkbox branch, the idempotency header, the queue count — each caught singly, reverted clean, raw committed).
- Full frontend suite green, lint clean, build clean — the §3 conditional derived-test-set block is NOT pasted.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-047.log`, `{{WORKLOG_DIR}}/SG-047_report.md`, `{{WORKLOG_DIR}}/SG-047_verify.log` (hollow labeled, mutations raw). First token `SG-047`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line (`$0` slice-metered; any job created is reported by id and LEFT running/pending — never cancelled by the slice); three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `frontend/src/components/shell/AssetImportModal.tsx` (new) · `frontend/src/components/shell/import-modal.test.tsx` (new) · `frontend/src/components/shell/AppHeader.tsx` (CTA hunk only) · `frontend/src/components/catalog/ProductGrid.tsx` (empty-CTA hunk only) · `docs/worklogs` (3 files). **Anything else is a STOP** — including every file under `backend/` (excluded BY RULE per `PG-SC-05`, grep-gated), the Capture route (stays), and any new dependency.
- Every requirement above names a file the ceiling enables it; if you find one that does not, STOP and say which.
- Cross-product (`PG-IC-01`): G1 the modal + test files; G2 the two CTA hunks; G3 the test file; G4 worklogs. No blanket exclusion is issued. No stop-gate shares a condition with a remediation step (`PG-IC-03`) — stops win, stated not assumed.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. `PG-EV-01`: mutations fed wrong values in the same run, shown failing singly. `PG-EV-02`: rendered DOM / committed outputs + the asserted request shapes, never exits. `PG-EV-05`: properties ("rejected files are named", "unchecked creates without running", "Process posts evidence_ids + idempotency key then routes to /inbox").
- Budget (uncalibrated per `G-A9`): 120s ordinary · 600s suite+lint+build · **1500s early-close** · **2100s overall** — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): modal + two CTA hunks; nothing else.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); premises verified in-slice with quoted reads — in particular `jobs.py:18-20,32-85`, `client.ts:105-120`, the two CTA sites, `InboxPage.tsx:16-26`.
- **FAIL-then-PASS honestly (`PG-EV-09`):** hollow run labeled hollow; green run; mutation run caught-singly + reverted; all three raw committed.
- Suite + lint + build green; secret scan 0; no `backend/` diff; no migration; dep list unchanged; created job ids reported and left in place (`PG-EV-06`); no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.
- No UI text promises beyond what exists (25 MB named as target with the server cap disclosed; unchecked path states the job waits in Inbox).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: created job ids (by id, left in place), live spend `$0` slice-metered, network = app API only.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-047 | Report: docs/worklogs/SG-047_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly (`<ref>:<ref>`, M21 — a bare fetch never updates a notes ref), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint+build · 1500s early-close · 2100s overall; $0 metered (+ live job ids reported, never cancelled); actual-versus-budget per leg with units.

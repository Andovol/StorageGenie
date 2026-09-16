# SG-051 — test-truth: stale CTA tests assert the dialog (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** D68 micro-slice: two tests pass vacuously re: clicks since SG-047 rerouted both CTAs to the import modal. Verified stale lines: `shell.test.tsx` tail test "Import Asset routes to /capture" asserts `href="/capture"`; `catalog.test.tsx:207-210` test "an empty result shows the dashed canvas with the Import New Item CTA to /capture" asserts the same. Product code (`AssetImportModal` interception in `AppHeader` + `ProductGrid`) is correct and untouched. **Authoring date (metadata, never a gate):** 2026-09-16. Transport: the standard job_spawn lane. Contract 0.27.0 (receipt echoes it).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no file under `backend/` is touched** (test-only slice; any product change is a STOP); **no migration**; **AI stays OFF**, **$0 metered**; no new dependencies; NETWORK: none.
**Guards invoked (0.27.0 — Architect copies these to the rating row):** `PG-EV-01` gate-seen-failing · `PG-EV-02` artifact-exists · `PG-EV-05` property-not-command · `PG-EV-09` both-runs-committed · `PG-SC-05` exclude-by-rule · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine, investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a test that never invokes the function, a grep scoped so narrowly it could not have matched — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata, never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint+build. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean. Report every issue and disagreement, including ones outside this slice's scope. End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none. Restart: none. NETWORK: none.**

## Why this exists

SG-047 rerouted both import CTAs to the modal via `Link` interception, leaving two tests asserting the retired `href` behaviour. They pass while proving nothing about the click. This slice rewrites exactly those two tests to assert the dialog opens and `/capture` does not render. No product file changes.

## G1 — rewrite the two stale tests (hunks only, same files)

- `shell.test.tsx` "Import Asset routes to /capture" → clicks the trigger, asserts the import dialog appears (role/label per the modal component) and no `/capture` route renders. Rename the test to what it proves.
- `catalog.test.tsx:207-210` empty-state CTA test → same dialog-open assertion on the grid's CTA.
- Nothing else in either file changes; no product file is touched (a needed product change is a STOP, not a silent edit).

## G2 — FAIL-then-PASS with a genuine FAIL half, both runs committed

- FAIL leg: temporarily revert the two interception hunks (stash or checkout the two product hunks only — product tree otherwise intact), run the two rewritten tests → they FAIL (dialog never opens); restore byte-identical (`diff` proof), commit the fail leg. This is a real behavioural FAIL, not an import hollow — label it as such.
- Green run: full frontend suite + lint + build, all green, committed raw. The §3 conditional derived-test-set block is NOT pasted.
- Mutation run optional: if the FAIL leg already falsifies both tests, no separate mutation is owed — say so explicitly with the two failure outputs quoted.

## G3 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-051.log`, `{{WORKLOG_DIR}}/SG-051_report.md`, `{{WORKLOG_DIR}}/SG-051_verify.log` (both runs raw). First token `SG-051`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line (`$0`); three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `frontend/src/components/shell/shell.test.tsx` (one-test hunk) · `frontend/src/components/catalog/catalog.test.tsx` (one-test hunk) · `docs/worklogs` (3 files). **Anything else is a STOP** — including every file under `backend/` (excluded BY RULE per `PG-SC-05`, grep-gated) and every product file (test-only slice; the temporary intercept revert is reverted byte-identical in-slice with `diff` proof, never committed as a product change).
- Every requirement above names a file the ceiling enables it; if you find one that does not, STOP and say which.
- Cross-product (`PG-IC-01`): G1 the two test hunks; G2 the verify log; G3 worklogs. No blanket exclusion is issued. No stop-gate shares a condition with a remediation step (`PG-IC-03`) — stops win, stated not assumed.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. `PG-EV-01`: the FAIL leg shows both rewritten tests failing on the reverted tree. `PG-EV-02`: rendered dialog / committed outputs, never exits. `PG-EV-05`: properties ("click opens the dialog", "`/capture` does not render on CTA click").
- Budget (uncalibrated per `G-A9`): 120s ordinary · 600s suite+lint+build · **1500s early-close** · **2100s overall** — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): two test rewrites; nothing else.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); the two stale lines verified in-slice with quoted reads.
- **FAIL-then-PASS (`PG-EV-09`):** FAIL leg (reverted intercepts, both tests red) + green run, both raw committed; intercept restoration proven byte-identical.
- Suite + lint + build green; secret scan 0; no product-file diff in the final tree (`git diff` names only the two test files + worklogs); no `backend/` diff; no migration; dep list unchanged; no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.
- Both rewritten tests assert dialog-open behaviour, never the bare `href`.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: no DB writes, live spend `$0`, no network.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-051 | Report: docs/worklogs/SG-051_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly (`<ref>:<ref>`, M21 — a bare fetch never updates a notes ref), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint+build · 1500s early-close · 2100s overall; $0 metered; actual-versus-budget per leg with units.

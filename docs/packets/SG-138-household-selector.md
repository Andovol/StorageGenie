# SG-138 — Land #4's HouseholdSelector extraction without its preview.log, plus a *.log ignore

**Settings travel on the trigger** (`SG-138 coder=opencode effort=high`, D8) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.40.0).

**Context and standing lines.** D8-authorized rewrite (owner quote "D8 - approved"; SG-134 verdict REWRITE-AS-SLICE on PR #4, head `e6a4f25`, base `33460cd`): #4 extracts a reusable `HouseholdSelector` across 5 pages — genuinely equivalent (SG-134 §1b case analysis) — but commits `frontend/preview.log` (vite `preview` stdout, NOT gitignored) and so cannot land as-is. THIS slice ports the 7 source files, drops the artifact, and ignores `frontend/*.log` at the root. Source files = the PR head's set minus the artifact (re-verify on the target; a changed head is a STOP): `frontend/src/components/HouseholdSelector.tsx` (new) + `HouseholdSelector.test.tsx` (new, 59 lines) + `CapturePage.tsx` + `CatalogPage.tsx` + `ChatPage.tsx` + `InboxPage.tsx` + `PlanningPage.tsx`. Equivalence spec, embedded from SG-134 §1b (re-verify each against the tree — a difference is a finding): CatalogPage renders the "No households" empty option ONLY when the list is empty (`emptyOptionLabel` conditional, `""` falsy) + `showLabel={false}` bare `<select>` (base had no label) · CapturePage has NO empty option (`""`) + `labelStyle={{fontSize:13}}` + `selectStyle={{padding:6,borderRadius:6,marginLeft:6}}` verbatim · Chat/Planning/Inbox render `Household {select}` via defaults (`showLabel=true`, `emptyOptionLabel="Select household"`) + `onChange` writes `household_id` to `localStorage`. The `households as Household[] | undefined` cast is noise (keep or drop — decide, report). **Authoring date (metadata, never a gate):** 2026-09-28. Transport: the standard job_spawn lane. Contract: recorded `0.40.0` == published (`f26dbd3`, D4 adoption); host link from SG-137's echo (`0.40.0` from `/home/andrei/storagegenie-contract/VERSION`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** REWRITE slice. Writes: the 7 ported files + root `.gitignore` (`frontend/*.log` line ONLY — any other ignore change is a STOP) + `docs/worklogs` (3 files) — and NOTHING else. `frontend/preview.log` is NEVER created (if a `vite preview` probe runs, its stdout stays in the log, never a file — and `git status` must show no `.log` file at end). No merge/close/rebase of PR #4 here (workstation closes it after landing). No backend, no migration. Vitest via `node_modules/.bin/vitest` (`npx` absent — SG-135 F4). No secret in fixtures (`CO-100` — assert it).
**Money posture:** REAL metered $0.000000 USD bound (no USD-metered call exists on any path). `PG-PR-06` stated upfront; actual-versus-budget per leg with units in the report.
**Guards invoked (0.40.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-10` · `PG-SC-02` · `PG-SC-09` · `PG-SC-10` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite, 2400s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none. Restart: none. Deploy: none.**

## G0 — read the head, confirm the port set (reads only — stated, not solved)

- Diff the head against the tree; confirm the 8-file set (7 sources + artifact) and that the 7 sources' hunks still apply to the current tree (SG-135/136/137 touched no page files — VERIFY, never inherit). A hunk that no longer applies is adapted by hand and reported line-by-line, never force-merged.
- Confirm `frontend/preview.log` exists in NEITHER the tree NOR the port (grep + `git check-ignore` quoting the new `frontend/*.log` rule as IGNORED — `PG-SC-10`: the ignore line must cover the artifact path or the rule is decoration).

## G1 — port + prove equivalence (no fail-pre red exists — stated, not hidden)

- Port the 7 files + the ignore line. No fail-pre red is demanded: this is a behaviour-preserving extraction, so green/green with the mapping proof below is the correct shape (a manufactured red would prove the harness, never the equivalence).
- Equivalence proof, per page (behaviour-preservation rail — identical output per site): the ported `HouseholdSelector.test.tsx` green + every page test file covering the five routes green via vitest (name each file + result; `CO-101`) + the prop-mapping table (page → emptyOption/showLabel/styles/onChange) quoted against the shipped code. A page whose rendered output cannot be tied to a passing test is reported UNPROVEN for that page, never covered by the suite's overall green.
- Full frontend suite green-except-base-proved-reds if in-bound (reds stash-reproved on bare BASE); else UNRUN + file-level greens as shipped proof. `eslint` on touched files exit 0. `git status` shows NO `.log` file anywhere.

## G2 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-138.log`, `SG-138_report.md`, `SG-138_verify.log` (port table + mapping table + test captures + ignore proof + no-log status). First token `SG-138`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend **real $** $0.000000 USD + zero metered calls; contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** WRITES — the 7 ported files + the single ignore line + the 3 worklog files. **Any other write — `preview.log` creation, product behaviour change, backend, merges, closes — is a STOP.**
- Cross-product (`PG-IC-01`): G0 needs diff reads (reads INCLUDE `git` network reads; `gh` is known-absent — touching it is a STOP); G1 needs the port + vitest runs (modify-versus-call: tests CALL the real component/pages through vitest); G2 needs the worklog commit + notes receipt. Per-command-class bounds (120s ordinary / 600s suite / 2400s overall), never one blanket timeout. No criterion demands what the ceiling forbids — stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): port the seven, ignore the log, prove the mapping. No prop-API redesign, no test-framework changes, no page-behaviour tweaks — however small.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): ported — are all 7 files' hunks present with no `preview.log` and the ignore rule catching its path? equivalent — does every page map to identical rendered output under passing tests? clean — is the diff exactly 7 sources + 1 ignore line + worklogs?
- Port table quoted + mapping table quoted + ported + page tests green quoted + full-suite quoted-or-UNRUN + `check-ignore` IGNORED proof + `git status` no-log proof + $0.000000 USD; no vacuous pass (an unread head, an unmapped page, or a suite silence read as green evidences nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000 USD + zero metered calls. Actual-versus-budget per goal with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-138 | Report: docs/worklogs/SG-138_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite · 2400s overall; expected ~900s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S=2100`); REAL metered $0.000000 USD + zero metered calls; actual-versus-budget per goal with units.

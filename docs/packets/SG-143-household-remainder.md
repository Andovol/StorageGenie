# SG-143 — Port the 3 blocked HouseholdSelector pages (className passthrough, L3 word carried)

**Settings travel on the trigger** (`SG-143 coder=opencode effort=high`, L3 finish chain P1) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.40.0).

**Context and standing lines.** L3 finish-chain slice 2 of 5 (design `docs/superpowers/specs/2026-09-29-roadmap-finish-design.md`, plan `docs/superpowers/plans/2026-09-29-roadmap-finish.md`): SG-138 shipped the selector subset and STOPped on 3 pages (`docs/worklogs/SG-138_report.md:33-77,134-139`). Architect re-verified 2026-09-29 on the post-SG-142 tree: `frontend/src/components/HouseholdSelector.tsx` is 50 lines with props `value/onChange/households/showLabel/labelStyle/selectStyle/emptyOptionLabel/id` and NO `className` prop; `CapturePage.tsx:30` and `InboxPage.tsx:33` selects carry `className={THEMED_CONTROL_CLASS}`; `CatalogPage.tsx:197-260` renders no household select (delegates to `AppShell` → toolbar); `ChatPage.tsx:79` + `PlanningPage.tsx:71` already use the shared selector. **The className-prop API word rides this L3 chain — the choice below is stated, never re-asked.** THIS slice adds the passthrough prop and ports all 3 blocked call-sites with byte-identical output. **Authoring date (metadata, never a gate):** 2026-09-29. Transport: the standard job_spawn lane. Contract: recorded `0.40.0` == published (`f26dbd3`, D4 adoption); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** PORT slice. Writes: `HouseholdSelector.tsx` (the passthrough prop ONLY), the 3 call-sites (`CapturePage.tsx`, `InboxPage.tsx`, `CatalogToolbar.tsx` — expected; enumerate the real set on the target and report any difference either way), frontend tests, `docs/worklogs` (3 files) — and NOTHING else. Served code changes so this slice owns its refresh per D145: rebuild + exactly ONE recreate + verify (production restart, carried by the L3 stage approval + D145 standing). No secret in fixtures (`CO-100` — assert it).
**Money posture:** REAL metered $0.000000 USD bound (no USD-metered call exists on any path). `PG-PR-06` stated upfront; actual-versus-budget per leg with units in the report.
**Guards invoked (0.40.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-EV-09` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06`.

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

**DATABASE: none. Restart: exactly one recreate of the served stack (D145 owned refresh). Deploy: rebuild + one recreate + verify, this slice.**

## G0 — equivalence map on BASE (committed — the fail-pre shape for a behaviour-preserving port)

- For EACH of the 3 call-sites, quote the current select markup verbatim (expectation: Capture/Inbox labelled select with `className={THEMED_CONTROL_CLASS}` + `CONTROL_STYLE` + `localStorage` write; Catalog toolbar select at `CatalogToolbar.tsx` — differenced either way, re-map never force-applies) plus the guarding test assertion (`theme-adoption` Capture block, `InboxPage.test` block — VERIFY the line numbers on the target, never inherit them).
- A call-site whose markup no longer matches is a finding: re-map it, and if the port becomes impossible inside the ceiling, STOP that call-site and ship the rest with the STOP committed.
- Commit the map BEFORE any edit — a port without a committed BASE map proves nothing.

## G1 — add the prop + port all 3 call-sites (both runs committed)

- `HouseholdSelector` gains an optional passthrough for the select's class (expected name `selectClassName`, default unset so Chat/Planning output is byte-identical — DECIDE the exact prop and report; old props stay byte-compatible, no other API change).
- All 3 call-sites render through the shared component with output IDENTICAL to the G0 map (per-page mapping table, quoted). The two themed-class tests stay green UNCHANGED — a red there is a regression, never a test to update.
- Prove it through the real configs (`PG-SC-12`): `tsc --noEmit` exit 0 quoted in full; the touched files' vitest green; FULL frontend suite green-except-base-proved-reds (reds, if any, stash-reproved on bare BASE); `eslint` on every touched file exit 0. Backend suite NOT re-run (backend diff empty — state the empty diff as the reason, never silence).

## G2 — serve it: rebuild + exactly ONE recreate + verify (`PG-PR-04`, `PG-EV-08`)

- BEFORE the recreate, capture the served bundle marker (read-only) and quote it — a served claim without a BEFORE capture evidences nothing.
- Rebuild, exactly ONE recreate (container-id change is the proof, never RestartCount), health ×6 exact, gate 301/401, alembic head unmoved, table counts delta exactly zero, the 3 pages 200 through the fresh server with the household select present in served output.
- AFTER bundle marker quoted: it moves exactly by the SG-143 build (name the marker delta).

## G3 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-143.log`, `SG-143_report.md`, `SG-143_verify.log` (G0 map + G1 runs + G2 captures, diff ceiling proof). First token `SG-143`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend **real $** $0.000000 USD + zero metered calls; contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** WRITES — the selector prop + the 3 call-sites + frontend tests + the 3 worklog files. **Any other write — other components, backend, config, other tests — is a STOP.** Reads: the tree, suites, one image rebuild + one recreate (D145). Pulling/running the service image for the owned refresh counts as authorized execution.
- Cross-product (`PG-IC-01`): G0 needs markup reads + test-assertion reads (120s class); G1 needs the prop edit + 3 call-site edits + typecheck + suites — modify-versus-call: vitest CALLS the real component through its real config (600s class); G2 needs rebuild + recreate + served captures (the authorized production restart — `PG-PR-03` stated: a denial stops the slice, never routes around); G3 needs the worklog commit + notes receipt. Per-command-class bounds (120s ordinary / 600s suite / 2400s overall), never one blanket timeout. No criterion demands what the ceiling forbids — stated so the check exists on paper.
- `PG-PR-10`: no live-production write is asked for anywhere — resolution is temp/test plus served reads; the recreate is the only production mutation and rides D145 + the L3 stage approval.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): add the prop, port the markup, serve it. No toolbar redesign beyond the call-site, no hook changes, no style-token changes — however small.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): mapped — is every call-site's output identical to its committed BASE block through the shared component? guarded — are both themed-class tests green unchanged? typed — is `tsc --noEmit` exit 0 with the full suite green? served — new bundle live (container-id change + marker delta) with counts delta zero? clean — is the diff exactly prop + call-sites + tests + worklogs?
- G0 map quoted from the commit + G1 runs quoted + G2 BEFORE/AFTER captures + $0.000000 USD; no vacuous pass (a suite silence read as green, a prop that changes Chat/Planning output, or a toolbar rewrite beyond the call-site evidences nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000 USD + zero metered calls. Actual-versus-budget per goal with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-143 | Report: docs/worklogs/SG-143_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite · 2400s overall; expected ~900s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S=2100`); REAL metered $0.000000 USD + zero metered calls; actual-versus-budget per goal with units.

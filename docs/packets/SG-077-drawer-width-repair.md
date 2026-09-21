# SG-077 — inspector drawer panel width repair (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** D99-approved defect repair (owner-reported, root-caused by the Architect in-tree, no guessing). `frontend/src/components/shell/ItemInspectorDrawer.tsx:17` sizes the drawer panel with `EMPTY_PANEL = "max-w-2xl w-full border-l border-border bg-card p-6 overflow-y-auto z-50"` — Tailwind classes in a project WITH NO Tailwind (verified: no tailwind dependency, `tokens.css` defines no `max-w-2xl`/`w-full`). The fixed-position `aside` therefore gets no usable width; the `aspect-ratio: 1/1` viewer well blows up to viewport scale and pushes every field below the fold — the owner sees a giant photo and "no information". THIS slice constrains the panel with project-native CSS only. **Authoring date (metadata, never a gate):** 2026-09-21. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published (`b495b59`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** frontend ONLY — one component + its test. No backend, no migration, no secrets, no provider calls ($0). No deploy, no restart (`PG-PR-04` stated — ships on a later rider). NETWORK: none (prove it).
**Money posture:** $0.000000 actual vs $0 bound.
**Guards invoked (0.28.2 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-06` (authority: NONE) · `PG-EV-09` · `PG-SC-02` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` (NO DEPLOY stated).

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite/build, 1800s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none. Restart: none. Deploy: none.**

## G1 — constrain the drawer panel (project-native CSS only)

- Replace the dead Tailwind width classes on the `aside` with a REAL width constraint the project's CSS honors: an explicit inline `maxWidth` (e.g. capped well under viewport) and/or a `tokens.css` utility if one fits — additive only, never a framework. The viewer well keeps `aspect-ratio: 1/1` but must NEVER exceed the panel: cap it (max-height / contained) so the photo, metadata, tabs and fields all fit without page-scale blowup. No new dependency, no Tailwind, no CDN.
- FAIL-then-PASS: a render test asserting the panel carries a bounded width (computed/inline `maxWidth` present and sane — not `"none"`/absent) and the viewer well is contained. Pre-change run fails (no width constraint — quoted raw, committed); post-change passes. The existing `drawer.test.tsx` suite stays green UNCHANGED (behavior untouched — a behavior-test edit is a STOP-and-report).
- Enumerate every OTHER Tailwind-shaped class in the file (`max-w-*`, `w-full`, `z-50`, etc. — criterion: class names no stylesheet in this project defines) and either replace each with a working equivalent or report it as intentional-dead with its reason. Silence is not coverage.

## G2 — what must NOT change

- Same drawer, same tabs, same fields, same handlers, same PATCH shape, same copy. Zero behavior change: the full existing drawer + shell suites pass UNCHANGED.
- `npm run build` green (quoted) + `npx vitest run` on the drawer/shell suites green (quoted). Secret scan 0.

## G3 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-077.log`, `SG-077_report.md`, `SG-077_verify.log` (raw test/build outputs + BOTH fail-then-pass runs). First token `SG-077`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `frontend/src/components/shell/ItemInspectorDrawer.tsx` · its test file (`drawer.test.tsx` — presentation asserts may be ADDED, behavior asserts untouched) · `frontend/src/theme/tokens.css` (additive utility ONLY if the width needs one, hunk quoted with reason) · `docs/worklogs` (3 files). **Anything else is a STOP** — backend, other components, `App.tsx`, deps, compose, `.env`, migrations.
- Cross-product (`PG-IC-01`): G1 needs the drawer file + its test; nothing else. No criterion touches the backend or the network.
- Angle-token standing line: any in-scope file carrying `<...>` literals is re-probed by char codes after editing; tests constructing such strings build them from character codes (SG-062 lineage).
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).
- Simplicity (`G-A7`): a width constraint + a well cap + dead-class enumeration; no drawer redesign, no new component.

## Acceptance criteria

- Panel carries a bounded, project-honored width (test fail-pre → pass-post, raw both sides); viewer well contained (photo cannot exceed panel); every other dead-framework class in the file replaced or individually justified.
- Existing drawer/shell suites green unchanged; build green; secret scan 0; $0; no backend diff; no new dependency; no network; no vacuous pass.
- No migration; no deploy claimed.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-077 | Report: docs/worklogs/SG-077_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite/build · 1800s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.

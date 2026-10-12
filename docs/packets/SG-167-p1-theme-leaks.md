# SG-167 — P1 theme leaks: Chat HouseholdSelector + Inbox Resolve button

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` named here: derived set = `frontend/src/routes/ChatPage.test.tsx` + `frontend/src/routes/InboxPage.test.tsx` (run by file; full suite waived with substitute below).

Autonomy: L2 (project standing; 1 retry; D-1012-5, owner quote "Approved."). No spend ($0 — no metered call exists on any path; a metered call is a STOP-and-report). Exits with both leaks themed + targeted tests green, unserved. Contract: recorded 0.46.0 == published payload (tag contract-v0.46.0; G-L1 CURRENT 2026-10-12 session-start, installed 487841b1) == host 0.46.0 (SG-166 echo from /home/andrei/storagegenie-contract/VERSION) — echo verbatim + source path. Authoring date (metadata, never a gate): 2026-10-12.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

**BASE REF: automation.** Resolved commit goes in the report, never here.
**DATABASE: none.** No datastore touch of any kind (a live query is a STOP-and-report).
**Restart: none.** Served code changes but the running service is untouched → no refresh (D145); serving rides a later close-out deploy, never this slice (state this explicitly in the report).

## Why this exists

Owner-verified UI audit (6 screenshots, 2026-10-12) found two native-white leaks in the dark theme. ISS-2: `ChatPage.tsx:79-86` renders `<HouseholdSelector>` with NO `selectStyle`/`selectClassName`, so the select falls back to the browser-default white control — every other route passes `CONTROL_STYLE` + `THEMED_CONTROL_CLASS` (`InboxPage.tsx:34`, `CapturePage.tsx:36-37`, `ExpiryPage.tsx:123-142`; pair defined `CatalogToolbar.tsx:63-72`). ISS-3: `InboxPage.tsx:46` renders the review-queue `Resolve` `<button>` with NO className — the only unthemed button in the tree (white bg, black text on dark). Both confirmed on screenshots (white Household select on /chat; white Resolve on /inbox). No backend, no taxonomy, no Inbox copy changes — theming only.

## G1 — theme both leaks via the shared pair

G1a Chat: pass `selectStyle={CONTROL_STYLE}` + `selectClassName={THEMED_CONTROL_CLASS}` (imports from `../components/shell/CatalogToolbar`, CapturePage precedent) into the Chat `HouseholdSelector`; no other Chat hunk. G1b Resolve: give the `Resolve` button the shared themed treatment both its neighbours already carry — decide inside these constraints whether that is exactly `CONTROL_STYLE` + `THEMED_CONTROL_CLASS` (CatalogToolbar pair) or the file's existing button language, and report the choice with its reason; no other Inbox hunk. Criterion, not a list: after the slice, NO bare `<select>` or `<button>` without a theme class remains on either route — enumerate all selects/buttons on both routes ON THE TARGET and report the enumeration with the difference either way. No new vocabularies, no copy changes, no layout changes.

## Constraints

Scope ceiling: `frontend/src/routes/ChatPage.tsx` + `frontend/src/routes/InboxPage.tsx` + their two test files + `docs/worklogs/SG-167_*`; nothing else moves (a third product file is a STOP-and-report). Secrets: none involved. Spend: $0. Publish-before-bound: report + receipt before 1050s elapsed (half of `RUN_BUDGET_S=2100`, standing lever). Expected duration ~300s (SG-161..164 merge slices were 2–5 files unserved; this is 2 files; lane enforces `RUN_BUDGET_S`). Hang bounds: ordinary 120s, suite/file runs 600s — none near the 900s idle kill. Cross-product (PG-IC-01): no blanket bans; the ceiling's two route files are exactly what every criterion touches. Full suite waived (2-file presentation change; substitute = derived 2-file vitest + `tsc --noEmit` + eslint on the touched files, all quoted). No served-code proof demanded: the running service is deliberately untouched; the report states the tree is unserved and names the close-out deploy as the serving vehicle.

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout. **Name the bound in the packet** — 120s is
> a reasonable default for ordinary commands, and a build, a test suite or a migration gets the bound its
> own work needs. **A command producing no observable progress within its bound is killed and reported.**
> **No bound reaches the lane's idle kill (`IDLE_KILL_S`, default 900 s):** a run printing nothing for
> that long is killed whole. Run longer work in the background and check it with short calls.
> Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure
> to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Acceptance criteria

- A1: Chat Household select renders with the shared themed pair (assert the select's className carries the themed control class in the real `ChatPage` render — PG-SC-12, the consumer's bytes, not a unit copy); no other Chat hunk (diff proves).
- A2: Resolve button renders themed (assert className in the real `InboxPage` render); route-wide enumeration of selects/buttons on both routes shows zero unthemed left, reported with the list.
- A3: derived set green by file (`ChatPage.test.tsx` + `InboxPage.test.tsx`) + `tsc --noEmit` + eslint on touched files, all quoted; fail-then-pass where behaviour changed (pre-change run shows unthemed, post shows themed), BOTH runs committed (PG-EV-09).
- A4: SG-167 report + notes-ref receipt read back on remote (Dispatch-ID trailer + Work-HEAD, mapped fetch); publish-before-bound honored with elapsed quoted; production writes = none (stated, with the unserved-tree statement).
- A5: guards invoked: PG-EV-02, PG-EV-09, PG-SC-12, PG-IC-01, PG-IC-07, PG-IC-09.

## Report

Echo `SG-167` as the first token. Destinations: `docs/worklogs/SG-167_report.md` + fail/pass logs. Close with FIRST READ / DURING EXECUTION / REMAINING.

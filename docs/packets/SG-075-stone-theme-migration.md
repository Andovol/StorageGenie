# SG-075 — site-wide Stone theme migration: every screen onto the token system (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** D96-approved design slice (owner: "very nice and functional"). The live UI renders browser-default styling with hardcoded inline colors (measured 2026-09-21: the ONLY hex literals in `frontend/src` outside `theme/` sit in `App.tsx` — 6 hits; every other screen leans on unstyled defaults, which is exactly the "plain html" the owner reported). The Stone token system is BUILT, tested, and wired but unused: `frontend/src/theme/tokens.css` (utility classes `bg-card`, `text-foreground`, `border-border`, badges, `focus-ring`, font stacks), `ThemeProvider` + pre-hydration theme script in `main.tsx`/`index.html`. `ThemeToggle`/`useTheme` are imported NOWHERE — dark mode is unreachable in the UI. THIS slice migrates all 9 routes + all shared components + the App nav onto the tokens, surfaces the toggle in the nav, and brings consistent spacing/typography/focus discipline — NO behavior change, NO new screens, NO backend. **Authoring date (metadata, never a gate):** 2026-09-21. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published (`b495b59`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** frontend ONLY. No backend, no migration, no `.env`, no secrets, no provider calls ($0). No deploy, no restart (`PG-PR-04` stated — visual proof rides the later owner-gated rider + the owner's own eyeball). NETWORK: none (prove it).
**Money posture:** $0.000000 actual vs $0 bound.
**Design authority:** token + spacing + typography calls inside these constraints are yours (decide and report); BEAUTY is the owner's on the deploy — ship tastefully, not safely. No behavior change: every route keeps its elements, order, copy, and handlers; only presentation moves.
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

## G1 — token migration, every screen (no behavior change)

- Migrate ALL 9 routes (`AnalyticsPage`, `AssetDetailPage`, `CapturePage`, `CatalogPage`, `ChatPage`, `InboxPage`, `PlanningPage`, `ReviewPage`, `SettingsPage`), the App nav, and every shared component they render onto `tokens.css` utilities (`bg-background/bg-card/bg-card-muted/bg-muted/bg-primary`, `text-*`, `border-border`, `badge-*`, `font-sans/font-mono`, `focus-ring`). Hardcoded hex/rgb literals: ZERO outside `theme/` + tests when done (grep-gated — the pre-change grep is quoted; `App.tsx`'s 6 hits are the known seed).
- Where a needed utility does not exist (spacing scale, card radius, page-header pattern), EXTEND `tokens.css` additively with a comment naming the addition — never restyle by one-off inline values. Token-file edits are reported hunk by hunk.
- Enumerate the component set on the target (criterion: files under `frontend/src/routes` + `frontend/src/components` + `App.tsx` rendering user-visible markup) and report any file deliberately left unmigrated with its reason — silence is not coverage.
- Surface `ThemeToggle` in the App nav (it exists, tested, unreachable). Clicking it must flip the `dark`/`light` document class AND persist (`sg-theme`) — proved by a real interaction test, not a render snapshot.

## G2 — proof without a browser (stated composition)

- No headless browser exists on the box, so visual proof composes from three legs, stated not blurred: (1) per-screen tests asserting themed landmarks (each route's header/nav/card carries a token class — FAILS pre-change where screens are unstyled, quoted raw, committed); (2) the token-adoption grep (zero hardcoded literals outside `theme/`+tests); (3) `npm run build` + full `vitest` green. BEAUTY itself is owner-judged on the deploy rider — this slice proves ADOPTION, never taste.
- Full backend suite untouched and unrun (no backend file may change — a backend diff is a STOP); `ruff`/`mypy` not applicable; `eslint` clean; `tsc --noEmit` clean; secret scan 0.

## G3 — what must NOT change

- Zero behavior change: same routes, same elements, same order, same copy, same handlers, same API calls. Any test asserting behavior (not presentation) stays green UNCHANGED — a behavior-test edit is a STOP-and-report (presentation tests may be extended, each edit with reason).
- No new runtime dependency, no font/CDN fetch (system stacks only — the tokens' choice), no `.env`, no compose, no backend, no migration.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-075.log`, `SG-075_report.md`, `SG-075_verify.log` (raw suite/build/grep outputs + BOTH fail-then-pass runs). First token `SG-075`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines. The report ALSO carries a screen-by-screen adoption table (file → token classes applied → test proving it) so the audit never re-derives coverage.

## Constraints

- **Scope ceiling:** `frontend/src/routes/` · `frontend/src/components/` · `frontend/src/App.tsx` · `frontend/src/theme/tokens.css` (additive utilities only) · frontend test files the derived set names (presentation tests may be EXTENDED, each edit with reason; behavior tests untouched) · `docs/worklogs` (3 files). **Anything else is a STOP** — backend, `main.tsx`, `index.html`, `ThemeProvider.tsx`, `package.json`/deps, compose, `.env`, migrations, prompts.
- A set is a fact too: STATE the migration criterion and ENUMERATE the file set on the target — your enumeration, difference from my 27-file expectation reported either way.
- Cross-product (`PG-IC-01`): G1 needs read-write on screens + tokens; G2 needs the test files + build. No criterion touches the backend or the network. Reads MAY pull/run the already-built local images only.
- `npm run build` green (quoted) + `npx vitest run` (600s) green + `eslint` clean + `tsc --noEmit` clean. Secret scan 0.
- Angle-token standing line: any in-scope file carrying `<...>` literals is re-probed by char codes after editing; tests constructing such strings build them from character codes (SG-062 lineage).
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).
- Simplicity (`G-A7`): classes onto existing tokens, additive utilities only where missing, one toggle surfaced; no new design framework, no component library, no custom CSS architecture.

## Acceptance criteria

- Zero hardcoded color literals outside `theme/` + tests (grep quoted both sides); every enumerated screen file migrated or explicitly excepted with reason.
- Per-screen themed-landmark tests fail-pre → pass-post (raw both sides, committed); toggle interaction test flips class + persists; behavior tests green unchanged.
- Build + vitest + eslint + tsc green (quoted); secret scan 0; no backend diff; no new dependency; no network (prove it); $0; no vacuous pass.
- No migration; no deploy claimed; visual sign-off explicitly deferred to the owner on the rider.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-075 | Report: docs/worklogs/SG-075_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite/build · 1800s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.

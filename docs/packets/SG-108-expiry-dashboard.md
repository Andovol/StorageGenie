# SG-108 — Expiry dashboard: /expiry route + nav reading the SG-107 engine, owns its refresh ($0, opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D143 L3 Arc B slice 2 of 3 (engine GREEN 98 → dashboard → calibration; one retry/slice; D150 run-to-completion: packetize, dispatch, audit, rate, chain — no per-slice words). D143 dashboard scope: blueprint §11.2 screen 7 urgency view (expired/this-week/this-month/safe) + new `/expiry` route + nav + category filter + household scoping; in-app only, no sender. SG-107 shipped the engine (`GET /v1/plugins/expiry-tracker/status`, image `8dce9eb2`, live 200/404/422 — re-verify, never inherit). THIS slice builds the page that reads it + serves it (first frontend-served slice owning its refresh under D145). NO backend changes (prove by empty diff over `backend/` — any backend hunk is a STOP), NO migration, NO sender/scheduler, NO opened-date stream. F-SG107-1 answered HERE (see G2). F-SG105-3/4/5/6 stay open: no `ProductCard` hunks, no link-token changes, no other-route width changes — PageContainer + themed tokens + `THEMED_CONTROL_CLASS` only. $0 — no metered call exists on any path (a metered call is a STOP-and-report). **Authoring date (metadata, never a gate):** 2026-09-24. Transport: the standard job_spawn lane. Contract: recorded `0.33.0` == published (`b232b84`; D129 adoption, G-L1 clean 2026-09-24); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** dashboard ONLY. New `routes/ExpiryPage.tsx` + test + `api/client.ts` fetcher + `api/types.ts` types + `App.tsx` nav/route hunks + shell-test nav update (7 content paths counting `docs/worklogs`) — NOTHING else (`backend/` empty diff or STOP; no `CatalogPage`/`ProductCard`/token hunks). Exactly ONE recreate. Key NAMES only; `docker compose config` FORBIDDEN (`PG-SC-05`).
**Money posture:** $0.000000 actual vs $0 bound — no metered call exists on any path.
**Guards invoked (0.33.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-EV-09` · `PG-SC-02` · `PG-SC-05` · `PG-SC-07` · `PG-SC-09` · `PG-SC-12` · `PG-DP-02` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint, 600s build+recreate+verify, 1500s early-close, 2100s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none live** (read-only counts/health/gate probes only — a write of any kind is a STOP). **Restart: ONE backend recreate (D145 standing + D143 L3 + D150). Deploy: THIS slice (frontend-served; bundle EXPECTED to differ — new route code; a byte-identical bundle here would be the finding, `PG-SC-09` inverse stated upfront).**

## G1 — capture BEFORE (every observable the proof moves; `PG-EV-08`)

- Image id, served bundle name+size+sha256 (loopback bytes AND in-image file — the consumer-decode rule, `PG-SC-12`), `alembic current` (hypothesis single head `20260923_sg100_enrich_snapshot` — VERIFY, `PG-IC-09`), 25-table counts, health exact, gate 301/401, `"Expiry"` literal count in served bundle (hypothesis 0 — the new-route marker). Quote all raw.

## G2 — dashboard page + nav (patterns handed over, no rediscovery)

- `routes/ExpiryPage.tsx` on the `AnalyticsPage.tsx` shape (verified 2026-09-24 — re-verify): `useHouseholds` + `localStorage household_id` + `useQuery` gated on effective household; wrapped in `PageContainer` (SG-105 consistency — `InboxPage`/`CapturePage` precedent, re-verify import path `components/shell/PageContainer`); household `<select>` uses `THEMED_CONTROL_CLASS` (SG-105 precedent — re-verify the export name on target, never inherit it).
- Data: new `fetchExpiryStatus(householdId, category?)` in `api/client.ts` via `apiGet` on `/v1/plugins/expiry-tracker/status` (empty-string params are dropped by `buildUrl` — verified `client.ts:16-22`, so an unset filter sends nothing); types in `api/types.ts` mirroring the SG-107 response keys exactly (`as_of, household_id, category, rows, summary, unresolved_rows` — verify against the live route or the SG-107 test, `PG-IC-09`).
- Sections in urgency order: Expired (`expired`) → This week (`this-week`) → This month (`this-month`) → Safe (`safe`) + Unresolved (reasons labelled Proposed / Needs evidence / Unparseable date / No date — THIS label map, no invention). Row: display name (link to `/assets/:id?household_id=`), category, expiry date + date_type, days remaining, tier pill labelled Critical / Urgent / Upcoming / Long lead / Safe / No tier (THIS map — tier `null` renders "No tier", never blank).
- Category filter: options from the served taxonomy (`useTaxonomy`, `useAssets.ts:61-68` — re-verify), "All categories" default; the filter narrows the query (route already proves narrowing server-side — pass the slug through, assert the request params in test).
- **F-SG107-1 ANSWERED HERE (decided by the Architect, not delegated):** unclassified assets are outside the engine stream (SG-107 design call #4 stands); the dashboard shows an "Uncategorized" line sourced from the SERVED `GET /v1/analytics/summary` (`categories.uncategorized` — `AnalyticsPage` precedent, no new backend) beside the engine summary, never merged into it. If the summary shape on target differs, that is the finding that decides the fallback — never a guessed number.
- `App.tsx`: `NavLink to="/expiry"` labelled Expiry (nav order: after Analytics — verify the exact anchor block on target) + `<Route path="/expiry" element={<ExpiryPage />} />`. The shell test asserting the legacy nav (`shell.test.tsx:373` "byte-identical legacy nav" — re-verify) EXPECTEDLY changes: update it to include Expiry in the same commit, and the diff of that hunk is quoted (a silent nav change elsewhere is a STOP-and-report).

## G3 — tests + gates ($0)

- New `routes/ExpiryPage.test.tsx` (fail-then-pass, BOTH raw runs committed, `PG-EV-09`; seen-to-fail in-run, `PG-EV-01` — `AnalyticsPage.test.tsx` mock pattern precedent: mock `../hooks/useAssets` + `../api/client`): bucket sections render in urgency order with exact labels; tier pills map incl "No tier"; unresolved reasons labelled; category filter changes the request params; empty-zeroed body renders the empty state (not a crash, `PG-SC-07`); uncategorized line renders from the summary mock. `PG-SC-02`: writer = SG-107 engine route (untouched, cited), reader = this page — the test asserts the page calls `/v1/plugins/expiry-tracker/status` with `household_id` (+ `category` when set).
- Full frontend suite green (`tsc` + `vite build` + `eslint` + `vitest` — quote counts, never inherit them), backend suite untouched (no backend diff — state the empty-diff proof instead of re-running it). Secret gate 0 real over the changed files (quote the grep, `PG-EV-09` obligation attaches to the claim).

## G4 — refresh + verify (D145 owned refresh)

- One frontend-inclusive rebuild + exactly ONE recreate + verify. AFTER proofs quoted raw against G1 BEFORE: new image id, bundle name DIFFERED with `"Expiry"` literals 0→1 in the loopback-served bytes (the consumer-decode proof, `PG-SC-12`), `alembic current` unchanged, counts delta exactly zero, health exact ×6, gate 301/401, app page fetch 200 through the fresh server.
- Post-restart sweep WAIVED (`PG-DP-02` — restart-gated); substitute: in-process vitest pre-restart + the post-restart probes as authority. No browser-driven tests on this path — state the derived set and that it differed nowise.
- Actual-versus-budget per leg with units (`PG-PR-06` stated against the build+recreate+verify bound).

## G5 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-108.log`, `SG-108_report.md`, `SG-108_verify.log` (raw outputs + BOTH fail-then-pass runs + every gate + BEFORE/AFTER pairs). First token `SG-108`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `routes/ExpiryPage.tsx` + test + `api/client.ts` fetcher + `api/types.ts` types + `App.tsx` nav/route hunks + shell-test nav update + `docs/worklogs` (7 content paths) — NOTHING else (`backend/` empty diff or STOP; no `ProductCard`/token/other-route hunks; `docker compose config` FORBIDDEN). Ordered paths committable (re-verify `.gitignore` before commit, `PG-SC-10`).
- Cross-product (`PG-IC-01`): no criterion demands backend, migration, sender, scheduler, opened-date, second recreate, press, or any metered call — no cell collides; stated so the check exists on paper. Reads include vitest/TestClient-shape mocks + host commands + the authorized image build and ONE recreate; pulling/running any OTHER image or launching unnamed runtimes counts as execution — not authorised.
- Privacy: identifiers TEXT only; host `.env` never printed, never read into any artifact (`PG-SC-05` by rule, literal grep-gate quoted).
- No fixed dates except this header's authoring-date metadata; fixture dates are sample data (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- `/expiry` renders bucket sections in urgency order with exact labels, tier pills incl "No tier", labelled unresolved reasons, working category filter + household scoping, uncategorized line from the served summary; nav carries Expiry; shell-test nav update quoted.
- Tests fail-pre/pass-post both committed raw; frontend gates green; served bundle carries the marker 0→1 with counts delta 0; $0; production otherwise untouched; no vacuous pass.
- Question each criterion answers (`PG-SC-09`): sections — does the page show engine truth in blueprint bucket order? filter — does narrowing reach the server? refresh — did the served bundle actually change while data stood still?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-108 | Report: docs/worklogs/SG-108_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint · 600s build+recreate+verify · 1500s early-close · 2100s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.

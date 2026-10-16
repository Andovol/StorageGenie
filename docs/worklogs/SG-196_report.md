SG-196 — model opencode-go/deepseek-v4.1-flash, effort=max (read from the coder process argv, /proc/244865/cmdline `opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant max`; served model unknown — provider metadata not read, PB-4/CO-78), workdir /home/andrei/StorageGenie, remote origin git@github.com:Andovol/StorageGenie.git. BASE REF requested: automation; actual resolved 04f18520cfce4bde4e63dccc8f3c5ac3ad116da1 (local HEAD at admission, worktree clean; no fetch was run at t0, but the end push 04f1852..ce27175 was accepted as a fast-forward from 04f1852, so the remote tip was the resolved base). WORK_HEAD faea4d60804325dbf169f73e018c43d0aa3066ed.

Contract echo (CODER.md line 3, host copy /home/andrei/storagegenie-contract, VERSION 0.50.0): "**Contract version: 0.50.0** — **echo this line verbatim in your receipt.** It is the only proof that you read this file rather than assumed its contents." RULES.md sha256 49338e39a5749821e7e26724d28715d4d27b0a34e01b359ec91bc3d85239e3ed equals RULES.sha256 — no difference. rules_check.sh: G-L1 the contract dir is not checked out at a tag (UNCHECKED), G-L5/G-L7 gh-unauthenticated (UNCHECKED), G-L6 bytes printed; exit 3 — environment, same as SG-190/SG-194/SG-195, recorded, not slice scope.

(a) issues / deviations / surprises
1. Census difference (PB-1; reported, not hidden): the base tree has NINE product `useHouseholds(` call sites, not the packet's eight — the extra is `frontend/src/components/shell/AppHeader.tsx:16` (the import-modal household id, the old Nav shape). It sits outside the packet's scope ceiling and outside the EXPECTED branch set, so it was NOT migrated and NOT widened (G2's report-not-widen rule applied); it still shares the `["households"]` cache key with the provider, so network I/O stays one request. Named as a recommended follow-up.
2. Interim work commit `a0c814b` (unpushed) had three "(control)" rows coupled to candidate-only anchors (the nav combobox, the nav-fired review-tasks fetch); the base FAIL run exposed them (11 failed / 2 passed, 3 controls failing for the wrong reason). The controls were rewritten to prove absence on states present on both trees (the Inbox route supplies the SG-195 alert / loading anchor); the interim commit was amended while unpushed (no published history rewritten, CO-54 respected). Final base run: 8 failed / 5 passed, every failure structurally absent-on-base. Recorded in the worklog EPISODE paragraph.
3. The worklog's SESSION paragraph (written before the lane check) said "no systemd lane unit for this run" — wrong: the run IS `dispatch-storagegenie@SG-196.service` (MainPID 244780, ExecMainStartTimestamp 2026-10-16 20:15:14Z, coder PID 244865), RUN_BUDGET_S=2100. Corrected by an append carried with this report commit; the correction, not the wrong line, is the fact.
4. Design calls inside the constraints (PB-6, decided and reported): (i) badge renders iff the shared review-tasks read has loaded — a loaded zero renders the honest "0"; the three absent states (error/loading/no-household) render NO badge and are each controlled; the aria-label carries the count exactly when the badge shows. (ii) Capture and Planning keep their SG-195 household alerts, now reading the context's isError — reported-not-rebuilt per G2; on those two routes a household failure shows at nav AND route (preserved branches), on every other route once at nav. (iii) household alert text is now on 3 surfaces (nav + Capture + Planning): still <3 ROUTES for the nav addition alone, duplication reported, no shared helper (SG-195 precedent). (iv) `useReviewTasks` extracted into `hooks/useAssets.ts` (query reuse explicitly allowed by the ceiling) so Nav and InboxPage share one definition, key and shape. (v) ReviewPage's inline `["review-tasks", household]` query left untouched (outside the ceiling); the cache is shared regardless.
5. Test edits beyond route tests (all REQUIRED by the hook-shape migration; each edit names the preserved behavior in-code): shell.test (renderCatalog + one inline render), catalog.test (renderCatalog), import-modal.test (/inbox route render) — component tests that render migrated pages; plus provider wrappers in the five route test files, query-error-alerts.test, theme-adoption.test (5 page renders + swept-array entries), and mock-shape changes in InboxPage.test / import-modal.test (importOriginal spread: only useHouseholds stubbed, real useReviewTasks runs) and theme-adoption.test (useReviewTasks fixture). No assertion text changed.
6. No old row failed on the candidate full suite, so no D443 single-row base rerun was owed. Counts are this run's own (296), not carried: SG-195's 283 + this slice's 13.
7. Health probes are not applicable to this slice (jsdom-only, no live interaction; the packet says so) — stated, not silently omitted.
8. Vacuity (PB-3): no criterion could pass vacuously — the FAIL half runs against an isolated base worktree with the sha256-equal module and fails for the structural reason; the diff is 21 files (+556/-161); the badge/alert controls assert absence on loaded/pending paths; the 13-row module's 8 prove-rows each fail on base (combobox ×3, alert ×3, badge ×2).

(b) actions
- Work commit faea4d60804325dbf169f73e018c43d0aa3066ed (21 files, +556/-161; 20:24:0xZ as a0c814b, amended 20:25:3xZ): new `frontend/src/hooks/HouseholdContext.tsx`; `frontend/src/hooks/useAssets.ts` (+useReviewTasks); `frontend/src/App.tsx` (provider wrap, nav selector, nav household alert, Inbox badge, import id from context); the 7 route files migrated (CatalogPage also carries the G2 facets/saved-searches alerts); new `frontend/src/App.household-nav.test.tsx` (13 tests); 10 existing test files edited only where the migration required (preserved behavior named in-code).
- Evidence commit ce2717541643630456a5e0f6919290665a08ac42 (docs-only, 7 files): SG-196_worklog.log, SG-196_focused_candidate.log, SG-196_base_newrows_fail.log, SG-196_suite_candidate.log, SG-196_tsc.log, SG-196_eslint.log, SG-196_census.log.
- Push observed: 04f1852..ce27175 automation -> automation (exit 0). Receipt note pushed separately (below). This report commit adds SG-196_report.md + SG-196_receipt.log + the worklog correction.
- External / production effects (CO-85): NONE with side effects — no deploy, restart, migration, schema or host change, no provider/paid call ($0.000000; no app spend exists on this path), no credential or .env handled, no sudo. Local commits, git pushes and a notes ref only.
- Durations (UTC box clock; lane ExecMainStartTimestamp 1792181714 = 20:15:14Z; per-leg from committed log stamps): session startup to first output 20:15:14 -> 20:21:11 (~357 s, no output — under the 900 s idle kill); orientation + FIRST READ + recon -> ~20:22:50 (~100 s); implementation + dev run + work commit -> ~20:24:00; control repair + amend -> 20:25:35; verification leg 20:25:36 -> 20:26:44 (~68 s: focused PASS 6.12 s, base FAIL ~14 s, full suite 11.71 s, tsc/eslint, census); evidence commit + push -> ~20:27:0x; receipt publish + read-back -> 20:27:59Z. Elapsed at report writing (epoch 1792182530 = 20:28:50Z) 816 s of 2100 (38.9%; deadline 20:50:14Z) against the packet's ~900 s uncalibrated expectation — under. No single command over 60 s; no bound hit; no command killed.
- Retry count 0 (no re-dispatch). Test-command count 5 vitest invocations (dev ×3 incl. the module-only check, focused candidate ×1, base FAIL ×1, full suite ×1) + 2 gate commands (tsc, eslint). Provider-call count 0. Failed prove executions 1 (the base run that exposed the coupled controls, material change made in-slice).
- Highest-impact action: the single shared HouseholdContext — 15 product call sites collapse to one provider query plus the reported AppHeader outlier, and the nav now carries the selector, the household failure alert and the Inbox open-task badge.

(c) verification

FAIL half — candidate test module vs BASE, isolated worktree /tmp/opencode/sg196-base @ 04f1852 (module sha256 48fea66946f449101071d8390edfc6ea2c7780785fe96578b8bf02d3da35acd2 equal in both trees; SG-196_base_newrows_fail.log):

    $ node_modules/.bin/vitest run src/App.household-nav.test.tsx   (cwd=/tmp/opencode/sg196-base/frontend, timeout 600)
    FAIL  shared household context > one household fetch; the nav selector shows the fallback and persists it (A1)
    FAIL  shared household context > a nav selector change reaches the route selector in the same session (A1)
    FAIL  shared household context > a persisted household_id is used on a fresh mount (A1)
    FAIL  shared household context > a failed households read alerts in the nav (G1)
    FAIL  nav Inbox badge (G3) > the badge shows the loaded open-task count and the accessible name carries it
    FAIL  nav Inbox badge (G3) > a loaded zero-task read renders the honest zero badge, never a hidden count
    FAIL  Catalog household-adjacent alerts (G2) > a failed facets read alerts naming the facets
    FAIL  Catalog household-adjacent alerts (G2) > a failed saved-searches read alerts naming the saved searches
      Test Files  1 failed (1)
           Tests  8 failed | 5 passed (13)
    vitest_exit=1
    (failure reasons checked: 3x Unable to find role="combobox" /household/i, 3x Unable to find role="alert", 2x Unable to find role="link" name "Inbox, N open review tasks" — structurally absent on base. The 5 controls pass on the base too; worktree removed after.)

PASS half — focused candidate post-commit (echoed candidate HEAD faea4d6 == work commit; echoed base 04f1852 == packet start; SG-196_focused_candidate.log):

    $ node_modules/.bin/vitest run <11-file derived set>   (cwd=/home/andrei/StorageGenie/frontend, timeout 600)
      Test Files  11 passed (11)
           Tests  153 passed (153)
    vitest_exit=0  elapsed 6.12 s
    (derived set = src/App.household-nav.test.tsx + the 10 edited test files; grep -rl "HouseholdProvider|useHouseholdContext|useReviewTasks|inbox-open-count" in the log header.)

Full suite on candidate (D443; echoed candidate HEAD faea4d6 == work commit; SG-196_suite_candidate.log):

    $ timeout 900 node_modules/.bin/vitest run
      Test Files  30 passed (30)
           Tests  296 passed (296)
    vitest_exit=0  elapsed 11.71 s
    (no old row failed on the candidate, so no base rerun was owed; backend suite untouched/unrun — no backend in the ceiling.)

Gates (SG-196_tsc.log, SG-196_eslint.log):

    $ node_modules/.bin/tsc --noEmit -> no output, tsc_exit=0
    $ node_modules/.bin/eslint src -> no output, eslint_exit=0
    health: not applicable (jsdom-only slice, no live interaction; stated per packet).

Receipt (CO-60/CO-97; bound lane notes-ref; mapped refspec; transcript as executed, SG-196_receipt.log):

    $ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
    local_tip_before=3284f3322eb29820214e448aba0f5eac42fac7af
    $ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-196 | Report: docs/worklogs/SG-196_report.md | Work-HEAD: faea4d60804325dbf169f73e018c43d0aa3066ed" faea4d60804325dbf169f73e018c43d0aa3066ed
    add_exit=0
    $ git push origin refs/notes/storagegenie-coder-reports
       3284f33..70d7ae3  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
    notes_push_exit=0
    $ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg196-fetched
    $ git notes --ref=refs/notes/sg196-fetched show faea4d60804325dbf169f73e018c43d0aa3066ed
    Dispatch-ID: SG-196 | Report: docs/worklogs/SG-196_report.md | Work-HEAD: faea4d60804325dbf169f73e018c43d0aa3066ed
    show_exit=0
    remote notes tip: 70d7ae301a4bbbb7b994ef45a1f7c34fff688459 (ls-remote readback)
    (the note anchors the WORK commit, so this report commit does not touch the annotated object; the report path exists in the pushed tree once this commit lands — same construction as SG-195. The retired finalizer was not used.)

INTENT
- G1 context: code hoists household selection into one provider (one useHouseholds call at App level) exposing { households, isError, error, householdId, setHouseholdId } with localStorage-first + fallback + auto-persist; the check expects a nav selector that drives every route in-session, persistence across a fresh mount, and exactly one households request; the approved packet says exactly that. X=Y=Z.
- G1 nav alert: code renders `{householdsIsError && <div role="alert">Could not load households: {String(error)}</div>}` in the nav; the check expects the alert on a rejected households read and its absence on the loaded path; the approved packet says exactly that (no refetch control invented). X=Y=Z.
- G2 branches: code renders `role="alert"` text-only conditionals for Catalog useFacets / useSavedSearches failures; the check expects each named alert on its mocked failure and the loaded path alert-free; the approved packet says exactly that. X=Y=Z.
- G3 badge: code renders the open-task badge from the shared ["review-tasks", household] data with aria-label "Inbox, N open review tasks" when loaded and NO badge on error/loading/no-household; the check expects the count, the accessible name, and the three absences; the approved packet says "absent … never a false zero" — the loaded-zero case (renders "0") is my design call inside the constraint, reported in (a)4. X=Y=Z at every packet-named state.

TWINS: not applicable — feature/exposure slice, not a defect-construct repair; the equivalent sweep is the household-query census (BASE 9 product call sites -> TARGET 1 provider call site + AppHeader reported; isError census in SG-196_census.log), reported in (a)1/(a)4.

acceptance
- A1 MET: one fetch — T1 asserts exactly one /v1/households apiGet on an App render and the nav selector's fallback + persistence; T2 asserts a nav change reaches the route's own selector and requests (jobs with hh-b) in-session; T3 asserts localStorage-first on a fresh mount; per-route fallback/persist preserved — the existing route suites run green under the provider (behavior-preservation rail; full suite 296/296). AppHeader's remaining read shares the cache (reported, (a)1).
- A2 MET: EXPECTED set resolved — Catalog/Inbox/Analytics household reads migrated into the single provider query whose failure now surfaces at the nav branch (T4), Catalog facets + saved searches branched (T11/T12); nothing already-branched was rebuilt (Capture/Planning re-sourced); no out-of-EXPECTED site was widened (AppHeader reported, (a)1). FAIL genuine (8 structurally-absent-on-base rows, sha-equal module, both runs committed: SG-196_base_newrows_fail.log + SG-196_focused_candidate.log); controls assert unchanged loaded/pending paths + absence (5 controls, T5/T8/T9/T10/T13); census enumerated on target with the difference reported both ways.
- A3 MET: badge shows the loaded open count with the accessible name carrying it (2 and 0 rows); absent on error (T8 control — Inbox's own alert proves the shared read's error state), loading (T9 control), empty-household (T10 control); no false zero anywhere.
- A4 MET: first token SG-196; notes-ref receipt on refs/notes/storagegenie-coder-reports published, pushed (3284f33..70d7ae3, exit 0) and mapped-fetch/read-back verified (show transcript above; remote tip 70d7ae3); Work-HEAD faea4d6 recorded in the note; branch push complete (04f1852..ce27175 observed) and this report lands on automation; elapsed per leg in (b) vs the ~900 s uncalibrated expectation (816 s at report writing, under; lane clock, RUN_BUDGET_S=2100 stated); constraints answered below; FIRST READ / DURING EXECUTION / REMAINING dispositioned.

constraints answered
- Scope ceiling respected: exactly App.tsx, the 7 route files, hooks/* (context module + useReviewTasks query reuse), one new test module, plus the migration-required existing-test edits named in (a)5; AppHeader.tsx NOT touched (reported-not-widened); HouseholdSelector.tsx unchanged (props sufficed); no backend, no router structure, no new routes, no screenshots/driver (jsdom only — zoom/touch/dark/auth-live stand, stated not silent).
- Simplicity: no shared helper component for duplicated texts; the context module is the one shared unit.
- Secrets: none handled; nothing sensitive in logs or the report.
- PB-2 denial path: no privileged operation attempted; no denial occurred; stop path never reached.
- Hang bounds: reads 120 s, focused 600 s, full suite 900 s — applied per command; no timeout finding (nothing hit a bound; nothing killed; idle kill never approached beyond the documented 357 s no-output startup window).
- No interactive prompt or polling loop; no sudo; no host change.
- Test scope per D443: full suite ONCE on the candidate (296/296); on the base ONLY the new module's FAIL half; no old row failed on candidate (no base rerun owed); no carried counts.
- tsc + eslint gates: both exit 0 at the work HEAD.
- No waste cut owed (slowest_waste = none, SG-197); every leg used.
- CO-103 skipped as unnecessary: none — every covered step was needed; health probes are N/A by the packet (stated), not skipped.

UNCLEAR
FIRST READ:
- AGENTS.md's coder-read paths and .rules-cache/ are absent on this host/workdir (untracked by design); used /home/andrei/storagegenie-contract/ (complete 0.50.0 copy, RULES.md hash verified against RULES.sha256). rules_check.sh G-L1/G-L5/G-L7 UNCHECKED lines are environment (dir not tag-checked-out / gh auth), not slice scope. Disposition: recorded, block-free; same as SG-190/SG-194/SG-195.
- Packet premises verified: route-selector line numbers, the 4 EXPECTED unbranched sites, Capture/Planning already branched, Nav's import-id derivation — all match; the one difference is the 9th useHouseholds site (AppHeader), reported in (a)1 and handled by report-not-widen.
DURING EXECUTION:
- The interim work commit + control repair episode ((a)2) — the only material in-slice change after a failing prove execution; one failed prove execution recorded, no two-attempt exhaustion on any criterion.
- The lane-unit misstatement in the worklog SESSION paragraph ((a)3) — corrected by append; the report and correction carry the true lane facts.
REMAINING (named, not silently done):
- AppHeader.tsx still runs its own useHouseholds observer (same cache key; no extra network request); migrating it is the natural next slice and was kept out by the stated ceiling.
- ReviewPage's inline review-tasks query remains a second code definition of the same key (outside the ceiling; shares the cache).
- Authed-live coverage, screenshots/driver checks and zoom/touch/dark measurement remain unmeasured (jsdom-only slice; the packet excludes them).
- Backend suite not run (no backend in the ceiling — stated, not silent).

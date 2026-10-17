# SG-202 audit — close-out deploy rider (Architect, 2026-10-17)

**Rated from the diff and the raw logs, not the narrative.** Audited diff: `3857b6a` (7 evidence files under `docs/worklogs/SG-202_*`, +414 insertions, zero product/config/schema/migration/test change) + paste commit `2717aec` (report + receipt log). Report `docs/worklogs/SG-202_report.md` read in full; prestate/poststate/recreate/health_end/build/tests/receipt logs read.

**Rating: 97, no flag.** `deduction_attribution: coder` — SG-202-I1 (first API-shape capture omitted the required `household_id`, returning the missing-param 422 envelope; self-caught and corrected with a supplementary capture in the same log). `slowest_waste: none` (every named phase's output is used). Elapsed 379 s of `RUN_BUDGET_S=2100` (18.0%) against the packet's ~300 s expectation — 79 s over, stated per `G-A9`; the overage is orientation/reading + evidence/receipt legs, not the deploy (15 s + 1 s).

## Verified

- **A1** — exactly ONE `docker compose build backend` issuance (`build_exit=0`, 15 s) and ONE `docker compose up -d --no-deps backend` (`up_exit=0`, 1 s), both with `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-202/docker.sock`; default socket never touched; zero denials. New container `d868f373b661…` Created `2026-10-17T12:03:52.700720908Z`, image `sha256:15a1fe63…` (== the build log's exported manifest list sha — an independent cross-check that the rebuilt image is the one running), RestartCount 0, healthy. Health green start (12:03:02Z) and end (12:05:15Z), six post-recreate GETs all 200.
- **Served-bytes deltas** — post bundle `dd4f1bd0…` (325039 B) != pre `8ba02c64…` (325053 B, == the SG-197 serve); post index.html `e3eb6736…` != pre `5ce95f29…`; CSS `e1e5ff63…` unchanged — a real expected result, neither slice's diff touches CSS. SG-196 markers present in the served bundle bytes (`inbox-open-count` ×1, three household/facets/saved-search alert strings, `Select household` ×3). SPA fallback serves the new index on six routes; CORS preflight 200.
- **Schema/data** — production SQLite `sha256 e6bef157…` byte-identical pre-deployment, post-recreate and post-tests; 28 tables; all counts identical; alembic head `20260924_sg114_relation` unchanged; no migration, no slice-caused row change.
- **A2** — base requested `automation` → resolved `23c59b16…` == `origin/automation`; `f757ebd`/`faea4d6`/`144190c` all ancestors (reachability form, `PG-IC-07`). Merged-vs-served product diff: exactly the two expected commits, 24 files, +622/−170, frontend-only; `backend/app/models` + `backend/alembic` empty.
- **A3** — first token `SG-202`; all constraints answered; FIRST READ / DURING EXECUTION / REMAINING dispositioned.
- **A4** — notes-ref receipt on `refs/notes/storagegenie-coder-reports`: `add` + push (`67fbd02..ffcb51f`), mapped fetch to `refs/notes/sg202-fetched` and `show` read-back, remote tip `ffcb51f2ed52e861b040c896bf3c949f564f700c` re-read by ls-remote; first line `Dispatch-ID: SG-202 | Report: docs/worklogs/SG-202_report.md | Work-HEAD: 3857b6a…`. Focused tests: 12 files / 162 passed / 0 failed, exit 0.

## ISS-4 (5th instance) — not a slice fault

The trigger returned `result=report_unreadable id=SG-202 exit=0 reason=report_missing`; the status verb reads `inactive reason=report_missing`. The report IS present and committed (`2717aec`, 145 lines) and the receipt IS on the remote with a verified read-back — so the receipt-based failure condition (`DISPATCH.md` §2) does **not** fire, and this is the known runner-report-readback shape (instances now SG-195, SG-196, SG-198, SG-199, SG-202), filed Launcher #84. No re-trigger issued. **No `FLAG:TRUST`:** the required final report exists and is valid; the missing line is the runner's read of it, not the artifact.

## Dispositions

| Item | Disposition |
|---|---|
| SG-199 REMAINING (density, auth-live, live-container, zoom/touch/dark) | Density numbers → SG-203 (measure the existing grid/table toggle) then SG-204 (proposal + renders); auth-live + live-container stay blocked (no credentials/host grant), stated |
| ISS-4 runner misfire (now 5th instance) | Carried to Launcher #84; no re-trigger; not a slice fault |
| Live browser rendering of SG-196's branches (jsdom-only proof) | Folded into SG-203/SG-204's rendering session (the driver renders the routes); noted as still unproven live until then |
| SG-196 report-vs-audit delta line (`+556` vs audit `+565`, 9 lines) | Docs-only records discrepancy, no product impact; recorded in `docs/reviews/review-ledger.md`; no repair slice |
| Backend suite two environmental rows (pyzbar/libzbar, tesseract) | Known-host condition; Launcher provisioning; no project action |

## Note on the rating basis

No new tests were written by this slice (rider: the 12 focused modules are pre-existing), so `AUDIT.md`'s test-body rule has no new body to read. The rating rests on the evidence logs and the immutable diff, both of which I read directly rather than accepting the report's summary.

# SG-193 — Close-out deploy rider: served live, rated 97

Immutable audit: base `16bdaf1` → work `eb6ba1b` (9 logs) → paste `3c89c69`. Forced-command status at end: `result=done id=SG-193 exit=0`; trigger job exit 0. Mapped notes fetch read TWO receipts: the WORK_HEAD note and the paste-commit dual-annotation note, both `Dispatch-ID: SG-193 | Report: docs/worklogs/SG-193_report.md | Work-HEAD: eb6ba1bdd86c89e27ad715fa37a696ee08a69fd8`; the paste note adds `Settings: coder=opencode coder_source=command model=opencode-go/deepseek-v4.1-flash model_source=command effort=max effort_source=command`. Local pulled `--ff-only` to the exact paste HEAD (`3c89c69` == origin/automation). Scope: in-slice diff is evidence-only (10 files, all `docs/worklogs/SG-193*`, +925); zero product diff in-slice (`CO-48` class 1 as claimed); live service replaced. No new dependency, one restart (the authorized recreate), production DB untouched (sha `e6bef157…` identical pre/post/tests).

Holistic rating: **97/100**, no flag. Deduction attribution: coder (I1 partial capture gap, disclosed). Contract: packet expected recorded/published/host 0.47.0; host echoed **0.50.0** (VERSION + verbatim lines 3-4 quote); RULES.md sha256 `49338e39…` unchanged across both echoes. Handled exactly as the packet ordered (echo + report differences, no repair).

## Evidence accepted

- A1: one rebuild (exit 0, 31 s) + one recreate (exit 0, 2 s) through the unit lane socket (`DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-193/docker.sock` in both transcripts; zero denials). New instance proven by ID/Created: `8f5b9707d92e`/2026-10-13 → `e8a6ed6985ef`/2026-10-15T19:48:14Z, image `865a0e05…`→`c3b85d5a…`. Health start/end identical ok/ok/ok + twelve post-recreate 200s. Served bytes all CHANGED as expected (index `dc9fbbbf…`, JS `fd4a916e…` 324210 B, CSS `e1e5ff63…`); build-log filename == served filename (serve identity chain). Schema NONE (alembic head unchanged), counts NONE (28 tables, DB byte-identical).
- A2: merged-vs-served diff = exactly the six expected commits (29 files +1443/−114; no models/alembic) — independently confirmed by the Architect pre-dispatch with the same range query. Still-broken named: SG-176 UI absent, SG-178 visibility unrepaired, other slices' REMAINING stand; I5 premise correction accepted (SG-177 bare-resolve arm discharged by served SG-188 — measured live 422s on both lists + test, not a re-argument).
- A3: nine logs (hashes committed) + report; elapsed 623 s vs ~600 s expectation (lane stamps, +4%); constraints each answered; FIRST READ / DURING EXECUTION / REMAINING dispositioned; first token SG-193.
- A4: both notes verified by independent read-back; branch + report pushes complete; bound lane receipt, retired finalizer untouched.
- Focused tests (`PG-DP-02` substitute): backend 11 modules 76/0 exit 0; frontend 3 modules 50/0 exit 0; prod DB sha re-checked after runs. SG-190 driver correctly excluded (not in-process-runnable, stated).
- Deduction: I1 (−2) — `PG-EV-08`'s API arm lacks the live pre-serve capture (container already replaced; second runtime correctly refused). Disclosed with fix-forward; post-serve shape captured live; before-leg covered by SG-188's committed base runs + merged diff. No silent gap.
- No deduction: I2/I6 invocation errors corrected in-slice with appended reruns (working rerun discipline); I3 cosmetic log blemish (no measurement affected); I4 cross-project concurrency (permitted, no interaction); elapsed within noise of an uncalibrated expectation.

## Dispositions

| Item | Destination |
|---|---|
| ISS-1 (unserved replay corrections) | **RESOLVED** — served live: bundle changed, SG-185/186 code in served tree, live probes green |
| ISS-2 (10-14 vs 10-15 date variance) | Fixed in the audit commit (decisions-file dates → 2026-10-15; consumed packet date left as metadata) |
| Contract 0.47.0 → 0.50.0 delta (tag fetched read-only; 12 files +749/−56; RULES.md untouched; new SECOND_OPINION.md; run-coder rework) | **D-2 owner adoption decision** (new item, this turn). Next dispatch BLOCKED until adopted (recorded 0.47.0 ≠ published 0.50.0, controlled-axis mismatch per DISPATCH §2). Not a slice fault |
| SG-193 REMAINING-1/2 | Closed here (dual note verified; audit/rating this turn) |
| SG-193 REMAINING-3 (SG-176/178 open; post-SG-193 delta) | STATE ordered work (micro-slice after D-2, then candidates) |
| SG-193 REMAINING-4 (six slices' lists) | Stand as recorded |
| Serve | Live: container `e8a6ed6985ef` / image `c3b85d5a` / bundle `fd4a916e`; last verified deployment is now SG-193 (supersedes SG-192) |

Harness context-size reading unavailable; no conclusion made.

MERGED: all four heads landed by their real hunks — #32 (expiry batch map + bolt.md line) and #35
(`__all__` reorder) byte-exact blobs; #38 (synthesis debug logging + its test) byte-exact; #41 (loser
batch fetch) hunk-exact on SG-151's moved base — behavior identical across six ordered merge scenarios.
FULL suite delta exactly +1 green (the #38 test), base-reds identical. One finding reported loudly: the
#32 batch classification map differs from per-asset semantics ONLY in a state the two write services
cannot produce. Served code; no rebuild/recreate here (close-out rider serves).

# SG-153 — merge Batch D: independents (#32 + #35 + #38 + #41, unserved) — report

**Dispatch-ID:** SG-153
**Role:** Coder (never Architect — no dispatch verb run for any ID, no unit started or polled).
**Work dir:** `/home/andrei/StorageGenie`
**Origin remote (as on host):** `git@github.com:Andovol/StorageGenie.git` (fetch+push)
**BASE (packet ref `origin/automation` requested → resolved commit):** `c035b3ad8ecdc91e5223113b4c23d3ca9542f4b5`
(the ref and the resolved commit are stated separately — two fields, never one; ref == commit this run).
**WORK_HEAD:** `a5c0b88c96a7d3b1df724ebb83386b441c21cbe8` (G1 product commit; G0 product commit is its
parent `c846500`).
**Contract:** recorded `0.40.0` == published — source path `/home/andrei/storagegenie-contract/VERSION`
(`0.40.0`); `git -C /home/andrei/storagegenie-contract rev-parse HEAD` =
`f26dbd32e3c4bd7cf878333fba719a6ca1d10c3c` (subject `Contract payload 0.40.0`); payload `RULES.sha256` =
`5b65629377bbac9e40bfa7e2f4d4e42a5667b3a08ec786beb47c6a677d9ac33c`. (`.rules-cache/` is absent on the
host — SG-145 F-SG145-1; the live checkout above is the contract path.)
**Model / effort (`CO-78`, from process arguments):** model `opencode-go/deepseek-v4.1-flash`, effort
`high` — source `/proc/1172432/cmdline` (parent `opencode run --auto --dir /home/andrei/StorageGenie
--model opencode-go/deepseek-v4.1-flash --variant high # SG-153 …`). No system-prompt identity used.
**Spend:** **$0.000000 actual USD** — zero metered calls on every path (local fetch/apply, pure-unit +
`TestClient` suite, temp-SQLite probes, lint/type). No USD-metered call exists on any path.
**Live clock (`PG-IC-07`):** first capture `2026-09-29T15:00:19Z`; G2 suite `15:03:27Z→15:04:03Z`;
as-of-report-writing `2026-09-29T15:06:33Z`.
**Autonomy:** `L2` (merge-batch arc, D-0929-3 2nd word). **DATABASE none, restart none, deploy none**
(served-code change ships via the standing close-out rider — `PG-PR-04`; stated).

## Verdict: **MERGED** (unserved slice, no rider, no rebuild/recreate/deploy)

## Premise verification (a difference is a finding, not an obstacle)

| Packet premise | Measured on host 2026-09-29 | Verdict |
|---|---|---|
| Four heads mutually independent; all MERGE per SG-149 | Fetched `refs/pull/{32,35,38,41}/head`; all four apply 3-way cleanly onto this BASE (exit 0 each); no overlap among the six touched files. | confirmed |
| #41 lands AFTER #39's candidates change; file moved by SG-151 | `candidates.py` merge-base blob `3a6f919` ≠ BASE blob `7c2e981` (SG-151 #39). 3-way apply clean; applied #41 hunk byte-identical to head hunk. | confirmed (3-way clean) |
| #32 batch map equals per-asset semantics; `.jules/bolt.md` line | Blob-exact landing; batch path query count 15→1; result identical on every REACHABLE state; one divergence only on an unreachable two-accepted-classification state (F-SG153-1). | confirmed with a stated boundary |
| #35 pure `__all__` reorder, set-equal | AST-eval BASE set == landed set (`SETS_EQUAL`, 21 names); import ok, no missing attrs. | confirmed |
| #38 two `logger.debug` lines + test asserting BOTH messages | Blob-exact; test overlaid on BASE archive is RED on the first message assert, green at candidate; drives both changed lines. | confirmed |
| #41 loser batch fetch, checks in order | Six ordered scenarios: behavior (404/403/409/409 messages, values, DB states) identical BASE vs candidate; only the loser fetch drops N→1 statement. | confirmed |
| suite 2/648 with 2 known base-reds (`test_signals`, SG-152) | Full suite at candidate `2 failed, 649 passed` (+1 = the #38 test); reds are the same two `test_signals` cases. | confirmed (delta) |
| `test_sg107_expiry_engine.py` exists; `synthesize.py:192` SynthesisFormatError | File present (20407 B); `sed -n 192p` = `raise SynthesisFormatError("answer is not parseable JSON")`. | confirmed |
| alembic single head `sg114` | `alembic heads` → `20260924_sg114_relation (head)`; no migration touched. | confirmed |

## G0 — land #32 + #35, prove semantics preserved (`PG-EV-08`, `PG-SC-12`)

- **Blob identity.** `git apply --3way` of each head's diff; landed `git hash-object` == `origin/pr/N:file`:
  `.jules/bolt.md` `bcbe3b28…`, `expiry_engine.py` `a7f6c31c…`, `models/__init__.py` `85b11319…` — all
  IDENTICAL. Real hunks applied; no memory reimplementation.
- **#32 batch semantics (differential, not eyeball).** `probe32.py` loads the BASE `expiry_engine.py` as a
  separate module (`git show origin/automation:…`) and runs BASE vs candidate `compute_status` on one
  dataset. Assertion SELECTs: **BASE 15 → candidate 1**. Full result identical on every reachable state
  (`reachable_map_mismatch_count: 0`). **One divergence only on a deliberately UNREACHABLE edge** (two
  accepted classifications, newest invalid JSON): BASE returns `None` for the asset (skipped), candidate
  falls through to the older valid slug (asset included). Reachability: `assertion_service.upsert_assertion`
  supersedes the previous *accepted* assertion and `expiry_tracker._write_assertion` supersedes the
  previous *active* one — so at most one active/accepted assertion per `(asset, field)` exists via the app.
  Reported as **F-SG153-1**, not silently resolved.
- **Tie-break quote.** Both paths order by `Assertion.created_at.desc()` with **no secondary key**; a tie
  is resolved by row order, not by a declared tiebreaker. Ties are unreachable for these maps because at
  most one active/accepted assertion per `(asset, field)` is maintained. No test pins tie behavior.
- **#35 set-equality.** BASE `__all__` set vs landed set (AST literal-eval, not eyeball): `SETS_EQUAL`,
  21 names; `import app.models` → `import_ok 21 21`, `missing_attrs []`.
- **Affected tests (#32/#35 legs):** `tests/test_sg107_expiry_engine.py tests/test_sg111_lifecycle.py -q`
  → **30 passed**.
- **Fail-pre/post (`PG-EV-09`).** #32 adds no product test; its discriminating evidence is the batch-shape
  probe (15→1 assertion SELECTs) plus the BASE-vs-candidate differential above (both captured in the
  verify log). #35 needs no behavior gate beyond set-equality + import (per packet); both captured.
- Committed `c846500`.

## G1 — land #38 + #41 by their real hunks (`PG-SC-12`)

- **#38 blob identity.** `synthesize.py` `7ebd4b5a…`, `test_sg099_synthesis.py` `ff2c13f6…` — IDENTICAL
  to head. **Fail-pre:** candidate test overlaid on a BASE archive (`git archive origin/automation`) →
  `test_extract_json_logs_candidate_failures` RED, failing exactly on
  `assert any("Candidate JSON parsing failed" …)` (BASE has no logger). **Pass-post** at candidate → 1
  passed. The test invokes the real `_extract_json("invalid json {also invalid}")`, ends in
  `SynthesisFormatError`, and asserts **both** debug messages — it drives both changed lines (not a
  terminal-error placebo).
- **#41 hunk identity.** Landed `candidates.py` blob differs from head only because SG-151's #39 change is
  in the base; the applied #41 hunk (headers stripped) diffs clean against the head hunk → `HUNK_IDENTICAL`.
- **#41 order/value differential.** `probe41.py` run in two subprocesses (BASE archive vs candidate),
  canonical label-normalised JSON, ordered scenarios: S1 missing-first, S2 foreign-first, S3 decided-first,
  S4 blocked-first, S5 blocked-resolved+good, S6 good-only. Behavior fields (outcome class, status codes
  404/403/409/409, messages, returned winner/losers/resolved, candidate states, task status counts) are
  **BEHAVIOR_IDENTICAL**. Only the loser fetch changes: statement counts equal except S5 `10→9` (one
  `.in_()` query replaces one query per loser); S6 (1 loser) stays 7. Checks run in the same order on the
  same values.
- **Derived affected suites:** 87 passed.
- Committed `a5c0b88` = WORK_HEAD.

## G2 — gates (`PG-EV-01`, `PG-IC-08`)

- **FULL backend suite:** `2 failed, 649 passed, 32 warnings in 32.98s`; failures are exactly
  `test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` and
  `test_signals.py::test_ocr_has_text_boxes_and_mean_confidence` — the known SG-151/152 base-reds.
  **Blast radius:** delta is exactly `+1` green vs recorded BASE `2/648` = the one new #38 test; **no other
  delta** → not a STOP.
- **ruff:** `ruff check .` → `All checks passed!`
- **mypy-delta:** `mypy app` → `Found 41 errors in 9 files (checked 90 source files)` — **delta 0** vs the
  recorded BASE `41/9`.
- **Secret scan** over added diff lines (`CO-100`) → no match (exit 1).
- **Diff ceiling:** `git diff --stat BASE HEAD` = exactly the six PR files (+112/−14):
  `.jules/bolt.md`, `backend/app/models/__init__.py`, `backend/app/services/candidates.py`,
  `backend/app/services/enrich/synthesize.py`, `backend/app/services/expiry_engine.py`,
  `backend/tests/test_sg099_synthesis.py`. No fifth file, no config, no migration, no benchmark.
- Worktree clean after the product commits (`CO-55`).

## Findings

- **F-SG153-1 (#32, reported not fixed).** The batch classification map stores the newest *valid* accepted
  slug (falling through to an older accepted assertion when the newest is invalid JSON / missing a
  category), whereas the per-asset `_accepted_classification_slug` returns `None` for the newest accepted
  assertion regardless of validity. The two differ only when **two accepted classification assertions exist
  for one asset with the newest invalid and an older valid**, a state neither write service can create
  (both supersede the previous active/accepted row). Measured by the differential: `base_row=None
  cand_row={...}` for that edge; all reachable states equal. Reachable behavior is preserved; the boundary
  is stated so the next slice inherits it rather than discovering it.
- **F-SG153-2 (environment, carry-over).** `.rules-cache/` is absent on the host (SG-145 F-SG145-1); the
  contract checkout `/home/andrei/storagegenie-contract` is the live source. Offered for reconciliation.
- **F-SG153-3 (transient fetch).** Three of four `git fetch origin refs/pull/N/head` calls returned
  `Permission denied (publickey)` on the first attempt and succeeded on retry while `ssh -T git@github.com`
  authenticated; recorded as transient, not a credential problem. No privileged operation was routed
  around.
- **F-SG153-4 (out of scope, practice note).** As SG-150 F-SG150-2 / SG-151 F-SG151-4: work commit
  messages carry the `SG-153` ID (repo practice) although `CO-53` reads otherwise; flagged, not resolved.
- No denied privileged operation occurred; no leg was routed around (`PG-PR-03`). No command was killed by
  its bound.

## Acceptance criteria — assessed (`PG-SC-09`)

- **landed:** PASS. #32/#35/#38 landed blobs are byte-identical to their heads; #41's applied hunk is
  byte-identical to its head hunk on the moved base (its file blob differs only by SG-151's prior change).
- **equal:** PASS for all reachable states (batch map = per-asset semantics; tie-break quoted) and for the
  #41 check order/values (`BEHAVIOR_IDENTICAL`). The one unreachable-edge divergence is named in F-SG153-1
  — the criterion is not claimed beyond what was measured.
- **clean:** PASS. Diff is exactly the six files the four PR diffs touch; worklogs are the only other
  writes.
- **No vacuous pass (stated loudly):** #32's evidence is a BASE-vs-candidate differential that includes a
  divergence, not an empty set; #35 is a computed set-difference, not an eyeball; #38's fail-pre is RED on
  the asserted message; #41's order proof compares two real subprocess runs. The full suite ran (not
  skipped) with base-reds quoted. No reimplementation from memory evidenced any pass.
- **PG-PR-03 (stated):** this slice changes served code but does not touch privilege, DB or deploy; the
  close-out rider serves the live change.

## Guard invocation (as listed in the packet)

`PG-EV-01` (suite/gates) · `PG-EV-02`/`PG-EV-05` (captures committed in the verify log) · `PG-EV-08`
(BASE probe before edits) · `PG-EV-09` (fail-pre and pass-post both committed) · `PG-SC-09`
(per-criterion questions above) · `PG-SC-12` (real hunks + blob/hunk identity; no memory reimplementation)
· `PG-IC-01` (cross-product: G0/G1 fetch/apply 120s, G2 suite 600s + gates 120s — no criterion demands
what the ceiling forbids) · `PG-IC-07` (live clock) · `PG-IC-08` (blast-radius exactly +1 green; no other
delta) · `PG-IC-09` (every given fact re-verified) · `PG-PR-03` (no denied probe, none routed around) ·
`PG-PR-04` (no rebuild/recreate/restart/deploy; liveness rides the close-out rider).

## Receipt

- Work pushed to `automation`; worktree clean (`CO-55`). No `storagegenie-evidence` push, no
  `{{RECEIPT_CMD}}`. The receipt is the note on `refs/notes/storagegenie-coder-reports`.
- **WORK_HEAD note** (`a5c0b88c96a7d3b1df724ebb83386b441c21cbe8`): existing-note check empty
  (`error: no note found`, exit 1), then added, pushed, and verified from a **mapped** fetch
  (`refs/notes/sg153-fetched-e1`); executed output, verbatim:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports show a5c0b88c96a7d3b1df724ebb83386b441c21cbe8
error: no note found for object a5c0b88c96a7d3b1df724ebb83386b441c21cbe8.
existing_note_exit=1

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-153 | Report: docs/worklogs/SG-153_report.md | Work-HEAD: a5c0b88c96a7d3b1df724ebb83386b441c21cbe8" a5c0b88c96a7d3b1df724ebb83386b441c21cbe8
add_wh_exit=0

$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   493fa33..98b4652  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_exit=0

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg153-fetched-e1
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg153-fetched-e1
fetch_exit=0

$ git notes --ref=refs/notes/sg153-fetched-e1 show a5c0b88c96a7d3b1df724ebb83386b441c21cbe8
Dispatch-ID: SG-153 | Report: docs/worklogs/SG-153_report.md | Work-HEAD: a5c0b88c96a7d3b1df724ebb83386b441c21cbe8
show_wh_exit=0
```

- The first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`).

**Final-tip dual-annotation** (note-anchor inoculation, SG-092 precedent) on the docs tip
`76464f7a36bc2e93f58433d498d0232ef536ca54`; mapped-fetch `show`, verbatim:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-153 | Report: docs/worklogs/SG-153_report.md | Work-HEAD: a5c0b88c96a7d3b1df724ebb83386b441c21cbe8" 76464f7a36bc2e93f58433d498d0232ef536ca54
add_tip_exit=0

$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   98b4652..20962c4  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_exit=0

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg153-fetched-e2
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg153-fetched-e2
fetch_exit=0

$ git notes --ref=refs/notes/sg153-fetched-e2 show 76464f7a36bc2e93f58433d498d0232ef536ca54
Dispatch-ID: SG-153 | Report: docs/worklogs/SG-153_report.md | Work-HEAD: a5c0b88c96a7d3b1df724ebb83386b441c21cbe8
show_tip_exit=0
```

## Budget — actual versus budget (units stated)

| Leg | Command class | Budget | Actual |
|---|---|---|---|
| Orientation + premise verification (fetch, diffs, blob hashes, 3-way checks, contract) | ordinary | 120 s | ~120 s |
| G0 land #32+#35 + blob identity + differential probe + #35 set-equality + tests | ordinary | 120 s | ~35 s |
| G0 fail-pre/post + #38 archive probe + #41 two-subprocess differential | ordinary | 120 s | ~30 s |
| G2 full suite | suite class | 600 s | 32.98 s |
| G2 targeted suite + ruff + mypy + secret + ceiling | ordinary | 120 s | ~45 s |
| Worklogs + commit + push | ordinary | 120 s | < 30 s |
| Receipt notes (add/push/fetch-mapped/show, dual) | ordinary / notes-push | 120 s / 300 s | < 30 s |
| **Overall** | — | **2400 s (lane `RUN_BUDGET_S=2100`)** | ~ well inside cap (15:00:19Z→ report) |

Actual-versus-budget per goal: every leg well inside its class; overall well inside the 2400 s cap. No
command was killed by its bound; no interactive command ran. **Real metered spend $0.000000 USD, zero
metered calls.**

## UNCLEAR

- **FIRST READ:** the packet says "#32: batch map equals per-asset semantics" as a CONFIRMED fact. A
  BASE-vs-candidate differential shows equality for every state the app can reach, but one
  direct-DB-only state (two accepted classifications, newest invalid) falls through differently. I read
  "equals" as reachable-state equality under the maintenance invariant and reported the boundary as
  F-SG153-1 rather than bending the measurement.
- **DURING EXECUTION:** loading the BASE `candidates.py` in-process would have re-declared the `candidate`
  table on the shared `Base`, so the #41 differential was run as two subprocesses (BASE archive vs
  candidate) and compared as canonical label-normalised JSON. Also three of four pull-ref fetches returned
  a transient `Permission denied (publickey)` before succeeding on retry — recorded, not worked around.
- **REMAINING:** the `#32` edge (F-SG153-1) and the `.rules-cache/` absence (F-SG153-2) are outside a
  mechanical merge's fix boundary and offered for reconciliation. Nothing on this slice's account is live
  until the standing close-out rider rebuilds/recreates (Deploy: none here). The repo-root `venv/` vs
  `backend/venv` split (SG-152) is unchanged.

## RECOMMENDED-NEXT

- **Close-out deploy rider** (standing directive), then **hue screenshots verdict** — per the packet.

**note=yes**

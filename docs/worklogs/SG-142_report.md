SG-142 — cap-join fix: report (CHANGED — the None-job ledger rows now count)

**Dispatch-ID:** SG-142 · **Verdict:** FIXED and SERVED — `_recorded_spend` now counts the `job_id IS NULL` ledger rows as a shared, month-boxed, unattributed pool, so the monthly cap sees the true household spend (live served figure moved 0.0072005 -> 0.01086845, exactly the 9 invisible `None`-job rows).

**Contract:** `Contract version: 0.40.0`. Source path `/home/andrei/storagegenie-contract/VERSION`; contract HEAD `f26dbd32e3c4bd7cf878333fba719a6ca1d10c3c`; `RULES.md` sha256 `5b65629377bbac9e40bfa7e2f4d4e42a5667b3a08ec786beb47c6a677d9ac33c` (matches the installed payload hash in `AGENTS.md`). Recorded == published (D4 adoption).
**BASE** (`origin/automation` requested; resolved at start, two fields): requested `origin/automation`, resolved commit `2ae85918b3dc2d48c3db60d6317d45d53949a5cf` (== local HEAD at start). · **WORK_HEAD:** `f45cbdab143d71b0d802de00050f9623d6a608e4` (product + tests). G0 red `ff439b2`; G2 serve commit `a307f45`; this report at the final tip.
**Model/effort (CO-78, from process arguments):** pid `638369`, `/proc/638369/cmdline` = `opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant high` -> modelID `opencode-go/deepseek-v4.1-flash`, **effort `high`**. (Observation, not a STOP: the packet's model policy says the model id is omitted on the trigger and resolves by default; the live process args carry `--model` explicitly to the SAME id. Reported verbatim from argv per CO-78.)
**Spend:** real **$0.000000 USD**; **zero metered calls** on every path (temp SQLite + served read-only reads + one image rebuild/recreate; no provider call, no Jina, no model call).
**Authoring date (metadata only):** 2026-09-29. Live clock at capture: 2026-09-29T09:28-09:31Z (`PG-IC-07`).

## (a) Issues / deviations / surprises

- **F-SG142-1 (the load-bearing fact — semantics decided, blast-radius premise corrected).** `provider_call` has NO household column; the ONLY route to a household is `provider_call.job_id -> job.household_id` (`backend/app/models/provider_call.py:23-25`). The four writers that stamp `job_id=None`, enumerated by grep: `app/services/chat/service.py:293,331`, `app/services/planning/service.py:238,272`, `app/services/analytics/service.py:434,469`, `app/services/enrich/synthesize.py:307`. A `None`-job row therefore carries no household anywhere and can never satisfy the `Job` join. **Decision (design call inside the constraints): the fixed reader counts those rows as a SHARED UNATTRIBUTED POOL boxed to the same month, added to the household's job-joined rows.** It never attributes a row to a household by guessing; because the pool is unowned it counts against every household reading that month — the fail-closed direction for a cap (under-counting is the reported defect). **Consequence for `PG-IC-08`:** its literal reading ("only households owning NULL-job rows may move; an all-joined household in a NULL-bearing DB reads byte-identical") is UNSATISFIABLE given this schema — no household can "own" an unattributable row, and any counting fix moves every reader of that month. The no-change case that DOES hold and is tested: **a month with zero `None`-job rows reads byte-identical** (`test_no_change_when_month_has_no_null_job_rows`), which is exactly the world the existing `test_sg125`/`test_sg132` files live in (both byte-unchanged and green). This is reported, not hidden; excluding instead would change no figure and would leave the cap fail-open (the defect), so pool is the decided semantics.
- **F-SG142-2 (one justified test edit — a line-pin shift, not a semantics edit).** `tests/test_privacy_audit.py::test_g0_redact_call_sites_are_reader_and_direct_adapter` pins `services/providers/reader.py:465` through M45's documented line-tracker. The spend-reader hunk adds 18 lines above the `redact_image(` call site, moving the pinned line to 483. The caller SET is byte-identical (still exactly `opencode_go.py:310` + `reader.py:483`). Justification line by line: the assertion compares the full caller set only as `file:line` strings; the docstring itself records this exact pin moving for SG-101 and SG-125; SG-142 is the same class. Updated the one line + the shift-history sentence. The two ledger files named by the packet (`test_sg132_jina_ledger_wiring.py`, `test_sg125_ledger_retention.py`) are BYTE-UNCHANGED and green.
- **F-SG142-3 (EROFS sandbox on build).** Plain `docker compose build backend` failed: `failed to update builder last activity time: open /home/andrei/.docker/buildx/activity/.tmp-...: read-only file system`. The established SG-132 workaround (`BUILDX_CONFIG=/tmp/opencode/buildx`) was used; build exited 0. Same documented sandbox; not routed around, not a privilege escalation.
- **F-SG142-4 (packet figures are pre-SG-132; corrected).** The packet quotes "0.0067 vs 0.0104 true". On this tree (post-SG-132, which added the one `$0.0005` Jina row of 2026-09-25) the live joined-only figure is **0.0072005** and the true month total is **0.01086845** (`0.0072005 + 0.003667950`). The pre-fix **0.010368** the packet cites is SG-132's own pre-final-report figure. Difference investigated and explained; not bent to match.
- **F-SG142-5 (pre-existing environment reds, base-proved).** `tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` and `::test_ocr_has_text_boxes_and_mean_confidence` fail because `pyzbar/libzbar` and `tesseract` are absent on this host. Both reproduce with `reader.py` stashed to bare BASE; unrelated to SG-142.

## (b) Actions

- Changed product path (1): `backend/app/services/providers/reader.py` — `_recorded_spend` now returns `joined(household, month) + unattributed_pool(month)`; docstring records the semantics and the live delta.
- Changed tests (2): NEW `backend/tests/test_sg142_cap_join.py` (G0 red then green, 4 tests pinning the decided semantics); `backend/tests/test_privacy_audit.py` (M45 line-pin 465 -> 483, F-SG142-2).
- The 3 worklog files: `docs/worklogs/SG-142.log`, `SG-142_verify.log`, `SG-142_report.md`.
- Commits: G0 red `ff439b2` · G1 fix `f45cbda` · G2 serve `a307f45` · report at the final tip. Pushed `origin automation`. No push to `storagegenie-evidence`; `{{RECEIPT_CMD}}` not run.
- External/production effects: 1 image rebuild + exactly ONE recreate (D145 owned refresh). No live rows read as missing, none created; no live press; no provider/Jina/model call. No migration (query-only change, `models/`+`alembic/` empty diff).
- Retry count 0. `git diff --stat 2ae8591 HEAD` = `reader.py` + 2 test files + 2 worklogs (before this report); report adds the third worklog. No other write anywhere.
- Highest-impact action: deciding the correct semantics for household-less spend (shared pool, fail-closed) and proving the served figure move from a BEFORE/AFTER served capture.

## (c) Verification (raw captures in `docs/worklogs/SG-142_verify.log`)

- **G0 fail-pre (committed red `ff439b2`, on unmodified BASE):** G0 seed = one joined row `0.006700` + one `None`-job row `0.003700`; `_recorded_spend` returned `0.0067` against expected `0.0104` (`3 failed, 1 passed in 0.72s`) — the `None`-job row is invisible. Premise CONFIRMED.
- **G1 fail-post (real reader, `PG-SC-12`):** 4/4 green; `test_sg142 + test_sg132 + test_sg125` = 16/16 (the two ledger files byte-unchanged). No-change case reads identical.
- **Suite:** full backend suite `2 failed, 632 passed in 34.27s`; both reds base-proved (F-SG142-5, pyzbar/tesseract absent).
- **Lint/type/secret:** `ruff check .` -> `All checks passed!`; `mypy app` -> `41 errors in 9 files` both candidate and BASE (delta 0; `reader.py` in no error line); `test_privacy_audit.py` 11 passed incl. the CO-100 no-secret gate.
- **G2 served:** BEFORE (old container) `0.0072005`; rebuild `BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend` exit 0; exactly ONE recreate, container `2e623765ce226dc779defcdc67b05820f33ecee5e81d6ac4162e08df5d1057fa` -> `229da27dfa7bfccff138ea8013d12379fea40c17a65df12bfbc59b8225578d44` (image `995b20df...` -> `5f5b3ac3...`); health x6 `{"status":"ok","db":"ok","storage":"ok"} 200`; gate `http:80 301`, `https:443 401`; alembic head `20260924_sg114_relation` unmoved; table counts delta exactly 0 (provider_call 18->18, job 9->9, household 1->1, enrich_snapshot 4->4, candidate 8->8, asset 6->6). AFTER `0.01086845`; delta `+0.00366795` = the 9 `None`-job rows' month sum.
- **No vacuous pass:** the figure is produced by the committed G0 seed through the real reader; the suite run is a full `pytest -q` with a non-empty result; the migrate path was never touched (no migration in the diff).

## Receipt (note on `refs/notes/storagegenie-coder-reports`) — pasted verbatim

Work committed and pushed to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}` (packet's M20-corrected block). Note added on WORK_HEAD `f45cbda`, notes ref pushed, refspec fetched into the mapped name `refs/notes/sg142-fetched` (a bare refspec would only rewrite `FETCH_HEAD`), `show` pasted:

```text
$ git notes --ref=refs/notes/storagegenie-coder-reports show f45cbda
error: no note found for object f45cbdab143d71b0d802de00050f9623d6a608e4.
pre_show_exit=1

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-142 | Report: docs/worklogs/SG-142_report.md | Work-HEAD: f45cbda" f45cbda
add_exit=0

$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   9123120..198c744  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_exit=0

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg142-fetched
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg142-fetched
fetch_exit=0

$ git notes --ref=refs/notes/sg142-fetched show f45cbda
Dispatch-ID: SG-142 | Report: docs/worklogs/SG-142_report.md | Work-HEAD: f45cbda
show_exit=0
```

The final tip is dual-annotated with the same message (note-anchor inoculation, SG-092 precedent). Final line: `note=yes`.

## Actual versus budget (units: seconds, live clock UTC)

- G0 recon + seed + fail-pre: ~1s pytest / 120s ordinary class — within.
- G1 edit + targeted 2.04s + suite 34.27s + ruff + mypy (candidate and BASE) + privacy gate: ~70s total / 600s suite class — within.
- G2 rebuild + one recreate + health/gate/counts/BEFORE-AFTER captures: ~120s (build the bulk; recreate+health ~20s) / 600s class — within.
- G3 worklog + report + notes receipt: ~180s / 120s (notes) and 300s (push) classes — within.
- No command killed or timed out. Overall well under 2400s. Real spend $0.000000 USD / $0 bound; zero metered calls.

## UNCLEAR

- **FIRST READ:** whether "the correct semantics" should pool the household-less rows or exclude-and-disclose them. I read it from the packet's own expected shape ("NULL-job rows counted without inventing a household") plus the fail-post requirement that the seed total must change; exclusion leaves the figure unchanged and the cap fail-open, so pool is the decided call. The literal `PG-IC-08` blast radius is unsatisfiable with this schema (F-SG142-1) and I flagged it rather than bending the figure.
- **DURING EXECUTION:** the packet's numbers (0.0067 / 0.0104) are pre-SG-132; live is 0.0072005 / 0.01086845 (F-SG142-4). Also, the privacy line-pin (`reader.py:465`) broke from my line shift (F-SG142-2) — a real coupling between the spend-reader and the M45 redactor pin; fixed per the documented convention. And plain `docker compose build` hit the EROFS sandbox; used the SG-132 BUILDX_CONFIG workaround (F-SG142-3).
- **REMAINING:** the monthly cap stays inert in live until `SG_MONTHLY_CAP` is set (out of scope); the shared pool over-counts across households by design (fail-closed) and would need a `provider_call.household_id` (a migration, NOT authorized here) to be exact; `0.05/1M` is not the max Jina pack rate (F-SG124-3, carried).

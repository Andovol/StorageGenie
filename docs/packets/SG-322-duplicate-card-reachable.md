# SG-322 — Make SG-304's duplicate-photo card reachable: an open duplicate must not read as already in the catalog

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases. No live database read or write. **No migration:** if the change needs a schema change, STOP and report.
**Restart: none.** No deploy; screenshots and a rider follow.
**Provider: none.** No key, no `.env`, no spend.

**Contract:** recorded `0.61.0` (`AGENTS.md`, D36). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line if you received one; **if you received none, say exactly that** — never the line from `AGENTS.md`.

**Approval:** owner D33 (*"D33 approved."*), D35; stage C (*"d14 ok"*, L3). This slice makes SG-304's approved F10 choice reachable; it adds no new behaviour.

## Why this exists

SG-321 (screenshots, Muse) tried to photograph SG-304's duplicate-photo card in the real app and could not: the review page showed *In your catalog* instead (its log: *"`ReviewPage` shows `In your catalog` when `candidate.asset_id` truthy, and `committed_asset_id` returns duplicate target for proposed duplicates"*). Expected cause (`UNVERIFIED` — establish it, `PB-1`): `committed_asset_id` (`backend/app/services/candidates.py:1015-1044`) returns a **duplicate proposal's own `asset_id`** as the first hop (`:1024-1027`), **whatever the candidate's state**, so an **open** duplicate's read (`backend/app/api/v1/candidates.py:275`, and the Inbox's `backend/app/api/v1/jobs.py:170`) carries the matched item's id, and `frontend/src/routes/ReviewPage.tsx:100` takes the *In your catalog* branch. SG-304's tests passed because they render the card with a hand-made candidate whose `asset_id` is empty.

**The rule to build:** a candidate reads as *in your catalog* **only once it has been decided** — *same pack* (`duplicate_linked`), accepted, or *another pack* (the new item). **An open or held duplicate reads with no `asset_id`**, so the three choices show. Establish from the code which candidate states mean "decided" and name them; keep SG-271's rule (a decided candidate shows *In your catalog*) and SG-275's older-row hops unchanged.

## G0 — Preflight, and rescue SG-321's evidence

Run exactly this, then `date +%s`:

```
mkdir -p output/SG-322-scratch/docker-config output/SG-322-scratch/logs
export DOCKER_CONFIG="$PWD/output/SG-322-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-322/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-322/
docker version
docker run --rm busybox true
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** **Every file you write outside the repository's tracked paths goes under `output/SG-322-scratch/`** — logs into `output/SG-322-scratch/logs/`, every base-run capture, every `tee` and redirect, the build. **Never `/tmp`, for anything** (SG-304r2 left a log in `/tmp`). Run every command from the repository root; build with an absolute `--outDir "$PWD/output/SG-322-scratch/build"`. `output/` itself and `output/dispatch` never touched. **No server is started.**

**SG-321's report commit `2fcc629` was never pushed** (its push was refused because the branch had moved). Then, literally:

```
git cat-file -t 2fcc629 || git for-each-ref --format='%(refname) %(objectname:short) %(subject)' 'refs/quarantine/preserve-*'
```

If `2fcc629` (or a `preserve-` ref whose subject names SG-321) exists, bring in **only its `docs/worklogs/SG-321*` and `docs/worklogs/SG-304_shots/` files**: `git checkout <that commit> -- docs/worklogs/SG-321_report.md docs/worklogs/SG-304_shots` (plus any other `docs/worklogs/SG-321*` it holds), and commit them as `SG-321 evidence (rescued by SG-322; its push was refused)`. If neither exists, write `SG-321 evidence: not found` with the command output into the report and go on. **Nothing else from that commit.**

## G1 — The fix

In `committed_asset_id` (or its caller, if you establish that is the right place — say why), return the duplicate proposal's own asset **only for a decided candidate**. Report the exact condition, with file and line, and every caller you checked (`api/v1/candidates.py:275`, `api/v1/jobs.py:170`, any other you find by grep — quote the grep).

## G2 — Tests, one file at a time, FAIL-then-PASS, then the full gate

**Backend** (`backend/tests/test_sg322_*.py`), built on `backend/tests/test_sg304_duplicate_pack.py`'s `_setup`, **through the real API read** (`GET` the candidate as `ReviewPage` does — name the route): (1) an **open** duplicate reads with no `asset_id` and still carries its `duplicate_of_asset` match; (2) **held** → no `asset_id`; (3) after *same pack* → `asset_id` = the existing item; (4) after *another pack* → `asset_id` = the **new** item, not the existing one; (5) the Inbox read (`jobs.py`) agrees with (1) and (3). **Frontend** (`ReviewPage.sg322.test.tsx`): the page fed the **API shape of case (1)** — no `asset_id`, a `duplicate_of_asset` match — shows the three choices and not *In your catalog*; fed case (3)'s shape it shows *In your catalog*. **Write each test file in its own step and commit it at once.** FAIL on base (`17cf09e`), PASS on candidate; logs `docs/worklogs/SG-322_fail.log`, `SG-322_pass.log` (names and first assertion only). Older tests that break are named, old → new, none loosened; **an older test that breaks because it relied on an open duplicate reading as committed is a finding — quote it.**

**The full gate, never skipped:** `eslint` (only the known `App.household-nav.test.tsx` error), `tsc`, the build into scratch, `make backend-test` (host and image proof), `make frontend-test` (**the whole suite, 0 failed**), then every `*sg322*`, `*sg304*` and `*sg271*` file and every older file changed here, **run twice**. Logs `docs/worklogs/SG-322_<step>.log`, exact counts.

**Time rule: if the tests are not all committed by 600 s by your stamps, commit what exists, mark the rest `REMAINING`, and run the gate. The gate is never skipped.**

## Acceptance criteria

- **A1** — G0 preflight and SG-321's evidence rescued or reported not found, with the command output.
- **A2** — G1: the cause confirmed or falsified with file and line; the condition named; every caller checked.
- **A3** — G2 FAIL on base, PASS on candidate, backend and frontend; the five backend cases each with the `asset_id` read back.
- **A4** — Gate green with exact counts; the named files twice green.
- **A5** — No migration; zero Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; **no `/tmp`**; tree clean except `output/`; scratch removed before the report.
- **A6** — `PB-3` vacuity: a failure would look like an open duplicate still carrying `asset_id`, a decided one losing it, *another pack* pointing at the old item, the Inbox disagreeing, a frontend test fed a hand-made shape the API never sends, a test passing on base, a red suite. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Backend:** `backend/app/services/candidates.py` (`committed_asset_id` only), and its callers only if the fix belongs there (say why). New `backend/tests/test_sg322_*.py`.
- **Frontend:** **no product file**; new `ReviewPage.sg322.test.tsx`; older tests only where they relied on the wrong read.
- **Evidence:** `docs/worklogs/SG-322*`, and SG-321's rescued `docs/worklogs/SG-321*` and `docs/worklogs/SG-304_shots/`.
- **Any other product file is a STOP and report — even when the fix there is right** (`PG-EV-03`). No migration file.
- **Authorised runtimes:** the preflight, the `make` gates, tests, `eslint`, `tsc`, the build into scratch. No install, no server, no browser. No deploy or touch of the running app (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **600 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, remove scratch, commit, write the report, publish.** **No optional goal.** Order G0, G1, G2; commit after each test file. Expected ≈700 s (`UNVERIFIED — my estimate`: SG-304r2 571 s for four test files and the gate).

## Report

Destination: `docs/worklogs/SG-322_report.md`. The first line states the slice ID, model and effort read from the process arguments (if they are not visible, say so and do not infer them), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; G0's rescue result; each premise confirmed or falsified with file and line; the fix; the five backend cases with values; test changes named; gate counts; changed files; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-322`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-322 | Report: docs/worklogs/SG-322_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

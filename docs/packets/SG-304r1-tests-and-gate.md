# SG-304r1 — Finish SG-304: its tests, FAIL-then-PASS, and the full gate (G1 and G2 are already on the branch)

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases. No live database read or write. **No migration:** if the change needs a schema change, STOP and report.
**Restart: none.** No deploy; a screenshot slice and a rider follow.
**Provider: none.** No key, no `.env`, no spend.

**Contract:** recorded `0.59.0` (`AGENTS.md`, D30). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line if you received one; **if you received none, say exactly that** — never the line from `AGENTS.md`.

**Approval:** owner D33 (*"D33 approved."*), D35; stage C (*"d14 ok"*, L3); the plan review SG-305/SG-306 set this slice's safeguards (below). **This is SG-304's one retry.**

**What happened:** SG-304 (`2221bc9..122a269`) committed G1 (`60ba8cd`, the same-name warning) and G2 (`122a269`, `as_new_pack`) and pushed them, then went silent for 900 s while writing **four test files in one batch** and was killed (`killed=idle`); the test files were lost. **So: write one file per step, and commit each file as soon as it exists.**

## Why this exists

The capture walk (`docs/worklogs/SG-269_findings.md` F9, F10) found two wrong turns when the owner buys the same product twice:

- **F9 — manual capture, same name:** two manual captures named *Olive Oil* with different dates make two items with no warning (`POST /v1/assets`; create path `backend/app/services/asset_service.py`). Two packs are often right — but the owner should be told, and offered the existing item.
- **F10 — same photo imported twice:** the second import is marked `duplicate_of_asset`, and accepting it returns `duplicate_linked` and creates nothing (`backend/app/services/candidates.py` `commit_candidate`, around `:1151–1159`). **A second pack with a new date cannot be recorded; the new date is lost.**

**Safeguards from the plan review (binding):** the same name is not product identity — **never merge quantities, never overwrite another pack's date, always keep the option to create another pack**; the gate uses **two same-name packs with distinct dates**, exercises **every choice and cancel**, and checks quantities, dates and unrelated fields before and after.

Locations are `UNVERIFIED` hypotheses — **establish each from the file before changing it** (`PB-1`), including where the manual-capture form posts (`frontend/src/components/AssetForm.tsx` expected), where a duplicate candidate is shown and decided (`frontend/src/components/CandidateCard.tsx:21` shows *"Exact duplicate of asset <id>"* — a raw id; `frontend/src/routes/ReviewPage.tsx:55`; `POST /v1/candidates/{id}/decision`, `backend/app/api/v1/candidates.py:122`), and whether the asset list read already filters by name (`q` in `backend/app/api/v1/assets.py`).

## G0 — Preflight

```
mkdir -p output/SG-304r1-scratch/docker-config
export DOCKER_CONFIG="$PWD/output/SG-304r1-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-304r1/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-304r1/
docker version
docker run --rm busybox true
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** Scratch only in `output/SG-304r1-scratch/`. **No `/tmp` for anything.** Run every command from the repository root; build with an absolute `--outDir "$PWD/output/SG-304r1-scratch/build"`. `git status --short` clean except `output/` before the report; `output/` itself and `output/dispatch` never touched. **No server is started.**

## G1 — Read what SG-304 built, before testing it

Read the diff `2221bc9..122a269` (backend `candidates.py`, `api/v1/candidates.py`; frontend `AssetForm.tsx`, `CandidateCard.tsx`, `ReviewPage.tsx`, `api/client.ts`, `labels.ts`) and say, with file and line, whether it does what these two goals say — **report a gap; fix it only if it is inside the scope ceiling and small**:

- **F9:** before a manual capture creates an item, a live item in the household with the same trimmed, case-insensitive name shows one line and **Add another pack** (creates as today) · **Open it** (creates nothing, opens the existing item) · **Cancel** (creates nothing, keeps the form).
- **F10:** a `duplicate_of_asset` candidate shows the existing item **by name and date**, never by id, with **It's another pack** (`as_new_pack`: a new item from the candidate's own fields and date; the existing item untouched) · **It's the same pack** (today's `duplicate_linked`) · **Decide later** (hold). **Check in particular:** what `as_new_pack` does when sent with `hold` or `reject` (it must change nothing), and that the candidate's own date task follows the new item.

## G2 — Tests, one file at a time, FAIL-then-PASS, then the full gate

**Backend** (`backend/tests/test_sg304_*.py`): two same-name packs with distinct dates — (1) duplicate + *another pack* → two assets, each with its own date and quantity, the first asset's every field identical before and after; (2) duplicate + *same pack* → one asset, its date unchanged, the response `duplicate_linked`; (3) *hold* → nothing created, nothing changed; (4) a decision without the new option behaves exactly as before. **Frontend** (`*.sg304.test.tsx`): the F9 warning appears on a name match and not without one; each of the three F9 choices does what G1 says (create called once / not called / form kept); the F10 card shows a name and date, not an id; each F10 choice sends the right decision. **Write each test file in its own step and commit it at once** (four files, four commits — never several files in one call). FAIL on base (`2221bc9`, before G1 and G2), PASS on candidate; logs `docs/worklogs/SG-304r1_fail.log`, `SG-304_pass.log` (names and first assertion only). Older tests asserting replaced wording updated, each named, old → new, none loosened.

**The full gate, never skipped:** `eslint` (only the known `App.household-nav.test.tsx` error), `tsc`, the build into scratch, `make backend-test` (host and image proof), `make frontend-test` (**the whole suite, 0 failed**), then every `*sg304*` file and every older file changed here, **run twice**. Logs `docs/worklogs/SG-304r1_<step>.log`, exact counts.

**Time rule: if the tests are not all committed by 550 s by your stamps, commit what exists, mark the rest `REMAINING`, and run the gate. The gate is never skipped.**

## Acceptance criteria

- **A1** — G1's read of SG-304's code, each goal confirmed or a gap named with file and line; any fix named.
- **A2** — G2 FAIL on base, PASS on candidate, backend and frontend; the four backend cases each shown with before/after values of both assets.
- **A3** — Gate green with exact counts; files twice green.
- **A4** — No migration; zero Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; no `/tmp`; tree clean except `output/`; scratch removed before the report.
- **A5** — Preflight; health 200 start and end; phase seconds from stamps.
- **A6** — `PB-3` vacuity: a failure would look like a merged quantity, an old pack's date changed, a duplicate that still cannot become a new item, a warning on no match, an id on screen, a test passing on base, a red suite. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Backend:** `backend/app/services/candidates.py` (the duplicate commit path only), `backend/app/api/v1/candidates.py` and the `CandidateDecision` schema file (the one option only); `backend/app/api/v1/assets.py` **only** if the list read cannot filter by name (say why). New `backend/tests/test_sg304_*.py`.
- **Frontend:** `frontend/src/components/AssetForm.tsx` (or the manual-capture form you establish, named), `frontend/src/components/CandidateCard.tsx`, `frontend/src/routes/ReviewPage.tsx`, `frontend/src/lib/labels.ts`, the API hook that posts the decision; new `*.sg304*` tests; older tests only where they assert replaced wording.
- **Any other product file is a STOP and report — even when the fix there is right** (`PG-EV-03`). No migration file.
- **Authorised runtimes:** the preflight, the `make` gates, tests, `eslint`, `tsc`, the build into scratch. No install, no server, no browser.
- Evidence: `docs/worklogs/SG-304r1*` only. No deploy or touch of the running app (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **600 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, remove scratch, commit, write the report, publish.** **No optional goal.** Order G0, G1, G2; commit after each test file. Expected ≈800 s (`UNVERIFIED — my estimate`: four test files ≈350 s; SG-318's gate ≈350 s).

## Report

Destination: `docs/worklogs/SG-304r1_report.md`. The first line states the slice ID, model and effort read from the process arguments (if they are not visible, say so and do not infer them), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; each premise confirmed or falsified with file and line; G1's findings; the four backend cases with before/after values; test changes named; gate counts; changed files; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-304r1`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-304r1 | Report: docs/worklogs/SG-304r1_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

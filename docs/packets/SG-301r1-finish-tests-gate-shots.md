# SG-301r1 — SG-301's retry: update the 26 old tests, prove FAIL on base, run the full gate, take the screenshots

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases, plus throwaway SQLite files under scratch for the screenshot app. No live database read or write.
**Restart: none.** No deploy; rider SG-310 follows this slice.
**Provider: none.** No key, no `.env`, no spend.

**Contract:** recorded `0.59.0` (`AGENTS.md`, D30). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line if you received one; **if you received none, say exactly that** — never copy a line from a packet or a project file.

**Approval:** owner D27, D31 (*"D30 and D31 approved"*), stage C (*"d14 ok"*, L3). This is **the one retry** of SG-301 (the engine refuses a same-ID rerun; `r1` is its suffix rule). **The full task is `docs/packets/SG-301-older-screens-design-and-font.md`; read it.** Its *RETRY — run 2* block is what this slice does; G5 and G6 there are binding as written, with the paths below.

## Why this exists

SG-301 run 1 (`a15b76d..ad3b6e7`, `docs/worklogs/SG-301_report.md`) stopped correctly at its 1100 s hard stop with G0–G3 done and committed (font 5.3.0 OFL-1.1, `frontend/src/lib/labels.ts`, developer copy removed on Inbox, Expiry and the asset page, the header and three screens in the look, EXPIRED 13 px, `SG-301_contrast.md`, two new test files passing). **Left:** 26 older tests failing on `automation` across `InboxPage.test.tsx`, `ExpiryPage.test.tsx`, `AssetDetailPage.test.tsx`, `JobCard.test.tsx`, `App.household-nav.test.tsx`, `components/shell/shell.test.tsx` (run 1's report names each); FAIL on base not run; the gate and the shots not done. **Verify G0–G3 by reading; do not redo them.** Run 1's scratch was moved by the engine's quarantine.

## G0 — Preflight

```
mkdir -p output/SG-301r1-scratch/docker-config
export DOCKER_CONFIG="$PWD/output/SG-301r1-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-301r1/docker.sock"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-301r1/
docker version
docker run --rm busybox true
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`, `PG-PR-03`). `PATH=$PWD/backend/venv/bin:$PATH` for make and `ruff`. `curl -s http://127.0.0.1:8003/v1/health` at start and end; both 200. **`date +%s` at the start of every step.** Scratch only in `output/SG-301r1-scratch/`; npm's cache there too (`~/.npm` is root-owned, run 1). **No `/tmp`.** `output/` itself and `output/dispatch` are never touched.

## R1 — G4 remainder

(a) **FAIL on base:** a `git worktree add output/SG-301r1-scratch/base a15b76d`, `frontend/node_modules` symlinked from the main tree, the two new files copied in; log names and first assertion to `docs/worklogs/SG-301_fail.log`. An import error alone is reported as such, not as a behavioural FAIL. Remove the worktree with `git worktree remove` afterwards.
(b) **The 26 older tests:** update each assertion to the new plain wording, or remove an assertion only where the text is gone on purpose; **name every changed assertion and its reason.** A test asserting **behaviour** (not wording) that now fails is a **STOP and report**. The pre-existing `eslint` error in `App.household-nav.test.tsx` stays out of scope.

## R2 — G5, the full gate

As SG-301's G5, logs `docs/worklogs/SG-301_<step>.log`: `eslint` on every frontend file changed in `a15b76d..HEAD`; `tsc --noEmit`; the frontend build with `outDir` in scratch; `make backend-test` with the image proof (the image build runs `npm ci` against the new lockfile — it must pass); `make frontend-test`; the SG-301 files and every older file you changed, twice consecutively. Exact counts.

## R3 — G6, the screenshots

As SG-301's G6 (6 shots into `docs/worklogs/SG-301_shots/`), with backend `127.0.0.1:18301`, frontend `127.0.0.1:14301` **built with `VITE_API_BASE=http://127.0.0.1:18301`** (a bundle pointing at 8003 is a STOP). In `INDEX.md`, per shot: sha256 (12), size, the proving text and the page heading's computed `font-family`, **read from the DOM**; for Inbox, Expiry and asset shots also that none of `optimistic concurrency`, `blueprint`, `Phase 0`, `AWAITING_REVIEW`, or an `Import <hex>` fragment appears in the rendered DOM. Distinct-hash check quoted. Stop servers by PID, never `pkill -f`.

**Remove `output/SG-301r1-scratch/` by that exact path before you write the report** — a scratch folder left behind blocks the next dispatch (`dirty_unattributable`, run 1).

## Acceptance criteria

- **A1** — FAIL on base logged with names and first assertion (or the import-error fact).
- **A2** — Every one of the 26 assertions changed or removed, each named with its reason; no behaviour test changed.
- **A3** — Gate green with exact counts; image proof passing with `npm ci`; the named files twice green.
- **A4** — 6 shots with hash, size, proving text, DOM font family, DOM absence of the removed strings; distinct-hash check.
- **A5** — Scope: test files, evidence, and only a product fix that a red in R2 strictly needs within SG-301's scope ceiling; zero backend, migration, Dockerfile, compose, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; no `/tmp`.
- **A6** — Preflight proven; health 200 start and end; phase seconds; scratch removed before the report.
- **A7** — `PB-3` vacuity: a failure would look like a red row, a test passing on base, an assertion deleted without a reason, the system font in a shot, a removed string in the DOM, two shots with one hash, a bundle pointing at 8003, scratch left behind. Say which you checked.
- **A8** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

SG-301's scope ceiling binds (its packet), plus: older frontend test files named in run 1's report; evidence `docs/worklogs/SG-301*`. **Authorised runtimes:** SG-301's list, plus `git worktree add/remove` under the scratch path. **A denied privileged operation is a STOP** (`PB-2`).

## Hang bounds

As SG-301's packet; image proof **600 s**.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1200 s by your stamps, stop, remove scratch, commit, write the report, publish** — a hard line, not a target. **No optional goal.** Order R1, R2, R3; commit after each. Expected ≈1100 s (`UNVERIFIED — my estimate`: test updates ≈300 s, gate ≈300 s, scratch app and shots ≈500 s per SG-302/SG-308). A stop leaves the rest `REMAINING`.

## Report

Destination: `docs/worklogs/SG-301r1_report.md` (run 1's report stays as it is). The first line states the slice ID, model and effort read from the process arguments, working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; each changed assertion and reason; gate counts; the shot table; changed files; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-301r1`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-301r1 | Report: docs/worklogs/SG-301r1_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.** A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

# SG-307r1 — Finish SG-307: three small fixes, then the full gate SG-307 did not reach

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named: the full suites run.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — test databases. No live database read or write.
**Restart: none.** No deploy; a screenshot slice and a rider follow.
**Provider: none.** No key, no `.env`, no spend.

**Contract:** recorded `0.59.0` (`AGENTS.md`, D30). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line if you received one; **if you received none, say exactly that.**

**Approval:** owner D18, D33 (*"D33 approved."*: SG-307, its shots, rider, wording slice, SG-304); stage C (*"d14 ok"*, L3). This is SG-307's one retry.

## Why this exists

SG-307 (`0dd3fa7..991c4d5`, report `docs/worklogs/SG-307_report.md`) built the catalog and item panel in the new look and passed FAIL-then-PASS (11/1 on base, 12/12 on candidate) and `tsc`, but **stopped at the 1100 s line before the full gate**. The audit found three things to fix first (locations `UNVERIFIED` — establish each):

1. **A band-aid on the Pantry buttons:** `frontend/src/theme/tokens.css` (around `:239`) forces paper on `[data-testid="pantry-tile"] button` with `!important`, because SG-307's packet kept `PantryPage.tsx` out of scope while its inline `ACTION_STYLE` (`frontend/src/routes/PantryPage.tsx:51`) still says `hsl(var(--card))`. **Fix it at the source:** `ACTION_STYLE` uses the paper ground and `--line` border (or the shared `sg-paper-control` rule), and the `!important` Pantry block is removed. Keep the tile buttons ≥ 40 px tall (SG-300).
2. **"Food Beverages":** `labelAssetType` (`frontend/src/lib/labels.ts:102`) title-cases unknown keys, so `food_beverages` reads *Food Beverages*. The Expiry page already shows *Food & beverages* and *Documents/other* — **find where those words come from and use that one source** in `labelAssetType` for every key it has; say which source.
3. **"Version N" on the item panel** (`frontend/src/components/shell/ItemInspectorDrawer.tsx:448`) is system detail an owner does not need. Remove it from the screen; keep the value as a `data-version` attribute if a test needs it. The `If-Match` header behaviour does not change.

## G0 — Preflight

```
mkdir -p output/SG-307r1-scratch/docker-config
export DOCKER_CONFIG="$PWD/output/SG-307r1-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-307r1/docker.sock"
export PATH="$PWD/backend/venv/bin:$PATH"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-307r1/
docker version
docker run --rm busybox true
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8003/v1/health
```

`docker version` shows a **Server** section and the run is rc 0; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). Health 200 at start and end. **`date +%s` at the start of every step.** Scratch only in `output/SG-307r1-scratch/` (npm's cache there too); **no `/tmp` for anything**; `git status --short` clean except `output/` before the report. `output/` itself and `output/dispatch` are never touched. **No server is started.**

## R1 — The three fixes, with tests

Each fix above, then in `*.sg307r1.test.tsx`: a Pantry tile button's inline style no longer names `--card` and `tokens.css` has no `!important` rule for `pantry-tile`; `labelAssetType("food_beverages")` equals the Expiry page's word; the panel renders no `Version` text. FAIL on base (`origin/automation`), PASS on candidate; logs `docs/worklogs/SG-307r1_fail.log`, `SG-307r1_pass.log` (names and first assertion only). Older tests asserting replaced wording updated, each named. Commit.

**Time rule: if R1 is not committed by 500 s by your stamps, commit what is done, mark the rest `REMAINING`, and go to R2. R2 is never skipped.**

## R2 — The full gate

As SG-312's G3 (`docs/packets/SG-312-sg301-design-follow-ups.md`; SG-301r1's R2 before it): `eslint` (the one known error in `App.household-nav.test.tsx` named, nothing else), `tsc`, the frontend build into scratch, `make backend-test` (host and image proof), `make frontend-test`; then **every `*.sg307*` file and every older file SG-307 or this retry changed, run twice**. Logs `docs/worklogs/SG-307r1_<step>.log`, exact counts. Commit.

## Acceptance criteria

- **A1** — The three fixes, each saying how and naming the file; the source of the category words named.
- **A2** — R1 FAIL on base, PASS on candidate; older tests named.
- **A3** — Gate green with exact counts; files twice green.
- **A4** — Zero backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; no `/tmp`; tree clean except `output/`; scratch removed before the report.
- **A5** — Preflight; health 200 start and end; phase seconds from stamps.
- **A6** — `PB-3` vacuity: a failure would look like an `!important` Pantry rule still present, `--card` in `ACTION_STYLE`, *Food Beverages* rendered, *Version* rendered, a red gate step, a twice-run that differs. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Product:** `frontend/src/routes/PantryPage.tsx` (`ACTION_STYLE` and the buttons using it only); `frontend/src/theme/tokens.css`; `frontend/src/lib/labels.ts`; `frontend/src/components/shell/ItemInspectorDrawer.tsx` (the version line only); the file that holds the Expiry category words only if reusing it needs an export. Any other product file is a STOP and report (`PG-EV-03`).
- **Tests:** new `*.sg307r1*` files; older tests only where they assert replaced wording or styling, each named.
- **No backend file.**
- **Authorised runtimes:** the preflight, the `make` gates, tests, `eslint`, `tsc`, the frontend build into scratch. No install, no server, no browser.
- Evidence: `docs/worklogs/SG-307r1*` only. No deploy or touch of the running app (`PG-EV-06`).
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; host suite **600 s**; image proof **600 s**; frontend suite **600 s**; one test file **300 s**; frontend build **300 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, remove scratch, commit, write the report, publish.** **No optional goal.** Order G0, R1, R2; commit after each. Expected ≈700 s (`UNVERIFIED — my estimate`: three small fixes ≈250 s; SG-312's gate ≈300–400 s).

## Report

Destination: `docs/worklogs/SG-307r1_report.md`. The first line states the slice ID, model and effort read from the process arguments (if they are not visible, say so and do not infer them), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; each premise confirmed or falsified with file and line; how each fix was met; test changes named; gate counts; changed files; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-307r1`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-307r1 | Report: docs/worklogs/SG-307r1_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

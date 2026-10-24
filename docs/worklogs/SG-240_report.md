SG-240 — roadmap row 11: the cosmetics opened-date countdown and the app's logging configuration.

Identity (CO-78, from process arguments, never a system-prompt label): `model=opencode-go/deepseek-v4.1-flash effort=max`, read from `/proc/3340493/cmdline` (`opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant max ...`). Served-model response metadata unavailable; no substitute value claimed.

dir=`/home/andrei/StorageGenie`; remote=`git@github.com:Andovol/StorageGenie.git`.

BASE: ref requested `origin/automation` -> resolved commit `8e227604507f6fb864fd5cee41123bd1456330b3` (equals the start HEAD; measured 2026-10-24T15:18Z). The two fields are separate; no served image is claimed to equal this hash.

WORK_HEAD: the commit that carries this report. A file cannot carry its own hash (CO-55(b)); `docs/worklogs/SG-240_receipt.log` names it after publication.

Contract echo (`/home/andrei/storagegenie-contract/CODER.md` line 3, verbatim): "**Contract version: 0.52.0** — **echo this line verbatim in your receipt.** It is the only proof that you".

Contract chain: repo `AGENTS.md` line 4 `0.52.0` == `/home/andrei/storagegenie-contract/VERSION` `0.52.0` == `CODER.md` line 3 `0.52.0`. The separately published payload was not re-fetched (network bound: loopback plus container-runtime).

Spend: **$0.000000 actual vs $0 bound**; zero provider calls (no provider code path was invoked; no metered client ran).

Terminal class: **product change, not deployed** (`PG-PR-04`). The served app still runs the old code; the next close-deploy rider builds, recreates and observes the pass line live.

## (a) Premises, findings, deviations

Premises (a)–(h) were checked before building:

- (a) verified: `grep -rn "setLevel|basicConfig|dictConfig|logging.config" backend/app --include=*.py` returned nothing before this slice; the old-image container's fresh process under uvicorn's config measured `root_level=30 daily_effective_level=30 root_handlers=0` and zero daily-pass lines (`SG-240_premises.log`).
- (b) verified from the installed uvicorn 0.52.4, in the container, not memory: `disable_existing_loggers=False`, `root_entry=None`, loggers `uvicorn`, `uvicorn.access`, `uvicorn.error`; `uvicorn` has `handlers=['default'] propagate=False` (`SG-240_premises.log`).
- (c) verified: `app/services/reminders/daily.py:23` `logger = logging.getLogger(__name__)`, and the INFO line at `:75`; the new container emits exactly that line once.
- (d) verified: `candidates.py:897` writes `field_path=field_path` for candidate fields including `opened_date`; planning `OPENED_DATE_FIELD = "opened_date"` (`planning/service.py:55`) and chat (`chat/service.py:47`) read `json.loads` and keep only `str`.
- (e) verified: only `cosmetics_personal_care` declares `opened_date_tracking=True`; taxonomy already exposes the flag.
- (f) verified before the change: no opened-date write route and no countdown reader existed (only candidates/planning/chat references).
- (g) followed: `opened_countdown.py` takes caller-supplied `as_of`, has no clock, writes nothing, uses `lifecycle.active_clause()` and `expiry_engine._accepted_classification_slug`.
- (h) measured read-only in G5: 1 household, 7 ACTIVE assets, 1 accepted classification (`food_beverages`), **0 cosmetics**, **0 accepted opened dates** — the new section will render its empty state live.

Findings / deviations:

I1. **Full frontend eslint is not clean, and the one error is pre-existing in an untouched file outside the ceiling.** `eslint src` reports `src/App.household-nav.test.tsx:2:10 'fireEvent' is defined but never used` (exit 1). That file is unchanged from BASE (`git show HEAD:frontend/src/App.household-nav.test.tsx` line 2 already imports `fireEvent`) and the packet's ceiling forbids editing it, so it was not touched. `eslint` on every touched frontend file exits 0.
I2. **Full `mypy app` is not clean at BASE either**: 41 errors in 9 untouched files (`app/api/v1/assets.py`, `evidence.py`, `households.py`, `review_tasks.py`, `app/main.py`, `app/models/base.py`, `app/schemas/asset.py`, `app/services/asset_service.py`, `audit_service.py`). Filtering the output for the five touched backend files returns zero lines; `ruff` on all touched backend files is clean.
I3. The default `/run/docker.sock` denied this lane. The dispatch-scoped socket `/run/dispatch-storagegenie-SG-240/docker.sock` answered (`RUNTIME_SOCKETS=docker.sock`), and `DOCKER_CONFIG=/tmp/sg240-docker-config` was used because `/home/andrei` is root-owned. No `sudo` was attempted; this is a lane socket, not a privileged-denial workaround.
I4. The old-image "before" container answered health **503** because `/app/data/storage` did not exist in that throwaway container. The after proof creates the directory in its own container and answers 200; the 503 is a storage-dir absence, not the logging change.
I5. The packet's clamp example ("31 January opened date plus 12 months ends on 31 December") is arithmetically inconsistent with a 12-month window. The stated rule was implemented exactly (add months, clamp the day to the target month's last day): 31 January + 12 months ends 31 January next year; the clamp is proven with 29 February + 12 months -> 28 February.
I6. The G1 image was rebuilt from the final tree after the UI edits; the build reused cached frontend/npm and pip layers, changed no lockfile, and took 14.77 s.

## (b) Actions

Changed paths (ceiling only):

- `backend/app/logging_config.py` (new): one idempotent stderr handler, root level INFO, format `LEVEL: name - message`.
- `backend/app/server.py`: `configure_logging()` is the first statement of the lifespan, which runs after uvicorn applies its own config.
- `backend/app/plugins/expiry_tracker.py`: `OPENED_DATE_FIELD = "opened_date"`; `Category.opened_window_months` (cosmetics = 12, DECLARED UNCALIBRATED with the EU PAO source in the comment); `parse_opened_date` / `store_opened_date` using the existing `_write_assertion` (accepted assertion, supersede, audit row).
- `backend/app/services/opened_countdown.py` (new): pure countdown over ACTIVE rows; `add_months` calendar arithmetic with target-month clamp; nulls when no opened date.
- `backend/app/api/v1/plugins.py`: `POST /assets/{asset_id}/opened` and `GET /opened`.
- `backend/tests/test_sg240_logging_config.py`, `backend/tests/test_sg240_opened_countdown.py` (new).
- `frontend/src/api/types.ts`, `frontend/src/api/client.ts`: countdown/write types and wrappers.
- `frontend/src/components/OpenedCountdownSection.tsx` (new) and its test; `frontend/src/routes/ExpiryPage.tsx` (section below the unread reminders) and `ExpiryPage.test.tsx`.
- `docs/worklogs/SG-240*` (this report, the receipt transcript after publication, and the evidence captures).

G1 container proof: built `storagegenie-backend:sg240-proof` from this tree (`storagegenie-backend:latest` untouched), ran it detached with `--network none`, no bind mount, `DATABASE_URL=sqlite:////tmp/sg240-proof.db`, `mkdir -p /app/data/storage && alembic upgrade head && exec uvicorn app.server:app --host 127.0.0.1 --port 8000`; read `docker logs`; removed the container. The production container `storagegenie-backend-1` (image `storagegenie-backend:latest`) was never recreated, stopped or written to. No migration, restart, compose, nginx or host operation ran.

G5: one read-only HTTP census over `http://127.0.0.1:8003` (households -> paginated assets -> asset detail), counts only; no write route and no POST.

G2/G3/G4: implemented and tested as below. No production data was read or written beyond G5's census; no dependency file changed; no ignored file was staged.

## (c) Verification

**Q1 — PASS (container-proven).** In the throwaway container from this tree, under uvicorn's own `LOGGING_CONFIG`, the fresh-process probe reads `before_configure root_level=30 daily_effective_level=30 root_handlers=0` and `after_configure root_level=20 daily_effective_level=20 root_handlers=1`. Health inside that container: `200`. The raw `docker logs` startup section (full capture `docs/worklogs/SG-240_after.log`):

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     app.services.reminders.daily - Daily reminder pass completed as_of=2026-10-24 households_visited=0 reminders_created=0 errors=0
INFO:     127.0.0.1:43226 - "GET /v1/health HTTP/1.1" 200 OK
```

`grep -c "Daily reminder pass completed"` on that log = **1** (no duplicate). The zero counts are the container's own empty database; no household was seeded. The proof container was removed; `docker ps` afterwards listed only `storagegenie-backend-1 | storagegenie-backend | Up About an hour (healthy)` (old code, untouched). The before image logged **0** such lines (`docs/worklogs/SG-240_before.log`).

Seen-to-fail (PG-EV-01), unit gate without the module:

```
tests/test_sg240_logging_config.py:14: in <module>
    from app.logging_config import configure_logging
E   ModuleNotFoundError: No module named 'app.logging_config'
1 error in 0.13s
```

With the module: `1 passed`. The test asserts the daily logger's effective level is INFO and that one emitted record reaches the app handler exactly once.

**Q2 — PASS.** `backend/tests/test_sg240_opened_countdown.py` (16 tests total with G3): stores `field_path="opened_date"`, `value_json == json.dumps("YYYY-MM-DD")` (bare JSON string), `source_type="user"`, `review_state="accepted"`; a second write supersedes the first (one active row); refusals tested for non-tracking category (detail names `food_beverages`), unclassified asset, future date (`must not be after today (UTC)`), malformed/missing date, unknown asset (404), household mismatch (403); the audit row `plugin.assertion.write` is asserted with the stored value and accepted state.

**Q3 — PASS.** Known opened `2026-01-31` against `as_of=2026-02-15` returns `days_open=15`, `window_end=2027-01-31`, `days_remaining=350`, `window_months=12`, `window_source="category_default"`; no opened date returns `opened_date/days_open/days_remaining/window_end = null` (never zeros); a food asset and an unclassified asset are absent; `29 February 2024 + 12 months -> 28 February 2025` (clamp; `add_months` also checked for 31 Jan + 1 month and leap years); an empty household returns `{"household_id", "as_of", "rows": []}`; unknown household 404, malformed `as_of` 422; ARCHIVED assets are absent.

**Q4 — PASS on the code paths, with finding I1.** Component tests: row renders `Opened 2026-01-31`, `15 days open`, `350 days left`, `12-month default`; saving posts `{"opened_date": "2026-10-01"}` to the asset route and re-reads the same query key; empty household renders `No cosmetics items to track.`; a passed window says `Window passed 123 days ago`. Targeted: 17 passed (component + ExpiryPage). Full frontend suite: 30 files, 306 passed in 10.72 s. `tsc && vite build` clean (2.44 s). `eslint` on all touched files exits 0; full `eslint src` has the one pre-existing error named in I1 (untouched, outside the ceiling).

**Q5 — PASS (read-only).** `households=1`, `active_assets=7`, `by_accepted_category={'food_beverages': 1}`, `with_accepted_opened_date={}`. So the live household has no cosmetics item and no opened date; the new section will show its empty state. Full capture: `docs/worklogs/SG-240_census.log`.

**Suite and statics.** Host backend suite baseline at BASE: **2 failed, 740 passed** in 61.73 s. Candidate: **2 failed, 757 passed** in 61.85 s — the same two environmental reds named by the packet (`test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` and `::test_ocr_has_text_boxes_and_mean_confidence`), not fixed, no host change. `ruff` on touched backend files: clean. `mypy` on touched files: zero errors (the 41 pre-existing errors in 9 untouched files remain, I2). Diff touches ceiling paths only; no lockfile or ignored file staged.

**Worlds (`PG-SC-09`).** *Passes but is wrong* is ruled out by the pasted container log (the line is real and appears once), the before-image zero, the seen-to-fail module absence, and the countdown test asserting the real counts for a known date (not hardcoded). *The feature working makes the criterion fail* is a pass here: a zero-household pass still logs the line with zeros (observed), and a household with no cosmetics renders the empty state (observed in G5 and the component test).

## Receipt

The work was pushed to `automation` with a clean worktree before the note was added. The note was added on the work commit, the notes ref pushed, the refspec fetched into a mapped local name, listed and grepped for `SG-240`, and read back with `git notes ... show`. Executed output, verbatim (also committed as `docs/worklogs/SG-240_receipt.log`):

```
SG-240 receipt transcript utc=2026-10-24T15:45:29Z epoch=1792856729
Contract echo (/home/andrei/storagegenie-contract/CODER.md line 3, verbatim): **Contract version: 0.52.0** — **echo this line verbatim in your receipt.** It is the only proof that you
Work-HEAD=37d28e54d9bf3009a60c2dcca3c2a93034b54e03
$ git notes --ref=refs/notes/storagegenie-coder-reports show 37d28e54d9bf3009a60c2dcca3c2a93034b54e03
error: no note found for object 37d28e54d9bf3009a60c2dcca3c2a93034b54e03.
pre_show_exit=1
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-240 | Report: docs/worklogs/SG-240_report.md | Work-HEAD: 37d28e54d9bf3009a60c2dcca3c2a93034b54e03" 37d28e54d9bf3009a60c2dcca3c2a93034b54e03
notes_add_exit=0
$ git notes --ref=refs/notes/storagegenie-coder-reports show 37d28e54d9bf3009a60c2dcca3c2a93034b54e03
Dispatch-ID: SG-240 | Report: docs/worklogs/SG-240_report.md | Work-HEAD: 37d28e54d9bf3009a60c2dcca3c2a93034b54e03
notes_show_exit=0
$ timeout 300 git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   0d37c55..856a5a6  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
notes_push_exit=0
$ git fetch origin +refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-sg240-fetched
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-sg240-fetched
readback_fetch_exit=0
$ git rev-parse refs/notes/storagegenie-coder-reports-sg240-fetched
856a5a69e2fffe5133f8790c066d4dff95fee9ca
$ git notes --ref=refs/notes/storagegenie-coder-reports-sg240-fetched list | grep 37d28e54d9bf3009a60c2dcca3c2a93034b54e03
11f9e9750b362677de8be4309d26552e8aea1d7a 37d28e54d9bf3009a60c2dcca3c2a93034b54e03
$ git notes --ref=refs/notes/storagegenie-coder-reports-sg240-fetched show 37d28e54d9bf3009a60c2dcca3c2a93034b54e03
Dispatch-ID: SG-240 | Report: docs/worklogs/SG-240_report.md | Work-HEAD: 37d28e54d9bf3009a60c2dcca3c2a93034b54e03
fetched_show_exit=0
$ git notes --ref=refs/notes/storagegenie-coder-reports-sg240-fetched show 37d28e54d9bf3009a60c2dcca3c2a93034b54e03 | grep -c 'Dispatch-ID: SG-240'
1
note=yes
```

This report did not pre-claim `note=yes`; the line above was produced by the executed read-back after publication.

## Timing (CO-79 / PG-PR-06)

Lane start `2026-10-24T15:18:22Z`, epoch `1792855102` (the dispatch runtime directory's stamp). Report writing begins `2026-10-24T15:43:26Z`, epoch `1792856606`: **1504 s** elapsed of the 2100 s lane budget (71.6%) and 1504 s of the packet's 1500 s new-work bound — no new work started after the bound; only commit, report and receipt remain. Legs: baseline suite **61.73 s** (of 600 s; over 60 s, named); new backend tests **3.05 s**; G1 image build **14.77 s** (of 600 s) + container run/read/remove **6 s** (of 120 s); G5 census, premises probes, lint/type checks and log writes are the aggregate remainder (each well under 60 s); candidate suite **61.85 s** (of 600 s; over 60 s, named); frontend targeted tests **1.91 s**; full frontend suite **10.72 s**; frontend build **2.44 s**. No command was killed; no command approached its bound.

## Constraints answered

- Scope: only the ceiling paths plus `docs/worklogs/SG-240*` were written; no model, migration, config, Dockerfile, compose, Makefile, reminders/planning/chat/candidates/expiry_engine edit.
- No production write, no restart, no migration, no host operation. `storagegenie-backend:latest` was not overwritten; the proof container was new, throwaway and removed.
- `PG-PR-04`: the served app still runs the old code; this slice makes the change live only at the next close-deploy rider.
- `PG-IC-07`: time-dependent checks use the live UTC clock (opened-date refusal, daily-pass line `as_of=2026-10-24`); fixed dates are only known-pair test inputs for the pure countdown.
- `PG-IC-01`: every goal maps to a ceiling file; no blanket exclusion claimed.
- Role guard: no dispatch verb, no unit start/poll, no sudo, no secret in any artifact.

## Vacuity (PB-3)

No criterion rests on an empty diff, an empty set, a skipped gate or a grep that could not match. The container log is pasted and counted (1, not 0, on the candidate; 0 on the old image), the unit gate is shown failing without its module, the countdown test asserts real day counts against a supplied `as_of`, and the empty-household case asserts the same shape with an explicit empty list rather than a fallback. The only empty results are the live census (7 active assets, 1 classified, 0 cosmetics) and the empty-state tests, and both are reported as the pass world the packet names.

## CO-103 skipped

- Full suite inside a container: the packet forbids a container sweep; the host suite ran, and the image run is scoped to the G1 proof.
- Browser render: component tests plus `tsc`/`vite build` cover the section; no browser was launched.
- Production deploy/live observation: `PG-PR-04` puts it in the next rider, not this slice.
- Seeding a household in the proof container: unnecessary; the zero-household line proves visibility and is the named pass world.
- Dispatch/status verb: the role guard forbids it.

UNCLEAR
FIRST READ: I read D1's "12 months" as a category default to be named in the response (not hidden), and the packet's clamp example as illustrative; the arithmetic did not match 12 months, so I implemented the stated rule and flagged the example.
DURING EXECUTION: the default Docker socket denied the lane and the dispatch-scoped socket worked; the old-image "before" container's health was 503 only because its throwaway container lacked the storage directory; full frontend lint and full mypy carry pre-existing reds in untouched files outside the ceiling.
REMAINING: the served app still runs the old code; the logging configuration and the countdown become live at the next close-deploy rider. The live household has no cosmetics item, so the first live view will be the empty state. The pre-existing eslint and mypy reds in untouched files remain.

Verification: PASS

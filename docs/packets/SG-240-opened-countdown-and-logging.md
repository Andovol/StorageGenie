# SG-240 — Roadmap row 11: the cosmetics opened-date countdown, and the app's logging configuration

`PB-1`–`PB-6` bind (`CODER.md` §14).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none.** Scratch only: the backend tests use a temporary SQLite, and the G1 container proof's SQLite lives **inside the throwaway container**. The production SQLite is not read and not written by this slice. **Restart: none.** No service, container, image, nginx or host operation of any kind touches the running app — the G1 proof runs a **new, throwaway container** from an image built under a **new tag**, with no bind mount and no write to any existing container.

**Autonomy: L3** (owner-approved stage: roadmap row 11 plus its close-deploy rider). Settings ride the trigger, never this packet.

**Context and standing lines.** Eight items, all as **hypotheses about the tree carrying this packet** — verify each before building on it; a difference is a finding, not an obstacle (`PB-1`, `PG-IC-09`):

- **(a) The app configures no logging.** Nothing in `backend/app/` calls `logging.basicConfig` or `dictConfig`. SG-239 MEASURED this in the served container: the root logger's level is 30 (WARNING), so the daily pass's INFO record is **dropped** — the container log holds zero of it. Reproduced in a throwaway container from the shipped image.
- **(b) uvicorn applies its own `LOGGING_CONFIG` at startup** (uvicorn 0.52.4 in `backend/requirements.lock`). That config defines the `uvicorn`, `uvicorn.error` and `uvicorn.access` loggers and **no root entry**, and `logging.config.dictConfig` clears existing handlers — so a `basicConfig` executed at import time is undone. **Verify this in the container, from the installed uvicorn's own config, not from memory.**
- **(c) The daily pass's success line is emitted by `logger = logging.getLogger(__name__)`** in `backend/app/services/reminders/daily.py` — logger name `app.services.reminders.daily`, level INFO, one line per pass carrying `as_of`, `households_visited`, `reminders_created`, `errors`. SG-238 added that line; SG-238's `caplog` test proved **emission**, not **visibility**.
- **(d) The `opened_date` assertion convention is a BARE field path and a bare JSON string.** `backend/app/services/candidates.py` writes a candidate field as an assertion with `field_path` equal to the field name (`"opened_date"`) and `value_json = json.dumps(value)` — a bare JSON string for a date. The two existing readers expect exactly that: `backend/app/services/planning/service.py` (`OPENED_DATE_FIELD = "opened_date"`, reads `json.loads(...)` and keeps it only `if isinstance(..., str)`) and `backend/app/services/chat/service.py` (same shape).
- **(e) `cosmetics_personal_care` is the only category with `opened_date_tracking=True`** (`backend/app/plugins/expiry_tracker.py`, `CATEGORIES`). `Category.profile()` already publishes that flag, and `GET /v1/assets/taxonomy` already exposes it per category.
- **(f) There is no user-facing write path for an opened date and no countdown read path.** The only writers of an `opened_date` assertion are the candidate-accept path and the extraction proposal; nothing counts days-open.
- **(g) `backend/app/services/expiry_engine.py` is the precedent for a pure computation over existing rows**: a caller-supplied `as_of` day, no clock of its own, no writes, ACTIVE assets only via `lifecycle.active_clause()`, and the accepted category slug read through `expiry_engine._accepted_classification_slug`.
- **(h) The live household's data shape is UNKNOWN to the packet's author.** G5 reads it, read-only, and reports counts per category. Do not assume any cosmetics item exists.

**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.

**Standing lines:** no new dependencies and no change to `backend/requirements.lock` or `frontend/package-lock.json` · no provider calls ($0 — a metered call is a STOP-and-report) · NETWORK: loopback plus container-runtime only, nothing else · no secret in any artifact.

**Money posture:** this slice makes zero provider calls; the spend line reads $0.000000 actual vs $0 bound.

**Guards invoked:** `PG-EV-01` seen-to-fail · `PG-EV-02` artifact-not-command · `PG-EV-03` stop-not-disclosure · `PG-EV-05` property-not-command · `PG-EV-07` real-source · `PG-EV-08` pre-state-before-claim · `PG-EV-09` both-runs-committed · `PG-EV-11` advisory-first · `PG-SC-01` read-and-write-path · `PG-SC-02` new-field-read-back · `PG-SC-08` baseline-in-the-same-slice · `PG-SC-09` name-the-world · `PG-SC-12` proof-against-the-real-thing · `PG-IC-01` cross-product · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-01` capability-model · `PG-PR-03` denied-is-stop · `PG-PR-04` how-code-becomes-live · `PG-PR-06` runtime-versus-budget · `PG-DP-01` delivered-by-the-delivery-path · `PG-DP-02` no-full-sweep-in-a-restart-gated-slice.

## Why this exists

Two debts, both recorded by this project's own audits, both cheap to fix and both blocking the next product row.

1. **The app logs nothing at INFO, so the daily pass is invisible in production.** SG-238 added the pass's success line and proved it **emitted** (a `caplog` test). SG-239 served that delta and MEASURED the opposite of what the reader expected: the container log held **zero** of the line, because the app configures no logging and uvicorn's config leaves the root logger at WARNING. The rider that would have shown the line live therefore could not. Roadmap row 11's close-deploy rider is where the line must first appear live — so the configuration has to land first.
2. **Roadmap row 11 is "Partly built" because a cosmetic has no opened-date countdown.** The data flag exists (`opened_date_tracking`), the proposals carry an `opened_date`, the planning and chat services already read an accepted one — but **nothing lets the user record the date**, and nothing counts the days. The blueprint's own wording for this category is "Opened-date secondary countdown".

Both ride in one slice because they are one small product step and one small platform step, and the owner's stage approves them together.

## Decisions the packet makes (implement these; do not re-derive them)

- **D1 — the countdown's end is the category's after-opening window.** The window is a per-category constant carried on the live `Category` row (`backend/app/plugins/expiry_tracker.py`), `cosmetics_personal_care` declaring **12 months**. The value is **DECLARED UNCALIBRATED** at the site with its source in a comment: the EU period-after-opening (PAO) symbol (Regulation 1223/2009 Art. 19) is the printed "12M" open-jar figure for cosmetics with a minimum durability over 30 months, and the printed figure varies per product — the pack may say 6M or 18M. **The response names the window and its source** (`window_months`, `window_source: "category_default"`) so the UI can show it and the number can be corrected later. A **per-item PAO override is parked** — out of scope for this slice.
- **D2 — storage is one accepted assertion.** `field_path = "opened_date"`, `value_json = json.dumps("YYYY-MM-DD")` (a bare JSON string, per premise (d)), `source_type = "user"`, `review_state = "accepted"`. A new value **supersedes** the previous active one. The plugin's own `_write_assertion` already does exactly this supersede-and-write, and it writes the audit row — **use it** rather than a second writer.
- **D3 — the read endpoint returns one row per ACTIVE asset whose accepted classification is in an opened-date-tracking category, including rows with no opened date yet** (so the UI can offer the form). An asset with no accepted classification, or in a category that does not track opened dates, is **not a row** — it is not an "unopened cosmetics item".
- **D4 — the UI is one new section on the Expiry page**, below the existing unread-reminders block: a row per cosmetics item with the countdown, and a date input plus a save button on a row that has no opened date yet.
- **D5 — the logging configuration is the app's own, at startup.** The mechanism is yours; the properties are not (G1).

## G1 — the app's logging configuration, proven in a container

The app's INFO records must reach the **container's log**, exactly once each, under the served entrypoint `uvicorn app.server:app`.

- Configure logging where it survives uvicorn's own configuration — the app's startup (the lifespan in `backend/app/server.py`) runs **after** uvicorn applies `LOGGING_CONFIG` (premise (b)). **Do not assume: show in the container which level the app logger actually has, before and after your change.**
- Required properties, all observable in a container:
  1. `app.services.reminders.daily`'s effective level is INFO (and the app's records are not dropped by an ancestor's level).
  2. The daily pass's success line **appears in the container's log** — `docker logs`, not `caplog`.
  3. Each app record appears **once** (no duplicate handlers, no doubled lines).
  4. The app still serves: the health endpoint answers 200 inside the container.
- **The proof runs in a container**, per the owner's instruction and SG-239's guard (*a `caplog` test proves emission, not visibility*):
  - build the image from **this slice's tree** under a **new tag** (`storagegenie-backend:sg240-proof`) — **never overwrite `storagegenie-backend:latest`**, which is the tag the running production container was built from;
  - run it **detached, throwaway, no bind mount**, with a SQLite **inside the container** (`DATABASE_URL=sqlite:////tmp/<name>.db`) and the schema created in that same container (`alembic upgrade head`, which reads `DATABASE_URL` from `app.config.settings`) before the app starts;
  - read `docker logs` and **paste the raw log lines** into the report;
  - remove the container when done.
- **The claim is VISIBILITY.** The counts in the line are the container's own: a container whose database holds no household logs `households_visited=0`, and that still proves the line is visible — say so plainly rather than seeding rows to make the line look fuller. If you do seed one household inside the throwaway container (never the production one), say that you did and why.
- The build must reuse the existing image cache layers; **no lockfile changes**. If a layer needs the network and the lane denies it, that is a STOP (`PB-2`, `PG-PR-03`) — **do not change a lockfile to work around it**.
- **A unit test** asserts the configuration's properties in-process (the app logger's effective level after configuration, and that a record emitted by `app.services.reminders.daily` is handed to the handler). It complements the container proof; it does not replace it.

## G2 — the write path: record the opened date

- **Plugin function** in `backend/app/plugins/expiry_tracker.py`: validate and store the opened date (D2). Validation: `YYYY-MM-DD` exactly; **a date after the live UTC day is refused**; the asset must have an **accepted classification whose category has `opened_date_tracking=True`** — refused otherwise, with a message naming the reason.
- **Route** `POST /v1/plugins/expiry-tracker/assets/{asset_id}/opened` in `backend/app/api/v1/plugins.py`, matching the file's existing shape: the plugin handshake (`_plugin(payload)`), the household-scoped asset lookup (`_asset`), `422` with a plain detail for a validation failure, `404` for an unknown asset, `403` for a household mismatch, and a `db.commit()` before the response. The response carries the asset id and the stored assertion in the file's existing `_assertion_view` shape.
- The write must leave the same trail every other plugin write leaves: the assertion row, the supersede of the previous active one, and the audit row.
- **Tests** (new module, `backend/tests/test_sg240_*.py`): the write stores an accepted assertion with a bare JSON string value; a second write supersedes the first; a non-`opened_date_tracking` category is refused; a future date is refused; a malformed date is refused; the audit row is written.

## G3 — the read path: the countdown rows

- **Pure computation** (new module `backend/app/services/opened_countdown.py`, or an equivalent place inside the ceiling) over existing rows, following premise (g): `as_of` is supplied by the caller (default: the live UTC day), there is no clock of its own, no write, ACTIVE assets only, the accepted category slug read as the engine reads it, and the window read from the **live** `CATEGORIES` row — never from a stored snapshot.
- Each row: `asset_id`, `display_name`, `category`, `opened_date` (nullable), `days_open` (nullable), `window_months`, `window_source`, `days_remaining` (nullable; negative means the window has passed) and the countdown's end date.
- **Calendar-month arithmetic**, not 30-day blocks: the end date is the opened date plus the window in months, **clamped to the last day of the target month** (a 31 January opened date plus 12 months ends on 31 December). State the clamp rule in the report.
- **Route** `GET /v1/plugins/expiry-tracker/opened?household_id=…&as_of=…` in `backend/app/api/v1/plugins.py`, shaped like the file's `status` route: `404` for an unknown household, `422` for a malformed `as_of`, `200` with `rows: []` when nothing matches (**never a fallback to another set**).
- **Tests**: a row with an opened date carries the real counts (a known opened date against a known `as_of`); a row without one carries nulls, not zeros; a non-`opened_date_tracking` asset is absent; a month-end opened date clamps as stated; an empty household returns the same shape with an empty list.

## G4 — the UI: the opened countdown on the Expiry page

- **Client wrappers** in `frontend/src/api/client.ts`, following the file's existing shape: one read wrapper for the countdown rows and one write wrapper for recording an opened date. **Types** in `frontend/src/api/types.ts`.
- **A new section on the Expiry page** (`frontend/src/routes/ExpiryPage.tsx`), below the unread-reminders block: one row per returned row, each showing the item name (a link to the asset, as the page already does), the opened date, the days open and the days left, and **the window with its source** ("12-month default" — the number is visible, never hidden). A row whose window has passed says so in words. A row with no opened date yet shows a **date input and a save button**; saving calls the write route and re-reads the same query key — **no local decrement, no optimistic removal** (the page's existing reminder pattern is the model).
- The section must render honestly when the household has **no** cosmetics item: an empty state, not a fake row.
- **Frontend tests**: the section renders a row with the countdown text from a fixture response; saving posts the date and re-reads; the empty case renders the empty state.

## G5 — the live household census (read-only)

Read the running app's data **read-only** (the loopback address the app serves on, per `{{HEALTH_CMD}}`'s host) and report, **as counts only and with no item names**: how many ACTIVE assets the household holds per accepted expiry-tracker category, and how many of them carry an accepted `opened_date`. This is the shape the next rider's live expectations rest on, and it is what tells the owner whether the new section has anything to show. **Read only** — no write, no route that mutates anything.

## Constraints

- **Scope ceiling:** `backend/app/server.py` · `backend/app/logging_config.py` (new, optional) · `backend/app/plugins/expiry_tracker.py` · `backend/app/api/v1/plugins.py` · `backend/app/services/opened_countdown.py` (new) · `backend/tests/test_sg240_opened_countdown.py` (new) · `backend/tests/test_sg240_logging_config.py` (new, or one module covering both) · `frontend/src/api/types.ts` · `frontend/src/api/client.ts` · `frontend/src/routes/ExpiryPage.tsx` · `frontend/src/routes/ExpiryPage.test.tsx` · `frontend/src/components/OpenedCountdownSection.tsx` (new) · `frontend/src/components/OpenedCountdownSection.test.tsx` (new) · `docs/worklogs/SG-240*`. **Anything else is a STOP** — including `backend/app/models/*`, `backend/app/db.py`, `backend/app/config.py`, `backend/app/main.py`, `backend/app/api/v1/reminders.py`, `backend/app/services/expiry_engine.py`, `backend/app/services/reminders/*`, `backend/app/services/planning/*`, `backend/app/services/chat/*`, `backend/app/services/candidates.py`, `backend/Dockerfile`, `docker-compose.yml`, `Makefile`, `backend/alembic/*`, `frontend/src/routes/AssetDetailPage.tsx`, any migration, and any dependency file.
- **Cross-product (`PG-IC-01`):** no blanket exclusion is issued; every acceptance criterion below names a ceiling file above. No goal requires what a constraint forbids.
- **How code becomes live (`PG-PR-04`):** **not in this slice.** The logging configuration and the countdown become live at the **next** close-deploy rider, which builds the image, recreates the container and observes the pass line in the production log. **The report states that the served app still runs the old code** — do not claim a live change.
- **No full-suite sweep on a container.** The backend suite runs on the **host** environment (as it does today); the image run in G1 is scoped to the container proof.
- **The two host reds** (`backend/tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` and `::test_ocr_has_text_boxes_and_mean_confidence`) are **environmental on this host** (SG-238 proved them green inside the project's own image; `make backend-test-image` is the repeatable command; the lane's `sudo -n` is denied and **no host change is authorised**). Quote the host suite's before/after counts with the same numbers and name the two reds as the ones that remain — **do not "fix" them and do not touch the host**.
- **Runtime-versus-budget (`PG-PR-06`):** elapsed per leg against the lane budget, in seconds, with the unit inside the number. Report actual-versus-budget.
- **Publish before the bound.** Order the work **G1 → G5 → G2 → G3 → G4** (cheapest and most load-bearing first), and at **1500 s elapsed** stop starting new work: commit what is finished, write the report, publish the receipt. **A partial slice WITH a receipt is a success; a complete slice with no receipt is a total loss.** The bound is uncalibrated and is set per packet (`G-A9`).
- No fixed dates except this header's authoring-date metadata; every time-dependent check reads the live clock at execution (`PG-IC-07`). No prompt or polling loop. No secret in any artifact.

## Acceptance criteria

- **Q1 (logging, container-proven):** the container's log contains the daily pass's success line **as it is written by the app** — raw `docker logs` output pasted; the app logger's effective level is INFO; no duplicated line; the health endpoint answers 200 in that container; the proof container is removed afterwards; the production container is untouched.
- **Q2 (write path):** recording an opened date stores an accepted `opened_date` assertion with a bare JSON string value and supersedes the previous one; the refusals (wrong category, future date, malformed date, unknown asset, household mismatch) each have a test; the audit row is written.
- **Q3 (read path):** the countdown endpoint returns rows carrying the real counts for a known opened date and a known `as_of`; nulls (not zeros) for an item with no opened date; no row for an asset outside an opened-date-tracking category; the month-end clamp holds; the empty household returns the same shape with an empty list.
- **Q4 (UI):** the section renders a row with the countdown text and the window's source; saving records the date and re-reads; the empty case renders an empty state; the frontend build, lint and type-check pass.
- **Q5 (census):** the live household's counts per category and per opened-date state are reported, read-only, as counts.
- **Worlds named (`PG-SC-09`):** *passes but is wrong* = a gate that asserts nothing (ruled out by the container proof's pasted log and the unit test's seen-to-fail demonstration) or a countdown with hardcoded numbers (ruled out by the test asserting the real counts for a known opened date); *the feature working makes the criterion fail* = the daily pass running with **zero** households (the line still appears, with zeros — that is a pass, not a failure) or a household with **no** cosmetics item (the section renders its empty state — that is a pass, not a failure).
- The **full backend suite runs once on the candidate** with its counts quoted; `ruff` and `mypy` on the touched files clean; frontend `eslint`, `tsc` and `vite build` clean; the diff touches ceiling paths only; **no production data read or written** beyond G5's read-only census; no dependency change; no ignored file staged; **no vacuous pass** (`PB-3`).

## Report

- Work dir `/home/andrei/StorageGenie`, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref:** push the work to `automation`, worktree clean (`CO-55`). Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-240 | Report: docs/worklogs/SG-240_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name, LIST the note contents and grep for this ID, `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- The report's LAST line is exactly one of: `Verification: PASS` — or `Verification: FAIL — <check>` naming the check that failed (`CO-104`).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s per command · 600s suite · 2100s overall (the lane's `RUN_BUDGET_S`); REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units. The Architect's expected elapsed time for this slice is **~1200 s** (bracketed from this lane's recent actuals — 700 s, 397 s, 268 s, 700 s, 324 s — not summed per-goal guesses).

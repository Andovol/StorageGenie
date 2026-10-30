# SG-258 — Household and document dates: classify from the asset page, let Documents/other hold a date, keep a date across reclassification, and correct or clear it

`PB-1`–`PB-6` bind (`CODER.md` §14).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: none.** No production database is opened, read or written; tests use temporary SQLite files.
**Restart: none.** The running container, its image tag and the host are untouched. The deploy rider is a separate slice.
**Provider: none.** No provider is called, no key is read or printed, **no spend**. Target: **$0**.

**Contract chain:** recorded `0.56.0` (this packet's commit) == published payload `contract-v0.56.0`. The host's contract at `/home/andrei/storagegenie-contract/CODER.md` line 3 is the echo this report must carry; the last receipt echo was `0.53.0` (SG-257). If the host still reads `0.53.0`, echo it and state the `0.53.0 → 0.56.0` delta (the Architect's record names it); do not invent a version. If it reads `0.56.0`, the chain is equal.

**Previous report's open items (SG-257):** its `REMAINING` is the root-owned `~/.docker`, so `DOCKER_CONFIG` and an explicit `DOCKER_HOST` stay required (G0); no open product item. Its `I4` (the visible `Clear` label is the accessible `Clear opened date` name) is an observation; the new controls use consistent accessible names and visible text. Its `I2` (the cache-satisfied image) does not apply — this slice builds no image. Its `I5` (live data moved since SG-251) is not this slice.

## Why this exists

Roadmap row 11 is the last product row in flight. Its cosmetics countdown and its opened-date edit/clear are built and served. Its **household-and-document half** is not, and the owner approved this stage on 2026-10-30 (`"d6 - approved"`, D6): a Household chemicals or Documents/other item can be classified, given a date, seen in the Expiry page and reminded at its category windows; documents gain their 60/30-day windows; an accepted date can be corrected; reclassification does not lose a date. No migration; no production data write; no provider call; $0.

Four gaps, each a hypothesis to falsify (`PB-1`):

1. **Documents/other cannot hold a date.** `documents_other` is `has_expiry=False` (`backend/app/plugins/expiry_tracker.py:160-167`), so `classify_asset` writes no expiry assertion and no manual task for it (`:434-450`), and `store_manual_expiry` refuses it as "non-perishable" (`:602-610`). Its shipped `DOCUMENTS_TIERS = {upcoming: 30, long_lead: 60}` (`:130-133`) and the served `long-lead-60-30` descriptor (`backend/app/plugins/descriptor.py:162-167`) are therefore dead. The blueprint's category table says Documents/other = "Long-lead windows (60/30 day) … reminder-only" (`inception/generic_asset_catalog_expiry_tracker_blueprint.md:384`). SG-073 left the question open (`docs/worklogs/SG-073_report.md:129`); this stage answers it. The blueprint's date rule also binds: "the system must never force a date onto a category that doesn't logically need one, and must never fabricate a plausible-sounding date when none is visible" (`:396`).
2. **The app has no way to put an item into either category.** The only writer of the classification is `POST /v1/plugins/expiry-tracker/assets/{asset_id}/classification` (`backend/app/api/v1/plugins.py:125-153`); `frontend/src/api/client.ts` has no classify function (`enterManualExpiry` at `:231`, `recordOpenedDate` at `:308`, `clearOpenedDate` at `:316`); the asset page does not load the taxonomy. `README.md:179-186` documents a curl flow.
3. **Reclassifying an item would erase its active date.** `classify_asset` writes a `{"status": "unknown"}` / `needs_evidence` expiry assertion (`expiry_tracker.py:437-440`), and `_write_assertion` supersedes the previous active assertion (`:344-348`). A proposed OCR date is superseded the same way (`:442-450`).
4. **An accepted date cannot be corrected in the app.** The asset page renders `ExpiryEntryForm` only while `expiryAssertion?.review_state === "needs_evidence"` (`frontend/src/routes/AssetDetailPage.tsx:403-405`); the page and the form both use `assertions.find((item) => item.field_path.endsWith("expiry_date"))` (`:330`; `frontend/src/components/ExpiryEntryForm.tsx:18`), which can pick a superseded or bare row. The asset-detail API returns **all** assertions with `created_at`, ordered by `field_path` only (`backend/app/api/v1/assets.py:131-144`; `backend/app/models/asset.py:40-44`), so the frontend can select the active one deterministically by exact field and latest `created_at`.

The second opinion (SG-260 blind, SG-261 critique) picked the same four approaches and raised the refinements below: suppress the OCR proposal for documents; add the category hint; add optional `If-Match`; preserve only a valid accepted date and clear on a move to `non_perishable`; gate the form on the classification profile; read the exact field and latest `created_at`; add Clear parity with D4; add a `valid_until` date type. They are folded into G1–G4. The keepsake scope risk is noted, not reopened: the owner's D6 outcome stands, and the category hint directs keepsakes to Non-perishable.

## G0 — Docker preflight before any gate claim

`make backend-test` runs the image proof, so prove the lane runtime first. The default `/var/run/docker.sock` is expected to be denied (SG-257 I1): set `DOCKER_CONFIG` to a writable temp directory and `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-258/docker.sock`; `docker version` must show a **Server** section, and `docker run --rm busybox true` must return **rc 0**. If either fails, **STOP as BLOCKED with the verbatim error** (`PB-2`, `PG-PR-03`); do not restart the daemon, use another socket or sudo. A different lane socket path is a finding. Use `PATH=$PWD/backend/venv/bin:$PATH` for every make invocation.

## G1 — Documents/other can hold a date, without a fabricated date

1. Set `documents_other.has_expiry=True` in `backend/app/plugins/expiry_tracker.py:160-167`. The tier map and the descriptor already ship; do not change them.
2. **Suppress the observed-date proposal for documents.** In `classify_asset`, do not call `_observed_date` for `documents_other` (`expiry_tracker.py:434`); a document's OCR date may be an issue date, not a validity date. The classify then writes the same `{"status": "unknown"}` / `needs_evidence` assertion and the same `_manual_task` as every other dateless category (`:436-440`). The user enters the date manually; nothing is fabricated.
3. `store_manual_expiry` now accepts documents because the flag is true (`:609-610`); do not special-case it. The SG-073 test that asserts `documents_entry` is `422 "non-perishable"` (`backend/tests/test_plugin_expiry.py:147-159`) must be updated to the new behaviour: the documents classify returns a `needs_evidence` assertion and a review task, and the manual entry returns 200.
4. Add a `VALID_UNTIL = "valid_until"` member to `DateType` (`expiry_tracker.py:39-45`) and a `valid-until` alias in `_DATE_ALIASES` (`:202-209`). `canonical_date_type` and `parse_manual_entry` already accept any member; the descriptor's `date_types` is built from the enum, so the served taxonomy gains it automatically. The documents form defaults to `valid_until`; the user can still choose another type. The engine ignores the type; no engine change.
5. **Category hint in the UI:** the classification control says "Documents/other: renewal or validity dates. Keepsakes, letters and photos belong under Non-perishable." The Non-perishable hint says "No date; no expiry reminder." The date form's copy for documents says "Date" and offers "Valid until", not "Expiry".

## G2 — A classification control on the asset page

1. Add `classifyAsset(assetId, householdId, category, versionToken?)` to `frontend/src/api/client.ts`: `POST /v1/plugins/expiry-tracker/assets/{assetId}/classification` with `{category}` and the household query; when `versionToken` is present send `If-Match: <token>`. The `apiPost` helper gains an optional headers argument if it lacks one (the `apiPatch` call at `AssetDetailPage.tsx:288` shows the shape); `enterManualExpiry` and `clearExpiryDate` take the optional token the same way.
2. Add an **optional** `If-Match` to the classify route (`backend/app/api/v1/plugins.py:125-153`). The token is the **active classification assertion's id** (`get_classification(db, asset.id)`), not `asset.version`: plugin writes do not bump the asset version. If the header is present and the active classification id differs, return **409** and change nothing. Existing callers without the header keep working. This is the stale-tab guard the second opinion asked for.
3. In `frontend/src/routes/AssetDetailPage.tsx`, add a classification section using the existing `useTaxonomy` hook (`frontend/src/hooks/useAssets.ts`; the Expiry page already uses it at `ExpiryPage.tsx:96`): a select of the served **active** categories, the current category shown from the classification assertion's `value.category`, a Save button that calls `classifyAsset` with the current classification assertion's id as the token, and a re-read of the asset on success. A 409 shows a clear "this item changed; reload" message and re-reads. An empty taxonomy shows a message, not an empty select (`PG-SC-07`).
4. Add a backend test that every served **active** category id round-trips through `canonical_category` (`expiry_tracker.py:216-229`); the descriptor hand-mirrors `CATEGORIES` (`descriptor.py:126-131`), so the test is the drift guard. The UI offers only the served active ids, so the alias map (`:171-187`) is not a UI path.
5. The control sends the category only; the category's default tier applies (`classify_asset` with `tier=None`). A tier override is not in this slice.

## G3 — Reclassification keeps an accepted date; a move to Non-perishable clears it

In `classify_asset` (`expiry_tracker.py:426-451`):

1. **Preserve only a valid accepted date.** Read the active expiry assertion (`_active_assertion`, `:322-332`). If the new category has expiry windows and the active assertion is `accepted` **and its value carries a valid `expiry_date` string**, keep it: return that assertion, write no placeholder and open no task. A null accepted assertion (from a clear) does **not** count; it gets the placeholder/task.
2. **A proposed or needs_evidence active assertion does not block the normal path.** For a non-document, the observed OCR date may be proposed; the form shows it with an Accept action (G4). If there is no observed date, write the placeholder and the manual task. For a document, the observed date is suppressed (G1), so the placeholder/task is the path.
3. **The reverse move to a dateless category clears the date.** If the new category has no expiry windows (`non_perishable`) and an active expiry assertion exists (accepted, proposed or needs_evidence), supersede it with a **null accepted** assertion through `_write_assertion(db, asset, EXPIRY_FIELD, None, "user", "accepted", None)`. The old row stays as `superseded`; the audit row records `value: null`; the engine's `compute_status` returns the asset as dateless; the form hides (G4); `store_manual_expiry` still refuses a non-perishable asset. The UI **confirms** the move when an active date exists: "This will clear the active date; the old value stays in the audit." The old date is not silently lost — it is superseded and auditable.
4. **The carried date is visible and correctable.** After a move between dated categories, the form pre-fills the kept date and its `date_type`; the UI hint says "the date is kept when the category changes; check it still applies." A `use_by` date moved to documents is visible and can be changed to `valid_until`; the backend preserves bytes, the user decides meaning.

## G4 — The date form: show it, pre-fill the active date, save, accept, clear

1. **Gate on the classification profile.** The classification assertion's `value.profile.tier_defaults` (`Category.profile`, `expiry_tracker.py:85-103`; written by `classify_asset` at `:430`) is the asset's own category profile. Show the form when it is non-empty; hide it for `non_perishable` (`tier_defaults: {}`). If the served asset payload does not carry the profile, fall back to the served taxonomy's `notification !== "none"` for the category. Do not hardcode a mode→windows map.
2. **Read the active expiry assertion deterministically.** In `AssetDetailPage.tsx:330`, filter `assertions` to `field_path === "plugin:expiry-tracker/expiry_date"` and `review_state !== "superseded"` and `!== "rejected"`, sort by `created_at` (the API returns it at `assets.py:142`; add it to the frontend `Assertion` type if missing), take the latest, and pass it to `ExpiryEntryForm`. Remove the form's own `find` (`ExpiryEntryForm.tsx:18`) and its asset query; the page is the one reader.
3. **The form** (`ExpiryEntryForm.tsx`) receives the active assertion, the category slug, the evidence ids and `hasWindows`. It shows for a classified category with windows in any state (accepted, proposed, needs_evidence). Pre-fill the date from the active value's `expiry_date` and the type from its `date_type` (documents default to `valid_until`). The page gives the form a `key` on the active assertion id, so the pre-fill follows a save, a clear or a category change. The button says **Accept date** for a proposed date and **Save date** otherwise; Save calls `enterManualExpiry` with the date, type and evidence ids. Disable Save when the date and type equal the active accepted values: a no-op Save must write nothing — no assertion and no audit row; prove both counts. A proposed date is accepted by the user's click, not by a silent write.
4. **Clear, with D4 parity.** Add `clear_expiry_date(db, asset)` beside `clear_opened_date` (`expiry_tracker.py:531-554`): the asset must be classified with a dated category; with no active expiry assertion it is a no-op (return `None`); otherwise write a null accepted assertion, keep the old row as `superseded`, and resolve any open `expiry.manual_entry` task (the user chose no date). Add `POST /v1/plugins/expiry-tracker/assets/{asset_id}/expiry/clear` with `_plugin`, `_asset`, the 422/404/403 mapping, and an **optional `If-Match`** carrying the active expiry assertion id (409 on mismatch; existing callers unchanged). Add `clearExpiryDate` to `client.ts` and the Clear button to the form; on success the form shows an empty date and the engine reports dateless.
5. **`If-Match` on the manual expiry route.** Add an optional `If-Match` to `POST /assets/{asset_id}/expiry` (`plugins.py:175-216`) carrying the active expiry assertion id; 409 on mismatch. The form sends the active id when it has one; the first date sends no header. The existing callers without the header keep working.
6. **The Expiry page's type label.** `ExpiryPage.tsx:257` renders `row.date_type` raw; use a shared date-type label map (the form's labels) so `valid_until` reads "Valid until" and the existing types keep their labels. Add a small test for the label.

## G5 — Tests and the gate

**Backend** (`backend/tests/test_plugin_expiry.py`, `backend/tests/test_sg233_reminders.py`):

- Documents: classify → `needs_evidence` + a `review_task`; manual entry 200 with `valid_until`; the 60-day and 30-day reminders fire for a date 45 and 20 days out; the OCR evidence carrying a date does **not** produce a proposed document date; the household 30-day reminder still fires. Update the SG-073 documents assertions (`:147-159`) and keep the non-perishable test (`:349-363`) unchanged.
- Reclassification: dated food → documents keeps the accepted assertion (same id/state); dated food → non_perishable clears it (the old row is `superseded`; the active is a null accepted; `compute_status` is dateless); a proposed/needs_evidence active gets the placeholder/task; a cleared (null) active in a dated category gets the placeholder/task.
- `valid_until`: accepted by the manual route and read back in the asset detail/form.
- `If-Match`: the classify route 409 on a stale classification id; the manual expiry route 409 on a stale expiry id; the clear route 409 on a stale expiry id; the category/date unchanged after each 409.
- The taxonomy drift test: every served active category id round-trips through `canonical_category`.
- The clear: the old row `superseded`, one active null assertion, the audit row, the task resolved, the engine dateless; the no-op writes nothing.
- The 422/404/403 cases: unknown asset, household mismatch, unclassified asset, non-perishable manual entry (still 422).

**Frontend** (`AssetDetailPage.test.tsx`, `ExpiryEntryForm.test.tsx`, `ExpiryPage.test.tsx`):

- The classification control lists the active categories, shows the current one, saves with the token, re-reads; a 409 shows the message; an empty taxonomy shows the message.
- An accepted + a superseded expiry row: the form pre-fills the active date, not the dead one; Save without a change writes no new assertion and no new audit row; Clear writes the null and the form empties; a proposed row shows Accept; a documents row shows the form with `valid_until`; a non-perishable row hides the form.
- The Expiry page shows "Valid until" for `valid_until`.

**The gate:**

- The new tests must be **seen to FAIL on the pre-change code** and pass on the candidate; commit both runs (`PG-EV-09`). The discriminating cases: documents manual entry 422 on base; the classify control absent; the clear route 404; the form gate absent; the exact-field active read absent.
- `make backend-test` once: the host suite green, the two marked tests still **deselected**, then the image proof. Quote the exact counts; do not force a fixed number (`PG-IC-08`).
- `make frontend-test` once: the full frontend suite green; quote its counts.
- Run the affected backend test modules **twice consecutively** and the affected frontend test files **twice**; both runs pass (`PG-DP-04`, the new routes are entry points).
- Targeted lint on **every changed or new file**: `ruff check` the backend files, `eslint` the frontend files; the repo-wide mypy reds (41 in nine untouched files) and the one pre-existing eslint error are out of scope and must not be "fixed". The report reconciles the changed paths against the gate's paths (`PG-EV-15`).
- `curl -s http://127.0.0.1:8003/v1/health` at start and end: both 200, unchanged.

## Acceptance criteria

- **A1** — Documents/other is `has_expiry=True`; classify writes the placeholder/task; manual entry accepts a date; the 60/30 reminders fire; a document's OCR date is never proposed; the SG-073 422 test is updated.
- **A2** — the asset page has a classification control over the served active categories; a stale classification token returns 409 and changes nothing; the taxonomy drift test passes; an empty taxonomy shows a message.
- **A3** — a dated item moved to another dated category keeps a valid accepted date; a proposed/needs_evidence active gets the form or the placeholder/task; a move to Non-perishable clears the active date (null accepted, old row superseded, engine dateless) behind a confirmation.
- **A4** — the form shows for a classified category with windows, reads the exact active plugin assertion and pre-fills it, accepts a proposed date, saves an accepted date, and clears to a null active; a no-op Save writes no new assertion and no new audit row; documents show `valid_until`; the Expiry page labels it.
- **A5** — the new tests are FAIL-then-PASS with both logs committed; the host suite, the image proof and the frontend suite are green; the new routes are run twice; counts quoted.
- **A6** — scope is only the named product files plus `docs/worklogs/SG-258*`; zero schema, migration, Dockerfile, compose, lockfile, dependency, model, database, host, provider, running-container or deploy bytes.
- **A7** — the Docker preflight is proven before the gate; health 200 at start and end.
- **A8** — `PB-3` vacuity: what each check would look like if it failed — the documents entry still 422; the classify control still absent; the date still lost on reclassification; the form still pre-filling a dead row; the clear still 404; a suite red. None of these may be the observed result.
- **A9** — the report ends with `Verification: PASS` or the honest failure reason.

## Scope ceiling

- **Changed product files:** `backend/app/plugins/expiry_tracker.py`, `backend/app/api/v1/plugins.py`, `backend/tests/test_plugin_expiry.py`, `backend/tests/test_sg233_reminders.py`, `frontend/src/api/client.ts`, `frontend/src/api/types.ts`, `frontend/src/routes/AssetDetailPage.tsx`, `frontend/src/components/ExpiryEntryForm.tsx`, `frontend/src/routes/ExpiryPage.tsx`, `frontend/src/routes/AssetDetailPage.test.tsx`, `frontend/src/components/ExpiryEntryForm.test.tsx`, `frontend/src/routes/ExpiryPage.test.tsx`.
- **Reads of any file are allowed; only the files listed here may be changed.** The only runtimes this packet authorises are the G0 Docker preflight, the `make` gate and the tests; no other container, image or runtime.
- **Allowed if extracted:** `frontend/src/components/ClassificationSection.tsx` and `ClassificationSection.test.tsx`. If you keep the control inline in `AssetDetailPage.tsx`, those files stay untouched. Either way, every changed or new file appears in the report and in the lint/test gate (`PG-EV-15`).
- Evidence: `docs/worklogs/SG-258*` only.
- **No changes** to schema, migration, `backend/app/models/**`, `backend/Dockerfile`, `docker-compose.yml`, `backend/requirements.lock`, dependency, `.env`, the **live** running container, its image tag, the host's packages, the database, or any provider. **No deploy.** The G0 and `make backend-test` build/run the existing test image and a throwaway proof container only; the live container and its image tag are untouched.
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`): never route around the socket, sudo or a missing package.
- No browser, no frontend production build beyond what the suite needs, no network in the tests.

## Hang bounds

Docker preflight **120 s**; host suite **600 s**; frontend suite **600 s**; image proof **300 s**; one test file **300 s**; ordinary commands **120 s**. Nothing may reach the lane's idle kill; longer work runs in the background and is checked with short calls. No interactive command.

## Budget

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. **Publish before the bound at 1500 s.** Expected ≈1500 s, bracketed from this lane's recent actuals (SG-240 1504 s for a comparable backend+frontend slice; SG-256 540 s for a smaller one; SG-257 451 s for a rider). If new work passes 1500 s, stop starting, commit, write the report, publish the receipt. A partial slice with a receipt is a success.

## Report

Destination: `docs/worklogs/SG-258_report.md`, evidence logs beside it (`docs/worklogs/SG-258_*.log`). The first line states the slice ID, model and effort read from the process arguments (never a system-prompt label), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. The report compares the engine elapsed time against the ≈1500 s expectation and names every phase over 60 s (`PG-PR-06`). It lists the changed files, the test counts, the FAIL-then-PASS logs, the contract echo, and every `UNCLEAR` / `REMAINING` line.

The receipt goes to the notes ref `refs/notes/storagegenie-coder-reports`, first line:

```
Dispatch-ID: SG-258 | Report: docs/worklogs/SG-258_report.md | Work-HEAD: <work commit>
```

Fetch the ref explicitly (`git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports`), add the note with `git notes --ref=refs/notes/storagegenie-coder-reports add -m "<that first line>" HEAD`, and push it (`git push origin refs/notes/storagegenie-coder-reports`). A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

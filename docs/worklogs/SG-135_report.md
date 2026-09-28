SG-135 report — land the 11 audited winners: ordered merges, journal union, tests, no serve

Dispatch-ID: SG-135
Work dir:   /home/andrei/StorageGenie
origin:     git@github.com:Andovol/StorageGenie.git
BASE ref:   origin/automation
BASE commit: fc7bf02a3af54300c703a15a724f10f344387835  (start HEAD; tree clean at start)
WORK_HEAD:  973009cc6560ff4da0d908ae623591eb04e9c61f  (work commit; receipt note target)
Model:      opencode-go/deepseek-v4.1-flash   (per process arguments /proc/self/cmdline `--model`)
Effort:     high                              (per process arguments /proc/self/cmdline `--variant high`)
Coder:      opencode  (env CODER=opencode; OPENCODE_PID=38785)
Contract:   echo 0.40.0 — source `/home/andrei/storagegenie-contract/VERSION` (published tip `f26dbd3`);
            `RULES.md` sha256 `5b65629377bbac9e40bfa7e2f4d4e42a5667b3a08ec786beb47c6a677d9ac33c`
            equals payload `RULES.sha256`. Recorded 0.40.0 == published. (`.rules-cache/` absent on host.)
Spend:      real $0.000000 USD · zero metered calls · no serving · no rebuild/recreate · no migration.
Gates:      DATABASE none · Restart none · Deploy none. Role guard held (Coder only; no dispatch verb).
Guards:     PG-EV-01 · PG-EV-02 · PG-EV-05 · PG-EV-07 · PG-SC-09 · PG-SC-12 · PG-IC-01 · PG-IC-07
            · PG-IC-08 · PG-IC-09 · PG-PR-03 · PG-PR-04 · PG-PR-06.

## 0. Method and evidence

- All 11 audited heads were re-verified against `refs/pull/N/head` on the target (`PG-IC-09`): every
  head SHA matched the packet exactly — none moved, so no PR was dropped. Fetched to `refs/audit/pr/N`.
- Each head landed as `git merge --no-ff` in the packet's order (bot authorship preserved in history;
  GitHub marks each PR merged on landing; `gh` never touched, no close by hand, no rebase).
- Conflicts: exactly **two** regions, both `.jules/bolt.md`, resolved by **UNION** of lines (every line
  kept, duplicates dropped once). **No third conflict region anywhere** (`PG-IC-08` holds).
- Landed-content proof per PR (`PG-SC-12`): post-merge signature grep derived from each head diff.
- Suites actually run (not skipped); the one red that is not base-provable is reported as a red, not a
  pass — no vacuous pass.

## 1. Merge table (11 rows, quoted from the commit)

| PR | audited head | merge commit | signature grep (post-merge, file:line) | targeted result |
|----|--------------|--------------|----------------------------------------|-----------------|
| #15 | `84dc691` | `0e2dee1` | `backend/app/api/v1/assets.py:515: ev = ev_map.get(eid)` | assets/evidence tests ✓ |
| #17 | `3269107` | `02e661e` | `backend/app/api/v1/assets.py:221,364: evidence_subquery = select(asset_evidence.c.asset_id)` | assets/facets/search tests ✓ |
| #20 | `aea591d` | `a334a0b` | `backend/app/services/dedup.py:43: def _similar_matches(` | `test_dedup.py` ✓ |
| #26 | `3dc8349` | `750cd0b` | `frontend/src/components/catalog/ProductCard.tsx:73: export const ProductCard = memo(function ProductCard({` | `catalog.test.tsx` ✓ (33) |
| #2 | `217ee06` | `6064822` | `backend/app/services/chat/__init__.py:11: SUPPORTED_CATEGORIES as SUPPORTED_CATEGORIES,` | `python -c` import ✓ |
| #28 | `0cd1c35` | `23d9456` | `frontend/src/components/WebAlternates.test.tsx:6: describe("WebAlternates", () => {` | vitest ✓ (4) |
| #29 | `431d323` | `e1d034b` | `frontend/src/components/shell/PageContainer.test.tsx:11: describe("pageContainerStyle", () => {` | vitest ✓ (6) |
| #31 | `3872595` | `84ef9ce` | `backend/app/api/v1/health.py:24: logger.warning("Database health check probe failed: %s", exc, exc_info=True)` | `test_health.py` ✓ isolated / red full-suite (F1) |
| #27 | `9b86ce3` | `5dfab2b` | `backend/app/services/google_taxonomy.py:121 def _token_index()`, `:145 def _score_candidates(` | taxonomy tests ✓ |
| #24 | `0211c8a` | `d1ae3b7` | `backend/app/services/analytics/service.py:160: def _parse_category_slug(value_json: str)` | `test_analytics.py` ✓ |
| #18 | `6e624c2` | `973009c` | `backend/app/services/chat/service.py:144: def build_catalog(db, household_id, category)` | chat/planning tests ✓ |

Every merge's **second parent equals the audited head** (checked for all 11). Merge order was the
packet's: #15 → #17 → #20 → #26 → #2 → #28 → #29 → #31 → #27 → #24 → #18. The 8 non-journal PRs
landed clean; #27 landed clean; **#24 and #18 each conflicted only in `.jules/bolt.md`** and were
union-resolved. Final journal carries all 5 entries (2026-09-28, 2026-09-24, 2026-09-14, two 2026-09-17).

### 1a. Union resolutions (verbatim)

```
# #24: ours = "## 2026-09-28 - Inverted Token Index ..." ; theirs = "## 2026-09-24 - Batch Fetching ..."
# resolution -> both entries kept, 2026-09-28 then 2026-09-24, then the pre-existing entries.
# #18: ours = "## 2026-09-17 - Pre-fetch Household Observations/Assertions ..."
#       theirs = "## 2026-09-17 - Batch Assertion and Attribution Queries ..."
# resolution -> both entries kept (same date, distinct titles), then #20's entry.
```

## 2. G1 — proof

**Targeted (`CO-101`), backend 10 files** (`test_assets_crud`, `test_evidence_upload`, `test_asset_facets`,
`test_search`, `test_dedup`, `test_google_taxonomy`, `test_plugin_taxonomy`, `test_analytics`, `test_chat`,
`test_planning`):
```
133 passed, 5 warnings in 7.22s
```
`test_health.py` in isolation: `3 passed`. #2 import: `import-ok`. Frontend (vitest, invoked via
`node_modules/.bin/vitest` because `npx` is absent on the host):
```
 ✓ PageContainer.test.tsx (6)   ✓ WebAlternates.test.tsx (4)   ✓ catalog.test.tsx (33)
 Test Files  3 passed (3)      Tests  43 passed (43)
```

**Full backend suite (600s bound):**
```
WORK_HEAD:  3 failed, 623 passed, 32 warnings in 30.61s
BASE:       2 failed, 624 passed, 32 warnings in 33.59s
```
- **Base-proved reds (2):** `test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier`
  and `test_signals.py::test_ocr_has_text_boxes_and_mean_confidence` — environment reds on bare BASE
  (`pyzbar/libzbar is not installed`; `tesseract is not installed`).
- **Not base-proved (1):** `test_health.py::test_health_reports_database_failure` — the test is new
  (#31) so it cannot exist on BASE; it passes in isolation and fails under full-suite ordering with
  `caplog.text == ''`. Root cause is **pre-existing base code**: `alembic/env.py:20 fileConfig(...)`
  (default `disable_existing_loggers=True`) sets `app.api.v1.health.disabled = True` process-wide when
  migration tests run earlier. See Finding F1. This red is reported, never read as green.

**ruff:** `All checks passed!` on WORK_HEAD and on BASE.
**mypy (strict):** BASE `41 errors in 9 files`; WORK_HEAD `44 errors in 10 files` → **delta +3**, all in
`app/services/dedup.py` (`arg-type` + `assignment` + `union-attr` from #20). Stated, never assumed zero.
**Migration surface:** `git diff --stat fc7bf02 HEAD -- backend/app/models backend/alembic` → empty.
**Changed files vs BASE:** exactly the 11 PRs' surfaces (9 modified backend/frontend + `.jules/bolt.md`
+ 2 new vitest files) — no out-of-scope write.

## 3. Findings (correcting the packet counts as a result)

- **F1 — #31's new test is red in full-suite ordering (not base-proved).** The packet expected
  `#31 → test_health.py` green. Measured: `test_health_reports_database_failure` passes alone, fails in
  the full suite (`caplog.text == ''`; response assertions still pass, so `logger.warning` did execute).
  Cause: `alembic/env.py:20` `fileConfig` disables the `app.api.v1.health` logger globally. Pre-existing
  base defect, activated by the new caplog assertion. I could not fix it — the scope ceiling forbids
  writing tests/app code — so it is reported loudly, not hidden.
- **F2 — the packet's "8 appenders" premise is off for this set.** Measured: **4** of the 11 heads
  touch `.jules/bolt.md` (#20, #27, #24, #18). Only 2 of those produced a conflict (#24, #18); #20 and
  #27 merged cleanly. Net effect matches the packet (journal-only conflicts), but the appender count is 4.
- **F3 — mypy delta is +3, not zero**, all introduced by #20 (`dedup.py`), pre-existing reds otherwise
  identical. ruff stays clean.
- **F4 — `npx` is absent on the host** (`node` 24.14.1, `npm` present, no `npx`); frontend tests ran via
  `node_modules/.bin/vitest`, so the vitest results are real, not UNANSWERED.
- **F5 — contract echo clean and equals published** (0.40.0, `RULES.md` sha256 `5b656293…`, tip `f26dbd3`);
  not an echo-diff finding.
- **F6 — the rewrites did not ride in** (#16, #11–#14 fold, #4-minus-artifact are SG-136/137/138): the
  changed-file set contains none of their surfaces. Scope ceiling held.

## 4. Actual vs budget

| goal | budget | actual | unit |
|---|---|---|---|
| G0 head re-verify + ordered merges + union | ~900s | ~43s | elapsed |
| G1 targeted + full suite + ruff/mypy/migration | ~700s | ~500s | elapsed |
| G2 worklog + report + receipt | ~200s | (this step) | elapsed |
| overall | 2400s cap / ~1800s expected | ~560s at report write | elapsed |

The 1500s stop point was never approached; no command was killed; every command ran under its class
bound (120s ordinary / 600s suite). Real metered spend **$0.000000 USD**, zero metered calls.

## 5. Receipt

- Work commit `WORK_HEAD = 973009cc6560ff4da0d908ae623591eb04e9c61f`, pushed to `origin/automation`
  (`fc7bf02..973009c`), worktree clean.
- No push to `storagegenie-evidence`; `{{RECEIPT_CMD}}` not run.
- Note added on WORK_HEAD on `refs/notes/storagegenie-coder-reports`, pushed, then re-fetched into the
  **mapped** local ref `refs/notes/sg135-verify` (a default fetch carries no notes; a bare refspec
  rewrites only FETCH_HEAD — mapped per `M20`). `show` output pasted verbatim below.
- Final tip dual-annotated with the same note (note-anchor inoculation, SG-092 precedent).
- `note=yes`

Executed output, pasted verbatim:
```
(pasted in the receipt-paste commit)
```

## UNCLEAR

- **FIRST READ:** the packet's "8 appenders" read as a property of these 11 heads; measured it is 4
  (#20, #27, #24, #18), and only 2 of those conflicted. Also the packet expected #31's `test_health.py`
  green; it is red under full-suite ordering.
- **DURING EXECUTION:** all 11 merges landed with journal-only conflicts exactly as intended, but the
  one red the slice did not anticipate comes from #31's own test colliding with a pre-existing alembic
  logging side effect — fixable only by writing test/app code, which the scope ceiling forbids.
- **REMAINING:** owner/Architect decision on (a) how to treat the #31 caplog red (reopen #31's test,
  or a follow-up slice that makes `fileConfig` non-disabling / scopes caplog), and (b) the +3 mypy errors
  in `dedup.py` from #20. The rewrites (#16, #11–#14, #4-minus-artifact) remain for SG-136/137/138.

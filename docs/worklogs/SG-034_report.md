# SG-034 report — manual entry on asset detail + on-screen corrections

**Dispatch-ID:** SG-034 · **Coder:** opencode · **Effort:** medium
**BASE REF:** `automation` → resolved commit `7987b8ec52dc35eb0de280c92377f5eaf1615bfb` (two fields, as required).
**WORK_HEAD:** the commit carrying this file; its hash is recorded by the G5 receipt note on
`refs/notes/storagegenie-coder-reports` (a committed file cannot contain its own commit hash).
**Work dir** `/home/andrei/StorageGenie` · **origin** `git@github.com:Andovol/StorageGenie.git`.
**DATABASE:** none — temp SQLite only, zero live rows. **Restart:** none — no service touched, nothing
deployed. **NETWORK:** none; **spend $0**.

**Model/effort per `CO-78`** — read from process arguments, never an identity line. Parent argv
(`/proc/$PPID/cmdline`), quoted verbatim (leading tokens):

```
opencode run --auto --dir /home/andrei/StorageGenie --variant medium # SG-034 — Manual entry on asset detail + on-screen corrections (opencode, medium)
```

Coder `opencode`, effort `medium` (`--variant medium`), **model `unknown`** — the CLI default IS the
model and is omitted per policy; no model id appears in argv or packet, so I write `unknown` rather
than a guess. Grandparent: `bash /usr/local/lib/dispatch/run-coder SG-034`.

## Verdict

GREEN. AssetDetail now corrects `quantity` / `unit` / `condition` through the existing
`PATCH /v1/assets/{id}` (same If-Match path, no backend write added): the new accepted assertion
supersedes the prior one and both the superseded row and the `asset.update` audit entry are visible on
the page. A `needs_evidence` asset now offers `ExpiryEntryForm` hand entry on its own detail page, and
entering a real date resolves not only the asset's own open `expiry.manual_entry` task(s) but also the
SG-033 F-SG033-2 orphans — open manual-entry tasks on split origins that share the asset's evidence —
audited and never deleted. A task whose origin did not share the evidence stays open. Pre-change, the
orphan stayed `open` (`assert 'open' == 'resolved'`, raw); post-change the full plugin file is 8 passed.
Full backend suite is green modulo the 2 known decoder env reds, re-verified at BASE in a detached
worktree (not inherited); `ruff` clean; mypy baseline 40-in-9 unchanged with zero hits in the edited
file; `npm run build` green; vitest 27 passed; secret scan 0; zero network, `$0` spend.

## Findings (packet premises verified; differences stated, not bent)

- **G1 premise verified.** `update_asset` loops `quantity/unit/condition` into `upsert_assertion`
  (`asset_service.py:77-82`), which supersedes the prior accepted row and writes `assertion.upsert`
  (`assertion_service.py:24-47`). Base AssetDetail edited `display_name` only
  (`AssetDetailPage.tsx:77-92`). No bypass found — every field goes through the same chain; **no STOP
  warranted**.
- **G1 backend test is already covered** — `test_assertions.py:48-101`
  (`test_patch_supersedes_assertion_stale_match_and_attaches_evidence`) asserts the
  `{superseded, accepted}` pair plus the `assertion.upsert` audit row. Per the packet ("ONLY if
  uncovered") no new backend test was added; the covered premise is cited with a WORK/base run
  (verify log §5c).
- **F-SG033-2 root cause confirmed at BASE.** `split_candidate` resolves only
  `candidate.multi_item` on the origin (`candidates.py:610-636`); children copy
  `evidence_ids_json` (`:601`) and set `split_from` (`:596`). An origin's `expiry.manual_entry` task
  therefore stays open while the child's asset carries the shared evidence.
- **Premise correction worth naming (link key).** The packet says orphans are found as "split origins
  sharing the evidence". I anchored on the **asset's linked evidence** (`asset_evidence`), not the
  request's `source_evidence_ids`, because the child's asset is the real anchor and `classify_asset`
  (which opens the asset's own manual task) supplies no evidence ids. Both coincide in the normal
  flow; the asset-link reading is the correct one. `source_evidence_ids` is still written onto the
  assertion as before.

## G1 — on-screen corrections for accepted fields

`frontend/src/routes/AssetDetailPage.tsx` only. The edit panel initializes
`display_name/quantity/unit/condition` from the asset on Edit; Save builds a payload of the non-empty
fields and calls the EXISTING `apiPatch('/v1/assets/{id}', payload, {household_id}, {'If-Match':
version})`. No backend change, no client change. New test `frontend/src/routes/AssetDetailPage.test.tsx`
edits quantity `2 → 3`, asserts the PATCH payload + If-Match, then asserts the re-read page shows the
`superseded` prior row and the `asset.update` history entry. Because `_asset_to_dict` returns all
assertions (including superseded) and the asset audit list, the history is genuinely visible.

## G2 — manual entry on asset detail + orphan pickup (F-SG033-2)

- **Detail page:** renders `ExpiryEntryForm` iff the asset's expiry assertion
  `review_state === "needs_evidence"` (`AssetDetailPage.tsx`), passing evidence ids. The component and
  its route (`POST /v1/plugins/expiry-tracker/assets/{id}/expiry`) are reused unchanged; client.ts and
  types.ts were not touched. Empty submit stays refused (Save disabled; `parse_manual_entry` also
  rejects a missing `expiry_date` with 422 — never a guessed date).
- **Service pickup:** `backend/app/plugins/expiry_tracker.py` gains `_orphan_manual_tasks` and extends
  `store_manual_expiry`. After the existing own-task resolution (`subject_ref=asset.id`), it finds
  `Candidate` rows with `state == "split"` in the household whose `evidence_ids_json` intersects the
  asset's linked evidence, and resolves their open `expiry.manual_entry` tasks. Each resolution sets
  `status="resolved"` (never deletes), writes a `review_task.resolve` audit row with
  `resolution.manual_entry_orphan == True`, and appends the task to the returned list so the existing
  route's `resolved_review_task_ids` reports own + orphan with **no `api/v1/plugins.py` change**.
- **`PG-SC-02` trace, one test:** `test_manual_entry_resolves_own_and_split_origin_orphan_tasks` seeds
  the asset + shared evidence, a split origin with an orphan task, and a second split origin on
  *different* evidence with its own open task; classifies the asset; POSTs `2030-05-06`; then asserts
  the accepted assertion value, own tasks resolved, orphan resolved and still present, the unrelated
  task still `open`, and exactly one orphan audit row. `PG-SC-07` negative is the unrelated-evidence
  task, which stays open.
- `plugins.py` route is read-only here and required **no** touch, so no M6 STOP.

## G3 — proof (raw runs in `docs/worklogs/SG-034_verify.log`)

| Gate | Result |
|---|---|
| PRE backend new test | **1 failed** in 0.85s — `assert 'open' == 'resolved'` (orphan stays open) |
| POST backend `pytest tests/test_plugin_expiry.py` | **8 passed** in 1.01s |
| PRE frontend new file | **2 failed** — "Unable to find a label … Quantity" / "… Manual expiry entry" |
| POST frontend new file | **2 passed** in 155ms |
| Full backend suite (WORK, 600s) | **2 failed, 127 passed** in 7.94s |
| Full backend suite (BASE `7987b8e`, detached worktree) | **2 failed, 126 passed** in 8.33s — same 2 decoder reds (base-proved, re-verified) |
| G1 chain coverage cited `pytest tests/test_assertions.py` | **1 passed** in 0.69s |
| `ruff check app tests` | `All checks passed!` |
| `mypy app` | 40 errors in 9 files (baseline 40-in-9 unchanged; **0** in `expiry_tracker.py`) |
| `npm run build` | green, 93 modules, built in 885ms |
| `vitest run` | 10 files, **27 passed** |
| Secret scan | **0** real-key matches (only the SG-031 sentinel, quoted twice incl. SG-033's log); 0 tracked `.env` |
| Health probe `CO-92` | unanswered — compose 0 services; `/v1/health` → 404; :8000 listener unrelated; delta 0 |

No migration; no prompt diff; no ignored file staged; no network (in-process `TestClient` only;
changed/new test files contain no network symbols).

## Budget (actual versus budget, per leg)

| Leg | Budget | Actual |
|---|---|---|
| Ordinary probes / single test runs (120s) | 120s | ≤ 1.1s each |
| Backend suite (600s) | 600s ×2 | 7.94s (WORK) / 8.33s (BASE) |
| `npm run build` (600s) | 600s | 885ms (plus `tsc` ~2s) |
| `vitest run` (600s) | 600s | 1.54s |
| Early-close (1800s) | 1800s | not needed |
| Overall (2400s) | 2400s | minute scale, well under |

## Live-state ledger

- Provider spend: **$0** (no live call; no provider seam touched).
- Network attempts: **0** external. The only socket is the localhost health probe (refused/404).
- Key reads: **0**.
- Deployments / migrations / restarts: **0**.
- Secrets: scanned by shape, **0** real matches; only the SG-031 test sentinel
  (`backend/tests/test_settings.py:47`).
- Ignored/staged files: **0** staged.

## Guards

`PG-EV-01` FAIL-then-PASS raw for both new tests (verify log §3–4) · `PG-EV-02` new test file exists and
is committed · `PG-EV-05` the properties asserted are supersede-history visibility and own+orphan
resolution, not command echoes · `PG-EV-09` both runs committed raw · `PG-SC-02` entry → assertion →
resolved task list traced in one test · `PG-SC-07` the unrelated-evidence task is the named smallest
case proved to stay open · `PG-SC-10` nothing staged as ignored · `PG-IC-01` cross-product (page +
existing PATCH / detail page + entry component + service) · `PG-IC-03` no remediation shares a condition
with a stop-gate; the 422 empty-entry refusal is the stop and stops win by default · `PG-IC-07` no fixed
dates in code (the test date `2030-05-06` is a fixture, not a derivation) · `PG-IC-09` premises
re-verified with quoted reads · `PG-PR-03/04/06/10` scope ceiling, zero live calls, per-leg bounds,
disposition.

## Role guard

Coder role only. I did not run any dispatch verb, did not start or poll any unit. No SSH performed.

## UNCLEAR

- **FIRST READ:** the orphan link key. The packet says orphans are "split origins sharing the evidence"
  without saying *which* evidence — the asset's linked evidence or the request's `source_evidence_ids`.
  I chose the asset's linked evidence (the child's asset is the real anchor; classification supplies no
  evidence ids). Flagged for the Architect to confirm or redirect.
- **DURING EXECUTION:** a split origin sharing the evidence is resolved even if this particular asset
  cannot be proven to descend from that origin (only co-evidence is known). This matches the packet's
  stated property, but if a future flow reuses one photo for independent assets, the co-evidence rule
  could over-resolve. No such flow exists today; named rather than silently assumed safe.
- **REMAINING:** `mypy` remains 40 errors in 9 files, unchanged from BASE and none in the edited file;
  reducing the pre-existing set is outside this ceiling. Also outside scope: split children get no
  per-child `expiry.manual_entry` task (SG-033 behavior, untouched here).

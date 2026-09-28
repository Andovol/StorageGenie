SG-136 report — batch-load asset assertions, prove the N+1 gone

Dispatch-ID: SG-136
Work dir:    /home/andrei/StorageGenie
origin:      git@github.com:Andovol/StorageGenie.git
BASE ref:    origin/automation
BASE commit: b828b4009643ab9e054c2ff146b2ca2d30b54745  (start HEAD; tree clean at start)
WORK_HEAD:   8166e79994a732a6a7fa176eb4b305f56fb0512d  (worklog commit; receipt note target)
Model:       opencode-go/deepseek-v4.1-flash   (per process args /proc/90023/cmdline `--model`)
Effort:      high                              (per process args /proc/90023/cmdline `--variant high`)
Coder:       opencode  (env CODER=opencode; OPENCODE_PID=90023; RUN_BUDGET_S=2100)
Contract:    echo 0.40.0 — source `/home/andrei/storagegenie-contract/VERSION` (published tip `f26dbd3`).
             Recorded 0.40.0 == published. (`.rules-cache/` absent on host, standing.)
Spend:       real $0.000000 USD · zero metered calls · no serving · no rebuild/recreate · no migration.
Gates:       DATABASE none (read-only on the app DB; temp DBs only) · Restart none · Deploy none.
             Role guard held (Coder only; no dispatch verb run, own unit never started/polled).
Guards:      PG-EV-01 · PG-EV-02 · PG-EV-05 · PG-EV-07 · PG-EV-09 · PG-SC-02 · PG-SC-09 · PG-SC-12
             · PG-IC-01 · PG-IC-07 · PG-IC-08 · PG-IC-09 · PG-PR-03 · PG-PR-04 · PG-PR-06.

## 0. Method and evidence

- Every packet premise was verified against the tree before building on it; two differed and are
  reported as findings, not bent to match (F1, F3).
- Fail-pre was committed **before any edit** (`ff9f5d3`) per `PG-EV-09`: the red test, the
  deterministic per-asset baseline fixture, and the G0 log. Fail-post is the WORK_HEAD commit.
- Query counts come from a **real seam**: a `before_cursor_execute` listener on the live
  `app.db.engine` (and `TestClient` for served routes), filtering on `FROM assertion`
  (`PG-SC-12`). No mock, no cached-session tautology.
- No vacuous pass: every count is at K≥3 (3 and 6), the equality rail is the pre-edit fixture, and
  the suite was run on both trees. Units are wall-clock seconds on the live clock (`PG-IC-07`).

## 1. G0 — enumerate + fail-pre (commit `ff9f5d3`)

**Callers of `_asset_to_dict` (assets.py):** `:88` (post_asset idempotent replay), `:99`
(post_asset), `:389` (get_asset detail), `:423` (patch_asset), `:493` (merge_asset), `:521`
(post_asset_evidence). **The committed `list_assets` route (`:264-334`) is NOT a caller** — it
builds a minimal inline row and never serializes assertions. So the packet's "asset list + asset
detail" expectation holds only for the detail half (F1).

**Fail-pre N+1 (temp DB, K assets × 4 assertions across 3 field paths incl. a `condition` tie):**
```
K=3  naive per-asset serialization: 3 assertion SELECTs
K=6  naive per-asset serialization: 6 assertion SELECTs
batched attempt (pre-slice): AttributeError: type object 'Asset' has no attribute 'assertions'
```
Baseline `_asset_to_dict` output per asset was written to
`backend/tests/fixtures/sg136_asset_dict_baseline.json` (deterministic ids/timestamps) and
committed first. Fail-pre test (`backend/tests/test_sg136_assertion_batch.py`):
```
3 failed, 1 passed, 2 warnings in 0.77s
  FAILED test_assertion_select_count_constant_in_k
  FAILED test_output_is_byte_identical_to_prechange_baseline
  FAILED test_empty_asset_world_issues_no_assertion_select
  PASSED test_lazy_per_asset_access_is_the_n_plus_one     (6 assets -> 6 assertion SELECTs)
```

## 2. G1 — decided shape + fail-post

**Decided shape.** Keep the relationship (it models the data and pins `field_path` ordering) and
**eager-load it with `selectinload(Asset.assertions)` where the loaded collection survives to
serialization**; `_asset_to_dict` iterates `asset.assertions`. A K-asset serialization is one
assertion SELECT, constant in K.

Three hunks (no secret within ten lines — `CO-100` asserted, diff scanned):
- `models/asset.py`: `assertions` relationship, `order_by="Assertion.field_path"`,
  `cascade="all, delete-orphan"` (the cascade was required — F4).
- `models/assertion.py`: back-populating `asset` relationship.
- `api/v1/assets.py`: `selectinload` import; the option at the **replay / get_asset /
  post_asset_evidence** query sites; `_asset_to_dict` reads `asset.assertions`; the now-unused
  `Assertion` import removed. PATCH/MERGE deliberately left lazy (F3).

**Fail-post (same seam):**
```
naive  K=3 -> 3   K=6 -> 6      (lazy relationship is still the N+1)
batched K=3 -> 1   K=6 -> 1      (CONSTANT in K);  output EQUAL True both K
```
**Byte-equality:** the committed test compares, per asset, both the direct `_asset_to_dict`
output and the served `GET /v1/assets/{id}` body to the pre-edit fixture — `4 passed`. The
`condition` tie (superseded + accepted at the same `field_path`) proves ordering is preserved, not
just set membership. Empty world: zero assets -> zero assertion SELECTs (`PG-SC-07`).

**`PG-IC-08` blast radius (expected counts written before measuring: `1 + K` pre, constant post —
met).** Served-route assertion-SELECT counts, BASE vs WORK, identical:
```
POST /v1/assets 1/1 · GET detail 1/1 · PATCH 2/2 · GET list 0/0 · MERGE 3/3
```

**Suite / lint / migration surface:**
```
WORK_HEAD suite (600s bound): 2 failed, 628 passed, 32 warnings in 30.20s
  reds = test_signals::{generated_codes..., ocr_has_text...} (base-proved env reds)
bare BASE (stash): 2 env reds + the 3 committed fail-pre SG-136 reds (5 failed, 625 passed)
mypy: BASE 41 errors / 9 files  ==  WORK 41 errors / 9 files   (delta 0, same file list)
ruff: All checks passed!
git diff --stat origin/automation -- backend/alembic/versions/  -> (empty)
```

## 3. Findings

- **F1 — packet premise differs: there is no served "asset list" caller.** `list_assets` builds its
  own inline rows and never calls `_asset_to_dict`; it issues **0** assertion SELECTs before and
  after. The N+1 is a property of serializing a **collection** of assets through the serializer; no
  such loop exists on a served route in this tree. I shipped the batching (constant-in-K) and proved
  it at the real seam, and here say plainly that "the list path N+1" never existed in production.
  This does **not** make the slice vacuous: the fix removes the per-asset SELECT from any K-asset
  serialization and the equality/count rails both execute.
- **F2 — baseline fixture household label.** The first post-change equality run differed from the
  fixture only in `household_id` (`sg136-hh` vs the captured `hh-1`); ordering and every other field
  matched. I aligned the **test** id to the fixture rather than regenerate/bend the fail-pre capture.
- **F3 — `selectinload` at PATCH/MERGE would regress the count.** `update_asset`/`merge_asset_redirect`
  commit and `db.refresh(asset)`, discarding a preloaded collection. Measured PATCH assertion
  SELECTs: 2 without the option (== pre-slice) vs 3 with it. I therefore did **not** add the option
  at those two sites, contrary to the packet's flat hint; the lazy load costs exactly the single
  SELECT the pre-slice explicit query did. All served counts are identical BASE vs WORK.
- **F4 — the relationship needed `cascade="all, delete-orphan"`.** First cut broke
  `test_search.py::test_fts_triggers_follow_asset_insert_update_delete` (FAILED on WORK, PASSED on
  bare BASE, stash-proved): on `session.delete(asset)` the ORM tried `UPDATE assertion SET
  asset_id=NULL` and hit NOT NULL. The schema FK is `ondelete="CASCADE"`; the matching ORM cascade
  restores correct delete semantics. Fixed in-slice; the FTS test is green.
- **F5 — #16's stale import is confirmed.** Its diff removes `app.models.assertion.Assertion` from a
  base that predates the SG-113/SG-114 imports; on this tree the import is genuinely unused only
  after `_asset_to_dict` uses the relationship, and I remove it on that basis, not by copying #16.
- **F6 — "N+1 measurably gone" is scoped honestly.** It is proven for a K-asset batch serialization
  (K=3 and K=6 -> 1), not claimed as a served-list speedup, because the list route serializes no
  assertions (F1). Stated so the acceptance reading is not stronger than the evidence.

## 4. Actual vs budget (units = wall-clock seconds, live clock `PG-IC-07`)

| goal | budget | actual | unit |
|---|---|---|---|
| G0 recon + fail-pre + committed capture (`ff9f5d3`) | ~600s class | ~300s | elapsed |
| G1 hunks + fail-post + seam/route counts + suite/mypy/ruff | ~600s class | ~360s | elapsed |
| G2 worklog + report + receipt | ~200s | ~45s + receipt | elapsed |
| overall | packet 2400s / env `RUN_BUDGET_S=2100` | 704s at report write | elapsed |

Real metered spend **$0.000000 USD**, zero metered calls, zero container execs. No command killed;
every command ran under its class bound (120s ordinary / 600s suite / 2400s overall).

## 5. Receipt

- Work commit `WORK_HEAD = 8166e79994a732a6a7fa176eb4b305f56fb0512d` (the two source hunks + the
  test + the 3 worklog files), pushed to `origin/automation`; worktree clean (`CO-55`).
- No push to `storagegenie-evidence`; `{{RECEIPT_CMD}}` not run.
- Note added on WORK_HEAD on `refs/notes/storagegenie-coder-reports`, pushed, then re-fetched into
  the **mapped** local ref `refs/notes/sg136-verify` (a default fetch carries no notes; a bare
  refspec rewrites only FETCH_HEAD — mapped per `M20`). `show` output pasted verbatim below.
- Final tip dual-annotated with the same note (note-anchor inoculation, SG-092 precedent).
- `note=yes`

Executed output, pasted verbatim:
```
$ git push origin automation
To github.com:Andovol/StorageGenie.git
   b828b40..8166e79  automation -> automation
$ git notes --ref=refs/notes/storagegenie-coder-reports add \
    -m "Dispatch-ID: SG-136 | Report: docs/worklogs/SG-136_report.md | Work-HEAD: 8166e79994a732a6a7fa176eb4b305f56fb0512d" \
    8166e79994a732a6a7fa176eb4b305f56fb0512d
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   9928245..d6c1456  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg136-verify
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg136-verify
$ git notes --ref=refs/notes/sg136-verify show 8166e79994a732a6a7fa176eb4b305f56fb0512d
Dispatch-ID: SG-136 | Report: docs/worklogs/SG-136_report.md | Work-HEAD: 8166e79994a732a6a7fa176eb4b305f56fb0512d
```

## UNCLEAR

- **FIRST READ:** the slice read as "#16 but batch the relationship" and the mechanism was exactly
  that; the surprise was that the packet's premise about the **list** route (§G0, acceptance) does
  not hold in this tree — `list_assets` never calls `_asset_to_dict` and serializes no assertions.
- **DURING EXECUTION:** two tree facts diverged from the packet's suggested shape and both were
  resolved in-slice with measurements: (a) the relationship needed an explicit cascade or asset
  deletion broke (F4); (b) `selectinload` at PATCH/MERGE costs an extra SELECT because those
  services `db.refresh()` (F3), so those two sites stay lazy and every served count is unchanged.
- **REMAINING:** (a) the two `test_signals` reds remain environment gaps (libzbar shared library,
  tesseract binary) by design; (b) PR #16 is superseded by this rewrite and should be closed on the
  Architect's word; (c) this slice is unserved (`PG-PR-04`) — serving it needs an owner rider word.

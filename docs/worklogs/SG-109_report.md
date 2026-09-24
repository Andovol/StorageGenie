# SG-109 report — Tier calibration on live dates: measure, verdict per category, change only with evidence

**Dispatch-ID:** SG-109
**Work dir:** `/home/andrei/StorageGenie` · **origin:** `git@github.com:Andovol/StorageGenie.git`
**Branch:** `automation`
**BASE_REF:** `origin/automation` → **BASE_RESOLVED:** `effd7d17461b4774ae509e64330e199f63f7f1cd` (== start HEAD)
**WORK_HEAD:** `dab94df5fc65d3f483f6b6179db4424598b4b025`
**Model / effort (CO-78, from process arguments):** argv = `opencode run --auto --dir /home/andrei/StorageGenie --variant high <packet>` → **model = CLI default** (no `--model` flag on argv; omitted per policy), **effort = `high`** (from `--variant high`).
**Spend (real $):** **$0.000000** — no metered call exists on any path (zero provider calls).
**Contract echo (verbatim):** `recorded 0.33.0 == published (b232b84; D129 adoption, G-L1 clean 2026-09-24)` — source path `/home/andrei/storagegenie-contract/VERSION` = `0.33.0`, `git -C /home/andrei/storagegenie-contract rev-parse HEAD` = `b232b845d74e89cb346c60fa4b9a40ec401c42dd` ("Contract payload 0.33.0"), `sha256sum RULES.md` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46` == payload `RULES.sha256`.

## What shipped

- **New** `docs/worklogs/SG-109_calibration.md` — the calibration record: per-category verdicts with
  measured numbers, the recompute query, and the revisit rule.
- **New** `docs/worklogs/SG-109.log`, `docs/worklogs/SG-109_verify.log` (this report).
- **No served-code change.** `backend/` diff is **empty** (0 lines; 0 untracked non-ignored files),
  quoted in the verify log. No plugin window value edited, no test edited, no route/engine/dashboard
  hunk, no migration. **Path executed = NO-CHANGE** (docs-only); G2 skipped entirely.

## G1 — live measurement (raw in the verify log)

One live household, read-only:

| Observable | Measured |
|---|---|
| `GET /v1/households` | **1** household `01a0a029-1477-7ca0-b200-bce78a96c679` |
| `GET /v1/plugins/expiry-tracker/status` | `as_of=2026-09-24`, `rows=[]`, `unresolved_rows=[]`, `summary.total=0`, HTTP 200 |
| `GET /v1/analytics/summary` → assets | `total=6`, `active=6` |
| `… → categories` | all `counts` = **0**; `uncategorized = 6` |
| `… → expiry` | `expired 0 · within_7_days 0 · within_30_days 0 · safe 0 · unknown 6` |
| Current windows (live `CATEGORIES`) | food 1/7/30 · medicine 1/3/14 · cosmetics 7/30/90 · household 30 · documents 30/60 |
| SG-107 pin test | **2 passed** in 0.80 s (quoted, not re-proved) |
| Resolved live rows (recompute query) | `{households:1, resolved_total:0, per_category:[]}` |

The SG-108 hypothesis is **re-verified, not inherited**: 6 assets, 0 accepted-expiry rows,
`uncategorized = 6` — all CONFIRMED.

## Per-category verdict (each cites a measured number)

| category | resolved live rows | `days_remaining` spread | verdict |
|---|---|---|---|
| `food_beverages` | **0** | (empty) | **KEEP — provisional** (no evidence) |
| `medicine_pharma` | **0** | (empty) | **KEEP — provisional** (no evidence) |
| `cosmetics_personal_care` | **0** | (empty) | **KEEP — provisional** (no evidence) |
| `household_chemicals` | **0** | (empty) | **KEEP — provisional** (no evidence) |
| `documents_other` | **0** | (empty) | **KEEP — provisional** (no evidence) |
| `non_perishable` | **0** | (empty) | **KEEP** (no windows by design) |

No measured row contradicts any window → **no CHANGE verdict**. `PG-SC-07`: the smallest population
that reaches "no evidence" is the **entire live catalog** (1 household / 6 assets / 0 resolved), and
it **is** reachable today (measured above). The no-change path returns KEEP-provisional with the
revisit rule — never an error, never a fallback number.

## G2 — numbered skip (change path NOT executed)

1. No G1 verdict is CHANGE: every category has **0** resolved live rows.
2. Zero measured rows contradicting a window → editing a window would tune against nothing
   (`PG-SC-09` inverse = the defect). No `expiry_tracker.py` window value edited.
3. No served code changed → D145 triggers no rebuild/recreate (`PG-PR-04`). No image built, no
   container recreated, no press, no writes; production untouched.

## G3 — calibration record (quoted from `docs/worklogs/SG-109_calibration.md`)

- **Recompute query** (derives the next calibration; executed, output above):
  ```sh
  curl -s http://127.0.0.1:8003/v1/households | jq -r '.[].id' \
  | while read -r hid; do
      curl -s "http://127.0.0.1:8003/v1/plugins/expiry-tracker/status?household_id=$hid"; echo
    done \
  | jq -s '{households: length, resolved_total: ([.[].rows[]] | length),
            per_category: ([.[].rows[].category] | group_by(.) | map({category: .[0], resolved: length}))}'
  ```
  The volatile count never lives in prose (`G-A3`) — the query does.
- **Revisit rule:** re-calibrate when any category holds **≥5 resolved live rows** (threshold itself
  uncalibrated, stated as such).
- **Path:** NO-CHANGE, because no measured row contradicts any window.

## Cross-product check (`PG-IC-01`)

No criterion demands engine-shape changes, new routes, dashboard hunks, migration, press, sender, or
any metered call — no cell collides. Reads executed: pytest/TestClient (pin test) + host read-only
GETs (households/status/analytics summary) + local module read (`CATEGORIES`). No image build, no
recreate, no unnamed runtime launched.

## Privacy gate (`PG-SC-05`)

Identifiers are TEXT only. Host `.env` never printed, never read into any artifact.
`grep -nE 'api[_-]?key|secret|passwd|password|bearer|private key|BEGIN [A-Z ]*PRIVATE KEY|sk-[A-Za-z0-9]|ghp_|AKIA|jina_'` over the changed files → `exit=1`, **0 real matches**; `.env` count in `git status` = 0.

## Acceptance-criteria question (`PG-SC-09`)

- **Measurement** — what do the live rows actually look like against current windows? The live
  catalog holds **0 resolved rows**, so no window acts on anything; raw captures quoted.
- **Change** — did any measured row contradict its window? **No** — 0 rows, so no change.
- **Record** — can the next calibration run without re-deriving the method? Yes: the recompute query
  + the ≥5 revisit rule are committed.

## Receipt note (M20-corrected block)

No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Work pushed to `automation`; worktree clean.
Commands executed (verbatim), on `WORK_HEAD=dab94df5fc65d3f483f6b6179db4424598b4b025`:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports show dab94df5fc65d3f483f6b6179db4424598b4b025
error: no note found for object dab94df5fc65d3f483f6b6179db4424598b4b025.
precheck_exit=1

$ git push origin automation
   effd7d1..dab94df  automation -> automation
push_automation_exit=0

$ git notes --ref=refs/notes/storagegenie-coder-reports add \
    -m "Dispatch-ID: SG-109 | Report: docs/worklogs/SG-109_report.md | Work-HEAD: dab94df5fc65d3f483f6b6179db4424598b4b025" \
    dab94df5fc65d3f483f6b6179db4424598b4b025
note_add_exit=0

$ git push origin refs/notes/storagegenie-coder-reports
   0b22546..174b4a9  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_notes_exit=0

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-sg109-fetched
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-sg109-fetched
fetch_exit=0

$ git rev-parse refs/notes/storagegenie-coder-reports-sg109-fetched
174b4a93cc7b4b233c8253210d1440efca130a67

$ git notes --ref=refs/notes/storagegenie-coder-reports-sg109-fetched show dab94df5fc65d3f483f6b6179db4424598b4b025
Dispatch-ID: SG-109 | Report: docs/worklogs/SG-109_report.md | Work-HEAD: dab94df5fc65d3f483f6b6179db4424598b4b025
show_exit=0
```

First line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Existing-note refusal would have been a STOP; the precheck showed no existing note. Final line **note=yes**.

## Three UNCLEAR lines

- **FIRST READ:** whether the live catalog would really be entirely uncategorized (the SG-108
  hypothesis) — it was; re-verified with raw captures, not inherited.
- **DURING EXECUTION:** whether `engine unresolved_rows = 0` contradicts `analytics expiry.unknown = 6`
  — resolved: the engine admits only assets carrying an accepted classification, and the 6 unknown are
  the unclassified assets outside the engine stream (SG-108 `F-SG107-1`); not a defect.
- **REMAINING:** the ≥5-resolved-rows revisit threshold is itself uncalibrated — adopted as a stated
  starting point, to be revisited when real rows arrive.

note=yes

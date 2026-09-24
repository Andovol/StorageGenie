# SG-109 calibration record — tier windows measured against live resolved rows

**Dispatch-ID:** SG-109 · **as_of:** 2026-09-24 (live clock at execution, `PG-IC-07`) ·
**Path executed:** **NO-CHANGE** (docs-only; G2 skipped — no measured row contradicts any window) ·
**Spend:** $0.000000.

This record is the calibration input for the next run. It states, per category, the
**measured** number of resolved live rows, their `days_remaining` spread, and the verdict
against the current windows. A change is allowed only on measured rows; a category with
zero resolved rows stays **provisional** and is never tuned to fit nothing (`PG-SC-09`).

## Live population measured

- `GET /v1/households` → **1** household: `01a0a029-1477-7ca0-b200-bce78a96c679` ("Popescu Household").
- `GET /v1/analytics/summary?household_id=…` → `assets.total = 6`, `assets.active = 6`;
  `categories.counts` all **0**; `categories.uncategorized = 6`;
  `expiry` = `{expired:0, within_7_days:0, within_30_days:0, safe:0, unknown:6}`.
- `GET /v1/plugins/expiry-tracker/status?household_id=…` → `rows: []`, `unresolved_rows: []`,
  `summary.total = 0`. (The engine only admits assets carrying an **accepted classification**;
  all 6 live assets are unclassified, so 0 enter the engine stream. The 6 "unknown" in the
  analytics block are those same unclassified assets — SG-108 `F-SG107-1` — and are **not**
  resolved expiry rows.)

**Resolved live rows across the whole live catalog = 0.** The smallest population that reaches
"no evidence" is therefore the entire live catalog, and it **is** reachable today (measured above).
The no-change path returns KEEP-provisional with the revisit rule below — never an error, never a
fallback number (`PG-SC-07`).

## Current windows (baseline, read live from `CATEGORIES`)

Proven by the SG-107 pin test `test_category_windows_are_the_declared_uncalibrated_data`
(quoted pass in the verify log) and re-read live from the module this slice:

| slug | tier_defaults | default_tier |
|---|---|---|
| `food_beverages` | critical 1 · urgent 7 · upcoming 30 | upcoming |
| `medicine_pharma` | critical 1 · urgent 3 · upcoming 14 | upcoming |
| `cosmetics_personal_care` | critical 7 · urgent 30 · upcoming 90 | upcoming |
| `household_chemicals` | upcoming 30 | upcoming |
| `documents_other` | upcoming 30 · long_lead 60 | long_lead |
| `non_perishable` | (none) | (none) |

## Per-category verdict (each cites a measured number)

| category | resolved live rows | `days_remaining` spread | current windows do | verdict |
|---|---|---|---|---|
| `food_beverages` | **0** | (empty) | nothing to tier | **KEEP — provisional** (no evidence) |
| `medicine_pharma` | **0** | (empty) | nothing to tier | **KEEP — provisional** (no evidence) |
| `cosmetics_personal_care` | **0** | (empty) | nothing to tier | **KEEP — provisional** (no evidence) |
| `household_chemicals` | **0** | (empty) | nothing to tier | **KEEP — provisional** (no evidence) |
| `documents_other` | **0** | (empty) | nothing to tier | **KEEP — provisional** (no evidence) |
| `non_perishable` | **0** | (empty) | no windows by design | **KEEP** (unchanged, not a calibration target) |

No category reached a CHANGE verdict: **zero measured rows contradict any window**, and no
window was moved. The shipped food/medicine/cosmetics profiles and the declared
household/documents values remain as they were; all remain DECLARED UNCALIBRATED (`G-A9`).

## Recompute query (derives the next calibration — no re-deriving the method)

Resolved-rows-per-category across every household (the exact input above; `jq` form, executed
this slice with output `{households:1, resolved_total:0, per_category:[]}`):

```sh
curl -s http://127.0.0.1:8003/v1/households | jq -r '.[].id' \
| while read -r hid; do
    curl -s "http://127.0.0.1:8003/v1/plugins/expiry-tracker/status?household_id=$hid"; echo
  done \
| jq -s '{households: length,
          resolved_total: ([.[].rows[]] | length),
          per_category: ([.[].rows[].category] | group_by(.) | map({category: .[0], resolved: length}))}'
```

`per_category` is the calibration input: each entry is `{category, resolved}` and the
`days_remaining` of the corresponding `rows` gives the spread to compare against the table above.
This count is **volatile** — it never lives in prose (`G-A3`); re-run the query.

## Revisit rule

**Re-calibrate when any category holds ≥5 resolved live rows.** This threshold is itself
**uncalibrated** (stated as such) — it is a starting point, not a measured constant. Until then,
the windows above stay provisional and are **not** changed. The trigger is checked by running the
recompute query; a category crossing 5 is the signal to re-open the per-category verdict table
and require fail-then-pass proof for any change.

## Why the no-change path executed

The G1 measurement found **0 resolved live rows in every category** — the live catalog holds no
date a window could act on. With no measured row to contradict a window, a change would be tuning
against nothing, which `PG-SC-09` (inverse) names as the defect. G2 (edit + rebuild + recreate)
therefore did **not** execute; no served code changed, so D145 triggers no refresh.

# SG-107 report — Expiry urgency engine: pure tier+bucket compute + read route, owns its refresh

**Dispatch-ID:** SG-107
**Work dir:** `/home/andrei/StorageGenie` · **origin:** `git@github.com:Andovol/StorageGenie.git`
**Branch:** `automation`
**BASE_REF:** `origin/automation` → **BASE_RESOLVED:** `107181644b54cc3f3dc2b3662ee511fe4ce1beaa` (== start HEAD)
**WORK_HEAD:** `<filled in the receipt-paste commit>`
**Model / effort (CO-78, from process arguments):** argv = `opencode run --auto --dir /home/andrei/StorageGenie --variant high <packet>` → **model = CLI default** (no `--model` flag on argv; omitted per policy), **effort = `high`** (from `--variant high`).
**Spend (real $):** **$0.000000** — no metered call exists on any path.
**Contract echo (verbatim):** `recorded 0.33.0 == published (b232b84; D129 adoption, G-L1 clean 2026-09-24)` — source path `/home/andrei/storagegenie-contract/VERSION` = `0.33.0`, `RULES.sha256` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46`.

## What shipped

- **New** `backend/app/services/expiry_engine.py` — pure compute: `days_remaining(expiry, as_of)`, `tier_for(category_slug, d)` reading the LIVE `CATEGORIES[slug].tier_defaults` (no hardcoded windows), `bucket_for(d)` (`<0` expired · `≤7` this-week · `≤30` this-month · else safe), `compute_status(db, household_id, as_of, category=None)`.
- **One route hunk** `backend/app/api/v1/plugins.py` — `GET /v1/plugins/expiry-tracker/status` (37 insertions / 1 deletion).
- **New** `backend/tests/test_sg107_expiry_engine.py` — 17 tests.
- **Refresh** — one backend rebuild + exactly ONE recreate + verify (D145 owned refresh).

Nothing else: `backend/app/models/`, `backend/alembic/`, `frontend/`, `backend/app/services/analytics/`, `backend/app/plugins/expiry_tracker.py`, `backend/app/main.py` all show an **empty diff** (quoted in the verify log).

## G1 BEFORE → G4 AFTER (raw values)

| Observable | BEFORE | AFTER |
|---|---|---|
| image id | `sha256:dc6a4382c99d247ef51dc7f3742c52cf195d3d563adccb5fbc690a8c158086cb` | `sha256:8dce9eb2cec50309d858b9eb13259a77cb597ede1b9ec35762141f86d11f0781` |
| container | `f2ca0be90eb0…` | `171e3d7ec196d7cbaa2d4f0b6f8c79457d5a0ee4b7a787140b20dc7efcdda9b8` (healthy t=12s) |
| served bundle | `index-DlD86cZ6.js` 307014 B `6e0a3af7…` | `index-DlD86cZ6.js` 307014 B `6e0a3af7…` — **byte-identical** (`cmp` equal; CSS too) |
| alembic current | `20260923_sg100_enrich_snapshot` | `20260923_sg100_enrich_snapshot` (unchanged) |
| table count | 25 | 25 |
| counts | all 25 tables | **delta exactly 0** on every table |
| health | `{"status":"ok","db":"ok","storage":"ok"}` | same, ×6 |
| gate | http 301 / https 401 | http 301 / https 401 |
| `GET /status` | n/a (route absent) | 200 empty-zeroed (live household has no accepted-expiry classified asset); 404 unknown household; 422 bad `as_of` |

The in-image engine + route are present in the fresh image (`/app/app/services/expiry_engine.py` `def compute_status` at :162; `@router.get("/status")` at :64) — the served code changed while the data stood still.

## G3 tests + gates

- New test file: **fail-then-pass, both raw runs committed**. FAIL (pre-implementation) = `ImportError: cannot import name 'expiry_engine'` (exit 2). PASS = **17 passed** (verbose list in the verify log).
- Boundary table through the REAL `CATEGORIES` for `d ∈ {−1,0,1,3,7,14,30,60,90,91}` on all six categories (food / medicine / cosmetics / household upcoming-only / documents 30+long_lead60 / non-perishable `{}`); the `"safe"` default is asserted reachable for every non-empty category (`PG-SC-12`), and `non_perishable` is asserted tier-null with bucket still computed.
- Discrimination: accepted tiers; a proposed near-date (d=0) stays `unresolved` with reason `proposed`; a superseded assertion is not tiered. All four reasons (`proposed | needs_evidence | unparseable | dateless`) exercised.
- Household isolation; `as_of` determinism (d 10 → 6 with an exact bucket+tier shift this-month/upcoming → this-week/urgent); urgency sort expired-first-then-ascending.
- No-write proof on the compute leg and on the route leg (all 25 table counts before == after).
- Route leg through the REAL `TestClient`: writer = existing classify + manual-entry endpoints, reader = the new route; row key set exact; `sum(by_bucket) == sum(by_tier) == len(rows)`; `unresolved == len(unresolved_rows)`; `total == rows + unresolved`; empty household / matching-nothing category / unknown slug all 200 zeroed; unknown household 404; bad `as_of` 422; default `as_of` = live today UTC.
- Full suite: **2 failed / 529 passed** — the two `tests/test_signals.py` decoder env reds, reproduced on the unmodified BASE (2 failed / 512 passed) before any edit; ruff **clean**; mypy **41 errors in 9 files** (baseline 41 in 9 → **delta 0**); secret grep on the changed files **0 real matches**.
- Post-restart sweep **waived** per `PG-DP-02` (restart-gated): substitute = the in-process suite pre-restart against the new code + the post-restart live probes as authority. No browser-driven tests exist on this path — the derived set differed nowise.

## Design calls (mine; decided, not asked)

1. **Accepted-only for classification too** (writer `classify_asset` always writes `accepted`; strictest consistent reading).
2. `tier_for` returns `"safe"` beyond the widest window (packet rule) and `None` for `d<0` and for a `{}` category.
3. **`summary.by_tier` uses key `"none"` for a null tier** so `sum(by_tier) == sum(by_bucket) == len(rows)` reconciles exactly; `total = len(rows) + len(unresolved_rows)`.
4. Assets with no accepted classification are **not part of the expiry stream** (skipped); the four unresolved reasons are all expiry-assertion states.
5. Unknown/invalid `category` slug → **empty zeroed 200** (matches nothing), never 404 and never an unfiltered fallback (`PG-SC-07`).
6. Route response adds `household_id` + `category` alongside `as_of` / `rows` / `summary` / `unresolved_rows`.

## Actual-versus-budget per leg

| Leg | Actual | Bound |
|---|---|---|
| G1 BEFORE capture | ~5 s | 120 s ordinary |
| fail run | 0.69 s | 120 s ordinary |
| pass run | 1.6 s | 120 s ordinary |
| suite + lint | 23.4 s pytest (+ ruff + mypy) | 600 s |
| build | 11 s | 600 s build+recreate+verify |
| recreate + health | 13 s | (same 600 s) |
| G4 AFTER verify | ~30 s | (same 600 s) |
| overall | ~6 min | 2100 s |

REAL metered spend: **$0.000000** (zero calls).

## Vacuous-pass check (`PG-SC-09`)

- Tier table: does the generic rule reproduce every category window without hardcoded numbers? Yes — asserted per-category expected values + a reachable `"safe"` default; the engine module contains no window literals.
- Discrimination: can a proposed date ever tier? No — asserted (accepted-only predicate; proposed near-date reported unresolved).
- Refresh: did the served code actually change while data stood still? Yes — image id changed and in-image engine/route present; bundle byte-identical; all 25 table counts delta 0.
- No acceptance criterion here passes on an empty diff or a skipped gate: the only empty diff is the explicitly-forbidden surfaces; the only empty result is the live household's honest zero (behavior proven in-process).

## Receipt note (M20-corrected block)

No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Work pushed to `automation`; worktree clean.

Commands executed and their verbatim output are pasted in the receipt-paste commit and the verify log; final line **note=yes**.

## Three UNCLEAR lines

- **FIRST READ:** whether a live `GET /status` returning an empty household body satisfied "200 read-only shape only" — decided yes (shape + status codes proven live; no fixture data created live per the constraint).
- **DURING EXECUTION:** whether an invalid `category` slug should be 422 or empty 200 — decided empty 200 per `PG-SC-07`.
- **REMAINING:** whether `by_tier` should expose a `"none"` key or omit untiered rows — chose the reconciling `"none"` key, documented for the dashboard slice.

note=yes

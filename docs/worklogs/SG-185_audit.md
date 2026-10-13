# SG-185 — R4 household-scoped replay repair, clean and complete

Immutable audit: base `aebe695c7a0cd96c3725ab50640ef5adfa599cdc` → work `341bd6946462dfafb8d4d5ba133a5c279b126f82` (fix + test + 8 logs) → report `5be388f6c8d3c8b7954ca5a5e5c045a7badbdbb`. Forced-command status at end: `result=done id=SG-185 exit=0`; status verb after: `result=reject reason=replay` (correct: receipted). Mapped notes fetch read the receipt: Dispatch-ID SG-185, report path, Work-HEAD `341bd69`, envelope settings (command). Local pulled `--ff-only` to the exact report HEAD. Scope diff `aebe695..5be388f`: product `backend/app/api/v1/assets.py` (+9/−3: comment + one-line qualification), new `backend/tests/test_sg185_asset_idempotency_household.py` (133 lines, 2 tests), 11 worklogs. No migration, no frontend, no config.

Holistic rating: **97/100**, no flag. Contract 0.47.0 echoed with sha match.

## Evidence accepted (re-read in the diff)

- Product hunk is exactly the D4 semantic: `if a and a.household_id == household_id` + comment documenting original-row-wins and fresh-key-for-requester (incl. the globally-unique-key consequence). Query-only; no new SQL predicate, so no composite index to measure.
- Test bodies drive real routes (`TestClient` on `app.main`, disposable households): two-household replay both ways with 201s, foreign GET/PATCH 403s, persisted-row assertions (Asset 1+1, single key row → A's id, B's `asset.create` audit with B's household). No placebo — the named paths and the failure behavior are exercised.
- FAIL half genuine on isolated base worktree (`B received A's id`, 1F/1P with the same-household control green); PASS half 11/11 incl. the pre-existing `test_asset_idempotency_is_persisted_and_reused`. ruff clean; mypy 41 == 41 both sides (assets.py 16 identical, +6 shift).
- G2 sibling discipline: `evidence.py:26` same-shape reported, NOT fixed (packet-declared out of scope, tests undisturbed); `jobs.py` rejects-only; `households.py` contextless; `deps.py` forwards; `list_assets` already scoped; D8 not bundled. CatalogPage untouched (zero frontend diff).
- Protocol: disposable env asserted pre-import, no `.env` handling, no denial (Docker probes excluded per packet), 2 health GETs 200/200, 414 s of 2100 s, 0 provider calls. Served defect not re-probed (POST-only path, packet is GET-only on production) — disclosed, correct.

No deduction: packet premises held without correction; no breach; no mismatch; no loops. I4 (fixture repetition, outside ceiling, named) and I5 (unbound overlay names, Makefile convention used + flagged) are disclosed process notes, not defects.

## Dispositions

| Item | Destination |
|---|---|
| Foreign-key no-dedup semantic | Documented in code + report; per-household registration needs schema change — parked unless owner asks (no slice) |
| F-SG180 evidence-key sibling | SG-186 (R6 integrity) packet to consider; named here, tests undisturbed |
| D8 archived-visibility | SG-188, per packet routing |
| Serve | Normal deploy course, not this slice (no G-K2 write here) |

Harness context-size reading unavailable; no conclusion made.

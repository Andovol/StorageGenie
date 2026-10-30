# SG-258 — Household and document dates: classify from the asset page, let Documents/other hold a date, keep a date across reclassification, correct or clear it

SG-258. model=opencode-go/deepseek-v4.1-flash effort=max, read from `/proc/1228283/cmdline` (`opencode run --auto --print-logs --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant max`). Served-model response metadata unavailable (no provider call made); no substitute claimed. dir=`/home/andrei/StorageGenie`; remote=`git@github.com:Andovol/StorageGenie.git`. BASE ref=`origin/automation`; resolved BASE COMMIT=`0d05310d8d7717419bcab05d0de4e54cebe69b0b`. WORK_HEAD=`a9ede3e89205c3a2ca70f2f80bf921b0725bf70d` (product+evidence commit; the report commit follows it, CO-55(b)). Terminal class: **CHANGED**.

Contract chain: repo `AGENTS.md` records `0.56.0`; host `/home/andrei/storagegenie-contract/CODER.md` line 3 verbatim: `**Contract version: 0.56.0** — **echo this line verbatim in your receipt.** It is the only proof that you`. The chain is equal (`0.56.0` == `0.56.0`); no `0.53.0 → 0.56.0` delta applied.

## (a) Issues / deviations / surprises

I1. **The packet's engine premise was wrong, measured, and corrected in a dependent file.** G3.3 says a null accepted expiry makes `compute_status` return the asset as dateless. The base engine returned `unparseable` for a null accepted value (measured on a temporary SQLite: `rows []`, `unresolved [{'reason': 'unparseable'}]`). Delivering A3/G5 therefore needed a 10-line change in `backend/app/services/expiry_engine.py` (null accepted value -> `dateless`; dicts with a bad date stay `unparseable`). This is a scope widening under `CO-09` (a discovered dependent), and it is the one product file outside the packet's named list. The coupled test `backend/tests/test_sg107_expiry_engine.py` also changed by one assertion (`passport` unresolved reason `dateless` -> `needs_evidence`, because SG-258 classifies documents with the placeholder). **A6 deviation disclosed:** no schema, migration, model, Dockerfile, compose, lockfile, dependency, database, host, provider, container or deploy bytes changed; two dependent files outside the packet list did.

I2. **`test_sg107_expiry_engine.py` was a hidden coupled test.** Its engine fixture classifies a passport as `documents` and asserted the old `dateless` reason. The owner-approved D6 behaviour writes the documents placeholder (`needs_evidence`), so the old assertion could not stand. Changed only that line; the slice and D6 are named here per `CO-38`.

I3. **The second `ExpiryEntryForm` caller is `ReviewPage.tsx`.** The form's new props were initially required, and the image proof's `tsc` caught the missing props (`ReviewPage.tsx(60,1358): error TS2739`). Fixed without touching `ReviewPage.tsx`: `categorySlug` and `hasWindows` are optional with defaults (`""`, `true`), so the review-workspace form keeps rendering. `AssetDetailPage` passes the real values and owns the gate. This was the only red the first image proof found.

I4. **`make backend-test` needed three invocations.** Run 1: host suite red on the coupled `test_sg107` assertion (760 passed / 1 failed). Run 2: host suite green, image proof red on the TypeScript prop error above. Run 3 (final tree): host suite 761 passed / 2 deselected, image proof 2 passed / 6 deselected, rc 0. `make frontend-test` ran twice: the first full run passed before the optional-prop fix; the final run on the final tree is the authoritative one.

I5. **A reclassification that writes the same `{"status": "unknown"}` placeholder reuses the existing active row.** `_write_assertion` returns the prior assertion when state and value are identical, so food -> household on an already-dateless asset adds no row (the manual task is reused too). This is existing write-path behaviour; the test asserts the observable state, not a new id.

I6. **The documents form's copy follows G1.4/G1.5 both ways.** Its title is "Manual date entry", the copy says "Date", and its default and first option is "Valid until"; the other date types (including "Expiry date") remain selectable, as G1.4 allows.

I7. **G0 used exactly the packet's lane socket.** `/var/run/docker.sock` was not probed. With `DOCKER_CONFIG=/tmp/opencode/sg258-docker` and `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-258/docker.sock`, `docker version` printed the Server block (29.9.2, API 1.56) and `docker run --rm busybox true` returned rc 0. No daemon restart, alternate socket, sudo or package install.

## (b) Actions

Changed product/test paths (13): `backend/app/plugins/expiry_tracker.py`, `backend/app/api/v1/plugins.py`, `backend/app/services/expiry_engine.py` (dependent widening, I1), `backend/tests/test_plugin_expiry.py`, `backend/tests/test_sg233_reminders.py`, `backend/tests/test_sg107_expiry_engine.py` (coupled test, I2), `frontend/src/api/client.ts`, `frontend/src/components/ExpiryEntryForm.tsx`, `frontend/src/routes/AssetDetailPage.tsx`, `frontend/src/routes/ExpiryPage.tsx`, `frontend/src/components/ExpiryEntryForm.test.tsx`, `frontend/src/routes/AssetDetailPage.test.tsx`, `frontend/src/routes/ExpiryPage.test.tsx`. `frontend/src/api/types.ts` was not changed (`Assertion.created_at` already existed). Evidence: `docs/worklogs/SG-258_{prestate,g0,fail_backend,fail_frontend,pass_backend,pass_frontend,gate_backend,gate_frontend,targeted_lint,health_end}.log` and this report. Work commit `a9ede3e89205c3a2ca70f2f80bf921b0725bf70d`; push and receipt follow this report.

G0: lane socket proven, `docker version` Server 29.9.2 / API 1.56, `docker run --rm busybox true` rc 0. Health start at 13:01:01Z and end at 13:17:32Z: both `{"status":"ok","db":"ok","storage":"ok"} http=200`, unchanged.

G1: `documents_other.has_expiry=True`; classify writes the `needs_evidence` placeholder plus the manual task; documents suppress `_observed_date`; manual entry accepts `valid_until` (enum + `valid-until` alias); the served taxonomy gains the date type automatically. G2: classification select over served active categories, current value, Save with the active classification id as `If-Match`, 409 handling, empty-taxonomy message, taxonomy drift test. G3: valid accepted dates survive a dated-to-dated move (same id/state/bytes); a move to `non_perishable` supersedes the old row with a null accepted, and the engine now reports `dateless`; a null/placeholder active gets the placeholder/task. G4: the form is gated by the classification profile, reads exact `plugin:expiry-tracker/expiry_date` and the latest `created_at`, pre-fills, accepts a proposed date, disables a no-op Save, clears to a null active through `POST .../expiry/clear`, and the Expiry page labels `valid_until` "Valid until". G5: tests, lint and gates in (c).

External effects: none. No production database opened, no schema/migration, no provider/key, no spend ($0), no container created beyond the throwaway image-proof container, no host or deploy change. Test command count: 21 invocations (12 backend: 2 FAIL, 5 targeted PASS, 1 coupled-file run, 1 single coupled test, 3 full gates; 9 frontend: 2 FAIL, 5 targeted PASS, 2 full gates). Docker commands: 2 (version, busybox). Highest-impact action: documents and household can now hold, keep, correct and clear a date through the asset page, with the date preserved across dated categories.

Durations: start 13:00:01Z (`ps lstart` of the coder process), end at report writing 13:18:46Z, elapsed 1125 s against the ≈1500 s expectation. Phases over 60 s: the three full backend host-suite runs at 68.72 s, 71.67 s and 68.87 s. All other phases together are the remainder; no other single command exceeded 60 s.

## (c) Verification

G0 (base runtime, before any gate claim):
```
DOCKER_CONFIG=/tmp/opencode/sg258-docker DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-258/docker.sock
Server: Docker Engine - Community
  Version:          29.9.2
  API version:      1.56 (minimum version 1.40)
version rc=0
run rc=0
```

Health:
```
START: {"status":"ok","db":"ok","storage":"ok"} http=200
END:   {"status":"ok","db":"ok","storage":"ok"} http=200
```

FAIL half, final candidate tests against BASE worktree `output/sg258-base` at `0d05310`:
```
backend: 12 failed, 17 passed, 11 warnings in 6.64s   (pytest rc=1)
frontend: Test Files 3 failed (3); Tests 16 failed | 26 passed (42)   (vitest rc=1)
```
The discriminating failures include documents manual entry 422, the absent classify control, the lost reclassification date, the clear route 404 and the dead-row pre-fill. Logs: `SG-258_fail_backend.log`, `SG-258_fail_frontend.log`.

PASS half, affected modules twice consecutively on the candidate:
```
backend run 1: 29 passed, 11 warnings in 7.36s   (rc=0)
backend run 2: 29 passed, 11 warnings in 5.66s   (rc=0)
frontend run 1: Test Files 3 passed (3); Tests 42 passed (42)   (rc=0)
frontend run 2: Test Files 3 passed (3); Tests 42 passed (42)   (rc=0)
```
Logs: `SG-258_pass_backend.log`, `SG-258_pass_frontend.log`.

Full gates (final tree):
```
make backend-test:
cd backend && python -m pytest -q -m "not requires_native_libs"
761 passed, 2 deselected, 49 warnings in 68.87s (0:01:08)
docker run --rm --network none -e SG_IMAGE_PROOF=1 storagegenie-backend:prover python -m pytest -q -m requires_native_libs tests/test_signals.py
2 passed, 6 deselected in 1.83s
backend-test rc=0

make frontend-test:
Test Files  30 passed (30)
Tests  324 passed (324)
frontend-test rc=0
```
Logs: `SG-258_gate_backend.log`, `SG-258_gate_frontend.log`.

Targeted lint, every changed backend/frontend file:
```
ruff: All checks passed! (rc=0)
eslint: rc=0
```
Log: `SG-258_targeted_lint.log`. The repo-wide mypy reds (41 in nine untouched files) and the one pre-existing eslint error were not touched or re-run.

Acceptance outcomes: A1 PASS (documents `has_expiry`, placeholder/task, manual 200, 60/30 reminders, OCR suppressed, SG-073 test updated). A2 PASS (control over served active ids, stale-token 409 with no change, drift test, empty message). A3 PASS (same accepted assertion across dated categories; null accepted + superseded old row + `dateless` engine on a move to Non-perishable, behind confirmation). A4 PASS (profile-gated form, exact-field latest active read, pre-fill, Accept, no-op Save writes nothing, Clear to null, `valid_until` label). A5 PASS (FAIL-then-PASS logs committed; host/image/frontend gates green; routes run twice; counts quoted). A6 **deviation disclosed in I1**: two dependent files outside the named list (`expiry_engine.py`, `test_sg107_expiry_engine.py`); every other byte is in scope and no schema/migration/etc. changed. A7 PASS (G0 proven first; health 200 start/end). A8 PASS (vacuity: documents entry observed 200 not 422; control observed present; the same assertion id survived reclassification; the form showed 2030-05-06, not the superseded 2020-01-01; clear observed 200 not 404; gates observed green not red). A9 PASS.

INTENT: code sets `documents_other.has_expiry=True` and suppresses OCR observation; the check expects `needs_evidence` + task and manual 200; the packet says A1.
INTENT: code classifies from the asset page with the active classification id in `If-Match`; the check expects 409/no-change and save/re-read; the packet says G2/A2.
INTENT: code preserves only a valid accepted date and clears on `non_perishable` with a null accepted; the check expects the same assertion id and a dateless engine; the packet says G3/A3.
INTENT: code gates the form on profile windows and clears to a null active; the check expects pre-fill, no-op Save writes nothing, Clear empties; the packet says G4/A4.
INTENT: code treats a null accepted expiry as `dateless` in the engine; the check expects `rows == []` and reason `dateless`; the packet says G3.3/G5.

TWINS: `ExpiryEntryForm` callers are `AssetDetailPage` (updated) and `ReviewPage` (unchanged; optional props preserve it). No product `endsWith("expiry_date")` reader remains; the exact-field reader is the only one. Backend callers of `classify_asset`, `store_manual_expiry`, `get_active_expiry` and `clear_expiry_date` are the plugin routes and tests named above.

UNCLEAR — FIRST READ: whether "engine dateless" meant `rows` exclusion or the unresolved reason; the packet said dateless, the base engine printed `unparseable`. Interpretation: the null accepted value is the clear representation, so the engine now prints `dateless` (I1).
UNCLEAR — DURING EXECUTION: whether a coupled test outside the scope list may be changed; treated as required by `CO-38`/owner D6 and disclosed in I2.
UNCLEAR — REMAINING: the packet's scope ceiling did not name the engine or `test_sg107`; both are changed and disclosed (I1/I2). No other open product item.

Verification: PASS

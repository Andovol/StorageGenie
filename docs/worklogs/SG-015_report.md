SG-015 | Expiry Tracker plugin skeleton + test-layer repairs

BASE ref requested: automation
BASE resolved: 340060579a9fcdf3d5f1a3f6918441aaf94bee6e
WORK_DIR: /home/andrei/StorageGenie
Origin: git@github.com:Andovol/StorageGenie.git
Coder: codex
Model: unknown (no model id appeared in process arguments; CLI default used)
Reasoning effort: high (verified from live process arguments: `codex exec ... -c model_reasoning_effort=high`)
Autonomy: L3, Phase 1 slice 4 of 7
Elapsed: 1097 s (18 m 17 s) / 2100 s (35 m) overall bound

Implemented

- `backend/app/plugins/registry.py:17-48` registers `expiry-tracker` 1.0.0 and raises explicit errors for unknown ids and version mismatches. The namespaced API maps both to 422 (`backend/app/api/v1/plugins.py:22-31`).
- `backend/app/plugins/expiry_tracker.py:34-152` defines date/unit/tier enums, active Food & beverages and Medicine/pharma profiles, inactive Phase 3 structures, non-perishable behavior, and the extension JSON Schema. Resolved tier defaults are Food 30/7/1 and Medicine 14/3/1 days, asserted by `backend/tests/test_plugin_expiry.py:82-93`.
- Classification, read-back, manual expiry, extension validation/write, and extension read-back are all under `backend/app/api/v1/plugins.py:61-199`, mounted by `backend/app/main.py:13,57`. No core route decorator changed; assets decorators remain the pre-existing list at `backend/app/api/v1/assets.py:20-273`.
- Classification storage reuses `assertion` with `plugin:expiry-tracker/` (`backend/app/plugins/expiry_tracker.py:28-31`) rather than adding a table or migration. The test reads classification back through GET and independently checks the stored row (`backend/tests/test_plugin_expiry.py:67-98`).
- Dateless active categories write an explicit `needs_evidence` expiry assertion and real `expiry.manual_entry` review task (`backend/app/plugins/expiry_tracker.py:351-357`). The test proves no accepted expiry before entry, then user-sourced accepted manual entry, evidence linkage, and resolved task (`backend/tests/test_plugin_expiry.py:147-189`).
- Non-perishable classification writes no expiry assertion and manual entry returns 422 (`backend/tests/test_plugin_expiry.py:211-225`). Inactive categories return 422 naming Phase 3 (`backend/app/plugins/expiry_tracker.py:168-180`).
- Extension validation rejects bad schema values and each of `identifier`, `condition`, `location`, and `status` (`backend/app/plugins/expiry_tracker.py:198-219`; `backend/tests/test_plugin_expiry.py:101-144`).
- G0 evidence setup is lazy/order-independent and remains test-only (`backend/tests/test_evidence_upload.py:30-72`); the stale migration assertion targets the explicit SG-013 revision (`backend/tests/test_signals.py:221-234`).

Verification

- Plugin file: `backend/tests/test_plugin_expiry.py` — 6/6 passed.
- G0 standalone: `backend/tests/test_evidence_upload.py` — 8/8 passed.
- G0 combined with SG-014 candidates: `backend/tests/test_candidates.py` + `backend/tests/test_evidence_upload.py` — 11/11 passed.
- SG-012…SG-014 seam group and export: `test_import_jobs.py` (3), `test_signals.py` (7, 2 decoder nodes deselected), `test_dedup.py` (4), `test_candidates.py` (3), `test_export.py` (4): 20 passed, 2 deselected. The export head test is green.
- Full backend: 47 collected, 45 passed, 2 failed. The only failures are the allowed carried nodes `backend/tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` and `backend/tests/test_signals.py::test_ocr_has_text_boxes_and_mean_confidence`, blocked by unavailable pyzbar/libzbar and tesseract. The stale migration node and all G0/plugin tests pass.
- Ruff: `venv/bin/ruff check app tests` — clean.
- Mypy: `venv/bin/python -m mypy app` — advisory, 40 errors in 9 files, 50 sources; baseline count, no out-of-ceiling changes.
- Migration count: zero new migrations. Existing SG-013 observation and SG-014 candidate migrations were tested through the explicit SG-013 downgrade and head re-upgrade; no live or production database was touched.
- Date-fabrication gate: `rg -n -i '\\btoday\\b|\\bnow\\b|timedelta' backend/app/plugins` returned no matches. The only date conversion is strict parsing of supplied/observed text (`backend/app/plugins/expiry_tracker.py:222-238,244-264`); no clock or shelf-life arithmetic exists.
- No criterion was passed vacuously: plugin tests invoke all routes, assert HTTP statuses and response bodies, query persisted assertion/review rows, and perform namespaced GET read-backs; the full suite collected 47 real nodes and emitted two named failures.

Scope and findings

- Changed only the packet ceiling: new plugin/API/test/ADR/worklog files, `main.py` mount, and TEST-ONLY G0 files. No frontend, runtime dependency, `.env`, secret, migration, restart, production write, or privileged operation was used.
- The packet expects `ARCHITECT.md`, `PACKET.md`, `DISPATCH.md`, and `PRODUCTION.md`, but none exists in the checkout. This is reported as a discrepancy, not treated as a pass.
- The two decoder failures remain a carried environment finding for the manual compose pass, per SG-013/D10; they were not hidden or repaired by changing product code.

Output paths: `backend/app/plugins/__init__.py`, `backend/app/plugins/registry.py`, `backend/app/plugins/expiry_tracker.py`, `backend/app/api/v1/plugins.py`, `backend/app/main.py`, `backend/tests/test_plugin_expiry.py`, `backend/tests/test_evidence_upload.py`, `backend/tests/test_signals.py`, `docs/adr/ADR-005-plugin-contract.md`, `docs/adr/ADR-009-expiry-tracker-design.md`, `docs/worklogs/SG-015.log`, `docs/worklogs/SG-015_report.md`.

UNCLEAR — FIRST READ: The four method-routing files referenced in AGENTS.md were absent; available repository state and the committed packet were used.
UNCLEAR — DURING EXECUTION: Decoder libraries were unavailable, leaving exactly the two pre-declared SG-013 decoder nodes red; no privileged workaround was attempted.
UNCLEAR — REMAINING: Manual compose must re-prove those two decoder nodes; Phase 3 category mechanics/UI and Phase 2 AI/provider work remain out of scope.

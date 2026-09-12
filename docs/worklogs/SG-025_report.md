# SG-025 report — provider seam: ADR-004/007/010 + gateway + ledger + fake

- Work dir `/home/andrei/StorageGenie`, origin remote as on host.
- BASE (packet ref `automation` resolved): `737765ee27094218b9cae7efc9338224f8c4e672`
  (`Packet SG-025 v2: G0 quarantine-adopt plus named PG-IDs (D39, 0.23.0 step 2)`).
- WORK_HEAD: filled at commit time (see G7).
- MODEL + effort provenance (owner rule, from process arguments): parent argv is
  `opencode run --auto --dir /home/andrei/StorageGenie --variant medium` (+ packet on
  argv); no `--model` flag present → **model = unknown (CLI default, omitted per
  policy)**, **effort = medium** (`--variant medium`). Never from identity lines.
- DATABASE: none — temp SQLite only, zero live rows. Restart: none — no service
  touched, new code NOT deployed (proof scoped to in-process tests).

## G0 — salvage (read-only)

- `git status --porcelain` at start: empty (clean).
- `git for-each-ref | grep -i quarantine`:
  `b6f17d5b9902932c550df26843df02ceec50ba7b commit refs/quarantine/SG-025-20260912T164340Z`
  (+ unrelated `refs/quarantine/preserve-20260907T083833Z`). No `quarantined=` trigger
  text was available to quote (read-only; never re-triggered).
- Debris stat (BASE..b6f17d5): 18 files incl. AGENTS.md, STATE.md, packet, 15 code/log
  files, 741 insertions. Adopted-vs-rebuilt: **rebuilt everything, adopted 0 lines
  verbatim**. The G2–G5 code shapes were verified sound (protocols/router/fake/model/
  migration/tests/ADRs match every G4 gate) and rewritten fresh to the same shape;
  three debris elements were explicitly NOT adopted because they contradict this
  packet: (1) AGENTS.md+STATE.md reverted to contract 0.22.0 (packet fires under D39
  0.23.0); (2) `docs/packets/SG-025-provider-seam-fake.md` self-edited to delete G0
  and the guard list; (3) verify log placed at `backend/docs/worklogs/` instead of the
  `{{WORKLOG_DIR}}` binding `docs/worklogs`. Nothing dropped silently.

## G1 — gates + Q2 probe

- Status quoted: empty output = clean (dirt would have been a STOP).
- Live head: versions dir holds `0201cf10c56c_001_core_foundation`,
  `20260908_sg013_observation`, `20260908_sg014_candidate`, `20260908_sg017_fts`;
  `down_revision` chain confirms head = **`20260908_sg017_fts`** (hypothesis CONFIRMED).
- Baseline (`venv/bin/python -m pytest -q`, 4.85s): **64 passed, 2 failed** —
  `test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier`
  (`assert any(... validated ...) → False`) and
  `test_signals.py::test_ocr_has_text_boxes_and_mean_confidence` (`assert ocr → []`).
  Both fail on the clean BASE tree (decoder QR/OCR legs, unrelated to this slice):
  cited as pre-existing with base commit + command + output per the standing line.
- `.env`: present, mode 600 (presence only, CO-44).
- Q2: `grep -c '^OPENCODE_API_KEY=' .env` = **0** — REPORTED, never a STOP. No secret
  literal anywhere in tree/logs (grep-gated, zero matches).

## G2 — provider surface (fake only)

- `backend/app/services/providers/protocols.py`: `ProviderResult` envelope (normalized
  output + raw payload + request id + usage/cost + model id + latency) + four Protocols
  verbatim-shaped (`VisionExtractionProvider.extract_items`,
  `OcrProvider.extract_text`, `EmbeddingProvider.embed`,
  `WebEnrichmentProvider.search_and_summarize`). **Sync by design** (service layer is
  fully synchronous; fake + Phase-2 callers run in-process) — decided and reported.
- `router.py`: config-driven ONLY (`RouterConfig`: provider id, fallback id,
  JSON-strictness, per-job cost budget, retryable-error set); never quality-ranked;
  budget-exceeded refuses BEFORE any call (zero invocations).
- `fake.py`: four shapes — valid / invalid-JSON-once-then-valid / needs_evidence /
  outage-raises-retryable.
- `PG-SC-05`: `grep -rn httpx|socket|requests|urllib app/services/providers/` =
  **no matches** (quoted). `config.py` untouched — no provider-routing settings needed
  (RouterConfig dataclass covers it).

## G3 — call ledger

- `backend/app/models/provider_call.py`: provider, model, prompt-template version,
  input hashes, output payload, cost/usage, latency, error state, nullable job FK;
  `TimestampMixin` + `new_id` per `audit_event.py`/`job.py` pattern (checked against
  `base.py`: `TimestampMixin` + `new_id`). One-line export + `__all__` in
  `models/__init__.py`. Production reader arrives SG-028; the read-back THIS slice is
  the ledger query inside the G4 tests (`PG-SC-02` — stated explicitly).
- Migration `20260912_sg025_provider_call` (down_revision = live head from G1).
  Temp-SQLite leg (via `DATABASE_URL` env since `env.py:23` overrides from settings):
  `Running upgrade 20260908_sg017_fts -> 20260912_sg025_provider_call` →
  HEAD-UP present **True** / DOWN-1 absent **True** / RE-UP present **True**;
  `alembic heads` = `20260912_sg025_provider_call (head)`.
- `downgrade` grep hits: 4 version-file `def downgrade` + pinned call-sites
  `test_search.py:247`, `test_signals.py:229`, `test_candidates.py:163`.
  Head-relative assertion fixed in-slice (`PG-SC-11`): `test_search.py:247`
  `downgrade(config, "-1")` → `downgrade(config, "20260908_sg014_candidate")`
  (after append, `-1` would unwind the NEW migration, not FTS).
  `test_postgres_dialect.py` EXPECTED_TABLES + import gained `provider_call`
  (else the new table reds the suite). Both are standing-line-mandated consequential
  edits, reported as scope notes, not silent extras.

## G4 — contract tests on the fake

- `backend/tests/test_provider_gateway.py` (5 tests): configured-provider selection;
  retryable-only fallback (non-retryable surfaces, no fallback); ledger row carrying
  every §3.3 field with read-back; budget refusal pre-call with zero invocations; all
  four fake shapes green.
- Fail-then-pass (`PG-EV-01`/`PG-EV-09`): PRE-change run FAIL —
  `ModuleNotFoundError: No module named 'app.models.provider_call'`
  (`1 error in 0.28s`); POST-change — `5 passed in 0.26s`. BOTH runs committed raw in
  `docs/worklogs/SG-025_verify.log` and quoted here from the log, not prose.
- Full suite (5.45s): **69 passed** (64 + 5 new), same 2 pre-existing signals reds —
  green-except-base-proved-reds. `ruff check` on all touched files: **All checks
  passed**. `mypy`: 1 error `app/models/base.py:8 unused type-ignore` — PRE-EXISTING
  (file untouched; reached via import; 40-advisory baseline known, no NEW error).
- No vacuous pass: fail run proves the tests invoke the new code (import error
  pre-change); budget test asserts zero-invocation counters; fallback test asserts
  per-provider invocation counts; ledger test round-trips every §3.3 field.

## G5 — ADRs (unconditional)

- `docs/adr/ADR-004-provider-abstraction.md`, `ADR-007-provider-privacy.md`,
  `ADR-010-guardrail-stage-0.md` — each with status + date + slice id. Committed.

## G6 — ledger / elapsed-vs-budget

- `docs/worklogs/SG-025.log`, `SG-025_report.md`, `SG-025_verify.log` (both raw runs).
  First token `SG-025`. Budgets (`PG-PR-06`, uncalibrated per `G-A9`): probes ~120s
  used of 120s; baseline 4.85s of 600s; migration leg ~60s of 300s; full suite 5.45s
  of 600s; overall ~25 min of 900s. Per-leg actuals with units stated here.
- Cross-product (`PG-IC-01`): G2 used only blueprint §6.1 shapes; G3 only
  model/migration pattern files; G4 only the fake; G5 only the embedded F-decisions;
  G1 only host gates + count probe. Recorded once, here.
- Guards row for the Architect rating: `PG-EV-01` fail-then-pass ✓ ·
  `PG-EV-02` artifact-exists (all files listed exist in tree) ✓ ·
  `PG-EV-04` fake-shape-of-payload (4 shapes, raw_payload asserted via ledger) ✓ ·
  `PG-EV-09` both-runs-committed (verify log carries PRE + POST) ✓ ·
  `PG-SC-02` ledger-readback (query inside G4 tests; prod reader SG-028) ✓ ·
  `PG-SC-05` rule-exclusion+grep (no-network-imports quoted) ✓ ·
  `PG-SC-10` no-ignored-commit (status clean of ignored paths; verified at commit) ✓ ·
  `PG-SC-11` migration-append (single new head, pin fix in-slice) ✓ ·
  `PG-IC-01` cross-product (above) ✓ · `PG-IC-03` stop-wins (no STOP fired; ceiling
  notes recorded, not ridden around) ✓ · `PG-IC-07` no-fixed-dates (revision id is the
  repo date-prefix convention — a name, not a gate) ✓ · `PG-IC-09` premises-live
  (head hypothesis confirmed; zero-provider-code premise confirmed by clean-tree
  baseline + pre-change import error) ✓ · `PG-PR-03/04/06/10` (denial text n/a —
  no privileged op attempted; no-service-touch; budgets above; no SSH) ✓.

## Issues and disagreements (incl. out-of-scope)

1. Attempt-1 debris contradicts the packet it claims to implement (contract revert,
   packet self-edit, wrong worklog path) — rebuilt, not adopted. Recommends the desk
   note that quarantine adoption needs a contradiction screen before merge.
2. `test_signals` QR/OCR reds pre-date this slice on clean BASE (decoder legs).
3. `mypy` base.py:8 unused-ignore pre-dates this slice (destination noted).
4. Scope note: `test_search.py` pin + `test_postgres_dialect.py` tables are
   standing-line-mandated (PG-SC-11 + suite-green) but outside the ceiling's file
   list — recorded explicitly rather than snuck in.
5. `config.py` left untouched with reason (no settings needed).

## UNCLEAR

- FIRST READ: none — every packet premise verified live (head, clean tree, Q2=0,
  zero provider code via pre-change import error).
- DURING EXECUTION: `alembic -x sqlalchemy.url` override is silently clobbered by
  `env.py:23` (settings win); the migration leg must go through `DATABASE_URL` env.
  Worth a comment in `env.py`, left untouched as out-of-scope.
- REMAINING: SG-026 cleared to fire; SG-027 waits on Q2 key (count 0 this slice);
  production ledger reader owed SG-028; ledger retention policy open until the
  production-datastore slice; `npm run build`-clean proof still queued (not this slice).

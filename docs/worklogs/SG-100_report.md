# SG-100 — Enrich snapshot persistence: model + migration + append-only writer (report)

**Dispatch-ID:** SG-100
**Coder / effort:** `opencode` / `high` (read from process arguments: `opencode run --auto --dir /home/andrei/StorageGenie --variant high <packet>`) — **model: cli-default** (no model id sent; omitted per policy; read from process args, never the system-prompt identity line).
**Work dir:** `/home/andrei/StorageGenie` · **Remote:** `origin` = `git@github.com:Andovol/StorageGenie.git`
**BASE (requested ref `origin/automation` resolved):** `4504d454d654f629861b25b6966dcd602c6eba26`
**WORK_HEAD:** `f5b460314c69c8ed6db64a5ad619c66c17612f70` · **Report:** `docs/worklogs/SG-100_report.md`
**Contract echo (verbatim):** `0.33.0` — recorded in `STATE.md:4` (`**Version:** \`0.33.0\` (D129 adoption 2026-09-23: checkouts \`e8f8113\` + \`999e94c\` + \`b232b84\` oldest-first, installed \`18de7fd7…\` = payload at all versions — clean)`) and `AGENTS.md:4` (`Rule-set version this project records: **0.33.0**`). Published-side re-hash **UNEXECUTED**: `.rules-cache/` is absent on this host and `origin` carries no `contract*` ref — see **F-SG100-3**.
**DATABASE: none live. Restart: none. Deploy: none. Container actions: none** (`PG-PR-04`). ONE migration file, never applied to production; tests run it on temp SQLite.
**Spend (real $):** **$0.000000** — no metered call exists on any path (scripted `httpx.MockTransport` only; no live call attempted, no image pulled/run).

---

## Result in one line

The slice is **complete and green**: the new append-only `enrich_snapshot` table chains from the live head and round-trips upgrade→downgrade→upgrade on a temp DB; the writer stores the verbatim raw body (byte-equal), records degraded snapshots loudly with their reason, and never updates; the committed brand-absent fixture is absence+parity pinned; the endpoint is untouched and still reads memory (`PG-SC-02`). Production was never opened.

## G1 — snapshot model + migration: **MET**

- New `backend/app/models/enrich_snapshot.py` on the `provider_call.py` pattern (`TimestampMixin + Base`, `String(36)` PK `default=new_id`). Columns: `id`, `source` (`"off"`/`"jina"`, indexed), `query`, `request_url`, `retrieved_at`, `status_code`, `raw_body` (`Text`, nullable), `raw_text` (`Text`, nullable), `no_result_reason` (`Text`, nullable), `version` (`String(64)`), plus `created_at`/`updated_at`. **No update path** — the model has no `onupdate`-driven correction route; corrections are new rows.
- Exported in `models/__init__.py` (import + `__all__`, same file).
- ONE new migration `backend/alembic/versions/20260923_sg100_enrich_snapshot.py`, `down_revision = "20260917_sg068_saved_search"` — verified as the live head in-slice via `ScriptDirectory` (R-RECON), **not inherited from the packet**. Upgrade creates the table + `ix_enrich_snapshot_source`; downgrade drops both.
- `PG-SC-02` stated whole: rows are written by G2 and read back in-slice through the writer's own `get_*` loader + test queries; the **endpoint does not read this table** until the live re-confirms slice — that absence is the design, not a gap (`api/v1/enrich.py` was not touched; its response still says `"snapshots_recorded": False`).
- Question answered (`PG-SC-09`): *does the schema hold verbatim history?* Yes — the table has a raw-body column and an append-only writer, proven by the round-trip and append tests.

## G2 — append-only writer (library, unwired): **MET**

- New `backend/app/services/enrich/snapshots.py`:
  - `record_off_snapshot(db, OffSearchSnapshot, *, query)` and `record_jina_snapshot(db, JinaSearchSnapshot, *, query)` — always `db.add` + `db.commit`, **never** `merge`/`update`/`delete`. A purity test scans the module's callables and source for any update/overwrite/upsert/merge/delete path and asserts none.
  - `serialize_raw_body()` stores the raw body as canonical JSON (`ensure_ascii=False, sort_keys=True`, compact separators) — lossless; a byte-equality test proves the stored body equals a fresh serialisation of the snapshot's raw body, and a **non-vacuous** test proves a deliberately reshaped body does **not** compare equal.
  - Degraded snapshots (`no_result_reason` set) are recorded loudly: `no_result_reason` + `raw_text` are stored, `raw_body` stays `None`, and the row is not dropped (OFF 503 and Jina missing-key both tested).
  - Loaders `get_snapshot(db, id)` and `get_snapshots_by_source(db, source)` read rows back by id/source.
- Question answered: *does the writer append without ever overwriting?* Yes — a second write of the same query creates a SECOND row (distinct id), and no update function exists.

## G3 — tests + gates: **MET ($0, temp DBs only)**

- New `backend/tests/test_sg100_snapshot_persistence.py` — **12 tests**, all offline: the REAL SG-081/082 fetchers run over scripted `httpx.MockTransport` transports (no network, no key crosses a wire, no metered call).
- **Fail-then-pass raw (`PG-EV-09`):** fail-pre = collection `ModuleNotFoundError: No module named 'app.models.enrich_snapshot'` (`exit=2`); pass-post = `12 passed in 0.96s`. Both raw in R-FAILPRE / R-PASSPOST.
- **Migration precedent named:** the upgrade→downgrade→upgrade-on-temp-DB pattern follows `backend/tests/test_foundations.py::test_foundations_migration_upgrade_downgrade_upgrade` (SG-035), located by grep in-slice. It is a temp `sqlite:///.../sg100_migration.db`; production is never opened.
- **Seen-to-fail (`PG-EV-01`):** empty/blank `query` → `ValueError` with 0 rows; the verbatim-equality test is shown to discriminate (reshaped body ≠ stored body); the no-update-path test asserts a real property, not a tautology.
- **Append-only:** second write of the same query → two rows with distinct ids.
- **Loader read-back:** `get_snapshot` by id (and `None` for unknown), `get_snapshots_by_source` per source.
- **Derived metadata (SG-088 rule):** `test_table_is_visible_through_derived_metadata` asserts `enrich_snapshot` is in `Base.metadata.tables`; `test_postgres_dialect.py` derives its table set from the same metadata, so no static list was touched.
- **Fixture:** committed `backend/tests/fixtures/enrich/off_absent_brand.json` (F-SG099-2 closed) with a test pinning both absence (`brands` key gone) and parity (removing `brands` from the committed `off_hit.json` yields exactly the committed fixture — a deterministic transform, not a hand-authored blob).
- **Gates:** ruff clean; mypy `41 → 41` errors (delta **0**; 84 source files checked, +2 new files, 0 new errors; grep confirms no error in the new files); secret-pattern grep over the 7 changed files **0 real**; full suite **2 failed, 498 passed** — the 2 failures are the known decoder env reds (`test_signals.py` pyzbar + tesseract absent), **stash-proved** at clean HEAD.
- Question answered: *is it proven on temp DBs with zero live touch?* Yes — every DB is a temp SQLite; the suite and the migration round-trip never open production.

## G4 — worklog and report: **MET**

`docs/worklogs/SG-100.log`, `SG-100_report.md`, `SG-100_verify.log` (raw outputs + BOTH fail-then-pass runs + every gate). First token `SG-100`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend **real $** $0.000000; contract echo + source path; three UNCLEAR lines.

---

## Findings

### F-SG100-1 — the snapshot objects do not carry the query text (design call, reported)

The packet's writer signature shows only the snapshot (`record_off_snapshot(db, OffSearchSnapshot)`), but neither `OffSearchSnapshot` (`client.py:49-59`) nor `JinaSearchSnapshot` (`jina.py:62-90`) carries the query. The writer therefore takes `query` as an explicit keyword argument (`record_*_snapshot(db, snapshot, *, query)`). This is the one field the snapshot lacks; it is reported rather than derived from the URL (deriving brand+name from a URL would be lossy and brittle). The packet's own instruction — "a field-name difference is a finding, never a bend" — is what this records.

### F-SG100-2 — M45 existing-file touch: privacy-audit allow-set (disclosed, minimal, root-caused)

`backend/tests/test_privacy_audit.py::test_g2_web_senders_are_the_two_researched_sources` is a name-only scan that enumerates every app file whose lines contain `jina`. Two new files legitimately name it — `services/enrich/snapshots.py` (persists a Jina snapshot) and `models/enrich_snapshot.py` (its `source` value is `"jina"`) — so the allow-set was extended with both and the docstring updated (exactly the SG-082/097/098/099 precedent the test itself documents). **Failing-test proof:** before the edit the test failed listing the two extra items (R-M45-FAILPRE); after, it passes (R-M45-PASS) and the full suite shows only the 2 known decoder reds. No other existing file touched.

### F-SG100-3 — contract published-side re-hash unexecuted

`.rules-cache/` is absent on this host and `origin` carries no `contract*` ref, so the G-L1 published-side hash could not be recomputed. Recorded `0.33.0` echoed verbatim from `STATE.md:4` + `AGENTS.md:4`; the Architect's 2026-09-23 G-L1 clean is taken as the published side.

---

## Acceptance criteria — status

| Criterion | Status | Evidence |
|---|---|---|
| Migration chains from the live head; upgrades/downgrades/upgrades on temp DB | **MET** | R-RECON + migration test; temp DB only |
| Table holds verbatim bodies byte-equal | **MET** | OFF + Jina round-trip tests; non-vacuous test |
| Re-write appends, never updates | **MET** | second-write test; no-update-path purity test |
| Loader reads back | **MET** | `get_snapshot` / `get_snapshots_by_source` test |
| Degraded snapshots recorded with reason | **MET** | OFF 503 + Jina missing-key tests |
| Brand-absent fixture committed with absence+parity pins | **MET** | `off_absent_brand.json` + fixture test |
| Tests fail-pre/pass-post both committed raw | **MET** | R-FAILPRE / R-PASSPOST |
| Gates green (ruff clean, mypy delta 0, secret 0, suite modulo 2 known reds) | **MET** | R-RUFF, R-MYPY, R-SECRET, R-SUITE, R-STASHPROOF |
| $0, production untouched, no deploy/restart/container | **MET** | MockTransport only; no production DB opened; migration file only |
| No vacuous pass | **MET** | see below |

**Vacuous-pass check (`PG-EV-01`, loudly):** no criterion passed vacuously. The fail-pre genuinely failed at collection (module absent); the round-trip test compares the stored body against a fresh serialisation and a **deliberately reshaped** body is shown to compare unequal (so the equality discriminates); the append test asserts two distinct ids and a row count of 2 (not merely "no exception"); the degraded tests assert the named reason text is present and the row count is 1; the no-update-path test asserts a structural property of the module, not a tautology; the migration test asserts the table is absent after downgrade, not just present after upgrade. The only criterion with a soft edge is the endpoint boundary: because the endpoint is deliberately NOT wired (`PG-SC-02`), there is no test asserting the endpoint reads the new table — that absence is the design and is stated, not hidden.

## Cross-product / privacy (`PG-IC-01`, `PG-SC-05`)

No criterion demands a live call, endpoint read/write, deploy, restart, or container act — no cell collides (`PG-IC-01`), stated so the check exists on paper. Only TestClient + host commands were run; pulling/running images or launching unnamed runtimes counts as execution and was not done. Fixture TEXT only; key NAMES only (`.env` values never printed, logged, quoted or committed); `docker compose config` never run (`PG-SC-05`). `PG-EV-06`: every row lives in a temp SQLite that pytest removes; no `INSERT`/`UPDATE`/`DELETE` against production. `PG-IC-07`: no fixed dates in code — `retrieved_at` is the live clock from the fetchers; fixture timestamps are sample data. `PG-IC-09`/`PG-PR-03`/`PG-PR-04`: migration file only, not applied; no restart/deploy/container action. `PG-SC-10`: all 7 paths are committable (verified — none ignored). `PG-SC-11`: end-relative assertions over the touched files grepped and listed (R-SC11) — only my own `"head"` upgrade calls; no existing assertion hardcoded the global head, and the full suite confirms none broke. `PG-EV-02`/`PG-EV-05`: the raw runs are pasted, not summarised; no number is fabricated.

## Report note on the notes ref (receipt)

Work pushed to `automation` (`4504d45..f5b4603`), worktree clean. Note added on `WORK_HEAD`, notes ref pushed, and verified against the **fetched, mapped** ref. Executed, verbatim:

```
$ git push origin automation
To github.com:Andovol/StorageGenie.git
   4504d45..f5b4603  automation -> automation

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-100 | Report: docs/worklogs/SG-100_report.md | Work-HEAD: f5b460314c69c8ed6db64a5ad619c66c17612f70" f5b460314c69c8ed6db64a5ad619c66c17612f70
note_exit=0

$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   0d1baad..75a70e9  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-fetched
ok fetched (1 new refs)

$ git notes --ref=refs/notes/storagegenie-coder-reports-fetched show f5b460314c69c8ed6db64a5ad619c66c17612f70
Dispatch-ID: SG-100 | Report: docs/worklogs/SG-100_report.md | Work-HEAD: f5b460314c69c8ed6db64a5ad619c66c17612f70
```

No push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`. The final tip (the docs-only receipt commit) is dual-annotated too (note-anchor inoculation, SG-092 precedent). `note=yes`.

---

## UNCLEAR

- **FIRST READ:** every packet premise about the tree held — the `provider_call.py` pattern, the current head `20260917_sg068_saved_search`, the OFF/Jina snapshot shapes, and the committed fixtures were all confirmed. The one premise that did not survive contact was the writer signature: the packet shows `record_off_snapshot(db, OffSearchSnapshot)` but the snapshot carries no query text, so the writer takes `query` as an explicit keyword (F-SG100-1). I read the field list in the packet as authoritative over the literal signature and reported the difference rather than bending the tree.
- **DURING EXECUTION:** the privacy-audit name-scan collision was self-caught by the full suite (F-SG100-2) and fixed minimally with failing-test proof. The migration round-trip on temp SQLite is fast and clean; the 2 suite reds reproduce at clean HEAD (stash-proved), so they are environmental, not mine.
- **REMAINING:** endpoint + UX consumption of the persisted snapshots (the live re-confirms slice, `PG-SC-02`); applying the migration to production rides a later owner-gated rider (`PG-PR-04`); a decision on F-SG099-1 (the metered TEXT path) still gates any live re-confirm; the published-side G-L1 hash when `.rules-cache/` is populated.

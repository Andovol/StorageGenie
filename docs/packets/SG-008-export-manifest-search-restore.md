# SG-008 — Export manifest verify/repair + search canonical tests + restore round-trip (Codex High)

> Facts below are what I believe from the tree that carries this packet. **They are EXPECTED conditions,
> not established truth. Verify each before building on it; a difference is a finding, not an obstacle.**
> For any number, path or quoted line I hand you: if your figures differ from mine, investigate and
> explain — **do not bend your answer to match mine. Correcting me is worth more than agreeing with me.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout. **Name the bound in the packet** — 120s is
> a reasonable default for ordinary commands, and a build, a test suite or a migration gets the bound its
> own work needs. **A command producing no observable progress within its bound is killed and reported.**
> Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure
> to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** A packet naming a tree hash is wrong by the time it runs — the packet commit becomes the tip. **The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.**

**DATABASE: none. Restart: none.** All verification runs against temp SQLite / `TestClient` with an isolated temp storage root, following the pattern in `backend/tests/test_health.py` and `test_assets_crud.py`. No prod-row writes; no service restart.

## Why this exists

`backend/app/api/v1/exports.py` (54 lines, verified 2026-09-03) serves `GET /v1/export` with assets, an `evidence_manifest` of `{id, sha256, storage_key, size_bytes}`, assertions and audit events — but the manifest carries **no schema version** (`BM-1` unbound), **no DB revision** (`BM-6` unbound), **no `Content-Disposition: attachment` header**, and its queries run as separate implicit reads rather than one explicit read transaction (`BM-6` unbound); the assertion loop is per-asset N+1. Search filters (`q` ILIKE, `asset_type`, `status`, `has_evidence`) exist at `backend/app/api/v1/assets.py:121-136` and SG-007 proved them against 5-asset mixed fixtures with exact id sets — but there is no canonical `test_search.py`, and `test_export.py` does not exist at all (`backend/tests/` holds only health, evidence, assets-crud, assertions). `GET /v1/jobs` (`jobs.py:36`) and `GET /v1/review-tasks` (`review_tasks.py:36`) return stub empties whose envelope shape was never asserted. The `IdempotencyKey` table is wired into `POST /assets` (`assets.py:28-41`) — the BM-2 question is whether the wiring is proved, not whether it exists; the second-transaction commit race and the missing TTL column were reported-not-redesigned in SG-007 and stay that way here.

Answers to SG-007's open UNCLEARs, so they are not rediscovered: run gates with `/home/andrei/StorageGenie/venv/bin` (`pytest`, `ruff`, `mypy` are not on PATH — observed 127); the ARCHITECT/PACKET/DISPATCH/CLOSE/LEDGER/PRODUCTION contract files are absent on the host, so all needed context is embedded in this packet; a non-fast-forward prefill is routine here — resolve it content-neutrally per G6, never force-push. Baseline: suite **14 passed** in ~1s, `ruff` clean, `mypy` 1 advisory at `evidence_service.py:95` (pre-existing, out of this slice's ceiling).

## G1 — Export manifest, committed tests first

- Add `backend/tests/test_export.py` (temp DB + temp storage, never prod paths): seed assets with evidence + assertions + audit rows, `GET /v1/export?household_id=` → 200; every seeded asset id present; every seeded evidence id present in `evidence_manifest` with non-empty `sha256` + `storage_key` + `size_bytes`; assertions and audit events non-empty; `manifest_version` field present (you choose the value, e.g. `"1"` — record the choice; this pins the `BM-1` contract); `db_revision` field present carrying the Alembic head id (BM-6); `Content-Disposition` response header contains `attachment`.
- New tests must FAIL first against the unmodified tree (quote the failing run), then pass after repair — both runs committed in the log (`PG-EV-09`). A new test passing before any change is a finding about the test, not a pass.
- Repair inside `exports.py` only, and only what the tests prove broken. Wrap the export reads in one explicit read transaction (BM-6) and say in the report which isolation the code actually holds — SQLite semantics stated honestly, not oversold.

## G2 — Search canonical tests

- Add `backend/tests/test_search.py`: `q`, `asset_type`, `status`, `has_evidence` (both polarities) each asserted against a fixture set containing matching AND non-matching rows with exact expected id sets. Overlap with SG-007's filter coverage is declared and intended — this module is Task 11's named artifact, not a discovery.
- Repair `assets.py` filter lines only where a test proves breakage. If all pass unmodified, that is the result: "already passed, hardened."

## G3 — Restore round-trip + stubs + idempotency proof

- Restore round-trip (early `UV-1` cut, manifest-only — file bytes are out of scope): parse the `GET /v1/export` JSON back into a FRESH temp SQLite database via the same models, assert asset count equals and evidence count equals the source. A count compared against itself (same connection, same objects) is vacuous — the sink must be a separately created database.
- Stubs: `GET /v1/jobs` and `GET /v1/review-tasks` → 200 with the paginated envelope keys present (`items`, `next_cursor`). Empty `items` is the expected Phase 0 shape, asserted as shape, never as proof of anything else.
- Idempotency wiring proof (BM-2): after `POST /assets` with an `Idempotency-Key`, assert a row exists in the `idempotency_key` table whose `response_json` carries the created asset id, and re-POST returns the same id. Report the second-transaction race window and the absent TTL column as findings — no redesign, no migration in this slice.

## G4 — Full suite + lint gates

- `pytest` full backend suite non-vacuous (exit 5 is a FAIL); `ruff check` on app + tests clean with output quoted and match counts named; `mypy` advisory count reported, not gated. Fail-then-pass runs for any repair committed in the log (`PG-EV-09`).

## G5 — Worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-008.log` and `{{WORKLOG_DIR}}/SG-008_report.md`, first token `SG-008`, every output path named in the report committed, three UNCLEAR lines at the end.

## G6 — Prefill the evidence ref, then auto-publish

- After WORK_HEAD is pushed to `automation`: `git push origin <WORK_HEAD>:refs/heads/storagegenie-evidence` (120s bound), then `git fetch origin refs/heads/storagegenie-evidence` and verify `git rev-parse origin/storagegenie-evidence` equals WORK_HEAD — quote both hashes. The publisher gates on this equality (`candidate_not_remote`); the prefill is what establishes it. If the push is non-fast-forward, merge content-neutrally and push the merge — never force-push (`CO-54`, as SG-005/SG-006/SG-007 demonstrated).
- Only then invoke `{{RECEIPT_CMD}}` with (`SG-008`, header `contract_sync=refresh version=0.17.2`, report path, WORK_HEAD), unmodified. A repair need is a finding, never a local patch to the wrapper.
- A `candidate_not_remote` from the unmodified publisher AFTER the verified prefill is a STOP — commit `BLOCKED`, push, report. Never hand-move the ref by other means and never force-push outside the publisher (`CO-54`).
- Verify the artifact, not the command: the evidence ref carries a commit with the `Dispatch-ID: SG-008` trailer — quote its hash. A zero-exit publish with no such commit is a FAIL.

## Constraints

- Scope ceiling: `exports.py`, `assets.py` filter lines, `schemas/common.py` only where tests prove breakage; the two new test modules; `docs/worklogs` files; the G6 prefill/publish mechanism. No evidence-service changes, no migrations, no frontend, no expiry/LLM/OCR, no `.env`/restart/secrets. Anything else is a STOP, not a stretch goal ("STOP and report" is not satisfiable by disclosure — disclosing an out-of-scope change does not authorize it).
- Cross-product (`PG-IC-01`): every acceptance criterion below is satisfiable inside the ceiling — none requires a migration (TTL stays a finding), none requires the evidence service, none requires a restart or a prod write.
- No datastore writes outside temp space; accidental prod rows reported with identifiers and left in place (`PG-EV-06`).
- Secrets: never commit `.env`, tokens, or `auth.json` contents — redact per `CO-44`.
- Privileged-denial: a denied `sudo` or `docker` operation is reported as unanswered per the block above, not routed around.
- Stash: worktree ends clean per `CO-55`.
- Test scope: full backend suite runs; every gate names the files it checked and its match counts; a gate emitting no output is a FAIL, not a pass.
- Budget: 120s per ordinary command, 600s for the suite, 2100s overall — report actual-versus-budget with units.
- Simplicity: verify before repairing; write no new checklist (`G-A7`).
- No Coder-side SSH checks: the dispatch key is absent inside the confined run — host paths and the prefill/publish return codes are the verification. Do not require what the confinement forbids.

## Acceptance criteria

- Export → 200 with all seeded assets, full `evidence_manifest` (sha256/storage_key/size_bytes), non-empty assertions + audit events, `manifest_version` + `db_revision` present, `Content-Disposition: attachment` — all observed via `TestClient` on temp paths, fail-then-pass quoted for new behavior.
- Each of the four filters proved against mixed matching/non-matching fixtures with exact id sets; `has_evidence` both polarities.
- Restore into a fresh temp DB yields equal asset and evidence counts; stubs return the 200 envelope; idempotency row with the asset id observed in-table.
- `pytest` full suite green and non-vacuous; `ruff` clean quoted; `mypy` count reported advisory.
- `docs/worklogs/SG-008.log` and `docs/worklogs/SG-008_report.md` committed; every output path in the report committed.
- `storagegenie-evidence` carries the `Dispatch-ID: SG-008` receipt commit; hash quoted; prefill equality quoted before publish.
- No criterion passed vacuously — an empty manifest, an untested filter polarity, or a same-object "round trip" is declared loudly, never a pass.

## Report

- Work dir `/home/andrei/StorageGenie`, remote `git@github.com:Andovol/StorageGenie.git`, `BASE` = packet start HEAD, `WORK_HEAD` = work commit hash.
- State model/effort provenance per `CO-78` — never from a system-prompt identity line.

## Budget

120s ordinary, 600s suite, 2100s overall (`TIMEOUT_S=2100` in wrapper).

# SG-007 — Asset CRUD verify/repair: manual create, pagination, provenance chain (Codex High)

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

**DATABASE: none. Restart: none.** All verification runs against temp SQLite / `TestClient` with an isolated temp storage root, following the pattern in `backend/tests/test_health.py` and `test_evidence_upload.py`. No prod-row writes; no service restart.

## Why this exists

`backend/app/api/v1/assets.py` (269 lines), `backend/app/services/asset_service.py`,
`backend/app/services/assertion_service.py` implement the full Task 9–10 surface — manual create with
per-field `accepted` assertions, evidence linking, cursor pagination with filters, detail with
evidence/assertions/audit, PATCH with `If-Match` optimistic concurrency and assertion supersession,
soft-delete via `ARCHIVED`, post-creation evidence attach — but `backend/tests/` covers only health and
evidence. This slice proves the catalog path the same way SG-006 proved the evidence path: committed
tests first, repairs only where tests fail.

Spots I already hold that deserve verification, not assumption (verify each; a verified no-op is a success):
- `asset_service.py:88-94` `attach_evidence` swallows all link errors silently (comment claims INSERT OR IGNORE intent) — log failures with asset + evidence ids instead of silence.
- `update_asset` bumps `(asset.version or 1) + 1`, suggesting `version` may start NULL — confirm the create path initializes it, repair if not.
- `list_assets` cursor pagination works around microsecond storage via `strftime` (`assets.py:140-150`) — the cursor round-trip test is what proves this workaround, not reading it.
- `post_asset` idempotency commits the key in a second transaction after create — correct under single-writer SQLite; report the race window honestly rather than redesigning it.

Expected conditions (verify, do not trust): SG-006 baseline green (suite 11 passed, `ruff` clean);
`AssetCreate`/`AssetUpdate` schemas gate writable fields; `decode_cursor`/`encode_cursor` live in
`backend/app/schemas/common.py`; household scoping enforced per-route with `403` on mismatch.

## G1 — Manual CRUD + idempotency + scoping, with committed tests

- Add `backend/tests/test_assets_crud.py` (temp DB + temp storage, never prod paths): create manual asset with `evidence_ids` → 201, detail shows the evidence item, one `accepted` assertion per supplied field, and an `asset.create` audit row; re-POST with the same `Idempotency-Key` returns the same id without a second row; unknown id → 404; cross-household read/patch/delete/attach → 403; archive sets `ARCHIVED` with version bump and `asset.archive` audit.
- Repair inside the asset files only, and only what the tests prove broken.

## G2 — Pagination and filters, proved by round trip

- In the same test module: create N>limit assets, page through with `limit` and returned `next_cursor` until exhaustion, asserting the union equals the created set with no duplicates and no gaps; `q`, `asset_type`, `status`, `has_evidence` each narrow correctly (each filter asserted against a fixture set containing both matching and non-matching rows — a filter tested only on matches is vacuous).
- If the `strftime` cursor workaround misbehaves (duplicates/gaps), repair it minimally and re-prove by round trip.

## G3 — Assertion provenance chain + evidence attach

- Add `backend/tests/test_assertions.py`: PATCH `display_name` with correct `If-Match` → old assertion `superseded`, new one `accepted` with the new value, version incremented, both visible in detail; stale `If-Match` → 409 with no state change; `POST /assets/{id}/evidence` attaches additional evidence post-creation (and 404s on unknown evidence id, 403 on cross-household evidence).
- `upsert_assertion` audit rows (`assertion.upsert`) asserted present.

## G4 — Full suite + lint gates

- `pytest` full backend suite non-vacuous (exit 5 is a FAIL); `ruff check` on app + tests clean with output quoted; `mypy` advisory count reported, not gated. Fail-then-pass runs for any repair committed in the log (`PG-EV-09`).

## G5 — Worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-007.log` and `{{WORKLOG_DIR}}/SG-007_report.md`, first token `SG-007`, every output path named in the report committed, three UNCLEAR lines at the end.

## G6 — Prefill the evidence ref, then auto-publish

- After WORK_HEAD is pushed to `automation`: `git push origin <WORK_HEAD>:refs/heads/storagegenie-evidence` (120s bound), then `git fetch origin refs/heads/storagegenie-evidence` and verify `git rev-parse origin/storagegenie-evidence` equals WORK_HEAD — quote both hashes. The publisher gates on this equality (`candidate_not_remote`); the prefill is what establishes it. If the push is non-fast-forward, merge content-neutrally and push the merge — never force-push (`CO-54`, as SG-005/SG-006 demonstrated).
- Only then invoke `{{RECEIPT_CMD}}` with (`SG-007`, header `contract_sync=refresh version=0.17.2`, report path, WORK_HEAD), unmodified. A repair need is a finding, never a local patch to the wrapper.
- A `candidate_not_remote` from the unmodified publisher AFTER the verified prefill is a STOP — commit `BLOCKED`, push, report. Never hand-move the ref by other means and never force-push outside the publisher (`CO-54`).
- Verify the artifact, not the command: the evidence ref carries a commit with the `Dispatch-ID: SG-007` trailer — quote its hash. A zero-exit publish with no such commit is a FAIL.

## Constraints

- Scope ceiling: asset + assertion paths only — no evidence-service changes, no export/search/UI, no expiry/LLM/OCR, no migrations, no `.env`/restart/secrets. Writes permitted: the two new test modules, repairs inside `asset_service.py` / `assertion_service.py` / `api/v1/assets.py` / schemas only where tests prove breakage, `docs/worklogs` files, and the G6 prefill/publish mechanism. Anything else is a STOP, not a stretch goal ("STOP and report" is not satisfiable by disclosure — disclosing an out-of-scope change does not authorize it).
- Cross-product (`PG-IC-01`): no acceptance criterion requires anything the ceiling forbids; the G4 gates observe, they do not modify.
- No datastore writes outside temp space; accidental prod rows reported with identifiers and left in place (`PG-EV-06`).
- Secrets: never commit `.env`, tokens, or `auth.json` contents — redact per `CO-44`.
- Privileged-denial: a denied `sudo` or `docker` operation is reported as unanswered per the block above, not routed around.
- Stash: worktree ends clean per `CO-55`.
- Test scope: full backend suite runs; every gate names the files it checked and its match counts; a gate emitting no output is a FAIL, not a pass.
- Budget: 120s per ordinary command, 600s for the suite, 2100s overall — report actual-versus-budget with units.
- Simplicity: verify before repairing; write no new checklist (`G-A7`).
- No Coder-side SSH checks: the dispatch key is absent inside the confined run — host paths and the prefill/publish return codes are the verification. Do not require what the confinement forbids.

## Acceptance criteria

- Create → 201 with evidence linked, per-field `accepted` assertions, and `asset.create` audit — all observed via `TestClient` on temp paths.
- Same `Idempotency-Key` re-POST → same id, no second row; 404 on unknown id; 403 on every cross-household route.
- Cursor pagination round-trips N>limit assets with no duplicates or gaps; each filter proved against mixed matching/non-matching fixtures.
- PATCH supersedes (old `superseded`, new `accepted`, version +1, both visible); stale `If-Match` → 409 with zero state change; attach endpoint links post-creation evidence (404/403 on bad/cross-household ids); archive → `ARCHIVED` + version bump + audit.
- `pytest` full suite green and non-vacuous; `ruff` clean quoted; `mypy` count reported advisory.
- `docs/worklogs/SG-007.log` and `docs/worklogs/SG-007_report.md` committed; every output path in the report committed.
- `storagegenie-evidence` carries the `Dispatch-ID: SG-007` receipt commit; hash quoted; prefill equality quoted before publish.
- No criterion passed vacuously — an empty page, an untested filter, or a skipped leg is declared loudly, never a pass.

## Report

- Work dir `/home/andrei/StorageGenie`, remote `git@github.com:Andovol/StorageGenie.git`, `BASE` = packet start HEAD, `WORK_HEAD` = work commit hash.
- State model/effort provenance per `CO-78` — never from a system-prompt identity line.

## Budget

120s ordinary, 600s suite, 2100s overall (`TIMEOUT_S=2100` in wrapper).

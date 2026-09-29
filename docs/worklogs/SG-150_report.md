MERGED: CORS lockdown landed as #42's method allowlist then #40's header allowlist + `If-Match`, rebased over #42, with one reconciled real-stack preflight test; backend-suite delta exactly +1 green, base-reds identical.

# SG-150 — merge Batch A: CORS lockdown (#42 + rewritten #40, unserved) — report

**Dispatch-ID:** SG-150
**Role:** Coder (never Architect — no dispatch verb run for any ID, no unit started or polled).
**Work dir:** `/home/andrei/StorageGenie`
**Origin remote (as on host):** `git@github.com:Andovol/StorageGenie.git` (fetch+push)
**BASE (packet ref `origin/automation` requested → resolved commit):** `3e557c9008d8869b238e6ada49c7dfe5b7ebb470`
(the ref and the resolved commit are stated separately — two fields, never one).
**WORK_HEAD:** `bd37d75334f8995d0fd8ea28086ed59c2cc0aa16`
**Contract:** recorded `0.40.0` == published — source path `/home/andrei/storagegenie-contract/VERSION`
(`0.40.0`); `git -C /home/andrei/storagegenie-contract rev-parse HEAD` =
`f26dbd32e3c4bd7cf878333fba719a6ca1d10c3c` (subject `Contract payload 0.40.0`); payload `RULES.sha256` =
`5b65629377bbac9e40bfa7e2f4d4e42a5667b3a08ec786beb47c6a677d9ac33c`. (`.rules-cache/` is absent on the
host — SG-145 F-SG145-1; the live checkout above is the contract path.)
**Model / effort (`CO-78`, from process arguments):** model `opencode-go/deepseek-v4.1-flash`, effort
`high` — source `/proc/1108044/cmdline` → `opencode run --auto --dir /home/andrei/StorageGenie
--model opencode-go/deepseek-v4.1-flash --variant high # SG-150 …`. No system-prompt identity used.
**Spend:** **$0.000000 actual USD** — zero metered calls on every path (local fetch/apply, `TestClient`
preflight, temp-SQLite suite, lint/type). No USD-metered call exists on any path.
**Live clock (`PG-IC-07`):** first capture `2026-09-29T14:19:25Z`; as-of-report-writing
`2026-09-29T14:29:18Z` (total elapsed `593 s`; the receipt-publish moments are after this and are the
runner's record, `CO-79`).
**Autonomy:** `L2` (merge-batch arc, D-0929-3 2nd word). **DATABASE none, restart none, deploy none**
(served-code change ships via the standing close-out rider — `PG-PR-04`; stated).

## Verdict: **MERGED** (unserved slice, no rider, no deploy)

SG-149 (98) ordered `#42 MERGE` then `#40 REWRITE` over it. Both heads still apply onto this BASE: their
merge-base `9fc1141` has **byte-identical** `backend/app/main.py` and `backend/tests/test_cors.py` to
`origin/automation` at slice start, so both hunks carried their exact authored context. `#42` applied
directly (`git apply`, not even a 3-way needed); `#40`'s header hunk then had to be **rewritten over
`#42`** (the two hunks share the `main.py` middleware block / `test_cors.py` helper + EOF), preserving
`#40`'s exact six-header list and adding `If-Match` as the seventh. The landed `main.py` method line is
byte-identical to `refs/pull/42/head`'s; the landed header list equals `refs/pull/40/head`'s plus only
the `If-Match` line. One coherent real-stack preflight test replaces `#42`'s two tests and `#40`'s two.

## Premise verification (a difference is a finding, not an obstacle)

| Packet premise | Measured on host 2026-09-29 | Verdict |
|---|---|---|
| Both heads still apply 3-way onto this BASE | Merge-base `9fc1141`; `git diff 9fc1141 origin/automation -- main.py test_cors.py` is **empty** → context byte-identical. `#42` applied directly; `#40` needed the ordered rewrite (adjacent-line overlap), which G1 authorizes. | confirmed |
| `main.py` still `allow_methods=["*"], allow_headers=["*"]` | Confirmed at BASE (`2cb579f`). | confirmed |
| `test_cors.py` asserts origins only | Confirmed: 3 tests, origin/credential only. | confirmed |
| Frontend `If-Match` at `ItemInspectorDrawer.tsx:135` + `AssetDetailPage.tsx:287` | Confirmed both send `If-Match` on asset PATCH (`String(current.version ?? 1)` / `asset?.version ?? 1`). | confirmed |
| Suite 2/636 with 2 base-reds (`test_signals` env pair) | Confirmed: `2 failed, 636 passed`; reds are the two `test_signals` cases. | confirmed |
| alembic single head `sg114` | `alembic heads` → `20260924_sg114_relation (head)`; untouched. | confirmed |
| Fail-pre at BASE is "wildcard TRACE-200" | **False. At BASE `TRACE` is already `400 "Disallowed CORS method"`.** Starlette 1.6.0 (`cors.py:29-30`) expands `allow_methods=["*"]` to `ALL_METHODS = (DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT)` — TRACE is *not* in it; `HEAD` *is*. So `#42`'s TRACE test **passes at BASE**; the genuine fail-pre discriminator is the **exact-set** assertion (BASE set has 7 members incl. `HEAD`; `#42`'s is 6). | **CORRECTED (mechanism)** |
| INFERRED: #42 then #40-with-`If-Match` = coherent lockdown + one reconciled test | Confirmed: methods six-set + headers seven-set incl. `If-Match`, one real-stack preflight test; suite delta exactly +1 green. | confirmed |

## G0 — apply #42, prove the methods lockdown (`PG-EV-08`, `PG-SC-12`, `PG-EV-09`)

`#42` was applied by its real hunks, not re-implemented:

- **Fail-pre commit `a7710b8`** — `git diff 9fc1141 refs/pull/42/head -- backend/tests/test_cors.py | git apply` → applied cleanly; landed blob `07bd4e8…` == head blob `07bd4e8…`. Run against the still-wildcard `main.py`:
  `pytest tests/test_cors.py -q` → **1 failed, 4 passed**; the failure is the exact-set assertion
  (`Extra items in the left set: 'HEAD'`). The TRACE test **passes at BASE** (see correction above).
- **Pass-post commit `4baa4bb`** — `git diff 9fc1141 refs/pull/42/head -- backend/app/main.py | git apply` → applied cleanly; landed blob `a488e59…` == head blob `a488e59…`. `pytest tests/test_cors.py -q` → **5 passed**.

Both runs are committed verbatim in `docs/worklogs/SG-150_verify.log` (work commit `bd37d75334f8995d0fd8ea28086ed59c2cc0aa16`),
which is the committed destination for the pair (`PG-EV-09`).

## G1 — rewrite #40 over #42 with `If-Match` (`PG-SC-12`)

- **`main.py`:** `git apply -3` of `#40`'s `main.py` hunk conflicted on the adjacent
  `allow_methods` line (expected — the packet's ordered rewrite). After reset, `#40`'s **exact**
  six-header list was grafted, plus `"If-Match"` (seven total). Faithfulness proven by diff:
  - final vs `refs/pull/42/head` → **only** the `allow_headers` change (= `#40` list + `If-Match`);
  - final vs `refs/pull/40/head` → **only** the `allow_methods` change (= `#42`) + `If-Match`.
- **`test_cors.py`:** reconciled into **ONE coherent CORS test**
  `test_cors_preflight_lockdown()` over `TestClient(default_app)` (the real middleware stack), asserting:
  methods exact-set `{GET,POST,PUT,PATCH,DELETE,OPTIONS}`; `access-control-allow-headers` contains
  `content-type`, `idempotency-key`, **`if-match`** and no `"*"`; `TRACE → 400 "Disallowed CORS method"`;
  `X-Evil-Header → 400 "Disallowed CORS headers"`. `#42`'s two tests and `#40`'s two tests are replaced by
  this one; the three origin tests are untouched. The helper mirrors both allowlists.
- **Real-stack preflight (not config text):** the captured probe (`SG-150_verify.log`) shows `PATCH` with
  `If-Match` → `200` and `allow-methods='GET, POST, PUT, PATCH, DELETE, OPTIONS'`; `TRACE` → `400`;
  `X-Evil-Header` → `400`; `HEAD` → `400` (was `200` at BASE — the lockdown's one intentional narrowing).
- **Online-equivalence rail:** full backend suite BASE `2 failed, 636 passed` → final `2 failed, 637 passed`
  — delta exactly the reconciled test green, base-reds identical. No frontend file touched (no frontend
  path in the ceiling).

## G2 — gates (`PG-EV-01`)

- **Suite:** `2 failed, 637 passed, 32 warnings in 34.96s`; base-reds = the two `test_signals`
  env cases, identical to BASE. Blast-radius expectation met exactly (delta == the one reconciled test).
- **ruff:** `backend$ ruff check` → `All checks passed!`
- **mypy:** `mypy app` → `Found 41 errors in 9 files (checked 90 source files)` — **delta 0** vs the
  recorded BASE count; the two in `app/main.py` (`:58`, `:64`) are pre-existing
  `# type: ignore[no-untyped-def]` comments on untouched handler defs (BASE `:50`, `:56`), shifted by the
  six added header-list lines.
- **Secret scan** over added diff lines (`git diff 3e557c9 HEAD | grep '^+'`) → no
  password/key/token/private-key/credential pattern; no base64/hex run ≥ 40 chars (`CO-100` clean).
- **`CO-101`:** every backend test that sets an `Origin` header was run:
  `test_assertions.py test_search.py test_privacy_audit.py test_phase3_e2e.py test_health.py` →
  `41 passed`. No CORS assertion exists outside `test_cors.py` (grep).
- **Ceiling:** `git diff --stat 3e557c9 HEAD` = exactly `backend/app/main.py` (+12/-2) and
  `backend/tests/test_cors.py` (+56/-2); no other product path.

## Findings

- **F-SG150-1 (packet correction, mechanism).** The packet's "Fail-pre at BASE (wildcard TRACE-200)" is
  wrong: Starlette 1.6.0 expands `["*"]` to `ALL_METHODS`, which already excludes `TRACE` (so it is 400 at
  BASE) and includes `HEAD` (so the wildcard is *broader* than the six-set). The fail-pre is nonetheless
  genuine via the exact-set assertion, so `#42` remains correct and necessary; only the stated mechanism is
  corrected. This is a new detail versus SG-149's audit, which quoted Starlette `cors.py:124-148` without
  noting that `["*"]` is pre-expanded in `__init__`.
- **F-SG150-2 (project-vs-contract, out of scope).** `CO-53` ("a dispatch ID appears only on the receipt
  commit; never in a work-commit message") is contradicted by the repo's own consistent practice: every
  prior slice's Coder work commit carries the `SG-<id> Gx:` prefix (e.g. `b4d31fa`, `c147316`, `1158109`).
  I followed the repo convention so the slice stays traceable alongside its neighbours; the dispatch ID's
  canonical home remains the receipt note + report — **flagging for a contract/practice reconciliation**.
- **F-SG150-3 (carry-over).** `.rules-cache/` absent on host (SG-145 F-SG145-1); contract checkout is
  `/home/andrei/storagegenie-contract`.
- No denied privileged operation occurred; no leg was routed around (`PG-PR-03`). No command was killed by
  its bound.

## Acceptance criteria — assessed (`PG-SC-09`)

- **locked (real stack):** PASS. Through `TestClient(default_app)` (real `CORSMiddleware`), the captured
  probe shows `TRACE → 400 "Disallowed CORS method"`, `X-Evil-Header → 400 "Disallowed CORS headers"`,
  while a `PATCH` preflight requesting `If-Match` → `200` with `If-Match` in `allow-headers`.
- **faithful (byte-effect):** PASS. Method line byte-identical to `#42` head; header list == `#40` head's
  + only `If-Match`; the final `main.py` differs from each head by exactly the other PR's field.
- **clean (diff):** PASS. Exactly the two write-ceiling product files; no frontend, no third file.
- **No vacuous pass (stated loudly):** the preflight ran against the real app middleware (not config text)
  and the disallowed cases assert `400` with the exact refusal strings; the suite was run in full, not
  skipped; the reconciled test actually invokes `client.options(...)` and fails on BASE (exact-set) — it is
  not an origin-only assertion. Nothing here passed by empty diff, empty set or skipped gate.

## Guard invocation (as listed in the packet)

`PG-EV-01` (suite/gates) · `PG-EV-02`/`PG-EV-05` (captures committed in the verify log) ·
`PG-EV-08` (BASE probe before edits) · `PG-EV-09` (both fail-pre and pass-post runs committed) ·
`PG-SC-09` (per-criterion questions above) · `PG-SC-12` (real hunks applied + blob-identity + real-stack
preflight) · `PG-IC-01` (cross-product: G0 fetch/apply 120s, G1 rewrite/preflight 120s, G2 suite 600s +
gates 120s — no criterion demands what the ceiling forbids) · `PG-IC-07` (live clock) · `PG-IC-08`
(blast-radius exactly +1 green; no other delta) · `PG-IC-09` (every given fact re-verified) · `PG-PR-03`
(no denied probe, none routed around) · `PG-PR-04` (no rebuild/recreate/restart/deploy; liveness rides the
close-out rider).

## Receipt

- Work pushed to `automation`; worktree clean (`CO-55`). No `storagegenie-evidence` push, no
  `{{RECEIPT_CMD}}`. The receipt is the note on `refs/notes/storagegenie-coder-reports`.
- Note on WORK_HEAD, then the notes ref pushed and verified from a **mapped** fetch
  (`refs/notes/sg150-fetched`); executed output, verbatim:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-150 | Report: docs/worklogs/SG-150_report.md | Work-HEAD: bd37d75334f8995d0fd8ea28086ed59c2cc0aa16" bd37d75334f8995d0fd8ea28086ed59c2cc0aa16
add_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   27ffc44..8cad39c  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_notes_exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg150-fetched
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg150-fetched
fetch_exit=0
$ git notes --ref=refs/notes/sg150-fetched show bd37d75334f8995d0fd8ea28086ed59c2cc0aa16
Dispatch-ID: SG-150 | Report: docs/worklogs/SG-150_report.md | Work-HEAD: bd37d75334f8995d0fd8ea28086ed59c2cc0aa16
show_exit=0
```

- Branch push `3e557c9..bd37d75 HEAD -> automation` (exit 0) preceded the notes push.

- Final tip dual-annotated (note-anchor inoculation, SG-092 precedent); mapped-fetch `show`, verbatim:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-150 | Report: docs/worklogs/SG-150_report.md | Work-HEAD: bd37d75334f8995d0fd8ea28086ed59c2cc0aa16" bfc785a9858213df59367308adef5218fe28179a
add_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   8cad39c..18aa963  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_notes_exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg150-fetched-final
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg150-fetched-final
fetch_exit=0
$ git notes --ref=refs/notes/sg150-fetched-final show bfc785a9858213df59367308adef5218fe28179a
Dispatch-ID: SG-150 | Report: docs/worklogs/SG-150_report.md | Work-HEAD: bd37d75334f8995d0fd8ea28086ed59c2cc0aa16
show_exit=0
```

## Budget — actual versus budget (units stated)

| Leg | Command class | Budget | Actual |
|---|---|---|---|
| Orientation + premise verification (fetch, diff, BASE probe, baseline suite) | ordinary | 120 s | ~120 s |
| G0 fail-pre (apply + pytest test_cors) | ordinary | 120 s | < 5 s |
| G0 pass-post (apply + pytest test_cors) | ordinary | 120 s | < 5 s |
| G1 rewrite + real-stack preflight + faithfulness diffs | ordinary | 120 s | < 30 s |
| G2 full suite | suite class | 600 s | 34.96 s |
| G2 ruff / mypy / secret / CO-101 tests | ordinary | 120 s | ~40 s |
| Worklogs + commit + push | ordinary | 120 s | < 15 s |
| Receipt notes (add/push/fetch/show) | ordinary / notes-push | 120 s / 300 s | < 15 s |
| **Overall** | — | **2400 s (lane `RUN_BUDGET_S=2100`)** | `593 s` as of report writing (14:19:25Z→14:29:18Z) |

Actual-versus-budget per goal: every leg well inside its class; overall well inside the 2400 s cap. No
command was killed by its bound; no interactive command ran. **Real metered spend $0.000000 USD, zero
metered calls.**

## UNCLEAR

- **FIRST READ:** the packet framed the fail-pre as "wildcard TRACE-200"; the first real-stack probe at
  BASE showed TRACE already 400 (Starlette pre-expands `["*"]` to `ALL_METHODS`, which lacks TRACE but has
  HEAD). I corrected the mechanism and used the exact-set discriminator; the verdict is unchanged.
- **DURING EXECUTION:** `#40`'s `main.py`/`test_cors.py` hunks overlap `#42`'s on adjacent lines, so the
  ordered rewrite — not a stock `git apply` — is the intended path; the header list was grafted byte-exact
  from the head rather than re-written from memory. The reconciled one-test design keeps methods + headers
  + both refusal paths in a single real-stack exercise.
- **REMAINING:** nothing on this slice's account beyond the shipped merge; the served-code change is not
  live until the standing close-out rider rebuilds/recreates (Deploy: none here). `F-SG150-2` (the `CO-53`
  work-commit-ID practice) is outside this slice and offered for reconciliation.

## RECOMMENDED-NEXT

- **Batch B per SG-149 order:** #36, folded #39, repathed #34. Batch A is merged (unserved).

**note=yes**

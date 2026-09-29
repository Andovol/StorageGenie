SG-149 report — outside-PR audit, 11-PR pile #32–42: every diff fetched as bytes, one verdict each, no merges

Dispatch-ID: SG-149
Role:       Coder (never Architect — no dispatch verb run for any ID, no unit started or polled)
Work dir:   /home/andrei/StorageGenie
origin:     git@github.com:Andovol/StorageGenie.git (fetch+push, as on host)
BASE ref:   origin/automation
BASE commit: 48e30c4fb848058c66188a74f4acab377bfd5fdd (start HEAD; worktree clean at start)
WORK_HEAD:  {{WORK_HEAD}}
Model:      opencode-go/deepseek-v4.1-flash  (per process arguments: /proc/<opencode-run-pid>/cmdline `--model`)
Effort:     high                            (per process arguments: /proc/<opencode-run-pid>/cmdline `--variant high`)
Coder:      opencode  (env CODER=opencode; lane job_spawn)
Contract:   echo 0.40.0 — source `/home/andrei/storagegenie-contract/VERSION`; tip
            `f26dbd32e3c4bd7cf878333fba719a6ca1d10c3c` (subject `Contract payload 0.40.0`);
            `RULES.md` sha256 `5b65629377bbac9e40bfa7e2f4d4e42a5667b3a08ec786beb47c6a677d9ac33c`
            equals payload `RULES.sha256`. Recorded 0.40.0 == published. (`.rules-cache/` absent on host —
            SG-145 F-SG145-1; the checkout above is the live contract path.)
Spend:      real $0.000000 USD · zero metered calls · zero suite runs · zero live calls · zero container execs.
            (The GitHub public REST read and the git pull-ref fetches are unmetered.)
Gates:      DATABASE none · Restart none · Deploy none.
Guards:     PG-EV-01 · PG-EV-02 · PG-EV-05 · PG-EV-10 · PG-SC-09 · PG-IC-01 · PG-IC-07 · PG-IC-09 · PG-PR-03
Autonomy:   L2 slice autonomy (verdicts only; nothing merges/rewrites/closes here).

## Standing-line compliance (stated before the evidence)

- **READ-ONLY audit.** The only writes are `docs/worklogs/SG-149.log`, `SG-149_report.md`,
  `SG-149_verify.log`. No merge, no PR close, no product/test/config write, no branch push other than the
  `automation` work commit required by the packet. `PG-PR-03`: a denied privileged operation is a STOP, not
  a signal to route around — none was encountered, so nothing was routed around.
- **No PR is merged as it stands.** Every "MERGE" below is a *recommendation for the owner's SECOND word*
  (`G-L7`), exactly as the packet says: this slice produces verdicts only. `REWRITE` = idea sound, diff not;
  `CLOSE` = one-line reason. (Equivalent to SG-133's label `REWRITE-AS-SLICE`.)
- Pull-ref fetches touched local git objects + `FETCH_HEAD` only; worktree clean proved at start and end.

## Premise verification (a difference is a finding, not an obstacle)

| Packet premise | Measured on host 2026-09-29 | Verdict |
|---|---|---|
| 11 open PRs #32–42 aimed at `automation`, author `Andovol` | **Confirmed exactly** — public REST `GET /repos/Andovol/StorageGenie/pulls?state=open` returns 11, numbers 32–42, all `state=open`, all `base.ref=automation`, all `user.login=Andovol`. No new arrivals, no disappearances. | confirmed |
| head names `bolt/`·`fix/`·`test-`·`perf/`·`clean-models-` | **Confirmed** (exact head refs quoted in §G0/verify log). | confirmed |
| Host `gh` unauthenticated, reads via `refs/pull/<n>/head` | **Confirmed** — `gh auth status` → `You are not logged into any GitHub hosts` (exit 1). Diffs fetched via `git fetch origin refs/pull/N/head` (prescribed). | confirmed |
| Contract recorded `0.40.0` == published `f26dbd3` | **Confirmed** — VERSION 0.40.0; tip `f26dbd3`; payload hash matches actual `RULES.md`. | confirmed |
| `.rules-cache/` is the contract path | **Absent on host** (`.rules-cache/` does not exist); used `/home/andrei/storagegenie-contract` (matches SG-145). | corrected |
| Overlap "notably #36/#39 and #40/#42" | **Confirmed, but incomplete** — measured also a 3-way `asset_service.py` cluster {#34,#36,#39}, an add/add on one new test path {#33,#37}, and `candidates.py` {#39,#41} (different functions). See F2. | corrected |
| #40 restricts CORS headers safely | **False** — the allowlist omits `If-Match`, which the project's own frontend sends. See F3. | corrected |

## G0 — every open-PR diff captured as bytes (`PG-SC-03`, `PG-IC-09`)

- **Enumeration (runtime):** `git ls-remote origin 'refs/pull/*/head'` lists all pull refs 2–42, then the
  public REST list fixes the *open* subset. Design call, disclosed: `gh` is unauthenticated, and pull-ref
  presence cannot distinguish open from closed (GitHub keeps refs for closed/merged PRs), so I used the
  **unauthenticated public REST read** to establish `state=open`. It is read-only, needs no token, and no
  login prompt appeared; the prescribed `refs/pull` path was still used for all diffs. Result: **11 open,
  #32–42** — the packet's exact expectation, no difference.
- **Fetch scope (one 120 s-class call):**
  `git fetch origin refs/pull/32/head refs/pull/33/head … refs/pull/42/head` → `fetch_exit=0`; all 11 heads
  resolved into `FETCH_HEAD` (quoted in the verify log). No ref was stored; no worktree file changed.
- **Byte capture:** for each head, `git diff --no-color $(git merge-base origin/automation <head>) <head>`
  written to a file and hashed. All 11 diffs are non-empty, text, and reachable. **0 UNREADABLE.**

| PR | head ref | merge-base | diffstat | bytes | sha256 |
|---|---|---|---|---|---|
| #32 | `bolt/batch-fetch-expiry-assertions-9805844303267441434` | `aa842682ee59` | +88/-5, 2 files | 6586 | `66f61238e3577916…` |
| #33 | `test-decode-cursor-invalid-format-2740448297750613393` | `9fc1141e9260` | +87/-0, 1 file | 3083 | `94d8d109cdd56df6…` |
| #34 | `fix/asset-service-exception-logging-3395863194390859121` | `9fc1141e9260` | +38/-2, 2 files | 2718 | `b8d42d92371690ca…` |
| #35 | `clean-models-all-exports-5061139618502718947` | `9fc1141e9260` | +4/-4, 1 file | 797 | `898f1cc23c46bd76…` |
| #36 | `perf/bulk-insert-asset-evidence-14308258920456442759` | `9fc1141e9260` | +110/-10, 2 files | 5298 | `f7485ff8da8de55d…` |
| #37 | `test-loads-json-error-handling-11643751385192757386` | `9fc1141e9260` | +78/-0, 1 file | 2579 | `736bb314de4c9c24…` |
| #38 | `fix-synthesis-empty-except-logging-14922827253064615080` | `9fc1141e9260` | +16/-4, 2 files | 2396 | `819dfa8963cbccae…` |
| #39 | `perf/bulk-insert-asset-evidence-3013153069290929288` | `9fc1141e9260` | +78/-4, 3 files | 3745 | `9697b7caeebed499…` |
| #40 | `fix/restrict-cors-allow-headers-9030401029426395364` | `9fc1141e9260` | +48/-2, 2 files | 2602 | `307290bb8a73a25d…` |
| #41 | `fix-n1-query-candidate-loser-merge-14169458296748822325` | `9fc1141e9260` | +4/-1, 1 file | 843 | `eb8e06fca7a11fd0…` |
| #42 | `fix/cors-overly-permissive-policy-381093961529617151`→`…7617649` | `9fc1141e9260` | +30/-2, 2 files | 2167 | `02ed0bae2b8571a2…` |

(Full 64-char hashes, `--name-status`, and the executed commands are in `SG-149_verify.log`.)

## G1 — verdicts (exactly one per PR, each resting on a quoted hunk)

| PR | verdict | reason + quoted evidence |
|---|---|---|
| **#32** | **MERGE** | Batch map reproduces the per-asset queries' semantics. New query: `db.query(Assertion).filter(Assertion.asset_id.in_(asset_ids), Assertion.field_path.in_([CLASSIFICATION_FIELD, EXPIRY_FIELD]), Assertion.review_state.not_in(("superseded","rejected"))).order_by(Assertion.created_at.desc())` then first-wins into `accepted_classification_map` / `accepted_expiry_map` / `latest_active_expiry_map`; `compute_status` consumes `classification_map.get(asset.id)`, `accepted_expiry_map.get(asset.id)`, `_unresolved_reason_from_assertion(latest_active_expiry_map.get(asset.id))`. Matches base `_accepted_classification_slug`/`_accepted_expiry` (`review_state=="accepted"`, `created_at.desc()`, first) and `_latest_active_expiry` (`not_in(("superseded","rejected"))`). Caveat: tie-break on equal `created_at` is DB-arbitrary in both shapes — the adopting slice should run `test_sg107_expiry_engine.py`. Also appends a `.jules/bolt.md` journal entry. |
| **#33** | **MERGE** | Adds `backend/tests/test_schemas_common.py` against the real module `app/schemas/common.py` (`decode_cursor`, `encode_cursor`, `loads_json`, `dumps_json`, `ProblemDetail`). Existing coverage is **empty** (`grep -rln "decode_cursor\|loads_json" backend/tests/` → no files), so this is not vacuous. All assertions match the base implementation (e.g. spec `f"{id}:{created_at.isoformat()}"` and legacy `ts|id` branches at `common.py:15-36`). Adopt, absorbing #37's unique cases. |
| **#34** | **REWRITE** | Idea sound (stop swallowing evidence-attach failures), but the diff keeps the broken per-item swallow and adds logging inside it: `except Exception as exc: logger.warning("Failed to attach evidence_id=%s to asset_id=%s: %s", eid, asset.id, exc)`. It conflicts with #36, which replaces that whole loop with a dedup + bulk insert that logs nothing — after #36 lands, #34's own test line `assert f"Failed to attach evidence_id={evidence.id} to asset_id={asset.id}" in caplog.text` cannot pass. Logging must ride the adopted bulk path. |
| **#35** | **MERGE** | Pure alphabetical reordering of `__all__`. All 21 names already exist: `from app.db import Base`, `from app.models.evidence import Evidence, asset_evidence`, `from app.models.location import Location, asset_location`. No import or export added/dropped (BASE `__all__` and head `__all__` are the same set). Cosmetic; harmless. |
| **#36** | **MERGE** | Strongest of the bulk-insert pair. `evidence_ids = list(dict.fromkeys(payload.get("evidence_ids") or []))` (dedup) + `db.execute(asset_evidence.insert(), [{"asset_id": asset.id, "evidence_id": eid} for eid in evidence_ids])`; `attach_evidence` now pre-reads `select(asset_evidence.c.evidence_id).where(asset_id==…, evidence_id.in_(…))`, inserts only `new_eids`. This removes the latent duplicate-key `IntegrityError` that the base loop swallows. Adds `backend/scripts/benchmark_asset_evidence.py`. SQLAlchemy 2.0.52 present (supports `Session.scalars`/`select`). |
| **#37** | **REWRITE** | Same idea as #33 but **collides on the exact new path** `backend/tests/test_schemas_common.py` (add/add). It carries cases #33 lacks (`loads_json` for list/int/bool; unicode `dumps_json` via `ensure_ascii=False`), so the right move is to fold those into the single adopted file, not to land two files. |
| **#38** | **MERGE** | Behaviour-preserving logging: `except ValueError as exc: logger.debug("Candidate JSON parsing failed: %s", exc)` and `logger.debug("Substring candidate JSON parsing failed: %s", exc)`, still ending in `raise SynthesisFormatError("answer is not parseable JSON")` at `synthesize.py:192`. New test drives the real `_extract_json("invalid json {also invalid}")` and asserts **both** debug messages are emitted, so it exercises the changed lines (not vacuous). |
| **#39** | **REWRITE** | Idea sound; overlaps #36 on the same `create_asset` hunk (`@@ -72,8 +72,11`) and lacks #36's dedup. Its **unique** contribution is `candidates.py:_create_asset_for_candidate` bulk insert (`db.execute(asset_evidence.insert(), [{...} for evidence_id in evidence_ids])`) at `@@ -904`. Fold that hunk into the #36 slice; do not land the duplicate `create_asset`/benchmark. Adds `backend/tests/benchmark_asset_evidence_insert.py`. |
| **#40** | **REWRITE** | **Defect (F3).** Restricting `allow_headers` is sound, but the allowlist omits `If-Match`: `["Content-Type","Authorization","Accept","Origin","X-Requested-With","Idempotency-Key"]`. The project's own frontend sends it: `frontend/src/components/shell/ItemInspectorDrawer.tsx:135` `apiPatch(\`/v1/assets/${asset.id}\`, payload, { household_id: householdId }, { "If-Match": String(current.version ?? 1) })` and `frontend/src/routes/AssetDetailPage.tsx:287` (same). Starlette (`starlette/middleware/cors.py:131-135`) fails any requested header not in the allowlist → `400 "Disallowed CORS headers"` for a cross-origin (dev, vite:5173) PATCH. Add `If-Match` (and rebase over #42). |
| **#41** | **MERGE** | `fetched_losers = db.query(Candidate).filter(Candidate.id.in_(loser_ids)).all(); loser_map = {loser.id: loser for loser in fetched_losers}`, then the same per-id loop with the identical checks: `None → 404`, `household_id != household_id → 403`, `state != "proposed" → 409`, blocking-task `count()` check, in the same order (`candidates.py:1237-1260`). Semantically equal to the base per-id `.filter_by(id=loser_id).first()`. |
| **#42** | **MERGE** | `allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"]` replaces `["*"]`. Covers every method the app uses; the only `ALL_METHODS` entry omitted is `HEAD`, which is CORS-safelisted (no preflight). New test asserts the exact response set and that `TRACE` yields `400 "Disallowed CORS method"` — matching Starlette `cors.py:124-148`. Confirmed correct. Overlaps #40 textually (same `main.py`/`test_cors.py` region). |

Verdict counts: **MERGE 7** (#32, #33, #35, #36, #38, #41, #42) · **REWRITE 4** (#34, #37, #39, #40) · **CLOSE 0**.
All findings are recommendations only; **nothing was merged, closed, or pushed except the worklog commit.**

## Overlap matrix (measured from the diffs, file + hunk level)

| cluster | measured | relation | implied resolution |
|---|---|---|---|
| asset-evidence batching | **CONFIRMED + expanded**: `backend/app/services/asset_service.py` hit by **#34, #36, #39** (three-way). #36 `@@ -71,9 +72,12` and #39 `@@ -72,8 +72,11` are the *same* `create_asset` evidence-link region; #34 `@@ -133,8 +136,13` and #36 `@@ -129,12 +133,23` are the *same* `attach_evidence` region. | **CONFLICT** (two overlapping regions) | MERGE **#36** first; REWRITE #39 (fold its `candidates.py` hunk); REWRITE #34 onto the bulk path. |
| CORS restriction | **CONFIRMED**: `backend/app/main.py:app.add_middleware` (#40 `@@ -34,7 +34,14`, #42 `@@ -33,7 +33,7`) **and** `backend/tests/test_cors.py:create_app_with_cors` + EOF. | **CONFLICT** (same region; complementary fields) | MERGE **#42** first; REWRITE #40 over it (add `If-Match`) — or land as one combined CORS slice. |
| schemas-common tests | **UNLISTED in packet**: #33 and #37 both **create** `backend/tests/test_schemas_common.py` (add/add). | **CONFLICT** | MERGE **#33**; REWRITE #37 (fold its unique cases into the one file). |
| candidates.py N+1 | #39 `_create_asset_for_candidate` `@@ -904` and #41 `merge_candidates` `@@ -1234` — same file, **different functions**. | **NO line conflict** | land both; #41 rebases after #39 (same file). |
| `.jules/bolt.md` | only **#32** touches it in this pile (single writer). | — | no journal-append conflict (unlike SG-133). |

## Safe merge order the verdicts imply (owner's SECOND word required; never executed here)

1. **#42** → then **#40** rebased with `If-Match` added (CORS pair; cannot land as-is in either order).
2. **#36** → then **#39** rebased (fold `candidates.py` hunk; drop the duplicate `create_asset`) → then **#34**
   rebased to log on the bulk path (or fold the logging into #36). #41 lands after #39.
3. **#33** → then **#37** folded/cloned into the single `test_schemas_common.py`.
4. Independent, any time: **#32**, **#35**, **#38** (and **#41** once #39 is settled).

Pairs that cannot land together as-is: {#40,#42}, {#34,#36}, {#36,#39}, {#33,#37}.

## Secret scan (`CO-100`) — scope and result

- **Scope:** `/tmp/opencode/sg149_diffs/pr-{32..42}.diff` — all **11** diffs, **32,814 bytes** total.
- **Patterns:** `api[_-]?key|secret|password|passwd|token|bearer|private[_-]?key|BEGIN [A-Z ]*PRIVATE KEY|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|github_pat_|sk-[A-Za-z0-9]{20,}|xox[baprs]-|-----BEGIN`.
- **Result:** 2 matching lines, **both in `pr-32.diff`**, and both the prose substring **"token"** inside
  "inverted **token** index" in the `.jules/bolt.md` journal text — **no credential-shaped string**.
  A second pass for base64/hex runs ≥40 chars returned only prose/filenames. **No secret found; no token
  printed.** (`CO-100` held.)

## Lessons (`G-L7` D336 shape — defect-fixing PRs only)

- **#32 / #39 / #41 (N+1 query defects).** Defect: per-row queries in `compute_status`,
  `create_asset`/`_create_asset_for_candidate`, `merge_candidates`. Why it survived: the project's tests
  assert *outcomes* (rows, statuses), never *query counts*, and no packet owned a "no N+1" gate — so a loop
  that issues one query per row is invisible to the suite.
- **#34 / #38 (swallowed exceptions).** Defect: `except Exception: pass` in `attach_evidence` and
  `except ValueError: pass` in `_extract_json`. Why it survived: before these PRs there was **no test** of a
  duplicate/failed attach (`grep -rIn "attach_evidence" backend/tests/` was empty) and the synth tests only
  assert the terminal `SynthesisFormatError`, so the silent branches were never entered or observed.
- **#40 / #42 (permissive CORS).** Defect: `allow_methods=["*"], allow_headers=["*"]` shipped from the
  scaffold. Why it survived: `test_cors.py` only asserted *origin* behaviour; nothing asserted the
  method/header allowlists, so the wildcard was unobserved. #40's own new defect (omitting `If-Match`) shows
  the bot allowlist was never checked against the frontend's real headers — there is no cross-origin
  preflight test on the `If-Match` path (frontend tests mock `fetch`).

## Findings / disagreements with the packet (reported, not bent)

- **F1 — enumeration method.** `gh` is unauthenticated (confirmed). I used the **unauthenticated public
  REST list** to distinguish *open* from closed, because `refs/pull/N/head` exists for closed PRs too; the
  prescribed pull-ref path fetched every diff. Disclosed as a design call; no token used, no login prompt.
- **F2 — overlap expectation incomplete.** Packet named {#36,#39} and {#40,#42}; measured also {#34,#36,#39},
  {#33,#37}, {#39,#41}.
- **F3 — #40 is functionally regressive** (missing `If-Match`) — quoted under the verdict.
- **F4 — #33/#37 are duplicate coverage** of the same module/path; union is best.
- **F5 — contract path.** `.rules-cache/` absent; live contract is `/home/andrei/storagegenie-contract`
  (restates SG-145).
- **F6 — benchmark scripts.** #36 adds `backend/scripts/benchmark_asset_evidence.py`; #39 adds
  `backend/tests/benchmark_asset_evidence_insert.py` (no `test_` prefix, so pytest does not collect it).
  The adopting slice should decide keep/drop; not a blocker.
- **F7 — self-correction (honest).** I hypothesised that #34's swallowed `IntegrityError` would leave the
  SQLAlchemy session needing rollback (`PendingRollbackError`). An isolated pure-SQLAlchemy probe
  (`/tmp/opencode/session_state_probe.py`, SQLAlchemy 2.0.52) **refuted it**: `caught: IntegrityError`,
  `commit after swallow: OK`. So #34's test is plausible; the diff's blocker is the #36 overlap, not a
  session-state failure. No test was run against the project (read-only).

## Acceptance criteria — assessed (`PG-SC-09`)

- **fetched — is every open PR's diff captured as bytes (or UNREADABLE with scope quoted)?** PASS. 11/11
  open PRs enumerated at runtime (API list + `ls-remote`), 11/11 diffs captured with byte counts + sha256,
  0 UNREADABLE. Scope quoted.
- **judged — does every PR carry exactly one verdict with quoted evidence?** PASS. 11 rows, one verdict
  each; each cites the hunk it rests on (quoted above). No PR judged without its fetched diff.
- **scanned — is the secret scan quoted over all diffs?** PASS. Scope (11 files, 32,814 bytes), pattern
  set, and result quoted; only benign "token index" prose matched.
- **clean — is the diff exactly worklogs?** PASS. The only added/changed files in the work commit are the
  3 `docs/worklogs/SG-149*` files; `git status --porcelain` is empty after (verify log).
- **No vacuous pass.** No empty diff was called a pass; every verdict quotes the changed lines; the secret
  grep is over all 11 diffs, not a subset; no merge happened.

## Receipt

- Work pushed to `automation`; worktree clean (`CO-55`). No `storagegenie-evidence` push, no
  `{{RECEIPT_CMD}}` (the Coder publishes the report note; the Architect publishes receipts).
- Note on `WORK_HEAD`, then `refs/notes/storagegenie-coder-reports` pushed and verified from a **mapped**
  fetch (`refs/notes/sg149-fetched`); executed output, verbatim:

```
{{WORKHEAD_SHOW}}
```

- Final tip dual-annotated (note-anchor inoculation, SG-092 precedent); mapped-fetch `show`, verbatim:

```
{{TIP_SHOW}}
```

## Budget — actual versus budget (units stated)

| Leg | Command class | Budget | Actual |
|---|---|---|---|
| G0 enumerate (`ls-remote` + public REST list) | ordinary | 120 s | < 10 s |
| G0 pull-ref fetch (11 heads, one call) | ordinary | 120 s | < 10 s |
| G0 byte diffs + hashes (11) | ordinary | 120 s | < 5 s |
| G1 source reads + local greps + secret scan | ordinary | 120 s | < 20 s |
| G2 worklogs + commit + push | ordinary | 120 s | < 10 s |
| Receipt notes (add/push/fetch/show, ×2) | ordinary / notes-push | 120 s / 300 s | < 15 s |
| **Overall** | — | **2400 s (lane `RUN_BUDGET_S=2100`)** | **wall-clock ≈ {{WALL}}** |

Actual-versus-budget per goal: G0, G1, G2 each well inside their 120 s class; overall well inside 2400 s.
**Real metered spend $0.000000 USD, zero metered calls.**

## UNCLEAR

- **FIRST READ:** the packet framed the pile as two overlaps ({#36,#39}, {#40,#42}) and a `gh`-unavailable
  read. First contact added two more overlaps ({#34,#36,#39} three-way; {#33,#37} add/add) and a real defect
  in #40 (`If-Match` omitted from its CORS allowlist).
- **DURING EXECUTION:** `gh` is unauthenticated as stated; pull-ref presence cannot distinguish open/closed,
  so the open-state fact came from the public REST list (design call, disclosed). All 11 diffs were
  reachable; no fetch was slow or killed.
- **REMAINING:** the verdict table needs the owner's SECOND word before any merge batch; #40 must gain
  `If-Match` and be rebased over #42; #34/#37/#39 need the fold-in rewrites; #33's file should absorb #37's
  extra cases. Nothing here closes a PR.

## RECOMMENDED-NEXT (merge-batch proposal the verdicts imply — not executed here)

For the owner's SECOND word. Each batch expects the project gates `make backend-test`
(`cd backend && python -m pytest -q`) and `make lint` (`python -m ruff check . && python -m mypy app`),
plus the file-scoped suites named.

- **Batch A — CORS (2 PRs, ordered):** **#42** then **#40 (rewritten** to add `If-Match` and rebase over
  #42**)**. Gates: `pytest tests/test_cors.py` + full suite + ruff/mypy.
- **Batch B — asset-evidence N+1 (3 PRs, ordered):** **#36**, then **#39 (fold `candidates.py` hunk;
  drop duplicate `create_asset`)**, then **#34 (log on the bulk path)**. Gates:
  `pytest tests/test_assets_crud.py tests/test_candidates*.py` + full suite + ruff/mypy.
- **Batch C — schemas tests (1 PR + fold):** **#33**, fold **#37**'s unique cases. Gate:
  `pytest tests/test_schemas_common.py` + full suite.
- **Batch D — independent (4 PRs):** **#32**, **#35**, **#38**, **#41**. Gates:
  `pytest tests/test_sg107_expiry_engine.py tests/test_sg099_synthesis.py tests/test_candidates*.py` +
  full suite + ruff/mypy.

**note=yes**

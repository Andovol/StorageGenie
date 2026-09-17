# SG-062 — money-integrity: error ledger rows keep usage the body actually carried (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** Phase 4 arc slice 2 (stage approved 2026-09-17, D83 — no second provider, one provider only). Purpose: close the ISS-11 residual family — ledger rows written for FAILED provider attempts understate or discard the usage/cost the response actually carried. Establish-or-fix framing: the defect direction below is a hypothesis with two corroborations; if your read proves the ledger is already right at a path, **not-a-defect on that path is a successful outcome** — document why; never manufacture a change. Recorded anchors (verify each in the tree, quote what you find):
- `backend/app/services/providers/opencode_go.py`: the adapter raises bare `ProviderError("invalid_json", "provider 200 with a non-JSON body")` at `:230` / `"provider 200 with a non-object body"` at `:232`, — these raise where a 200 BODY was received but no `usage`/`cost`/`latency` kwargs are attached to the exception; `:273` ("no choices") raises AFTER `guard_usage(body.get("usage"))` at `:270`, so usage is parsed and then dropped on that leg likewise; `:67` (empty content) and `:86`/`:90` (think-block) raise before usage parsing legitimately.
- `backend/app/services/providers/reader.py`: `_write_error_ledger` `:251-282` COMMITTED row carrying `getattr(exc, "usage"/"cost"/"latency_ms", None)` — it persists whatever the exception carries, `0.0`/absent when the attach is missing; `_mark_calls_failed` `:227-248` (SG-030 ISS-11 work, docstring quoted in the report); `_recorded_spend` `:210-224` sums committed rows for the monthly cap. The reader path needs NO hunk if the attach lands in the adapter — any reader logic hunk is a STOP-first finding.
- `backend/app/services/chat/service.py`: `_write_ledger` `:215-239` (success row, `error_state=None`) and `_write_error_ledger` `:242-267` — the error writer takes only `kind`/`message` and HARDCODES `cost=0.0`, `usage_json=None`, `latency_ms=None` (:259-261), so even when the caught exception carries usage it is dropped here. `backend/app/services/planning/service.py` mirrors this shape (expected `:215`-ish success at `:210`, error writer `:230` — verify the twin mirrors chat before mirroring the fix; quote lines).
- Corroborations from durable records (verify against the committed fixtures/ledger, do not build on my wording): SG-028 "failed calls never ledgered (error_state always NULL)"; SG-039 — the `glare` fixture failed `invalid_json` on both attempts and BOTH rows recorded `cost=$0.000000` (destination named "adapter-touching slice" since SG-029); ISS-11 CLOSED for returned-body rows (test pin at `tests/test_ai_pipeline.py:720ish` "schema_validation" rows keep real cost/usage + `error_state`).
**Authoring date (metadata, never a gate):** 2026-09-17. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published payload (tag `contract-v0.28.2`, `b495b59`, D82); **your host-side contract copy may be unreadable (F-SG056-3: `/home/andrei/launcher` was permission-denied for the Coder account at SG-061) — state WHICH contract version you read and its source path; an unanswered version echo is reported as such, never guessed.**
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** no migration; no new dependencies; no UI changes; no prompt/template changes; no provider calls — **$0, a metered call is a STOP-and-report**; results proven by deterministic scripted-provider tests with no network; NETWORK: loopback + container-runtime only, nothing else.
**Money posture (F2, unchanged):** spend UNCAPPED-but-ledgered with re-evaluation owed; this slice makes zero provider calls so the spend line reads $0.000000 actual vs $0 bound.
**Guards invoked (0.28.2 — Architect copies these to the rating row):** `PG-EV-01` gates-seen-fail · `PG-EV-02` artifact-not-command · `PG-EV-03` stop-not-disclosure · `PG-EV-05` property-not-command · `PG-EV-06` rows-your-run-creates · `PG-EV-09` fail-then-pass-committed · `PG-SC-01` write-path-first · `PG-SC-09` name-the-world · `PG-SC-10` no-ignored-commit · `PG-SC-11` tail-relative-assertions · `PG-SC-12` proof-on-the-real-thing · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-04` worst-case · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03` denied-is-stop · `PG-PR-04` live-proof-scoped · `PG-PR-06` runtime-vs-budget · `PG-DP-02` no-sweep-waiver.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none.** Tests use scratch temp SQLite; the production SQLite is touched by nothing. **Restart: none.**

## Why this exists

The ledger's single job is honest money provenance (F2: uncapped-but-ledgered). Three record paths handle failures today, and they disagree: the reader error writer preserves usage only when the raised exception carries it; the adapter drops usage on several raise legs where a 200 body WAS received; the chat/planning error writers hard-code $0. A parse-failed 200 can still be a billed completion — the SG-039 `glare` recurrence showed both its rows at `$0.000000`. Either the drops are real (rows understate spend and the monthly cap under-binds) or the ledger is already right; one slice establishes which, per path, with executable evidence.

## G1 — establish the current behavior on every failure leg (read + pin, quote-verbatim)

- Map every `ProviderError` raise leg in `opencode_go.py` (including transport/HTTP-status legs if any) into a table you report: **which legs have a received body or its bytes available at raise time** (usage could be carried) vs **which raise before any body** (honest `0.0`/absent). Quote each raise line with file:line.
- Quote the three record paths' handling today (`reader._write_error_ledger`, `reader._mark_calls_failed`, chat + planning `_write_error_ledger`) and state per path whether raised usage survives into the committed row.
- `PG-SC-12`, named: this establishment reads the REAL raise→record path (`opencode_go.py` → caught exception → record writer), and every costing assertion asserts the FIELDS that cross that boundary (what `exc` actually carries), never a fake's internal fields.

## G2 — fix where a body's usage is being dropped (scripted, deterministic)

- At each raise leg where body bytes are available but usage is not attached: attach `usage` (parsed or raw-parsed), the computed cost per `compute_cost` semantics already in that file, and latency to the raised `ProviderError` — so `reader._write_error_ledger` records them without a reader hunk.
- Chat + planning `_write_error_ledger`: thread the caught exception's usage/cost/latency into their signature and persist what the exception carries (`0.0` when absent — never invented); EXACTLY mirror the two writers' shapes; quote the planning twin verification.
- **Decimal rule:** preserve the usage/cost EXACTLY as the body carried it — never recompute, round, or fabricate; if the body's usage cannot be trusted, record it as carried and say why in the report.
- Every new/changed pin test is FAIL-then-PASS against the pre-change code (`PG-EV-09`): BOTH runs captured into the committed verify log — raw red quote + raw green quote, not prose.

## G3 — suite + lint + build (NO deploy)

- Derived test set (`0.28.2` test-set rule): **a hit is a FILE** — grep the test tree for assertions touching the raised shapes, `_write_error_ledger`, `_mark_calls_failed`, `error_state`, `usage_json`, `invalid_json`, `schema_validation`, and run EVERY node in each hit file that drives the changed code. Report the derived set vs your intuition.
- Backend suite + `ruff` + `mypy` delta-0 + frontend suite + `tsc && vite build` green; only base-proven pre-existing reds (cite base commit + recorded base-run; e.g. the 2 decoder env reds). Gates name files checked with counts+elapsed; silent gates FAIL.
- **NO DEPLOY, stated with reason (`PG-PR-04` scoped):** the changed behavior is failure-path ledger content, observable in production only on a live failing provider call; proving it live would bill a provider call purely to manufacture a failure — declined under the $0 posture. The next scheduled rebuild carries the change; no production-effect claim is made this slice beyond the tests.
- Prod DB untouched (state the construction); no migration; dep list unchanged; secret scan zero; no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.
- `PG-SC-09`: name the world where attaching usage to parse-failed rows is WRONG (e.g. the provider genuinely does not bill a failed parse — the row would overstate spend) and how the slice still ships (usage records what the body CARRIED, labelled; cost computed by the file's own existing `compute_cost` line, the same arithmetic the success path uses — the split is documented in both record writers, not invented).

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-062.log`, `{{WORKLOG_DIR}}/SG-062_report.md`, `{{WORKLOG_DIR}}/SG-062_verify.log` (raise-leg table + both runs of every FAIL-then-PASS). First token `SG-062`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend line (**real $** $0.000000 actual vs $0 bound); contract version echo + the source path read; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `backend/app/services/providers/opencode_go.py` (attach kwargs on raise legs; also any bare-`ProviderError` raise leg in the file's chat/planning extract path if it shares the shape — enumerate what you find) · `backend/app/services/chat/service.py` + `backend/app/services/planning/service.py` (error-writer hunks only) · `backend/app/services/providers/reader.py` (DOCSTRING only if the Coder needs one — no logic hunk; any logic hunk is a STOP-first finding) · backend tests (extend/new: pin tests for every fixed leg; say which files) · `docs/worklogs` (3 files). **Anything else is a STOP** — including `router.py`, `.env`, `docker-compose.yml`, `AGENTS.md`, prompts, migrations, frontend behaviour code.
- Every requirement above names a file the ceiling enables it; if you find one that does not, STOP and say which.
- Cross-product (`PG-IC-01`): the standing no-network line has one exception — the scripted-provider tests build NO real request at all, so nothing else forbids any criterion. **What would-cross-the-boundary coverage (`PG-EV-04`):** for the shapes that DID raise the dropped-usage legs, at least one test asserts what crosses the boundary — the exception's carried fields as handed to the record writer. Reads MAY pull/run the already-built local images only.
- Budget (uncalibrated per `G-A9`; this lane's backend error-path slices measured 28–140 s for small legs, suites ran under 600 s): 120s ordinary · 600s suite+lint+build · 1200s early-close · 1800s overall — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): attach-kwargs at the raise legs + two writer signature changes + tests; nothing else.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); premises re-verified in-slice with quoted reads — in particular the `opencode_go.py` raise legs, all three `_write_error_ledger`/`_mark_calls_failed` writers, the chat/planning twin mirror.
- Raise-leg table reported (leg, body-available?, carries usage? before/after); per-path verdict stated: defect fixed (FAIL-then-PASS raw in the committed verify log) or not-a-defect (evidence quoted).
- Committed rows on the scripted failing-with-usage leg carry the body's real usage + computed cost + `error_state` (quoted test + green run); success-path rows remain byte-identical in shape (no success-path hunk); pre-body legs still record honest `0.0`/absent (pin test).
- Suite + lint + build green (only base-proven reds); no-deploy reason stated; prod DB untouched; no migration; dep list unchanged; no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-062 | Report: docs/worklogs/SG-062_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), LIST the note contents and grep for this ID (log `--grep` does not match note bodies — proven twice), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint+build · 1200s early-close · 1800s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.

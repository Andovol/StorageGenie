# SG-057 — provision proof: backend-routed metered import E2E, one image (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** L3 stage D80 (consistency batch) slice 1 of 4: SG-057 provision-proof → SG-058 Untitled/split → SG-059 hygiene/port → SG-060 adapter caps. The owner set `SG_PROVIDER_ID=opencode-go` + recreated; `GET /v1/settings/ai` serves `provider_id=opencode-go, consent=true` (owner-pasted 2026-09-17). SG-049 proved the ADAPTER metered (direct call, $0.003630); SG-056 fixed the fake-path crash + deployed. NEVER PROVEN: the DEPLOYED BACKEND routes a real import through the metered adapter end-to-end. THIS slice proves exactly that with ONE image. **Authoring date (metadata, never a gate):** 2026-09-17. Transport: the standard job_spawn lane. Contract 0.27.0 (recorded == published payload == SG-056 receipt echo; packet states it).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** NO code hunks anywhere (pure live run — a diff outside `docs/worklogs` is a STOP); no migration; no new dependencies; NETWORK: loopback + the metered provider leg only (G2), nothing else.
**Money posture (F2):** spend UNCAPPED-but-ledgered with re-evaluation owed; every call commits its real cost/usage row surviving rollback (ISS-11); pre-call refusal (monthly cap) is respected — a refusal is a STOP-as-SUCCESS, never routed around. Stage 0 (F4): AI never auto-applies — candidates stay proposed for human review, always.
**Production-write authority (`PG-PR-10`):** production SQLite `sqlite:////data/db/storagegenie.db`, authorised by owner grant `D80` (L3 consistency batch, quote "L3 granted." with the provision-proof slice explicit). Scope: exactly ONE single-image import — job/evidence/candidate/ledger/audit rows reported with identifiers and LEFT in place. NO ACCEPT (never `POST /candidates/{id}/decision` — assets stay human-committed); anything beyond the §G2 delta table is a STOP-and-report.
**Guards invoked (0.27.0 — Architect copies these to the rating row):** `PG-EV-01` gate-seen-failing · `PG-EV-02` artifact-not-command · `PG-EV-05` property-not-command · `PG-EV-06` live-rows · `PG-DP-02` no-sweep-waiver · `PG-SC-03` read-before-stop · `PG-SC-09` name-the-world · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-04` worst-case · `PG-IC-07` no-fixed-dates · `PG-IC-08` blast-radius-is-stop · `PG-IC-09` premises-live · `PG-PR-03` denied-is-stop · `PG-PR-06` runtime-vs-budget · `PG-PR-10` which-database-plus-grant.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 900s for the import run (bounded below). A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: production SQLite `sqlite:////data/db/storagegenie.db` for the import ONLY (rows inherent and stay — `PG-PR-10`, D80); scratch temp SQLite for every test.**

## Why this exists

The metered adapter is proven (SG-049 G5) and the backend is configured (`opencode-go` + consent served live), but no backend-routed import has ever completed — the owner's live attempt hit the SG-056 crash, and every green run since was offline or direct-adapter. The failure mode this slice retires: provider selection / registry / budget-guard / candidate-plumbing breakage anywhere between the HTTP route and the ledger.

## G1 — pre-state capture FIRST (`PG-IC-08`, `PG-EV-08`)

- Starting tree quoted (clean expected; dirt = STOP first). Health exact. `GET /v1/settings/ai` quoted (expect `opencode-go` + `consent=true`; anything else = STOP-as-SUCCESS, zero spend).
- Blast baseline quoted from prod (counts only, no contents): asset/candidate/job/evidence/assertion/audit_event/provider_call counts + Toothpaste name. Ledger pre-existing rows listed by id. What does NOT count as grounds to stop: the `model_id` label value alone, per-job/per-month caps showing `null` (F2 uncapped by standing decision), frontend container state.
- Image pick: smallest-bytes food image in `backend/eval/corpus/sg029/images/` on the target (criterion — food preferred for lowest tokens; name it in the report). No other image is touched all slice.

## G2 — the import (bound FIRST, `PG-IC-04` worst case, `G-A9` uncalibrated)

- Bound FIRST: worst-case = 1 × the adapter's per-call estimate ceiling (compute in-slice from the estimator, quote the number); the runner's per-fixture guard enforces it; pre-call refusal (monthly cap) respected — refusal = STOP-as-SUCCESS with zero calls / zero rows. Overall import run bound 900s.
- Run the real HTTP path on loopback: `POST /v1/evidence` (multipart upload of the picked image) → `POST /v1/imports` (`evidence_ids`, fresh `Idempotency-Key` header — quote it) → `POST /v1/imports/{id}/run`, all with the household query. Quote every status + body.
- GO terminal state: job reaches AWAITING_REVIEW (or its exact success equivalent — state the observed state machine value) with ≥1 candidate in `review_state="proposed"` carrying extraction provenance. NO ACCEPT — never call the decision endpoint.
- Any other terminal state (FAILED at any step incl. ANALYZING_WITH_AI, unexpected state value) = finding with destination, NOT a Coder failure by itself: capture the step, the server error string, and the server-side log for that moment, then ship the report + receipt. A failed import still rates on evidence quality.
- Blast delta (`PG-IC-08` — expectations as diffs, never absolutes): job +1, evidence +1 (+1 stored file, quote id + hash), provider_call ≥1 (identifiers quoted, LEFT in place), candidate ≥1 all `proposed`, asset +0, Toothpaste name equal, all other tables equal. Anything else created = STOP-and-report. Ledger spend: cumulative actual vs the worst-case bound with units; every call's real cost/usage row surviving rollback (ISS-11 pattern).
- Secret handling: NO key bytes in any log, diff, or report (grep-gate the worklogs for key patterns before commit); `docker compose config` NEVER run.

## G3 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-057.log`, `{{WORKLOG_DIR}}/SG-057_report.md`, `{{WORKLOG_DIR}}/SG-057_verify.log` (per-call raw + import bodies raw). First token `SG-057`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend line (**real $** actual vs bound); three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `docs/worklogs/SG-057.log` + `docs/worklogs/SG-057_report.md` + `docs/worklogs/SG-057_verify.log`. **Anything else is a STOP** — including any backend/frontend file, prompts, eval, tests, `.env`, compose files, and any new dependency. Reads MAY run the already-built local containers only.
- Every requirement above names a file the ceiling enables it; if you find one that does not, STOP and say which.
- Cross-product (`PG-IC-01`): no blanket exclusion is issued. G2's STOP shares no condition with any remediation step — stops win (`PG-IC-03`).
- Test scope: no code changes, so no suite run — full sweep WAIVED explicitly per `PG-DP-02` (substitute = the quoted live import, named here). A gate emitting no tool output is a FAIL, not a PASS (`PG-EV-01` — every check pastes its raw output).
- Budget (uncalibrated per `G-A9`): 120s ordinary · 900s import run · 300s note push+verify · **1200s early-close** · **1800s overall** — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): one image, one import, one verdict; nothing else.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- `PG-SC-09`: name the world where the import succeeds yet the provision is still unproven (a fallback silently serving: e.g. deterministic-only path with zero provider calls and zero ledger rows — hence the acceptance REQUIRES ≥1 ledger row with real usage) and the inverse (import fails on image content, not wiring — hence server-log capture discriminates).

## Acceptance criteria

- G1 quoted read-only FIRST (settings + health + blast baseline); no provider call precedes it; STOP path pays $0.
- The import ran the real HTTP path with quoted statuses/bodies; verdict GO only with AWAITING_REVIEW + ≥1 proposed candidate + ≥1 real-usage ledger row, else a finding with step + server string + log.
- Blast delta exactly as tabled (diffs, either direction binds); Toothpaste equal; asset +0 (no ACCEPT — prove by the absence of decision-endpoint calls in the logs, not by assertion).
- Ledger rows reported with identifiers and LEFT in place; actual spend vs worst-case bound quoted with units; secret gate 0 hits quoted; `docker compose config` never run; no migration; nothing pushed to `storagegenie-evidence`; no ignored file staged; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Verdict line GO/STOP-as-SUCCESS/finding with the establishments quoted; spend **real $**.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-057 | Report: docs/worklogs/SG-057_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), LIST the note contents and grep for this ID (log `--grep` does not match note bodies — proven twice), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 900s import run · 300s note push+verify · 1200s early-close · 1800s overall; REAL metered $ (actual vs bound); actual-versus-budget per leg with units.

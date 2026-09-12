# SG-025 — Provider seam: ADR-004/007/010 + gateway + ledger + fake (opencode, medium)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Stage:** Phase 2 Slice 1 under D35 L3 (SG-025/026 cleared to fire; SG-027 alone waits on the Q2 key). This slice's approval IS D35 — no per-slice approval. Previous-slice UNCLEARs answered: SG-024's shm/wal `.gitignore` gap CLOSED by D33 (`ef60563` — verify live, don't re-litigate); `npm run build`-clean proof still queued (not this slice).
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; new migration heads update head-relative downgrade assertions (grep `downgrade`, list hits).

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.** (Owner standing requirement: the report quotes model provenance after EVERY slice.)

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, suite/migration legs name
> their own bound below. **A command producing no observable progress within its bound is killed and reported.**
> Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure
> to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none — temp SQLite only, zero live rows. Restart: none — no service touched, new code NOT deployed this slice** (`PG-PR-04`: proof scoped to in-process tests; the running service must not be touched).

## Why this exists

Blueprint §6 requires the provider abstraction before any cloud call; §3.3 requires every AI call ledgered (provider, model, prompt-template version, input hashes, output payload, cost/usage, latency, error state); SG-018 deferred ADR-004/007/010 to the Phase 2 door. Starting premises (verify live — `PG-IC-09`): zero provider code in tree (no gateway, adapter, prompt, or key under `backend/`); current migration head `20260908_sg017_fts`; backend suite green baseline; patterns to follow are `backend/app/models/audit_event.py` + `job.py` (TimestampMixin, `new_id`), migration `backend/alembic/versions/20260908_sg014_candidate.py` (create_table + downgrade), test header `backend/tests/test_health.py:1-14` (temp-DB env override before import).
Owner-settled decisions binding this slice (not re-decidable — dispute is a STOP, never a redesign): provider = OpenCode GO on its OWN subscription (Q1); spend uncapped for now but every call ledgered (F2); both users in, GPS-default-strip (F3); guardrail Stage 0, human confirmation mandatory (F4).

## G1 — gates + Q2 presence probe (Q2 is INFORMATION ONLY, never a gate)

- `git status --porcelain` quoted (clean expected — dirt is a STOP before all other goals).
- Live migration head quoted (expect `20260908_sg017_fts` — hypothesis); `python -m alembic heads` or versions-dir listing names the check.
- Full backend suite BASELINE (`venv/bin/python -m pytest -q`, bound 600s): green quoted, or pre-existing red cited with base-run proof per standing line.
- `.env` presence only (`CO-44` — never content).
- Q2 probe: `grep -c '^OPENCODE_API_KEY=' .env` count quoted. Count `1` means SG-027 is unblocked; `0` is REPORTED, never a STOP; the value is never printed, logged, or committed — a secret literal anywhere in tree/logs is a FAIL.

## G2 — provider surface, fake only (only if G1 passes)

- Create `backend/app/services/providers/` with `protocols.py` (four Protocols verbatim-shaped from blueprint §6.1: `VisionExtractionProvider.extract_items`, `OcrProvider.extract_text`, `EmbeddingProvider.embed`, `WebEnrichmentProvider.search_and_summarize`; results carry normalized output + raw payload + request id + usage/cost + model id + latency; sync-vs-async is your design call — decide and report), `router.py` (config-driven routing ONLY: provider id, fallback id, JSON-strictness, per-job cost budget, retryable-error set; NEVER quality-ranked; budget-exceeded refuses BEFORE any call), `fake.py` (scripted double, four shapes: valid / invalid-JSON-once-then-valid / needs_evidence / outage-raises-retryable).
- No real SDK, no key read, no network: any `httpx`/socket import under `providers/` is a STOP with the grep quoted (`PG-SC-05`: excluded by rule, grep-gated).

## G3 — call ledger (only if G1 passes)

- `backend/app/models/provider_call.py` (fields: provider, model, prompt-template version, input hashes, output payload, cost/usage, latency, error state, nullable job FK; TimestampMixin + `new_id` per `audit_event.py`/`job.py` pattern) + one-line export in `backend/app/models/__init__.py`. Production reader arrives SG-028 — the read-back THIS slice is the ledger query inside the G4 tests; state that explicitly (`PG-SC-02`).
- ONE new alembic migration (revision `20260912_sg025_provider_call`, down_revision = live head from G1): `upgrade head` + `downgrade -1` + `upgrade head` on TEMP SQLite quoted (bound 300s); tree-wide grep `downgrade` with hits listed, and any head-relative assertion this append breaks updated in-slice (`PG-SC-11`).

## G4 — contract tests on the fake (only if G2+G3 exist)

- `backend/tests/test_provider_gateway.py` proves: router picks configured provider; fallback fires on retryable error ONLY (non-retryable surfaces, no fallback); ledger row per call carrying every §3.3 field; budget-exceeded refuses pre-call with ZERO fake invocations; all four fake shapes green.
- FAIL-then-PASS (`PG-EV-01`/`PG-EV-09`): run the new tests PRE-change (expect FAIL: no-module/collection error), commit raw output to `docs/worklogs/SG-025_verify.log`, then POST-change green — BOTH runs quoted, fail run from the log not from prose.
- Full backend suite green-except-nothing (bound 600s); `ruff` clean on new files; `mypy` result quoted (40-advisory baseline known — a NEW error is a defect finding with a destination).

## G5 — ADR-004 + ADR-007 + ADR-010 (unconditional — no implementation without them)

- `docs/adr/ADR-004-*` (provider abstraction: capability interfaces, raw-response retention, routing/fallback config-not-code), `ADR-007-*` (privacy: both-users-in consent, GPS-default-strip, key lives in host `.env` 600 never in repo/logs, retention), `ADR-010-*` (guardrail Stage-0 rollout: mandatory human confirmation, no dosage automation). Each carries status + date + slice id.

## G6 — worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-025.log`, `{{WORKLOG_DIR}}/SG-025_report.md`, `{{WORKLOG_DIR}}/SG-025_verify.log` (both test runs, raw). First token `SG-025`; elapsed-versus-budget PER LEG with units; MODEL + effort provenance from process arguments (owner rule); live-state ledger (what runs now, what proved per goal, every stop with evidence, exact remaining delta if any).

## G7 — receipt note on the notes ref (proven SG-024 shape, unchanged obligation)

- Push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`.
- Note on the work HEAD LAST, no commit after (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-025 | Report: docs/worklogs/SG-025_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Verify with `show <WORK_HEAD>` and QUOTE executed output. Existing-note refusal is a STOP (never force-replace). Final line reads `note=yes`; zero-exit with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `providers/` new (3 files) + `provider_call.py` + `models/__init__.py` one-line export + ONE migration + `config.py` provider-routing settings ONLY if needed (else untouched with reason) + 3 ADRs + 1 test file + `docs/worklogs` (3 files). Anything else is a STOP with evidence. STOP beats retry itch — one L3 retry covers transients only, root cause or nothing.
- Cross-product (`PG-IC-01`): G2 needs only the blueprint shapes above; G3 only the model/migration pattern files; G4 only the fake; G5 only the embedded F-decisions; G1 only host gates + count probe. Recorded once.
- Secrets: names and counts only (`CO-44`, `PG-SC-05`). Privileged-denial: exact text, never route around (`PG-PR-03`).
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. No Coder-side SSH.
- Budget (`PG-PR-06`, uncalibrated per `G-A9`): 120s probes, 600s suites, 300s migration leg, 720s early-close, 900s overall — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): verify before asserting; no new checklists.

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first). Live head quoted (expected `20260908_sg017_fts` or finding explained).
- Q2 count quoted (0 reported, never a STOP; no secret literal anywhere — grep-gated).
- G2: four Protocols present verbatim-shaped; router refuses pre-call on budget; zero network imports under `providers/` (grep quoted).
- G3: ledger model + migration upgrade/downgrade/upgrade quoted on temp DB; `downgrade` grep hits listed, head-relative assertions intact.
- G4: pre-change FAIL + post-change green BOTH quoted from the committed verify log; four fake shapes green; full suite green-except-nothing or base-proved reds; ruff clean; mypy quoted.
- G5: all three ADRs committed with status/date/slice. MODEL + effort provenance quoted (owner rule). No vacuous pass.
- Worklog + report + verify log committed; notes ref carries `Dispatch-ID: SG-025` + `Report:`, quoted executed output, result `note=yes`.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments.

## Budget

120s probes, 600s suites, 300s migration, 720s early-close, 900s overall.

# SG-040 — Persist opened_date end to end (opencode, medium)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Stage:** Phase 3 slice added by owner decision `D47` (2026-09-14), under D46 L3. SG-038 landed (rated 98, work `a94397d`; live total $0.0009053). Closes SG-037 finding `F-SG037-3`: `opened_date` is extracted (SG-036) but NEVER written to an assertion, so the stage's exit bar "Cosmetics tracked with opened-date" is unmet. Runs BEFORE the SG-039 exit. **Authoring date (metadata, never a gate):** 2026-09-14. mypy advisory stands.
**Money posture:** **zero live calls in this slice** — all proofs offline on the scripted provider; any network attempt is a STOP. The metered cosmetics accuracy leg is SG-039's, not this slice's. Forks binding (dispute is a STOP): GO own-subscription (Q1) · uncapped-but-ledgered with re-evaluation owed (F2) · Stage 0 (F4).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no migration** (an alembic diff is a STOP — this is code only); frozen prompts are read-only context; `extract_items` behaviour must stay byte-identical; no live calls. Health probe: report against compose state — if no stack runs, `unanswered` with the compose/listen evidence is acceptable (starting a service is deploying, out of scope per the privileged-denial path).
**Guards invoked (0.23.0 step 2 — Architect copies these to the rating row):** `PG-EV-01` fail-then-pass · `PG-EV-02` artifact-exists · `PG-EV-05` property-not-command · `PG-EV-09` both-runs-committed · `PG-SC-02` config-readback · `PG-SC-05` rule-exclusion+grep · `PG-SC-07` no-data-bar · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03/04/06/10`.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine, investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a test that never invokes the function, a grep scoped so narrowly it could not have matched — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata, never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s backend suite, 600s `npm run build`, 600s vitest. A command producing no observable progress within its bound is killed and reported. Never run an interactive command.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean. Report every issue and disagreement, including ones outside this slice's scope. End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none — temp SQLite only, zero live rows. Restart: none — no service touched, nothing deployed. NETWORK: none** (`PG-PR-04`: proof is in-process tests; zero live calls; spend $0).

## Why this exists

Verified 2026-09-14 at SG-038's head: `ExtractionItem.opened_date` exists (`schemas.py:37`, SG-036) and the cosmetics taxonomy tracks it (`expiry_tracker.py` per-category flag), but nothing consumes it into storage —
- `build_candidate_from_extraction` maps only `display_name`/`expiry_date`/`lot` into candidate fields (`candidates.py:212-230`), and `opened_date` is not in `ALLOWED_CANDIDATE_FIELDS` (`:26-39`) nor `GATED_FIELDS` (`:25`), so even a hand-written field would be refused at commit (`:358-359`);
- the split-child builder replaces only `{display_name, expiry_date, lot}` (`:487`), so split children would drop it too;
- consumers read a value that never arrives: chat grounding reads `opened_date` from the plugin expiry assertion value (`chat/service.py:152-162`), and the planning catalog hardcodes `"opened_date": None` (`planning/service.py:144`).
Result: `opened_date` is always null downstream. This slice closes the chain: extraction → candidate → assertion → consumers.

## G1 — persist (candidates.py only)

- Add `"opened_date"` to `ALLOWED_CANDIDATE_FIELDS` AND to `GATED_FIELDS`. Gating rationale (record it in the report): dates are safety-critical per §5.2-7 and the design requires the same unknown-is-valid discipline as expiry dates — an opened date must be human-confirmed, never silently auto-accepted.
- In `build_candidate_from_extraction`, map `item.opened_date` into `fields["opened_date"]` with the SAME provenance envelope as the `expiry_date` block beside it (`:223-230`) — only when not None (no guessed values; a null opened date is simply absent, exactly like expiry).
- In the split-child rebuild, add `opened_date` to the item-derived key set (`:487`) and map it the same way as the existing `expiry_date`/`lot` items (per the SG-033 child shape).
- Frozen prompts, schemas, plugin, models: read-only context. If you find a fifth touchpoint, report it before touching (M6).
- Note the pre-check: no existing test pins the exact CONTENT of `GATED_FIELDS`/`ALLOWED_CANDIDATE_FIELDS` (grep checked 2026-09-14: only `test_phase2_e2e.py:287` reads `GATED_FIELDS` dynamically) — verify that in-slice and report any difference.

## G2 — consumers read the persisted value (chat + planning only)

- `chat/service.py` grounding (`:148-172`): the catalogue entry's `opened_date` must carry the asset's persisted opened date. The mechanism is yours — decide and report: read the asset's active `opened_date` assertion directly, or read it from wherever it lands (name the field_path you find/choose). Keep the existing expiry fields' behaviour unchanged.
- `planning/service.py` catalog (`:144`): replace the hardcoded `None` with the same read, so the planning prompt sees opened dates. `_backing_refs` (`:292-301`) optionally gains the opened-date assertion ref — decide and report.
- Backward compatibility: assets with no opened-date assertion (everything predating this slice) must behave exactly as today (null), proven by a test, not asserted in prose.
- Asset/candidate screens are GENERIC over assertions (`AssetDetailPage` assertions table, `CandidateCard.fieldInfo`) — verify that claim with a read, state the file:line, and do NOT build UI. If a screen turns out to filter fields by name, report it as a finding.

## G3 — proof

- FAIL-then-PASS raw for every new test (verify log; both runs committed). Minimum evidence set:
  1. An extraction carrying `opened_date` produces candidate `fields["opened_date"]` with provenance, `review_state` "proposed" (gated), and after accept an accepted `opened_date` assertion exists on the asset — assert the VALUE, not just presence.
  2. An extraction with `opened_date: None` produces NO `opened_date` field and NO assertion (never a guessed date).
  3. The split path: a split child whose item carries an opened date keeps it (mirror the existing split assertions).
  4. Chat grounding and planning catalog carry the persisted date for an asset that has it, and null for one that does not.
- Full backend suite from `backend/` (600s), `ruff` clean, `mypy` quoted (touched files add zero new errors — check the output list). `npm run build` green and `npx vitest run` (600s) green ONLY if any frontend file changes; if none changes, state the empty frontend diff instead of rebuilding (SG-035/036 precedent). Secret scan 0. No migration (prove the alembic diff empty), no frozen-prompt diff, no ignored file staged, zero network (prove it). Health probe per the standing line.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-040.log`, `{{WORKLOG_DIR}}/SG-040_report.md`, `{{WORKLOG_DIR}}/SG-040_verify.log` (both-runs raw). First token `SG-040`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line ($0); live-state ledger; three UNCLEAR lines.

## G5 — receipt note on the notes ref (proven shape, unchanged obligation)

Push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note on the work HEAD LAST, no commit after (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-040 | Report: docs/worklogs/SG-040_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`); verify with `show <WORK_HEAD>` and QUOTE executed output; existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `backend/app/services/candidates.py` (field lists + the two mapping sites) · `backend/app/services/chat/service.py` (grounding read) · `backend/app/services/planning/service.py` (catalog read) · `backend/tests/test_ai_pipeline.py` and/or `backend/tests/test_opened_date.py` (new — your call, name it in the report) · `backend/tests/test_chat.py` · `backend/tests/test_planning.py` · `docs/worklogs` (3 files). **Anything else is a STOP — including schemas, the plugin, models, migrations, frozen prompts, any UI, and any live call.**
- Every requirement above names a file the ceiling enables it (packet lesson M6) — if you find one that does not, STOP and say which.
- Money/privacy: zero spend; no key read; no network. Secrets: names and counts only (`CO-44`).
- Cross-product (`PG-IC-01`): G1 needs candidates.py + its tests; G2 the two consumers + their tests; G3 proves both offline. Timeouts are per-command-class (120/600/600/600), never one blanket bound. Recorded once.
- `PG-IC-03`: no remediation step in this packet shares a condition with a stop-gate — stops win by default; stated, not assumed.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. No Coder-side SSH. Full backend suite runs, so the §3 conditional derived-set block is NOT pasted.
- Budget (`PG-PR-06`, uncalibrated per `G-A9`): 120s probes, 600s suite, 600s build, 600s vitest, 1800s early-close, 2400s overall — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): reuse the exact `expiry_date` provenance/gating pattern; no new tables, no new field vocabulary, no new machinery.

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); every premise verified in-slice with quoted reads.
- An extraction-carried opened date reaches an accepted (user-confirmed) `opened_date` assertion after the candidate decision; a null opened date produces no field and no assertion anywhere.
- Split children preserve their item's opened date exactly as they preserve expiry/lot.
- Chat and planning grounding carry the persisted value for assets that have it; assets without it behave byte-identically to today (proven).
- `extract_items` behaviour unchanged; no migration; no frozen-prompt diff; the generic-rendering claim verified with file:line and no UI built.
- Suite green modulo the 2 known decoder env reds (base-proved premise — re-verify, do not inherit); `ruff` clean; touched files add zero mypy errors; secret scan 0; MODEL + effort provenance quoted; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: spend $0, network attempts 0 (proven), live DB writes 0.

## Budget

120s probes, 600s suite, 600s build, 600s vitest, 1800s early-close, 2400s overall.

# SG-027 — The one cloud adapter: vision spike first, then OpenCode GO (opencode, medium) — ATTEMPT 2

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Stage:** Phase 2 Slice 3 under D35 L3 + D36 (vision-spike-first, confirmed) + D42(a) (owner: model `lot` explicitly, re-spike once). Attempt-1 STOPPED clean (wrong-schema, rated 97): vision PROVEN live (HTTP 200, non-zero usage, label read correctly), content carried off-schema `lot` + `unknowns ["items.0.lot"]`. Attempt-2 closes exactly that gap, then builds the adapter on a green spike. Same slice ID with `--force` (replay bypass ONLY — a `Dispatch-ID: SG-027` receipt exists from the BLOCKED attempt-1; the flag changes nothing else). SG-025 + SG-026 landed 98. Forks still binding (dispute is a STOP): GO on its OWN subscription (Q1/F1); spend uncapped-but-ledgered, re-evaluation owed (F2); both users in, GPS-default-strip (F3); Stage 0 (F4). Q2 key in host `.env` (count 1 at attempt-1).
**Money facts (vendor docs, checked 2026-09-12 — supersede the old "estimate 0"):** vision model $15/mo included ($3/5h, $7.50/week); ~$0.15 per 1M input / ~$0.60 per 1M output off-peak (×2 at peak: 01:00–04:00 + 06:00–10:00 UTC Mon–Fri); images billed as input tokens by dimensions; attempt-1's call (868 in / 1361 out) ≈ $0.001. Ledger carries the COMPUTED figure per call, never 0-by-default. Privacy posture confirmed: model not trained on, 0-day retention.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; no migration expected — a `-1` that would unwind `sg025` is a STOP.
**Guards invoked (0.23.0 step 2 — Architect copies these to the rating row):** `PG-EV-01` fail-then-pass (10 banked PRE-FAILs turn POST-green + lot tests) · `PG-EV-02` artifact-exists · `PG-EV-03` stop-is-BLOCKED-commit · `PG-EV-04` shape-of-what-is-sent · `PG-EV-05` property-not-command · `PG-EV-09` both-runs-committed · `PG-SC-02` config-readback · `PG-SC-05` rule-exclusion+grep · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03/04/06/10`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, fixture legs 600s, the ONE live re-spike 300s single bound. **A command producing no observable progress within its bound is killed and reported.**
> Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure
> to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none — temp SQLite only, zero live rows. Restart: none — no service touched, nothing deployed** (`PG-PR-04`: proof is in-process tests + exactly ONE metered live call this attempt; cumulative live total = 2).

## Why this exists

Attempt-1 proved everything except schema compatibility: endpoint, Bearer auth, `json_object` on the vision model, 7.1s latency, usage shape, redaction, and the fact the model reads labels correctly AND volunteers a `lot` field. The strict schema forbids it, so honesty fails validation. D42(a) closes the gap by modeling `lot` explicitly (optional, never required, everything else still forbidden) and re-spiking once. Starting premises (attempt-1-verified, re-confirm cheaply — `PG-IC-09`): base `https://opencode.ai/zen/go/v1`, `POST {base}/chat/completions` `stream: false`, raw httpx NO SDK, model `deepseek-v4-flash-vision-exp`, Bearer auth, own UA + ONE stable session per conversation (never `pintel-*`, never per-call random), guards (empty-200 reject, non-zero usage, single-`<think>` strip then loud fail, `max_tokens` past truncation), 300s single live-call bound, key ONLY from backend env (value never printed/logged/committed, `CO-44`).

## G0 — schema fix + banked gates POST-green (first; all offline)

- Amend `providers/schemas.py`: add optional `lot: str | None = None` to the item (still `extra="forbid"` everywhere else; `unknowns` entries for `lot` honored exactly like other absent fields — null+listed passes, valued+listed fails). Small delta + reason quoted. Extend the contract tests by ONE `lot` test (null+listed ok, valued passes unlisted, valued+listed fails, non-string lot fails) — this delta to SG-026's test file is explicitly in-ceiling, reported.
- Turn the 10 banked PRE-FAILs green ONLY through building what they name (adapter per G2 — order inside G0/G2 is yours; the spike in G1 still gates SHIPPING, never building). Full suite runs from `backend/` (repo-root runs add the alembic CWD artifact — known harness shape, never cited as code failure).

## G1 — re-spike: EXACTLY ONE live call (only if G0 is green; gates first)

- Gates: `git status --porcelain` quoted (clean expected — dirt is a STOP); suite BASELINE from `backend/` (bound 600s): 76 passed + 2 known decoder reds + the 10 banked PRE-FAILs now POST-green (any OTHER red is a finding with a destination); `.env` presence only; Q2 count quoted (expect 1; 0 is a STOP, value never touched).
- Regenerate the synthetic label at RUNTIME (same recipe as attempt-1; never committed, never personal, never `/data/storage`). Pre-send redaction proof quoted (no EXIF/GPS on the exact buffer). Same headers (new stable session id for this attempt, e.g. `storagegenie-sg027-run2`), same `max_tokens` sizing; log header NAMES + stability, never values.
- GREEN = 200 + non-zero usage + content validates through the amended schema (lot honored). Quote model, latency, usage, COMPUTED cost (rate table above), validated shape. Any other outcome = STOP: `BLOCKED` commit + receipt with the scrubbed vendor response (`PG-EV-03`), no further live calls — cumulative total stays 2, never a third.

## G2 — the adapter (only on a green re-spike)

- New `backend/app/services/providers/opencode_go.py`: raw httpx, NO SDK (grep-gated STOP); the G1-verified facts only, never packet-inherited; identity-header builder (unit-tested offline); all guards; 300s call bound; header VALUES never logged.
- `backend/app/config.py`: named settings ONLY — provider id, model id (the single proven vision id; the future picker UI reads this setting — SG-031), key source (backend env only), per-job cost cap, monthly cap, consent flag. Env-overridable, logged when they bind. F2 encoded explicitly: mechanisms ship, enforcement values default disabled/uncapped with reason quoted (re-evaluation owed).
- `.env.example`: key NAMES only. Redaction helper shared (one function, tested offline). OUT: second provider, quality-switching, pipeline wiring (SG-028), UI (SG-031).

## G3 — proof (only on a green re-spike)

- Fixture tests NEVER live (header stability + prefix ban, format map, all guards on recorded shapes, redaction byte-proof, budget-refusal with zero calls, outgoing-payload shape with no key material). `PG-EV-04` on the wire shape.
- FAIL-then-PASS (`PG-EV-01`/`PG-EV-09`): the 10 banked PRE-FAILs + the new lot test POST-green, full raw runs committed; the live re-spike is single-run honesty (`G-A3`), quoted once. Full suite green-except-base-proved-reds (bound 600s, from `backend/`); `ruff` clean; `mypy` quoted. Read-back statement (`PG-SC-02`): every new config value read back in tests; PRODUCTION consumer SG-028.

## G4 — worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-027.log`, `{{WORKLOG_DIR}}/SG-027_report.md`, `{{WORKLOG_DIR}}/SG-027_verify.log` (offline both-runs raw + spike transcript: status/model/latency/usage/COMPUTED cost/validated shape — header values and key material NEVER included). First token `SG-027`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments (owner rule); spend line per live call; live-state ledger; three UNCLEAR lines.

## G5 — receipt note on the notes ref (proven shape, unchanged obligation)

- Push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`.
- Note on the work HEAD LAST, no commit after (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-027 | Report: docs/worklogs/SG-027_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Verify with `show <WORK_HEAD>` and QUOTE executed output. A duplicate-note refusal on the NEW head is impossible (new commit); refusal is a STOP (never force-replace). Final line reads `note=yes`; zero-exit with `note=no` is a FAIL.

## Constraints

- Scope ceiling: schemas.py `lot` delta + ONE lot test delta + `opencode_go.py` + redaction helper + `config.py` named-settings ONLY + `.env.example` names + fixture tests + `docs/worklogs` (3 files). ONE live call this attempt (TWO cumulative); a third cumulative call for any reason is a STOP with evidence. Anything else is a STOP. The L3 retry budget is spent by this attempt — a further failure STOPS to the owner, never a third run.
- Cross-product (`PG-IC-01`): G0 needs only schemas + banked tests; G1 only gates + count probe + runtime image; G2 only G1-verified facts; G3 only fixtures + the transcript. Recorded once.
- Secrets: names and counts only (`CO-44`); key value never in a logged variable — grep-gate. Privacy: synthetic image only; GPS-strip proven pre-send.
- Money: computed cost per live call (rate table above); budget-refusal proven offline; caps as F2-disabled mechanisms, stated. Nothing silently absent, nothing silently binds (`G-A8`).
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. No Coder-side SSH.
- Budget (`PG-PR-06`, uncalibrated per `G-A9`): 120s probes, 600s fixture legs, 300s single live spike, 1800s early-close, 2400s overall — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): verify before asserting; no new checklists.

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first). Attempt-1 facts re-confirmed cheaply or STOP with evidence.
- G0: `lot` modeled explicitly, everything else still forbidden (fabricated-value rule intact — prove with a valued+listed lot case); 10 banked tests identified as the POST leg.
- G1: EXACTLY ONE live call quoted (status/model/latency/usage/COMPUTED cost/validated shape) OR `BLOCKED` commit + receipt with scrubbed vendor response (cumulative total never exceeds 2).
- GREEN only: adapter + redaction + config (with model-id setting for SG-031) + `.env.example` as ceilinged; header values never logged; no SDK import (both grep-gated).
- Proof: banked PRE-FAILs + lot test POST-green BOTH quoted from the committed verify log; full suite green-except-base-proved-reds from `backend/`; ruff clean; mypy quoted. MODEL + effort provenance quoted (owner rule). No vacuous pass.
- Q2 count quoted (value never touched). Worklog + report + verify log committed; notes ref carries `Dispatch-ID: SG-027` + `Report:`, quoted executed output, result `note=yes`.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend lines for ALL live calls this slice (attempt-2: one).

## Budget

120s probes, 600s fixture legs, 300s single live spike, 1800s early-close, 2400s overall.

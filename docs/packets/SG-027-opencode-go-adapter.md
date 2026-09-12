# SG-027 — The one cloud adapter: vision spike first, then OpenCode GO (opencode, medium)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Stage:** Phase 2 Slice 3 under D35 L3 + D36 (vision-spike-first, confirmed). Approvals: D35 (stage) + D36 (amended order). SG-025 (seam) + SG-026 (prompts/schemas/eval, baseline 0.833) landed 98. Owner-settled forks binding this slice (dispute is a STOP, never a redesign): provider = OpenCode GO on its OWN subscription (Q1/F1); spend uncapped-but-ledgered with re-evaluation owed (F2); both users in, GPS-default-strip (F3); guardrail Stage 0 (F4). Q2 key placed in host `.env` (owner-confirmed 2026-09-12).
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; no migration expected — a `-1` that would unwind `sg025` is a STOP.
**Guards invoked (0.23.0 step 2 — Architect copies these to the rating row):** `PG-EV-01` fail-then-pass (offline gates) · `PG-EV-02` artifact-exists · `PG-EV-03` stop-is-BLOCKED-commit (no-vision STOP ships committed work + receipt, never prose alone) · `PG-EV-04` shape-of-what-is-sent (outgoing payload asserted pre-send) · `PG-EV-05` property-not-command · `PG-EV-09` both-runs-committed · `PG-SC-02` config-readback · `PG-SC-05` rule-exclusion+grep · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03/04/06/10`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, fixture legs 600s, the ONE live spike 300s. **A command producing no observable progress within its bound is killed and reported.**
> Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure
> to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none — temp SQLite only, zero live rows. Restart: none — no service touched, nothing deployed** (`PG-PR-04`: proof is in-process tests + exactly ONE metered live call).

## Why this exists

The seam (SG-025) and the strict schemas + eval baseline (SG-026) are proven on the fake. Exactly one cloud adapter ships in this slice — but the listed vision path is an UNPROVEN vendor listing, so the adapter is built ONLY after a live spike proves an image returns structured output (D36 fail-fast order). Starting premises, ALL relayed-not-proven, re-verify live in-slice before building on them (`PG-IC-09` — a relayed fact that fails live is a STOP, never inherited): base `https://opencode.ai/zen/go/v1`, `POST {base}/chat/completions` with `stream: false`, raw httpx NO SDK, vision model id `deepseek-v4-flash-vision-exp`, `json_object` for DeepSeek kin / `json_schema` elsewhere, identity headers (own `User-Agent` + ONE stable `x-opencode-session` per conversation — never `pintel-*`, never random-per-call), guards (reject 200-with-empty-content, require non-zero `usage`, strip ONE leading `<think>` then fail loudly, size `max_tokens` past truncation), timeouts 180s call / 60s wrapper, key ONLY from backend env `OPENCODE_API_KEY` (Q2 placed; `.env` presence-only per `CO-44`, value never printed/logged/committed).

## G0 — VISION SPIKE FIRST (fail-fast; nothing below starts on a red spike)

- Build the spike photo at RUNTIME: render a synthetic food/medicine label with PIL text (product name + a visible date + a blurred/partial region for one honest unknown) — deterministic, zero personal data. FORBIDDEN sources (G-K3 sensitive surface): `/data/storage`, `backend/data/`, any personal or household photo, any committed binary. No committed image exists in-tree (verified 2026-09-12: tests generate images at runtime) — do not commit one either (generated at runtime, never stored).
- Pre-send redaction proof (quoted): assert the outgoing bytes carry no EXIF/GPS (PIL check on the exact buffer sent) AND strip metadata by construction (re-encode stripped). Redaction failure is a STOP before any network call.
- Send EXACTLY ONE live call: the spike image + the SG-026 food prompt through the listed vision path, `max_tokens` sized past truncation, identity headers per the rule above (session id stable for this slice, e.g. `storagegenie-sg027-<run>` — one value, never per-call random, never another project's prefix; log header NAMES + the stability rule, never values).
- GREEN = HTTP 200 + non-zero `usage` + body parses as JSON validating through SG-026 `ExtractionOutput` (unknowns honored). Quote model id, latency, usage/cost (estimate, NOT billed truth), and the validated payload shape. Any other outcome (4xx/5xx/empty-200/zero-usage/unparseable/wrong-schema/unreachable-egress) = STOP: commit `BLOCKED: <vendor status + scrubbed body quoted>` + receipt (`PG-EV-03` — disclosure alone does not satisfy), worktree clean. The Phase 2 premise then returns to the owner (different provider or rescoped phase) — never a workaround, never a second live call, never a model-hunt across the catalog.

## G1 — gates (only if G0 green; report only)

- `git status --porcelain` quoted (clean expected — dirt is a STOP; prior quarantine refs are history, never adopt). Full suite BASELINE (bound 600s): green quoted or red cited with base-run proof (2 decoder env-reds known). `.env` presence only; Q2 count quoted (expect 1; 0 is a STOP — the spike cannot run without it — with the count quoted, value never touched).

## G2 — the adapter (only if G0 green)

- New `backend/app/services/providers/opencode_go.py`: raw httpx, NO SDK (any SDK import is a STOP with the grep quoted, `PG-SC-05`); `POST {base}/chat/completions`, `stream: false`; per-model `response_format` map as verified live in G0 (never inherited from this packet); identity-header builder (own UA + stable session; unit-tested offline for stability + no-`pintel`-prefix); guards exactly as listed above (empty-200 reject, non-zero usage, single-`<think>` strip then loud fail, `max_tokens` sizing); 180s call bound; header VALUES never logged (names only).
- `backend/app/config.py`: named settings ONLY — provider id, key source (backend env `OPENCODE_API_KEY`, never repo/log), per-job cost cap, monthly cap, consent flag. All env-overridable, logged when they bind. F2 posture encoded explicitly: cap MECHANISM ships, enforcement values default to disabled/uncapped with the reason quoted (re-evaluation owed) — mechanism without surprise.
- `.env.example`: key NAMES only, never values. Redaction helper (GPS-default-strip per F3/ADR-007) shared by spike and adapter — one function, tested offline.
- OUT: second provider/fallback, router quality-switching, pipeline wiring (SG-028), UI.

## G3 — offline gates + the single metered proof (only if G0 green)

- Fixture tests (NEVER live): header builder (stability + prefix ban), response-format map, all four guards against recorded vendor-shaped fixtures (empty-200, zero-usage, `<think>`-prefixed, truncated), redaction helper (GPS-bearing input → stripped output, byte-proven), budget-refusal at a tiny cap with zero calls. `PG-EV-04`: assert the SHAPE of the outgoing payload (endpoint, fields, no key material) without sending.
- Live proof: the G0 spike IS the smoke (no second live call — cost discipline). Cost printed from the response usage (estimate). FAIL-then-PASS (`PG-EV-01`/`PG-EV-09`) applies to the OFFLINE gates (PRE FAIL + POST green, both raw runs committed); the live spike is single-run honesty (`G-A3`), quoted not repeated.
- Full suite green-except-base-proved-reds (bound 600s); `ruff` clean; `mypy` quoted (untouched-file advisories are findings with destinations). Read-back statement (`PG-SC-02`): every new config value is read back in tests; the PRODUCTION consumer arrives SG-028.

## G4 — worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-027.log`, `{{WORKLOG_DIR}}/SG-027_report.md`, `{{WORKLOG_DIR}}/SG-027_verify.log` (offline both-runs raw + the spike transcript: status, model, latency, usage/cost, validated shape — header values and key material NEVER included). First token `SG-027`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments (owner rule); live-state ledger; three UNCLEAR lines.

## G5 — receipt note on the notes ref (proven shape, unchanged obligation)

- Push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`.
- Note on the work HEAD LAST, no commit after (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-027 | Report: docs/worklogs/SG-027_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Verify with `show <WORK_HEAD>` and QUOTE executed output. Existing-note refusal is a STOP (never force-replace). Final line reads `note=yes`; zero-exit with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `opencode_go.py` + redaction helper (inside it or one small module with quoted reason) + `config.py` named-settings ONLY + `.env.example` names + fixture tests + 1 test file for offline gates + `docs/worklogs` (3 files). ONE live call TOTAL (G0); a second live call for any reason is a STOP with evidence. Anything else is a STOP. One L3 retry covers transients only, root cause or nothing.
- Cross-product (`PG-IC-01`): G0 needs only the relayed endpoint facts + a runtime-rendered image; G2 only the G0-verified facts; G3 only fixtures + the G0 transcript; G1 only host gates + count probe. Recorded once.
- Secrets: names and counts only (`CO-44`); the key value is never read into a variable that gets logged — grep-gate `OPENCODE_API_KEY` to one config line + the count probe. Privacy: no personal image exists in this slice by construction; GPS-strip proven pre-send.
- Money: every live call prints usage/cost (estimate); budget-refusal proven offline; monthly/per-job caps exist as mechanisms with F2-disabled values stated. No cap is silently absent and none silently binds (`G-A8`).
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. No Coder-side SSH.
- Budget (`PG-PR-06`, uncalibrated per `G-A9`): 120s probes, 600s fixture legs, 300s single live spike, 1800s early-close, 2400s overall — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): verify before asserting; no new checklists.

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first). Relayed facts re-verified live or STOP with the vendor evidence quoted.
- G0: EXACTLY ONE live call quoted (status/model/latency/usage-validated-shape) OR a `BLOCKED` commit + receipt with the scrubbed vendor response (no second call, no workaround, no model-hunt).
- G0 GREEN only: adapter + redaction + config + `.env.example` as ceilinged; header values never logged (grep-gated); no SDK import (grep-gated); caps exist with F2-disabled values stated.
- G3: offline gates PRE FAIL + POST green BOTH quoted from the committed verify log; live proof is the G0 transcript (not repeated); full suite green-except-base-proved-reds; ruff clean; mypy quoted. MODEL + effort provenance quoted (owner rule). No vacuous pass.
- Q2 count quoted (0 = STOP, value never touched). Worklog + report + verify log committed; notes ref carries `Dispatch-ID: SG-027` + `Report:`, quoted executed output, result `note=yes`.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger includes the spend line (model, latency, usage/cost-estimate).

## Budget

120s probes, 600s fixture legs, 300s single live spike, 1800s early-close, 2400s overall.

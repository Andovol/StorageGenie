# SG-101 — Text-path token bound + empty-content accounting, one live proof call (opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D140-approved fix (owner quote "D140 - approved.") for F-SG099-1, slice 3 of the D139 L3 Arc A (SG-099 PARTIAL-live → SG-100 GREEN → fix+live-proof → live re-confirms + reviewer alternatives; D141: run to completion, no per-slice words). SG-099 proved the metered TEXT path unusable as configured: reasoning burn exhausts `DEFAULT_MAX_TOKENS=2000`, `content` arrives empty, `guard_content` rejects — billed but unledgered. Re-verified by the Architect 2026-09-23, re-verify: `build_text_payload` hardcodes `"max_tokens": DEFAULT_MAX_TOKENS` (`opencode_go.py:187-195`); `extract_text`'s empty-content raise carries NO accounting (`:374` bare `guard_content`, while the no-choices leg at `:369-371` attaches via `attach_body_accounting` — the SG-062 mechanism, `:104-120`); `guard_content`'s docstring (`:64-72`) claims empty-200 legs are unbilled, which SG-099's leg-2 usage disproves. THIS slice fixes both + proves the path with exactly one capped synthesis live call (which also closes SG-099's live leg). **Authoring date (metadata, never a gate):** 2026-09-23. Transport: the standard job_spawn lane. Contract: recorded `0.33.0` == published (`b232b84`; D129 adoption, G-L1 clean 2026-09-23); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** text path ONLY. The vision path keeps `DEFAULT_MAX_TOKENS` untouched (`test_opencode_go.py:135` pins it ≥1500 — that pin must stay green untouched). No synthesis-prompt/caller behaviour change (read-only except the estimate hunk below), no persistence/endpoint/UX, no deploy, no restart, no container action — the running service is untouched; the adapter change goes live on a later owner-gated rider (`PG-PR-04`). Exactly ONE metered TEXT call ≤$0.05 worst-case; no other network. Key NAMES only; `docker compose config` FORBIDDEN (`PG-SC-05`).
**Money posture:** REAL metered spend, ONE call, ≤$0.05 worst-case binds (`PG-IC-04`), actual-vs-budget with units (`PG-PR-06`).
**Guards invoked (0.33.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-06` · `PG-EV-09` · `PG-SC-05` · `PG-SC-06` · `PG-SC-10` · `PG-IC-01` · `PG-IC-03` · `PG-IC-04` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint, 60s per live call, 1500s early-close, 2100s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none** (no migration; the ONE live call runs on a temp DB per the SG-080 precedent and live counts read back identical before/after via a read-only query, `PG-EV-06`). **Restart: none. Deploy: none. Container actions: none** (`PG-PR-04`).

## G0 — consent/key-name gate (read-only, NAMES only)

- `ai_status()` enabled + provider key NAME present before any metered touch. Closed gate → live leg UNEXECUTED with the named reason, rest ships (SG-082 precedent; stopping there is SUCCESS for the remainder). STOP beats retry itch (`PG-IC-03`) — the one L3 retry covers transients only (zero commits + clean tree + transient signature, SG-084/090/091 precedent), never a routed STOP.

## G1 — separate text-turn bound (vision constant untouched)

- New constant `TEXT_MAX_TOKENS = 8000`, used by `build_text_payload` INSTEAD of `DEFAULT_MAX_TOKENS` (which stays exactly as-is for every other path). Derivation, uncalibrated (`G-A9`, Architect act per §2b): sample window n=1 — SG-099 leg 2 burned the full 2000-completion budget on reasoning with zero content bytes; 4× headroom for reasoning+content. Cost when it binds: worst-case text call ≈ (4000 input-upper-bound × 0.15 + 8000 × 0.60)/1e6 ≈ **$0.0054**, ~9× under the $0.05 per-call cap — recompute in-slice from the real `compute_cost` and report actual-vs-bound. FIRST establish which builder the vision path uses — if it shares `build_text_payload`, the split point moves there (decide and report; the load-bearing fact is which call sites reach the function you change).
- Joint caps statement (`PG-SC-06`): per-call $0.05 (synthesis + endpoint) + monthly ledger + adapter direct guards + router `cost_budget` — the new bound raises the text worst-case to ≈$0.0054 and moves NOTHING else; monthly posture unchanged.

## G2 — empty-content accounting (close the unledgered gap)

- The `:374` empty-content raise attaches body accounting EXACTLY like the `:369-371` no-choices leg (`attach_body_accounting(exc, usage, latency_ms)` — usage already in scope from `:366`), so a billed empty-200 always lands a `ProviderCall` row via the existing SG-030 `_write_error_ledger` contract. Correct the `guard_content` docstring's false unbilled claim (`:64-72`) in the same hunk, disclosed.
- `synthesize.py`'s `estimate_text_cost` MUST cover the new bound or the cap it guards is blind: wire `max_tokens=TEXT_MAX_TOKENS` for text-turn estimates (the one existing-file hunk outside `opencode_go.py`; needs failing-test proof — a test showing the old default understates a text-turn worst case — minimal + disclosed, M45, else STOP).

## G3 — tests + gates + the ONE live proof call

- New `backend/tests/test_sg101_text_path.py` (fail-then-pass, BOTH raw runs committed, `PG-EV-09`; seen-to-fail in-run, `PG-EV-01`): text payload carries the new bound while the vision constant is byte-untouched (assert `DEFAULT_MAX_TOKENS == 2000` + payload value); empty-content body with non-zero usage raises WITH usage/cost/latency attached (extend the `:333` raise-legs shape to the content leg); estimate covers the new bound (cap comparison binds); existing `test_opencode_go.py` + `test_chat.py` green unmodified (vision behaviour byte-identical).
- The ONE live call (60s bound): the SG-099 synthesis caller over fixture OFF+Jina through the FIXED path on a temp DB — EXPECTED to complete now. Quote cost/usage/model/latency + actual-vs-budget; a differently-shaped failure is a finding (report the body class), never a second call. Raw-body recorder on from leg 1 (SG-099 lever). Production counts identical before/after (read-only).
- Full suite green modulo the 2 known decoder env reds (stash-proved), ruff clean, mypy delta 0, secret gate 0 real.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-101.log`, `SG-101_report.md`, `SG-101_verify.log` (raw outputs + BOTH fail-then-pass runs + every gate + the live-call capture). First token `SG-101`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** actuals); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `opencode_go.py` hunks (bound + attach + docstring) + `synthesize.py` estimate hunk (M45 terms) + new test file + `docs/worklogs` (3 files) — NOTHING else. Ordered paths committable (`.gitignore` verified 2026-09-23, `PG-SC-10`).
- Cross-product (`PG-IC-01`): no criterion demands persistence, endpoint wiring, deploy, restart, container acts, vision-path changes, or a second metered call beyond the authorized retry — no cell collides; stated so the check exists on paper. Reads include TestClient + host commands only; pulling/running images or launching unnamed runtimes counts as execution — not authorised.
- Privacy: fixture TEXT only; key never in any file, log, or assertion (`PG-SC-05` by rule, literal grep-gate quoted).
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- Text payload carries the new bound; `DEFAULT_MAX_TOKENS` byte-untouched with its pin green; empty-content raise carries usage/cost/latency; estimate covers the new bound; worst-case recomputed ≈$0.0054 ≪ cap with joint caps stated.
- Tests fail-pre/pass-post both committed raw; gates green; vision tests unmodified-green.
- ONE live synthesis call completes with quoted actuals inside $0.05 on temp DB (or fails in a NEW disclosed shape with no second call); production counts identical; $0 otherwise; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** actuals. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-101 | Report: docs/worklogs/SG-101_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint · 60s per live call · 1500s early-close · 2100s overall; REAL metered ONE call ≤$0.05 worst-case (expected ≈$0.005 worst-case, <$0.002 expected); actual-versus-budget per leg with units.

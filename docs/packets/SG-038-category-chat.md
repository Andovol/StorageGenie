# SG-038 — Category chat (Food, then Medicine), grounded, with the adapter text op (opencode, medium)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Stage:** Phase 3 Slice 7 under D46 L3. SG-037 landed (rated 98, work `b7bd863`; live total now $0.000722). Plan: `docs/superpowers/plans/2026-09-14-phase-3-usability-then-agents.md` Slice 7. **Authoring date (metadata, never a gate):** 2026-09-14. **Ordering note:** SG-040 (opened-date persistence, from SG-037 finding F-SG037-3) runs after this slice and BEFORE the SG-039 exit; SG-039 stays last. mypy advisory stands.
**Money posture:** **ONE metered live run under a $0.05 ceiling** (SG-029/037 shape: ceiling printed and checked before the run, per-call model/latency/usage/cost quoted, key from the host environment only, never logged). All behaviour proofs offline on the scripted provider first; any SECOND live run, or spend past the ceiling, is a STOP. Forks binding (dispute is a STOP): GO own-subscription (Q1) · uncapped-but-ledgered with re-evaluation owed (F2) · GPS-default-strip (F3) · Stage 0, human confirmation mandatory regardless (F4).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no migration** (an alembic diff is a STOP); frozen extraction prompts (`extract-food-v1.md`, `extract-medicine-v1.md`, `extract-cosmetics-v1.md`, `planning-v1.md`) are read-only context; `extract_items` behaviour must stay byte-identical (the SG-028/029 extraction tests are the rail); only the ONE stated live run. Health probe: report against compose state — if no stack runs, `unanswered` with the compose/listen evidence is acceptable (starting a service is deploying, out of scope per the privileged-denial path).
**Guards invoked (0.23.0 step 2 — Architect copies these to the rating row):** `PG-EV-01` fail-then-pass · `PG-EV-02` artifact-exists · `PG-EV-04` shape-of-what-is-sent · `PG-EV-05` property-not-command · `PG-EV-09` both-runs-committed · `PG-SC-02` config-readback · `PG-SC-05` rule-exclusion+grep · `PG-SC-07` no-data-bar · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03/04/06/10`.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine, investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a test that never invokes the function, a grep scoped so narrowly it could not have matched — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata, never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s backend suite, 600s `npm run build`, 600s vitest. A command producing no observable progress within its bound is killed and reported. Never run an interactive command.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean. Report every issue and disagreement, including ones outside this slice's scope. End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: temp SQLite ONLY — zero live rows; the production DB is never opened for writing. Restart: none — no service touched, nothing deployed. NETWORK: exactly ONE metered live run** under the ceiling below (`PG-PR-04`: the running service is not touched; the live leg is a metered test leg against a temp DB, `PG-PR-06` bounds it).

## Why this exists

The seam declares a text capability but the real adapter does not implement it: `protocols.py:34-37` declares `extract_text`, the fake implements it, and `opencode_go.py` implements ONLY `extract_items(image_bytes, prompt)` (`:216`). SG-037 had to carry a 1×1 PNG to reach the model at all (F-SG037-1) — a carrier that cannot express a chat. Chat therefore needs a REAL text operation, and the router already dispatches by operation name (`router.execute("extract_text", ...)` → `getattr(provider, op)`, `router.py:52-72`), so no routing change is needed. No chat service, route, screen or prompt exists.

## G1 — the adapter text operation (the one seam change)

- `opencode_go.py`: implement `extract_text(text, prompt, *, estimated_cost=0.0)` on the real adapter, mirroring `extract_items`'s guards EXACTLY: pre-call per-job + monthly refusal, identity headers, 200/envelope checks, `guard_usage`, `strip_single_think`/`guard_content`, cost computed from usage, `ProviderResult` populated (model/latency/usage/cost/raw payload). Differences from `extract_items`: no image, no base64, no `parse_extraction_output` (the normalized output is the text plus the payload's metadata — decide the exact shape and report it). Payload built by a text builder beside `build_chat_payload` (message list, `stream: false`); **`PG-EV-04`: one offline test asserts the SHAPE of what would have been sent** (roles, content, model, no image part, no key material).
- `protocols.py`: only if the declared `extract_text` signature must be clarified — say so and why; no new protocol, no new vocabulary.
- `fake.py`: a scripted text response so every offline test runs with zero network.
- **Regression rail:** `extract_items` and the extraction pipeline behaviour must be byte-identical — the existing extraction/provider tests are the proof; a red there is a STOP, not a re-baseline.
- `reader.py`: NOT in scope unless a shared helper genuinely needs extracting — if you find it does, STOP and say which helper and why (M6).

## G2 — chat service + routes, grounded and Stage 0

- New `backend/app/services/chat/` + `backend/app/api/v1/chat.py` (register beside the v1 routers in `main.py`) + one versioned prompt file `backend/app/services/providers/prompts/chat-v1.md` (same front-matter discipline as the extraction prompts; never edited in place afterwards).
- Load-bearing facts (verify in-slice): consent is gated by `reader.ai_status()` before any provider object is built (`reader.py:97-101`) and the SG-037 route calls it the same way; planning already wrote `guardrail_event` rows with writers live in `backend/app/services/planning/service.py`; the per-call ledger row shape is `reader._write_ledger`/`_write_error_ledger`.
- Behaviour: `POST /v1/chat/{category}` takes the user message (+ category; Food and Medicine are the supported values — an unsupported category is an enforced `422`); the server builds the grounding context from that category's catalogue (assets + their expiry/opened assertions + source attributions when present), sends it through the seam as DATA, and returns the assistant text. **No consent → refuses before any call (0 invocations, 0 rows).** Empty category data → a valid answer path (say what it returns), not an error (`PG-SC-07`).
- **Cross-category refusal:** a question about the other category is not silently answered from the wrong data — the supported set is enforced server-side (`PG-SC-07`: state the smallest case and its behaviour).
- **Corrections → guardrail log:** an explicit `POST /v1/chat/{category}/corrections` (or an equivalently named explicit action) writes an append-only `guardrail_event` of kind `correction` carrying the message + category. **The write is user-initiated, never model-triggered** — untrusted model output must not be able to cause a write by itself; prove that with a test (`§12` posture).
- **Prompt-injection posture:** catalogue text is untrusted DATA, never instruction content (`§12.2`). The grounding builder places it in a delimited data section; a structural test asserts a hostile string in an asset name stays inside that section and never lands in an instruction position.
- No execution path: suggestions/answers change no asset, job or setting — prove it (catalogue bytes identical before/after a chat call), exactly as SG-037 did.

## G3 — chat screen

- New chat route + component (react-query/`apiPost` pattern) registered in `frontend/src/App.tsx` (nav + route — **in the ceiling this time, per M10**), with category selection (Food/Medicine), a transcript held in component state, the input, a "log correction" action, and clear display of the refusal reason when the call is skipped. **No schedule, no auto-send, no streaming** — out of scope.
- Frontend tests beside the new files (send → reply rendered; correction action posts; skipped/unavailable surfaces its reason; unsupported category). Pre-change fails (route/screen absent) — quoted raw with the post-change pass.
- `PG-SC-02`: the correction action traced screen → route → guardrail row asserted in a backend test; the grounding data traced catalogue → prompt → response path.

## G4 — proof: offline behaviour + ONE metered live run

- Offline (scripted provider, zero network, `_post` patched to raise): text op payload shape (`PG-EV-04`); chat grounded answer; no-consent refuses 0 calls/rows; unsupported category 422; empty data path; correction writes a `correction` event; model output cannot trigger a write; catalogue bytes identical before/after; injection string stays inside the data section. FAIL-then-PASS raw, committed.
- Live leg (exactly ONE, last): print the `$0.05` ceiling and check before the run; `SG_CONSENT=true`; key from host env, never logged; per-call model/latency/usage/cost quoted; exactly one ledger row; total quoted against the ceiling. Any second live run, ceiling breach, or key material in output is a STOP.
- Full backend suite from `backend/` (600s), `ruff` clean, `mypy` quoted (touched files add zero new errors — check the output list). `npm run build` green (quoted), `npx vitest run` (600s) green. Secret scan 0. No migration (prove the alembic diff empty), no frozen-prompt diff, no ignored file staged. Health probe per the standing line.

## G5 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-038.log`, `{{WORKLOG_DIR}}/SG-038_report.md`, `{{WORKLOG_DIR}}/SG-038_verify.log` (both-runs raw + the live receipt). First token `SG-038`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line (live total + $0 offline); live-state ledger; three UNCLEAR lines.

## G6 — receipt note on the notes ref (proven shape, unchanged obligation)

Push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note on the work HEAD LAST, no commit after (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-038 | Report: docs/worklogs/SG-038_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`); verify with `show <WORK_HEAD>` and QUOTE executed output; existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `backend/app/services/providers/opencode_go.py` (text op + its payload builder only) · `backend/app/services/providers/protocols.py` (signature clarify ONLY if needed) · `backend/app/services/providers/fake.py` (scripted text response) · `backend/app/services/providers/prompts/chat-v1.md` (new) · `backend/app/services/chat/` (new) · `backend/app/api/v1/chat.py` (new) · `backend/app/main.py` (registration only) · `backend/tests/test_chat.py` (new) · `frontend/src/App.tsx` (route + nav registration only) · `frontend/src/routes/` chat screen (new) + beside test · `frontend/src/components/` chat components (new, only if the screen needs them) + beside tests · `frontend/src/api/client.ts` · `frontend/src/api/types.ts` · `docs/worklogs` (3 files). **Anything else is a STOP — including `reader.py`, `router.py`, migrations, the SG-035 models, the frozen prompts, and any scheduling/streaming. ONE live run only.**
- Every requirement above names a file the ceiling enables it (packet lesson M6) — if you find one that does not, STOP and say which.
- Money: exactly one live run under the printed $0.05 ceiling; per-call cost quoted; nothing else metered. Privacy: key from host env only, never logged/printed; the prompt carries catalogue data only.
- Cross-product (`PG-IC-01`): G1 needs the adapter text op + fake + protocol; G2 the service + routes + prompt + main.py; G3 the screen + App.tsx + client; G4 proves all three offline then the single live leg. Timeouts are per-command-class (120/600/600/600), never one blanket bound. Recorded once.
- `PG-IC-03`: no remediation step in this packet shares a condition with a stop-gate — stops win by default; stated, not assumed.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. No Coder-side SSH. Full backend suite runs, so the §3 conditional derived-set block is NOT pasted.
- Budget (`PG-PR-06`, uncalibrated per `G-A9`): 120s probes, 600s suite, 600s build, 600s vitest, $0.05 single live run, 1800s early-close, 2400s overall — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): reuse the router's op dispatch, the `extract_items` guard shape, the SG-037 route/screen patterns; no new protocol, no new machinery.

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); every premise verified in-slice with quoted reads.
- The real adapter implements a text op with the same guards as `extract_items`; its payload shape is asserted offline with no image part and no key material; `extract_items` behaviour unchanged (existing extraction/provider tests green — a red is a STOP).
- Chat answers are grounded in the requested category's data; unsupported category is an enforced `422`; a cross-category question is not answered from the wrong data; no consent makes 0 calls and 0 rows; empty data is a stated valid path.
- A correction is written ONLY by the explicit user action; untrusted model output cannot cause a write; a hostile string in catalogue data stays inside the data section.
- Chat answers change no catalogue state (bytes identical before/after).
- Live leg: exactly one run under the printed ceiling with per-call figures quoted and one ledger row; total stated; zero key material anywhere.
- Suite green modulo the 2 known decoder env reds (base-proved premise — re-verify, do not inherit); `ruff` clean; `npm run build` green (quoted); secret scan 0; MODEL + effort provenance quoted; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: live spend total (quoted), offline $0, network attempts exactly the live leg's calls (proven count), live DB writes 0 (temp-DB evidence quoted).

## Budget

120s probes, 600s suite, 600s build, 600s vitest, $0.05 single live run, 1800s early-close, 2400s overall.

# SG-056 — FakeProvider signature drift: conform to the (image_bytes, prompt) surface (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** LIVE DEFECT 2026-09-17 (owner screenshot: Inbox import FAILED at ANALYZING_WITH_AI with `FakeProvider.extract_items() takes 2 positional arguments but 3 were given`). Root-caused by the Architect (systematic Ph1–2, PG-SC-01: write path `router.execute` at `router.py:52-71` is pure `*args` passthrough — read, no hunk; read path below): SG-027 built the surface `extract_items(image_bytes, prompt, *, estimated_cost)` (`reader.py:309` calls it; `ScriptedProvider` at `fake.py:104-110` and `OpenCodeGoProvider` at `opencode_go.py:235-241` match) but `FakeProvider.extract_items(image_ref)` (`fake.py:52`) + `VisionExtractionProvider` (`protocols.py:29`) kept the SG-025 1-arg shape. Every test double in the tree already uses the new shape (`test_ai_pipeline.py:569,680,742`, `test_phase2_e2e.py:202`, `test_planning.py:60`, `test_phase3_e2e.py:278`); only two direct old-shape calls remain (`test_extraction_contract.py:158`, `test_provider_gateway.py:159`) — which is why the suite is green while EVERY default-config import crashes. D78 (`SG_PROVIDER_ID=opencode-go`, owner-side) routes the owner around it; this slice fixes the road. **Authoring date (metadata, never a gate):** 2026-09-17. Transport: the standard job_spawn lane. Contract 0.27.0 (recorded == published payload == SG-049 run-2 receipt echo; packet states it).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** no migration (provider surface is code, not schema); no new dependencies; no provider calls ($0 — a metered call is a STOP-and-report); NETWORK: loopback + container-runtime only, nothing else.
**Money posture (F2):** spend UNCAPPED-but-ledgered with re-evaluation owed; this slice makes zero provider calls so the spend line reads $0.000000 actual vs $0 bound.
**Guards invoked (0.27.0 — Architect copies these to the rating row):** `PG-SC-01` read-both-paths · `PG-EV-01` gate-seen-failing · `PG-EV-02` artifact-not-command · `PG-EV-05` property-not-command · `PG-EV-09` both-runs-committed · `PG-SC-09` name-the-world · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live · `PG-PR-03` denied-is-stop · `PG-PR-04` code-becomes-live · `PG-PR-06` runtime-vs-budget · `PG-DP-02` no-sweep-waiver.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint+build, 900s host build/up. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none.** The on-box smoke (G4) is a bare `router.execute` call with no DB session — it writes zero rows anywhere. Tests use scratch temp SQLite. The production SQLite is touched by nothing.

## Why this exists

See Context: the default provider path (`fake`) crashes every import with a TypeError before any AI work. The fake is deliberately schema-invalid (SG-028: strict reader REJECTS its output — that behaviour is PRESERVED, never "fixed"), so after this slice a fake-routed import still fails — but with the designed extraction error, not an arg-count crash. Honest failure, not silent success.

## G1 — signature + protocol hunks (code, minimal)

- `fake.py:52`: `FakeProvider.extract_items` → the real surface `(image_bytes: bytes, prompt: str, *, estimated_cost: float = 0.0)`. Payload semantics UNCHANGED (schema-invalid by design, SG-028; the `source` field keys off the bytes it is handed). Accept-and-ignore is the design; recording bytes/prompts (ScriptedProvider-style) is allowed only if a test needs it — say why.
- `protocols.py:29`: `VisionExtractionProvider.extract_items` → the same surface (this protocol is the stale contract; the fix is the point).
- `reader.py`, `router.py`, `opencode_go.py`: NO HUNK (verify each is already conformant — a hunk here is a STOP-first finding, not a silent add).
- `test_extraction_contract.py:158` + `test_provider_gateway.py:159`: update the two direct old-shape calls to the new surface, keeping every assertion they make (they encode the drift; correcting them is the fix, not weakening).

## G2 — conformance rail (the missing guard; FAIL-then-PASS, `PG-EV-09`)

- New `backend/tests/test_provider_conformance.py`: every vision provider implementation in the tree accepts `(image_bytes, prompt, estimated_cost)` — FakeProvider (all four modes, called through `router.execute` so the passthrough is exercised, never the method directly), ScriptedProvider, and OpenCodeGoProvider AT SIGNATURE LEVEL ONLY (no construction with network, no key, no call — state the no-network construction used). `planning/service.py:4` is a docstring mention, not an implementation — enumerate it as considered-and-excluded.
- Enumerate ALL `extract_items` defs + call sites on the target first (criterion, not list — §2a); report the diff vs this packet's expectation either way.
- FAIL-then-PASS honestly: the new test RED on the pre-hunk tree (quote the TypeError), GREEN post-hunk; BOTH runs raw committed.

## G3 — suite + lint + hygiene

- Backend suite + frontend suite + `ruff`/`eslint` + `tsc && vite build` green; the only reds permitted are base-proven pre-existing (cite base commit + base-run command and output, or they are new findings with destinations). Gates name files checked with counts+elapsed; silent gates FAIL. `PG-EV-02`: built bundle bytes / committed logs, never exits. `PG-EV-05`: properties ("fake accepts the 3-arg surface through the router", "fake output still schema-invalid", "no other provider file touched").
- Secret scan 0 (no secrets touched); no migration; dep list unchanged; no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## G4 — deploy + on-box smoke (`PG-PR-04`)

- Rebuild + up backend (code becomes live no other way), idempotent re-`up -d` (same container, RestartCount=0), health exact, 8003 loopback-only. Full sweep WAIVED per `PG-DP-02` (substitute = G2 conformance + this smoke, named here).
- Smoke WITHOUT prod writes: `docker exec` python calling `router.execute("extract_items", b"smoke", "smoke", estimated_cost=0.0)` against the DEPLOYED container with the fake provider selected — quote the result (extraction error downstream of a SUCCESSFUL call, never TypeError). A live end-to-end import is explicitly OUT of scope (it would write prod rows without production-write authority, `PG-EV-06`).

## G5 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-056.log`, `{{WORKLOG_DIR}}/SG-056_report.md`, `{{WORKLOG_DIR}}/SG-056_verify.log` (G2 both runs + G4 smoke raw). First token `SG-056`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend line (**real $** $0.000000 actual vs $0 bound); three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `backend/app/services/providers/fake.py` (G1 hunk) · `backend/app/services/providers/protocols.py` (G1 hunk) · `backend/tests/test_extraction_contract.py` + `backend/tests/test_provider_gateway.py` (call-site hunks) · `backend/tests/test_provider_conformance.py` (new) · `docs/worklogs` (3 files). **Anything else is a STOP** — including `reader.py`, `router.py`, `opencode_go.py`, `AssetForm`, prompts, migrations, and any new dependency.
- Every requirement above names a file the ceiling enables it; if you find one that does not, STOP and say which.
- Cross-product (`PG-IC-01`): no blanket exclusion is issued. G-hunks and the STOP path share no condition with any remediation step — stops win (`PG-IC-03`). Reads MAY pull/run the already-built local images only.
- Budget (uncalibrated per `G-A9`): 120s ordinary · 600s suite+lint+build · 900s host build/up · **1500s early-close** · **2400s overall** — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): one signature, one protocol, two call sites, one rail; nothing else.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- `PG-SC-09`: name the world where the conformance test passes yet the live crash persists (a fourth caller passing a different shape; a stale container still running pre-deploy code) and why the slice still ships (G4 smoke runs against the DEPLOYED container; enumeration covers the callers).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); premises re-verified in-slice with quoted reads — in particular `reader.py:309`, `router.py:52-71`, `fake.py:52+104`, `opencode_go.py:235-241`, `protocols.py:29`, the six test-double defs.
- Provider enumeration with diff vs expectation either way; no hunk outside the ceiling.
- **FAIL-then-PASS honestly (`PG-EV-09`):** pre-hunk RED (TypeError quoted) + post-hunk GREEN, both raw committed. On-box smoke against the deployed container quoted (call succeeds, downstream extraction error, never TypeError).
- Suite + lint + build green (only base-proven reds); secret scan 0; no migration; dep list unchanged; prod DB untouched (smoke writes nothing — state the no-session construction); no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-056 | Report: docs/worklogs/SG-056_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), LIST the note contents and grep for this ID (log `--grep` does not match note bodies — proven twice), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint+build · 900s host build/up · 1500s early-close · 2400s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.

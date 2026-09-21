# SG-087 — privacy-controls audit: redaction + identifiers-only on every provider path, retention stated (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** D107-approved slice 3 of the Phase 5 hardening stage (plan `docs/superpowers/plans/2026-09-21-phase-5-hardening.md` Slice 3). THIS slice audits, builds nothing: prove EXIF/GPS absence on every provider path's outbound bytes, prove identifiers-only (no key material, no raw PII beyond the consented photo itself), and state retention from measured code + ADR-007 — inventing no new policy. A HOLE is a STOP-and-report; its fix rides its own slice, never this one. **Authoring date (metadata, never a gate):** 2026-09-21. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published (`b495b59`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** audit ONLY (enumerated ceiling below). No redaction-code changes, no consent-flow changes, no migration, no secrets in logs, no deploy, no restart (`PG-PR-04` — nothing becomes live; proof is scoped to offline tests + static enumeration). No provider calls, $0.
**Money posture:** $0.00 by construction — no metered call exists on any path. No bound to multiply out (`PG-IC-04` stated as not firing).
**Guards invoked (0.28.2 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-09` · `PG-SC-03` (hole→STOP; negative case below) · `PG-SC-05` · `PG-SC-09` · `PG-SC-11` (grep + verdict, see G3) · `PG-SC-12` · `PG-IC-01` · `PG-IC-03` (hole-STOP wins over continue — stated) · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` (NOTHING live stated).

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite, 1800s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none (temp fixtures only). Restart: none. Deploy: none.**

## G0 — enumerate every provider-path outbound carrier (a list is a fact)

- Criterion first: every call site that hands BYTES to a provider seam or an HTTP sender — the `redact_image` callers, the adapter's send path, the analytics/planning prompt builders' inputs, any stdlib/requests/httpx post/put carrying image bytes. Enumerate on target (criterion + `grep -rn`, raw output); my expectation: `reader.py:402` (pipeline), `opencode_go.py:299` (direct adapter), analytics/planning prompts text-only. Report the difference either way — a list I did not think of is a finding, not a failure.
- Name the EXIF hotspot on the record: `signals.py:251,278` reads EXIF into server-side observations (re-verify on target) — G1 traces whether anything derived there can reach a provider payload.

## G1 — EXIF/GPS absence on outbound bytes (proved, not asserted)

- Import the REAL `redact_image` — never re-implement it in the test (a fake that re-implements the logic proves the fake, `PG-SC-12`). Generate an EXIF/GPS-laden JPEG in-test with PIL (GPS tag present, asserted pre-redaction); commit NO binary fixtures.
- Prove: output carries zero EXIF/GPS tags (parsed, not string-matched) with pixels preserved (dimensions/mode quoted); the bytes handed at EACH G0 call site are the redacted form (assert on what crosses the real seam, `PG-SC-12`); ledger `output_payload` values on the exercised paths contain no EXIF segment; `signals.py`-derived EXIF values appear in NO provider payload (trace quoted end to end).
- Seen-to-fail (`PG-EV-01`): the tag-presence assertion MUST fail pre-redaction (run the same assertions against the unredacted input, quote the failure) — a gate never fed EXIF is decoration.

## G2 — identifiers-only (keys, PII, Enrich-absence)

- Key custody (ADR-007): probe presence/count ONLY (`grep -c '^OPENCODE_API_KEY=' .env` shape — value never printed, logged, or committed; a secret literal anywhere in tree/logs is a FAIL). Provider payloads carry hashes/ids (`input_hashes`), never key material.
- Enrich-absent assert: OFF/Jina are unbuilt, so NO photo/GPS bytes may reach any web path — prove by the G0 sender enumeration (every HTTP sender listed, each cleared or flagged).
- Consent: `consent=false` binds zero provider calls on every enumerated path (refusal BEFORE any call — re-prove on one path each, quoted).

## G3 — retention stated + committed test (no new policy invented)

- Retention statement from MEASURED code + `docs/adr/ADR-007-provider-privacy.md` (re-read on target): what is kept (evidence originals, ledger rows with output payloads/costs, redacted transients), where, for how long (if the code shows no TTL, state "no expiry; deletion is manual" — measured, never invented). Home decided and reported: new `docs/` note if the statement needs one, else worklog-only (stated, not silent).
- ONE new test file (`backend/tests/test_privacy_audit.py`): the G1/G2 proofs above on temp fixtures only. FAIL-then-PASS raw, both runs committed to `SG-087_verify.log` (`PG-EV-09`) — FAIL-PRE demonstrates the unredacted input failing (G1 seen-to-fail doubles as the pre-change run; state this composition explicitly).
- `PG-SC-11`: grep the test tree for end-relative assertions over privacy/redaction paths; list hits with verdicts (expectation: none — state the empty result raw).
- Suite green modulo the 2 known decoder env reds (base-proved premise — re-verify on bare BASE with stash, do not inherit); `ruff` clean; `mypy` delta 0 quoted; secret grep-gate over the diff (`api_key|OPENCODE_API_KEY|Bearer|[Tt]oken` identifiers, SG-037 shape) with 0 real secret shapes + the ADR-007 presence/count probe quoted.
- A HOLE (EXIF reaching a provider path, key material anywhere, an unlisted sender) is a STOP with the `BLOCKED:` commit — the fix is explicitly NOT in this slice. An incomplete enumeration is reported with the gap named, never stopped on (`PG-SC-03` negative case: only a confirmed hole stops).

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-087.log`, `SG-087_report.md`, `SG-087_verify.log` (raw outputs + BOTH fail-then-pass runs + every enumeration). First token `SG-087`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend **$0.000000 actual**; contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** ONE new test file · SURGICAL docs-note ONLY if G3 needs a home (quoted, else worklog-only) · `docs/worklogs` (3 files). **Anything else is a STOP** — redaction code, consent flow, prompts, app code, migrations/models, compose/`.env`, README (unless the retention home decision names it, quoted), STATE/AGENTS/packet dirs.
- Cross-product (`PG-IC-01`): no criterion changes product code, calls a provider, or touches the network beyond pushes; reads include the suite + static enumeration only — no container image pull/run; G4's suite run is covered by the same offline rule.
- A count or absence premise carries the RAW command output, never a paraphrase.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`). No commit named, no `HEAD ==` precondition — reachability form only.
- Simplicity (`G-A7`): enumerate → prove absence → state retention; no new machinery, no Enrich contact, no policy invention.

## Acceptance criteria

- G0 enumeration complete with criterion + raw output; every sender cleared or flagged; EXIF hotspot traced end to end.
- Redacted output tag-free (parsed) with pixels preserved; per-call-site redacted form asserted on the real seam; ledger payloads EXIF-free; unredacted-input failure quoted.
- Key presence/count only, zero literals; payloads identifiers-only; Enrich-absence proved by enumeration; consent refusal re-proved per path.
- Retention stated from measurement + ADR-007 with its home decided; new test FAIL-then-PASS raw both committed; suite/ruff/mypy/secrets per G3; $0.000000; no vacuous pass; hole→STOP honored (or no hole found, stated with the enumeration as witness).
- Question each criterion answers (`PG-SC-09`): G0 — what CAN leave the machine? G1 — is every outbound byte clean? G2 — do keys/PII stay home? G3 — is the proof committed and the retention record unambiguous? G4 — is the evidence committed, not merely reported?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **$0.000000 actual** (zero provider calls — containment per `PG-PR-04` stated: nothing live exists to contain).
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-087 | Report: docs/worklogs/SG-087_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite · 1800s overall; **$0.00** — no metered call exists on any path in this slice.

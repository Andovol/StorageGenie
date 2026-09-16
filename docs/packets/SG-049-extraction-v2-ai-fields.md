# SG-049 — extraction v2: AI quantity/unit/asset-type through candidates + label fallback + chat pointer (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** Stage D60/D74 (photo-first capture, L3) slice S3 of 3: S1 staged photo bytes, S2 made the name optional; THIS slice derives quantity/unit/asset-type via the provider through the existing candidate/review machinery. Owner-side pre-step (D73/D62, Q2): provider key in host backend `.env` (600) + `SG_CONSENT=true` + backend restart — **G0 verifies both before any provider touch; absent = STOP-as-SUCCESS** (ship offline proofs, live leg unrun). F-SG048-2 (planning/chat NULL labels) rides this slice. **Authoring date (metadata, never a gate):** 2026-09-16. Transport: the standard job_spawn lane. Contract 0.27.0 (recorded == published payload == SG-048 receipt echo; packet states it).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no migration** (an alembic diff is a STOP — candidate fields are JSON); v1 prompt files are FROZEN (any v1 byte change is a STOP); no new dependencies; NETWORK: loopback + the metered provider leg only (G5), nothing else.
**Money posture (F2):** spend UNCAPPED-but-ledgered with re-evaluation owed; every call commits its real cost/usage row surviving rollback (ISS-11); pre-call refusal (monthly cap) is respected — a refusal is a STOP-as-SUCCESS, never routed around. Stage 0 (F4): AI never auto-applies — new fields are human-confirmed, always.
**Guards invoked (0.27.0 — Architect copies these to the rating row):** `PG-EV-01` gate-seen-failing · `PG-EV-02` artifact-exists · `PG-EV-04` shape-of-unsent · `PG-EV-05` property-not-command · `PG-EV-06` live-rows · `PG-EV-08` before-capture · `PG-EV-09` both-runs-committed · `PG-SC-02` field-traced · `PG-SC-03` unread-dependency-as-goal · `PG-SC-05` exclude-by-rule · `PG-SC-08` baseline-in-slice · `PG-SC-09` name-the-world · `PG-SC-10` no-ignored-commit · `PG-SC-11` end-relative-assertions · `PG-IC-01` cross-product · `PG-IC-03` stop-wins · `PG-IC-04` worst-case · `PG-IC-07` no-fixed-dates · `PG-IC-08` blast-radius-is-stop · `PG-IC-09` premises-live · `PG-PR-03` denied-is-stop · `PG-PR-04` code-becomes-live · `PG-PR-06` runtime-vs-budget · `PG-PR-10` which-database-plus-grant. (`PG-DP-02/03/04` do not fire: deploy carries no restart-gated proof burden beyond G6's targeted checks; no reported failure; no new entry point.)

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint+build, 900s host build/up leg, live-leg bound set in G5. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: production SQLite `sqlite:////data/db/storagegenie.db` for the LIVE LEG ONLY (metered provider-call ledger rows are inherent and stay; NOTHING else — `PG-PR-10`, D73/D62); scratch temp SQLite for every test. Restart: backend container via compose rebuild+up (`PG-PR-04`). NETWORK: loopback + metered provider calls (G5) only.**

## Why this exists

S2 leaves quantity/unit/asset-type manual-only: `ExtractionItem` carries name/expiry/opened/date_type/lot only (`providers/schemas.py:30-41`, `extra="forbid"` — new keys are REJECTED today, re-verify), the three v1 prompts never ask for the new fields, and `build_candidate_from_extraction` never sets them (expiry/lot/opened pattern at `candidates.py:234-253` is the template). The ACCEPT path already reads them (`_create_asset_for_candidate`: `quantity`/`unit` via `_field_parts` at `:349-350`, `asset_type` at `:347` — verify, no hunk expected). F-SG048-2: `planning/service.py:153` + `chat/service.py:179` put raw `asset.display_name` into AI-catalog `"label"`s (NULL today for nameless assets). Chat shows raw `consent_disabled` with no pointer (FB-4c). Expected premises (re-verify per `PG-IC-09`): the cites above + `GATED_FIELDS` (`candidates.py:25`), `_review_state_for` (`:75-80`), `PROMPT_FILES` (`reader.py:51-55`), `ai_status` (`reader.py:97-103`), `ALLOWED_MODEL_IDS` (`settings.py:26`, vision path only), corpus `backend/eval/corpus/sg029/` (9 fixtures + manifest + images, SG-029 frozen baseline), `ChatPage.tsx` notice block.

## G0 — enablement gate FIRST (`PG-SC-03`): read what nobody has read, stop conditions both ways

- Establish, read-only: (a) `GET /settings/ai` (loopback) reports `consent=true`; (b) the provider key EXISTS (existence-only probe — e.g. length-check boolean — **never print, log, quote, or commit a single key byte**; `docker compose config` output is FORBIDDEN here — it prints secrets); (c) `ai_status()`-equivalent reports enabled for the configured provider.
- GO (all three true) → G1–G6. STOP (any false) → **STOP-as-SUCCESS**: commit offline proofs + `BLOCKED: awaiting owner key+consent (D62)` first line, push, receipt, clean tree. **Stopping here is the successful outcome** — say so in the report, never treat it as failure. No provider call may precede this goal.

## G1 — schema v2: `quantity`/`unit`/`asset_type` on `ExtractionItem` (`providers/schemas.py` hunk only)

- `quantity: float | None` — finite, `>= 0` (reject NaN/inf/negative at validation; illegible → null, never guessed). `unit: str | None` (non-blank when present, `max_length=50` matching the column). `asset_type: str | None` (non-blank when present, `max_length=50`; open vocabulary — the canonical mapping lives downstream, not in the schema).
- `extra="forbid"` stays; the `unknowns` machinery already covers new fields generically (`UNKNOWN_PATH_RE` + `field_name not in ExtractionItem.model_fields` — verify, add nothing). Contract tests extend `test_extraction_contract.py`: each new field parses, each invalid shape fails, unknowns-entry rules hold for the new paths.

## G2 — prompts v2 (three NEW files, v1 byte-identical) + `PROMPT_FILES` hunk

- New `extract-{food,medicine,cosmetics}-v2.md` (front-matter `template_version` v2): v1 rules + transcribe-only quantity (count/amount exactly as printed — no arithmetic, no serving-size math), unit verbatim as printed (null when absent), asset_type as the printed product kind (null when unclear); illegible/absent → null + `unknowns` entry; `confidence < 1.0` requires reasons (schema-enforced); JSON-only, no prose.
- `PROMPT_FILES` → v2 filenames. v1 files: NO HUNK (prove with `git diff` showing zero v1 bytes). Repair turn (`repair_prompt`) unchanged — it names no fields (verify).

## G3 — candidate plumbing (`candidates.py` hunks: `GATED_FIELDS` + three field blocks)

- `GATED_FIELDS` gains `quantity`, `unit`, `asset_type` → extraction-sourced values are ALWAYS `review_state="proposed"` (EXACT state per M11 — F4 Stage 0: human confirms, no threshold auto-accept, no exceptions). Deterministic `asset_type="unknown"` default stays as-is.
- `build_candidate_from_extraction`: `item.quantity`/`item.unit`/`item.asset_type` → fields with extraction provenance (confidence/provider/model/template/call ids — the lot block at `:244-253` is the template). `_create_asset_for_candidate` needs NO hunk (verify each of `:347,:349-350` reads the new fields — if one does not, that is a STOP-first finding, not a silent add).
- F-SG048-2 in this goal: ONE shared backend constant for the nameless label (module MUST be import-cycle-free — `app/models/asset.py` is the safe home; state the no-cycle reason), used at `planning/service.py:153` + `chat/service.py:179`; test asserts BOTH call sites fall back (enumerate the two, report the diff either way — sets are facts).

## G4 — eval: v2 measured WITHOUT moving the v1 baseline (`PG-SC-08`)

- v1 baseline proof: run the frozen v1 eval path pre/post and quote IDENTICAL metric values (any drift = STOP — the prompts/schemas moved under it). New-field scoring rides fixtures that carry v2 ground truth (additive manifest entries / new fixture files — never rewrite an SG-029 ground-truth value; `git diff` must show zero bytes changed in the nine `sg029_*.json` + `manifest.json` unless the run is additive-only and disclosed).
- `PG-EV-04`: the live leg mocks nothing it sends — mandate one test asserting the SHAPE of the v2 request payload (schema keys, response-format flag) against the fake transport. `PG-SC-09`: state the world where the live leg passes yet the outcome is wrong (parseable-but-wrong values) and why the slice still ships (confidence + uncertainty_reasons + mandatory human review gate, which this slice does not weaken).

## G5 — live leg: metered, capped, ledgered (only after G0 GO)

- Bound FIRST (`PG-IC-04` worst case, `G-A9` uncalibrated): at most **3 live images**, named in the report; cumulative worst-case = 3 × the adapter's per-call estimate ceiling (compute in-slice from the estimator, quote the number); the runner's per-fixture guard enforces it; pre-call refusal (monthly cap) respected — refusal = STOP-as-SUCCESS with zero calls / zero rows.
- Measure schema-conformance + cost, NOT accuracy: parse success per image, `unknowns` honesty (null-valued unknowns entries present, no fabrication), confidence/reasons present; every call commits its real cost/usage row surviving rollback (ISS-11 pattern); report cumulative actual vs the worst-case bound with units.
- Blast radius (`PG-IC-08`): non-ledger prod tables (asset/candidate/job/evidence/assertion/audit counts + Toothpaste name) IDENTICAL before/after — any other created row is a STOP-and-report. Ledger rows reported with identifiers and LEFT in place (they are the spend audit trail, `PG-EV-06`).
- Secret handling: NO key bytes in any log, diff, or report (grep-gate the worklogs for key patterns before commit); `docker compose config` NEVER run.

## G6 — chat pointer + deploy (FB-4c + `PG-PR-04`)

- `ChatPage.tsx`: the `consent_disabled` notice gains one plain line + link: `Enable AI in Settings to use chat` → `/settings`. Test asserts the link renders exactly in the disabled state and never in the enabled path. NO other Chat restyle (SG-055+ owns it).
- Rebuild + up, idempotent re-`up -d` (same container, RestartCount=0), health exact, served bundle hash changed, 8003 loopback-only, gate 301/401 (loopback Host-header form). Full sweep WAIVED per `PG-DP-02` (substitute = G5 live leg + targeted checks, named here).

## G7 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-049.log`, `{{WORKLOG_DIR}}/SG-049_report.md`, `{{WORKLOG_DIR}}/SG-049_verify.log` (G4 both runs + mutations raw, G5 per-call raw). First token `SG-049`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line (**real $** actual vs bound); three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `backend/app/services/providers/schemas.py` (G1 hunk) · `backend/app/services/providers/prompts/extract-{food,medicine,cosmetics}-v2.md` (3 new) · `backend/app/services/providers/reader.py` (PROMPT_FILES hunk) · `backend/app/services/candidates.py` (GATED_FIELDS + 3 plumbing blocks) · `backend/app/models/asset.py` (label-constant hunk) · `backend/app/services/planning/service.py` + `backend/app/services/chat/service.py` (label hunks) · `backend/eval/` (additive v2-eval hunks; frozen v1 bytes untouched) · `backend/tests/test_extraction_contract.py` + `backend/tests/test_sg049_*` (new) + label/plumbing test hunks · `frontend/src/routes/ChatPage.tsx` + `ChatPage.test.tsx` (pointer hunk) · `docs/worklogs` (3 files). **Anything else is a STOP** — including v1 prompt files (frozen), `reader.repair_prompt`, model whitelist/keys/consent wiring (owner env), `AssetForm`, `asset_service`, and any new dependency. No new files outside prompts + tests + worklogs.
- Every requirement above names a file the ceiling enables it; if you find one that does not, STOP and say which.
- Cross-product (`PG-IC-01`): no blanket exclusion is issued. G0's STOP shares no condition with any remediation step — stops win (`PG-IC-03`). Reads MAY pull/run the already-built local images only.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. `PG-EV-02`: parsed payloads / committed logs / served bytes, never exits. `PG-EV-05`: properties ("illegible quantity arrives null with an unknowns entry", "extraction asset_type is always proposed", "nameless labels read Untitled in both AI catalogs", "disabled chat links to Settings").
- Budget (uncalibrated per `G-A9`): 120s ordinary · 600s suite+lint+build · 900s host build/up · live leg per G5 bound · **1500s early-close** · **2400s overall** — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): three fields through the existing review machinery + label fallback + pointer line; nothing else.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).

## Acceptance criteria

- G0 quoted read-only FIRST with both outcomes handled; no provider call precedes it (STOP path) or every call follows a GO with the three establishments quoted.
- Starting tree quoted (clean expected; dirt = STOP first); premises re-verified in-slice with quoted reads — in particular `schemas.py:30-41`, `candidates.py:25-40 + :234-253 + :346-360`, `reader.py:51-55 + :97-103`, `settings.py:26`, the three v1 prompts, `planning/service.py:150-162`, `ChatPage.tsx` notice block, corpus manifest.
- Reader/label enumeration with diff vs expectation either way; v1 bytes provably untouched; v1 metrics byte-identical pre/post.
- **FAIL-then-PASS honestly (`PG-EV-09`):** pre-change failing run + green run + mutations caught-singly, all raw committed. Live per-call raw committed (`PG-EV-08`).
- Suite (backend + frontend) + lint + build green; secret scan 0 (incl. worklog grep-gate); no migration; dep list unchanged; non-ledger prod counts + Toothpaste name equal; ledger rows reported with identifiers; actual spend vs worst-case bound quoted; no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: G0 establishments, per-call cost/usage + ledger identifiers, cumulative actual vs bound, non-ledger counts before/after, live spend **real $**, loopback only.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-049 | Report: docs/worklogs/SG-049_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), LIST the note contents and grep for this ID (log `--grep` does not match note bodies — proven twice), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint+build · 900s host build/up · live leg per G5 bound · 1500s early-close · 2400s overall; REAL metered $ (actual vs bound per call + cumulative); actual-versus-budget per leg with units.

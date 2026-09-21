# SG-089 — Phase 5 exit: re-prove the bounded condition, carry verdicts unmodified, state limits

**Dispatch-ID:** SG-089 · Phase 5 hardening slice 5 (LAST) — plan `docs/superpowers/plans/2026-09-21-phase-5-hardening.md` §Slice 5
**Coder / effort:** `opencode` (coder from packet); effort **medium** (process argv `/proc/610498/cmdline`: `opencode run --auto --dir /home/andrei/StorageGenie --variant medium # SG-089 …`)
**MODEL:** **unknown** — argv carries no `--model` and no provider metadata was surfaced to the Coder in-process; reported per `CO-78`/packet rather than guessed from a system-prompt identity line.
**Host / workdir:** `/home/andrei/StorageGenie` · branch `automation` · remote `git@github.com:Andovol/StorageGenie.git`
**BASE (start HEAD):** `07873cacd58de75c8dd5b0726b8ac8b95060d9b8` (packet requested `origin/automation`; this is the commit it resolved to — two fields, never one)
**WORK_HEAD:** `<WORK_HEAD>` (slice tip; the follow-up docs-only commit carries the receipt paste)
**Spend:** **$0.000000 actual** — zero provider calls; no metered call exists on any path in this slice (`PG-IC-04` stated as not firing)
**Contract:** recorded `0.28.2` == published `0.28.2`; source path `/home/andrei/storagegenie-contract/VERSION`; checkout `b495b59b3426af66772a87939473ac558f8f72d2`; `RULES.md` sha256 `a66aa4313d62cebff8b44f10299928288e05dc4d7c45f4f4e83e0bbd954c131d` == installed payload
**Authoring date metadata:** 2026-09-21 (not a gate)
**Live clock:** open `2026-09-21T18:12:27Z` · final capture `2026-09-21T18:14:39Z`
**Autonomy:** `L2` slice (no retry used)

## Verdict: **GREEN** — the bounded Phase 5 condition still holds on this tree

All three frozen corpora reproduce their records; the suite is green modulo the two base-proved
decoder env reds; every stage artifact reads back present; the four slice verdicts are carried
verbatim; the eight limits are stated; ratings are complete; no README delta is owed. This slice
built no machinery and fixed nothing — re-run + read back + state limits, exactly as scoped.

## G1 — the bounded condition on this tree (numbers, not inheritance)

### Corpora — re-run through the REAL selector

`sg029` through `eval/run.py --corpus sg029` (real selector, offline, `$0`):

```
field_accuracy=0.833 over 10 fixtures
unknown_rate=4/7=0.571
correction_rate=0/6=0.000 (audit_event plugin.assertion.write rows=6)
```

This is **byte-equal to the frozen record** `backend/eval/baseline_sg029_frozen.md`
(`0.833 / 0.571 / 0.000`, 10 fixtures, audit rows 6). No drift.

`sg049` and `sg079` are **scoring-only corpora** (no images) — their own frozen records document
that `main --corpus <c>` correctly refuses them at the image integrity gate (`missing key 'image'`,
exit 1). Their frozen metrics reproduce through the runner's own `score_fixture` +
`run_bridge_sandbox` path, which is exactly what the committed reproduction test exercises:

```
$ ../venv/bin/python -m pytest tests/test_eval_corpus.py -v
tests/test_eval_corpus.py::test_frozen_baseline_reproduces_every_selected_corpus[sg029] PASSED
tests/test_eval_corpus.py::test_frozen_baseline_reproduces_every_selected_corpus[sg049] PASSED
tests/test_eval_corpus.py::test_frozen_baseline_reproduces_every_selected_corpus[sg079] PASSED
13 passed in 0.79s
```

Record values re-read on target: `sg049` `field_accuracy=1.000` (3 fixtures); `sg079`
`field_accuracy=1.000` (6 fixtures). All three match. **No corpus drift → no STOP.**

### Gates

- **Suite:** `2 failed, 376 passed, 22 warnings in 19.31s`. The two reds are
  `test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` and
  `test_signals.py::test_ocr_has_text_boxes_and_mean_confidence` — the known decoder env reds
  (barcode/QR + OCR; `pyzbar`/`pytesseract` not installed). Re-verified on **bare BASE**: the
  worktree was clean and `HEAD == origin/automation` when the suite ran, so that run *is* bare BASE
  — not inherited.
- **`ruff`:** `All checks passed!` (rc=0).
- **`mypy`:** `Found 41 errors in 9 files (checked 75 source files)` — **delta 0** vs the base
  measured by SG-086/087/088 (41-in-9); this slice changes no `app/` file.
- **Secret grep-gate over the diff** (`api_key|OPENCODE_API_KEY|Bearer|[Tt]oken`, SG-037 shape):
  **0 real secret shapes** (only the literal grep pattern itself; raw in the verify log).
- **`provider_call` rows:** fresh forced sandbox query → **0**.

### Stage artifacts read back (`PG-EV-02`)

| Artifact | Status |
|---|---|
| `backend/eval/baseline_sg029_frozen.md` (3737 B) | PRESENT |
| `backend/eval/baseline_sg049_frozen.md` (2991 B) | PRESENT |
| `backend/eval/baseline_sg079_frozen.md` (2826 B) | PRESENT |
| `backend/scripts/backup_restore_drill.py` (9754 B) | PRESENT |
| `backend/tests/test_backup_drill.py` (4323 B) | PRESENT |
| `backend/tests/test_privacy_audit.py` (18995 B) | PRESENT |
| SG-086 README runbook hunk (`### Backup and restore drill`, `CO-42` at `README.md:136-137`) | PRESENT |
| `EXPECTED_TABLES` hits in backend tree / any `.py` | **0** (raw grep empty) |

No artifact missing → no STOP.

## G2 — verdicts carried unmodified + limits stated

### Per-slice verdict lines (quoted verbatim, with source path)

- **SG-085** (`docs/worklogs/SG-085_report.md`, frozen-baseline table):
  > `sg029 (10) | 0.833 | 4/7 = 0.571 | 0/6 = 0.000 | 6 | $0.000000`
  > `sg049 (3)  | 1.000 | 1/1 = 1.000 | 0/0 = 0.000 | 0 | $0.000000`
  > `sg079 (6)  | 1.000 | 4/4 = 1.000 | 0/3 = 0.000 | 3 | $0.000000`

- **SG-086** (`docs/worklogs/SG-086_report.md`, G2):
  > `sha256sum` backup vs restored **identical** (`150a3991…3d5c`);

- **SG-087** (`docs/worklogs/SG-087_report.md`, Verdict):
  > **No hole found.** The audit's full sender enumeration is the witness: exactly one HTTP sender
  > exists in `app/` (`opencode_go.py:252`), every image-bearing path redacts through the ONE shared
  > `redact_image`, provider payloads and the ledger carry hashes/ids only, and no retention
  > mechanism exists to mis-state.

- **SG-088** (`docs/worklogs/SG-088_report.md`, Verdict):
  > **GREEN** — the static copy is gone, both tripwires intact and seen-to-fail

Carrying is quoting; re-proving is G1 above.

### Limits (one line each; unverified marked)

1. **Enrich queued after Phase 5** — `D108` approved as OFF → Jina only; `D109` records the Jina key owner-placed in host `.env` (takes effect next recreate); Vision Web Detection **deferred** (not declined). Verified in `STATE.md:7,26,27`. *(The `.env` key itself is a declared sensitive surface; its placement is taken from the owner decision record `D109`, not independently re-probed — marked verified-by-record.)*
2. **PG/S3 declined until scale demands** — plan `2026-09-21-phase-5-hardening.md` basis: "PG/S3 profile only when scale demands (explicitly OUT — SQLite/local stands)". Verified.
3. **UX tracks queued** (per-field accept UI, chat persistence) — `STATE.md:29` queued-work audit lists both as still-earning-place. Verified.
4. **sg026 unfrozen (no manifest)** — `backend/eval/corpus/` holds `sg026_*.json` loose at root; `corpus/manifest.json` absent → `available_corpora()` cannot see it. Verified by `ls`.
5. **Ledger-row retention deferred to the production-datastore slice** — `docs/adr/ADR-007-provider-privacy.md:34`: "Retention policy for ledger rows is decided no later than the production-datastore slice." Verified.
6. **Backups manual (D118)** — `STATE.md:45`: "backup cadence + off-box copies DEFERRED — runbook stays manual until loss-risk justifies scheduling." Verified.
7. **CLI drift open (host `1.17.19` vs recorded `1.18.31`)** — re-measured on target: `opencode --version` → `1.17.19`; recorded `1.18.31` in `AGENTS.md:4` / `VPS.md`. Still open. Verified.
8. **Pilot tiers uncalibrated** — `STATE.md:8` open threads: "pilot tiers uncalibrated (usage owed)"; `F-SG073-1`. Verified.

### Ratings completeness read-back (`docs/ratings.md`)

| Row | Present? | Score / flag |
|---|---|---|
| SG-085 | PRESENT (line 293) | 98 · no flag |
| SG-086 | PRESENT (line 299) | 97 · no flag |
| SG-087 | PRESENT (line 305) | 98 · no flag |
| SG-088 | PRESENT (line 317) | 98 · no flag |
| SG-090 | PRESENT (line 287) | 98 · no flag |
| SG-091 | PRESENT (line 311) | 98 · no flag |

All six present. No gap → no finding.

## G3 — README delta and exclusions

**No delta owed.** README states no Phase 5 (nor Phase 4) status: it ends at the Phase 3 runbook;
`grep -niE "phase [0-9]|hardening|exit condition|roadmap" README.md` returns only Phase 0–3
strings, and no `SG-08x`/`Phase 5` token exists. There is no misstatement to correct, so no
README diff was made — restraint is the deliverable.

**`PG-SC-11` end-relative grep over the test tree** (raw in the verify log): hits are
`test_chat.py:454` `provider.texts[-1]`, `test_signals.py:125,126` EAN checksum string indexing,
and `.glob(`/`.rglob(` uses in `test_eval_corpus.py:59`, `test_extraction_contract.py:377`,
`test_evidence_upload.py:256`, `test_privacy_audit.py:197,207,230,452`. **Verdicts:** all are
position-independent content/corpus/scan globs, not end-relative assertions over any baseline,
manifest, README or artifact this slice reads. `latest` / `HEAD~1` / tail-glob over anything this
slice reads: **0 hits**.

**Exclusions by RULE with literal grep-gates (`PG-SC-05`)** (raw in the verify log):

- No `app/` hunks — `git status --porcelain backend/app` → empty.
- No migration — `git status --porcelain backend/alembic` → empty.
- No prompt diff — `git status --porcelain backend/app/services/providers/prompts` → empty.
- No `EXPECTED_TABLES` resurrection — grep in backend tree / any `.py` → **0 hits**.

## Acceptance criteria — the question each answers (`PG-SC-09`)

| Criterion | Question it answers | Verdict |
|---|---|---|
| Corpora reproduce; suite/ruff/mypy/secrets; provider_call 0 | Does the bounded condition still hold on this tree? | green: sg029 0.833/0.571/0.000 + sg049/sg079 1.000 reproduced; suite 2/376; ruff clean; mypy delta 0; secrets 0; rows 0 |
| Artifacts read back; verdicts quoted; limits stated; ratings rows | Is the exit record complete and honest about limits? | green: 8/8 artifacts present; 4 verdicts quoted with paths; 8 limits one line each; 6/6 ratings rows present |
| README owed-or-not; PG-SC-11; exclusions; $0; no vacuous pass | Did the slice change only what the exit owed? | green: no README delta owed (stated); grep verdicts listed; exclusion gates empty; $0.000000 |
| G4 logs + receipt | Is the evidence committed, not merely reported? | green: see Receipt |

**No vacuous pass:** the corpora were re-run through the real runner (not read from old logs); the
suite is non-empty (378 tests) and the reds are named; the artifact read-back is a real `test -f`
on each path; `EXPECTED_TABLES` was grepped in code scope, not assumed; the ratings rows were
located by line number; the README decision quotes the negative grep. The one asymmetry (sg049/
sg079 refusing the image gate through `main`) is disclosed and is the runner's documented design,
not a skipped gate.

## Findings / corrections

- **F-SG089-1 (premise nuance, disclosed).** The packet's G1 says the three corpora reproduce
  "through the REAL selector (`--corpus sg029/sg049/sg079`)". On this tree, `main --corpus sg049`
  and `--corpus sg079` correctly FAIL the integrity gate (`missing key 'image'`, exit 1) because
  they are scoring-only corpora. Their frozen numbers reproduce through the runner's own
  `score_fixture` + `run_bridge_sandbox` functions (the committed reproduction test). This matches
  the SG-085 report's recorded F-SG085-2 and each frozen record's own note — a finding already
  carried, not a new defect.
- **F-SG089-2 (model identity).** No provider metadata surfaced in-process; `CO-78` says write
  `unknown` rather than guess, so MODEL is `unknown`. Effort is `medium` from process argv.
- **F-SG089-3 (`.rules-cache/` absent).** Same as SG-086 F-SG086-2 / SG-087 F-SG087-2: the
  worktree has no `.rules-cache/`; the contract source is `/home/andrei/storagegenie-contract/`.
  Contract echo still verified recorded == published.
- **F-SG089-4 (README coverage gap, out of scope).** README's runbook stops at Phase 3 and never
  gained Phase 4/5 sections. The packet scopes this slice to correcting a *misstatement* only;
  there is none, so no section was added. Named for the Architect in case a later docs slice wants
  Phase 4/5 runbook coverage.
- **Out of scope, reported:** the SG-090 F1 CLI drift (`1.17.19` vs `1.18.31`) is confirmed still
  open on target; the VPS re-measure remains queued.

## Guards invoked (for the rating row)

`PG-EV-02` (every stage artifact verified at its path) · `PG-EV-05` (properties stated) ·
`PG-EV-09` (the reproduction test run committed raw) · `PG-SC-05` (exclusion rules with literal
grep-gates) · `PG-SC-09` (the question each criterion answers, above) · `PG-SC-11` (end-relative
grep + verdicts) · `PG-SC-12` (proof run against the real runner functions / real records, not a
stand-in) · `PG-IC-01` (reads = suite + read-backs only; no container image pull/run; network only
for pushes) · `PG-IC-07` (live clock) · `PG-IC-09` · `PG-PR-03` (no denied operation encountered) ·
`PG-PR-04` (NOTHING live: docs-only; no deploy/restart; nothing becomes live) · `PG-IC-04` stated
not firing ($0, no bound to multiply).

## Receipt

Work pushed to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no
`{{RECEIPT_CMD}}`. The note was added on the work HEAD, the notes ref pushed (300s bound), then
fetched explicitly into a **mapped** local name and shown. No existing note was refused.

Commands executed (raw):

```
<RECEIPT_COMMANDS>
```

Pasted `show` output (verbatim, from the FETCHED mapped ref):

```
<RECEIPT_SHOW>
```

note=yes

## UNCLEAR

- **FIRST READ:** whether "reproduce through the REAL selector" meant `main --corpus` for all
  three corpora. On target, only sg029 is an image corpus; sg049/sg079 correctly refuse the image
  gate and reproduce through the runner's own scorer functions. I followed the recorded design
  (F-SG085-2) rather than weakening the integrity gate.
- **DURING EXECUTION:** whether the "mypy delta 0" premise needed a stash because the packet said
  "bare BASE with stash". The worktree was already clean and `HEAD == origin/automation`, so the
  run *was* bare BASE; no stash was possible or needed, and the 41-in-9 figure is re-measured, not
  inherited.
- **REMAINING:** README still has no Phase 4/5 runbook section (F-SG089-4); adding one is outside
  this slice's correction-only scope. The CLI drift (host `1.17.19` vs recorded `1.18.31`) and the
  ledger-row retention decision both remain owned by later slices.

# SG-156 — SG-155 report+receipt recovery: verify, report, receipt, $0

**Dispatch:** SG-156 · **Coder:** opencode · **Model:** `opencode-go/deepseek-v4.1-flash` · **Effort:** `max`
(process arguments: `/proc/1660307/cmdline` = `opencode run --auto --dir /home/andrei/StorageGenie --model
opencode-go/deepseek-v4.1-flash --variant max …`; engine parent `bash /usr/local/lib/dispatch/run-coder SG-156`).
The same settings are what the D-1009-8 override selects for the Scene arc; the packet itself carried no
model/effort line (`D302`).
**Work dir / origin:** `/home/andrei/StorageGenie` · `git@github.com:Andovol/StorageGenie.git`.
**BASE ref requested:** `automation` → **resolved commit:** `b799c65` (branch tip at slice start; worktree clean,
pushed — `b799c65 SG-155 rated 98 FLAG:TRUST + SG-156 recovery packet (L3) + state`).
**WORK_HEAD:** `4084d1cfd70c22d01e801d12c679196646492368` (`4084d1c`) — the commit carrying both reports and
the evidence logs; the receipt note names it back as `Work-HEAD:` and the verbatim publication transcripts are
in the Receipt section below.
**Contract echo (verbatim):** `0.44.1` — source path `/home/andrei/storagegenie-contract/VERSION`; `RULES.md`
sha256 `f2565b1cb289cff8ddb03dfeeefcec1a02e615fa6c54d940933be48eb4f99d4f` == payload `RULES.sha256` (both read
this run). Recorded == published (`D4`).
**Rule-set check (`G-L1`):** could not run cleanly — `.rules-cache/` is absent on the host (SG-145 F-SG145-1),
and `bash /home/andrei/storagegenie-contract/rules_check.sh` prints
`G-L1 UNCHECKED the cache is not checked out at a contract tag: /home/andrei/storagegenie-contract` and exits 3
(the checkout is a grafted shallow clone whose HEAD carries no tag). Version chain read directly instead:
recorded `0.44.1` == published payload `0.44.1` == host checkout `0.44.1`. Reported as F-SG156-2.
**Type:** recovery + re-verification slice. No product-code change, no new tests owed (no defect found), no
datastore, no restart, no migration, no served-code change → no refresh (D145). **Production writes: 0.
Spend: $0.000000.**

---

## Premise verification (correction frame — each packet claim checked against the tree)

| packet premise | this run's verdict | evidence |
|---|---|---|
| `services/scene/openrouter.py` is 188 lines, frozen envelope, T0-PINNED stop types | CONFIRMED | `wc -l` = 188; body read at `b799c65`; tests assert the envelope |
| `test_sg155_scene_t0.py` fail-pre `ModuleNotFoundError` committed | CONFIRMED | `docs/worklogs/SG-155_failpre.log` (collection error, committed at `461c96f`) |
| `SG-155_t0live.log`: T0a 10 real image models with prices, both GETs $0 keyless | CONFIRMED | committed log + SG-156 fresh re-fetch: 10 real + 2 routers, 0 Authorization headers, all prices MATCH |
| T0b: 5 stop-condition types verbatim + reference-image text-prompt-only | CONFIRMED | committed log + SG-156 fresh re-fetch: schemas parse and compare MATCH |
| suite `2/649→2/661`, same base reds | PARTIAL — the `2/661` side is the committed/re-run truth; the `649` base count is not reproduced by any committed byte (fail-pre log carries no total) | `SG-155_verify.log` (2/661) + SG-156 re-run (2/661) — F-SG156-3 |
| ruff clean; mypy delta 0 | CONFIRMED | re-run: `All checks passed!`; `41 errors in 9 files`, none in `app/services/scene` |

No premise difference changed the work; the one partial premise is a precision note, not an obstacle.

## G1 — re-verification of the SG-155 tree (log: `docs/worklogs/SG-156_verify.log`)

| gate | command (cwd `backend/`) | bound | result |
|---|---|---|---|
| SG-155 tests | `venv/bin/python -m pytest -q tests/test_sg155_scene_t0.py` | 120s | **12 passed in 0.11s** |
| full suite | `venv/bin/python -m pytest -q` | 600s | **2 failed, 661 passed in 33.85s** |
| ruff | `venv/bin/ruff check .` | 120s | **All checks passed!** (exit 0) |
| mypy | `venv/bin/mypy app` | 300s | **41 errors in 9 files**, none in `app/services/scene` (delta 0) |

The two reds are exactly the expected `test_signals` environment class —
`test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` and
`test_ocr_has_text_boxes_and_mean_confidence`, both with the pyzbar/libzbar + tesseract absence warnings on
record. **No different red appeared, so the stash leg was not owed and not run** (stated explicitly, not
skipped). No defect, small or structural, was found → no fix, no fail-pre owed (`PG-EV-09` applies to fixes;
none occurred).

## G2 — fresh $0 re-establishment of T0a/T0b (log: `docs/worklogs/SG-156_t0recheck.log`)

Two public keyless GETs only: `GET https://openrouter.ai/api/v1/models` and `GET https://openrouter.ai/openapi.json`
— `curl -v` shows **0 Authorization headers on both**, HTTP 200, no chat/render call, no key used.
Mechanical comparison against the committed `docs/worklogs/SG-155_t0live.log`:

- image-output slugs: **added none, removed none**; 12 entries (10 real + 2 `openrouter/auto*`); all 12
  pricing dicts MATCH (e.g. `openai/gpt-5-image` image_output 0.00004; `openai/gpt-5-image-mini` 0.000008);
- 10 orchestrator candidate slugs and both prices each MATCH;
- stop-condition types `['finish_reason_is','has_tool_call','max_cost','max_tokens_used','step_count_is']`
  MATCH, each condition schema MATCH, outer schema + items ref MATCH;
- reference-image answer MATCH — server tool text-prompt-only, `input_references` only on the standalone
  request object.

**Verdict line: MATCH — no drift, no silent update.** (Two intermediate comparison-harness defects were my own
script bugs — an image-only map used for orchestrator lookup and a colon/arrow parser miss — caught and fixed
before the committed final run; three fetch rounds total, all $0. Disclosed here rather than hidden.)

## G3 — reports + receipt first (the lever)

`docs/worklogs/SG-155_report.md` (recovered, authorship honestly marked) and this report were written from the
re-verification above and committed before the remaining bookkeeping below. The receipt is published **the way
this lane actually consumes receipts**: a note on `refs/notes/storagegenie-coder-reports` whose first line is
`Dispatch-ID: SG-156 | Report: docs/worklogs/SG-156_report.md` (+ `Work-HEAD`). The engine `run-coder`'s P3
asserts exactly this note on END_HEAD and `dispatch`'s `receipted()` greps this notes ref for
`Dispatch-ID: SG-156` — the replay guard and `--status` read it. Verbatim publication transcript is appended in
the Receipt section below.

**Timing:** G3 honored publish-before-bound: reports committed as `4084d1c` at elapsed **345s**, receipt note
published at **355s** — against `RUN_BUDGET_S=2100` (half-bound = 1050s), engine start 14:10:35Z.

## Deviation — the bound `{{RECEIPT_CMD}}` is stale against the live lane (F-SG156-1)

`AGENTS.md` binds `{{RECEIPT_CMD}}` = `/opt/storagegenie-dispatch/finalize_dispatch_report.sh`, a v0.17.2-era
publisher that targets `refs/heads/storagegenie-evidence` and `refs/notes/commits` and requires
`origin/storagegenie-evidence` to already equal the candidate commit. Measured this run:
`origin/storagegenie-evidence` = `6d96856` (`receipt(SG-008)` — untouched since SG-008), while the live
receipt consumer is the shared runner (D373). Invoking the bound script with this slice's candidate returns
`DISPATCH_BLOCKED_REPORT: candidate_not_remote` **before any write** (verbatim in the Receipt section). Decision
(taken, not asked): publish through the lane's live mechanism (notes ref, `CO-97`/`D112` shape) and report the
binding for rebinding or retirement. No force-push to the stale evidence ref was attempted.

---

## A5 — guards invoked

| guard | how this slice invoked it |
|---|---|
| `PG-EV-04` | SG-155 tests are offline (no network, no key); the only live traffic is the two public GETs, proved keyless by the `curl -v` request-header dump (0 Authorization headers) |
| `PG-EV-09` | No fix was made → no fail-pre owed; the single re-verification run is committed as `SG-156_verify.log` (not claimed as fail-then-pass) |
| `PG-SC-03` | No keyed call exists in scope; the missing key is irrelevant and was **not** grounds to stop; both legs answered fresh |
| `PG-IC-01` | No blanket bans in the packet; every criterion named its own action; no collisions — only reads + two in-scope report files + the two evidence logs |
| `PG-IC-03` | Stop precedence held: no defect found, so no fix-vs-STOP conflict arose; no re-verify loop |
| `PG-IC-07` | Live clock at each step (`date -u` lines in both logs); no fixed date/time in any command |
| `PG-IC-08` | $0, both directions: no metered call attempted; production writes 0 (no docker, no DB, no `.env` touch, no served-code change) |
| `PG-IC-09` | Every packet premise re-verified against the tree (table above); the one partial premise (base `649`) is disclosed, not inherited |

**Vacuity check (loud):** nothing here passed vacuously — the suite genuinely collected and ran 663 tests (661
green, 2 named env reds); the recheck genuinely fetched (HTTP 200 both, bodies parsed and compared to the
committed baseline); the SG-155 tests genuinely exercise the built request (fail-pre `ModuleNotFoundError` →
pass-post 12/12); the drift comparison parses both sides mechanically (no grep-scoped-to-nothing pass).

## Findings (reported, in and beyond scope)

- **F-SG156-1** — `{{RECEIPT_CMD}}` binding stale vs the live lane (section above).
- **F-SG156-2** — `G-L1` unusable on this host: `.rules-cache/` absent from the repo and the contract checkout
  is a grafted shallow clone whose HEAD is not tagged, so `rules_check.sh` cannot reconcile hashes (`UNCHECKED`,
  exit 3). Version chain read directly instead.
- **F-SG156-3** — packet premise `suite 2/649→2/661`: `649` not evidenced in any committed byte; `2/661`
  confirmed twice (original log + this run's re-run).
- **F-SG156-4** — SG-155's traceability gap is exactly as rated: no `Dispatch-ID` receipt for SG-155 exists;
  only the engine's kill-path `Partial-Receipt-ID: SG-155` note on the notes ref. This report + SG-156's receipt
  reference the recovered verification.

## UNCLEAR

- **FIRST READ:** whether A3's "identity line … first-hand" meant the SG-155 report must be authored by the
  original SG-155 process. Impossible (that process died before writing it) — resolved by authoring it in the
  SG-156 run from re-verified evidence with authorship marked honestly at the top.
- **DURING EXECUTION:** whether the packet's `{{RECEIPT_CMD}}` instruction should be followed literally. The
  bound script's precondition fails on this lane (`candidate_not_remote`), while the live engine consumes the
  notes-ref note; resolved by publishing the real receipt (notes ref) and reporting the stale binding as
  F-SG156-1 with the script's own refusal as evidence.
- **REMAINING:** Architect action on F-SG156-1 (rebind/retire `RECEIPT_CMD`) and F-SG156-2 (`G-L1` on a
  grafted cache); SG-155's audit may now be re-read against a complete report+receipt; comparison slice SG-157
  and T1b SG-158 are queued by the packet (outside this slice).

---

## Receipt — publication evidence (appended by the receipt-evidence commit)

Mechanism: note on `refs/notes/storagegenie-coder-reports` — the ref `run-coder`'s P3 asserts and `dispatch`'s
`receipted()` greps. Published on WORK_HEAD `4084d1c` at 2026-10-09T14:16:30Z (elapsed 355s of the 2100s budget).

    $ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-156 | Report: docs/worklogs/SG-156_report.md | Work-HEAD: 4084d1cfd70c22d01e801d12c679196646492368" 4084d1cfd70c22d01e801d12c679196646492368
    $ git push origin refs/notes/storagegenie-coder-reports
       8b588ee..6b65cc9  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
    $ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg156-fetched
     * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg156-fetched
    $ git notes --ref=refs/notes/sg156-fetched show 4084d1cfd70c22d01e801d12c679196646492368
    Dispatch-ID: SG-156 | Report: docs/worklogs/SG-156_report.md | Work-HEAD: 4084d1cfd70c22d01e801d12c679196646492368
    note_show_exit=0

`note=yes` — the note was read back from the **remote** (mapped fetch), not merely from the local store. This
receipt-evidence commit (the tip carrying this section) is annotated with the same note body after it is
committed (dual annotation, SG-092/SG-154 precedent); the engine then appends its
`Settings: coder=… model=… effort=…` line and re-proves the note on the remote (P3) before the dispatch is done.

Bound `{{RECEIPT_CMD}}` probe (F-SG156-1), same work HEAD, **no writes performed** (checked before staging):

    $ timeout 120 /opt/storagegenie-dispatch/finalize_dispatch_report.sh SG-156 "contract_sync=refresh version=0.17.2" docs/worklogs/SG-156_report.md 4084d1cfd70c22d01e801d12c679196646492368
    DISPATCH_BLOCKED_REPORT: candidate_not_remote
    finalize_exit=1

Production writes this slice: **0** (no docker, no DB, no `.env` touch, no served-code change). Spend:
**$0.000000** (two public keyless GETs only, 0 Authorization headers, re-proven in
`docs/worklogs/SG-156_t0recheck.log`).

SG-157 — Coder comparison: independent T0 re-verification on muse-spark/xhigh, $0

**Dispatch:** SG-157 · **Coder:** opencode · **Model:** `opencode-go/muse-spark-1.3-contributor` · **Effort:** `xhigh`
(read first-hand from process arguments, never from a system-prompt identity line: `/proc/1673911/cmdline` =
`opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/muse-spark-1.3-contributor --variant xhigh …`;
engine parent `bash /usr/local/lib/dispatch/run-coder SG-157`, pid 1673872.)
No effort refusal occurred at trigger or in-slice: the packet's CAVEAT condition never fired (see F-SG157-1).
**Work dir / origin:** `/home/andrei/StorageGenie` · `git@github.com:Andovol/StorageGenie.git`.
**BASE ref requested:** `automation` → **resolved commit:** `b948727` (branch tip at slice start; worktree clean —
`b948727 SG-156 rated 99 + RECEIPT_CMD rebound to notes-ref + SG-157 packet + state`).
**WORK_HEAD:** `10940c27e106bef1a75097a343dadfef0231c1b0` (`10940c2`) — the commit carrying the report and both
evidence logs; the receipt note names it back as `Work-HEAD:` and the verbatim publication transcripts are
in the Receipt section below.
**Contract echo:** `0.44.1` — recorded in `AGENTS.md` (rule-set line) == host checkout
`/home/andrei/storagegenie-contract/VERSION` = `0.44.1` (both read this run; `RULES.md` sha256 not re-read —
SG-156 already recorded the match, cited not re-derived).
**Rule-set check (`G-L1`):** same host limitation as F-SG156-2, re-measured: `.rules-cache/` absent from the repo
and `bash /home/andrei/storagegenie-contract/rules_check.sh` prints `G-L1 UNCHECKED …` and exits 3.
**Type:** same-scope comparison re-verification. No product-code change, no new tests owed (no defect found), no
datastore, no restart, no migration, no served-code change → no refresh. **Production writes: 0. Spend: $0.000000.**

---

## Premise verification (each packet claim checked against the tree / lane)

| packet premise | this run's verdict | evidence |
|---|---|---|
| SG-155 seam `backend/app/services/scene/openrouter.py` + 12 offline tests exist | CONFIRMED | `wc -l` = 188 (+7-line `__init__.py`); `backend/tests/test_sg155_scene_t0.py` read in full before running |
| `SG-155_t0live.log` + `SG-156_t0recheck.log` committed, both MATCH | CONFIRMED | both read; SG-156 log ends `VERDICT: MATCH` |
| SG-155/156 reports committed | CONFIRMED | `SG-155_report.md` (141 lines, recovered-authorship header), `SG-156_report.md` (173 lines) |
| expect 12/12, suite 2/661 same 2 `test_signals` env reds, ruff clean, mypy no scene errors | CONFIRMED | this run's `SG-157_verify.log` (see G1) |
| lane refuses `medium`/`xhigh` by name (caveat) | NOT OBSERVED — no refusal at any step | trigger `… --variant xhigh` executed; see F-SG157-1 |
| `{{RECEIPT_CMD}}` retired → notes-ref mechanism (F-SG156-1) | CONFIRMED, followed | receipt section below; no bound-script invocation attempted |

## G1 — independent re-verification (log: `docs/worklogs/SG-157_verify.log`)

Derived from my own reading of the test file (imports: `json`, `pytest`, `settings`, scene module — no network,
no key; asserts the explicit > settings-field > env > `None` seam, the frozen envelope, and three loud-refusal
constructors), then executed:

| gate | command (cwd `backend/`) | bound | result |
|---|---|---|---|
| SG-155 tests | `venv/bin/python -m pytest -q tests/test_sg155_scene_t0.py` | 120s | **12 passed in 0.09s** |
| full suite | `venv/bin/python -m pytest -q` | 600s | **2 failed, 661 passed in 33.07s** |
| ruff | `venv/bin/ruff check .` | 120s | **All checks passed!** (exit 0) |
| mypy | `venv/bin/mypy app` | 300s | **41 errors in 9 files**, none in `app/services/scene` (`grep -c services/scene` = 0) |

The two reds are exactly the expected `test_signals` environment class
(`test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier`,
`test_ocr_has_text_boxes_and_mean_confidence`; log shows the pyzbar/libzbar + tesseract absence warnings).
**No different red appeared, so the stash leg was not owed and not run** (stated explicitly, not skipped).
No defect found → no fix, no fail-pre owed (`PG-EV-09` applies to fixes; none occurred).

## G2 — fresh $0 T0a/T0b pass (log: `docs/worklogs/SG-157_t0recheck.log`)

Two public keyless GETs only (`curl --max-time 110`, bound 120s each): `GET
https://openrouter.ai/api/v1/models` (HTTP 200, 782046 bytes, `curl_exit=0`) and `GET
https://openrouter.ai/openapi.json` (HTTP 200, 2617419 bytes, `curl_exit=0`) — `curl -v` request dumps show
**0 Authorization headers on both** (verbatim `>` lines in the log). No chat/render call, no key used.
Comparison ran in my own harness (`/tmp/opencode/sg157_recheck.py`, stdlib only, vacuity guards: every derived
set must be non-empty or the harness FAILS loudly):

- **T0a image-output shortlist** (derived from live `architecture.output_modalities`, field probed not assumed):
  **12 entries, 10 real + 2 `openrouter/auto*`; slugs added none, removed none; all 12 pricing dicts MATCH.**
  `image_output` prices: gemini-2.5-flash-image 0.00003 · gemini-3-pro-image 0.00012 ·
  gemini-3-pro-image-preview 0.00012 · gemini-3.1-flash-image 0.00006 · gemini-3.1-flash-image-preview 0.00006 ·
  gemini-3.1-flash-lite-image 0.00003 · gemini-nano-banana-2.1 0.00003 · gpt-5-image 0.00004 ·
  gpt-5-image-mini 0.000008 · gpt-5.4-image-2 0.00003.
- **Orchestrator candidates:** all 10 SG-155 slugs re-looked-up in the fresh 469-entry catalogue — prompt and
  completion prices all MATCH. Beyond SG-156 (which re-checked but did not re-rank), I **independently
  re-derived the ranking** under a stated filter (image-in + text-out + tools/tool_choice support + paid
  prompt>0, `:free` excluded): 264 candidates; narrowing per SG-155's stated rule (no `:batch`, no `~`
  routing aliases) gives **179 — exactly SG-155's `paid vision+tools total: 179`** — and the narrowed top-10
  in order **equals the baseline 10**. The orchestrator shortlist is now derived, not just re-checked.
- **T0b stop schema:** 5 condition types `['finish_reason_is','has_tool_call','max_cost','max_tokens_used',
  'step_count_is']` MATCH; all 7 schema objects MATCH (outer compared decomposition-aware: the baseline log
  prints `items` on its own line — see harness disclosure 3); items ref MATCH.
- **Reference-image answer:** all 4 objects MATCH; server-tool config still declares no reference-image field →
  **TEXT-PROMPT-ONLY, unchanged**.

**Verdict line: MATCH — no drift.** (Three comparison-harness defects of mine — a shell typo that broke the
first T0a fetch, a baseline-format assumption on `Name -> {json}` lines, and an over-strict outer-schema
comparison — all caught and fixed before the committed final run; four fetch rounds total, all $0. Disclosed
here rather than hidden.)

## Comparison section (per observation vs SG-155/156; no aggregate scores — D30)

- **Approach — harness shape:** SG-156 compared with an undescribed script (two named bugs: an image-only map
  reused for orchestrator lookup, a colon/arrow parser miss). I wrote a fresh stdlib harness with explicit
  vacuity guards (empty derived set = loud FAIL) and an architecture-field probe. Observation: both runs hit a
  colon/arrow baseline-format bug independently — the SG-155 log's `Name -> {json}` rendering is the sharp edge,
  not model-specific behavior.
- **Approach — orchestrator depth:** SG-156 re-checked the 10 baseline slugs without re-ranking; I additionally
  re-derived the ranking and reproduced SG-155's total (179) and order exactly. Observation: the extra depth
  cost one filter iteration (the broad 264-candidate top-10 visibly contains `:batch`/`~` entries SG-155
  excludes) and converted a re-check into a derivation — worth it for a comparison run, arguably overkill for
  a recovery run.
- **Errors — count and profile:** SG-156 disclosed 2 harness bugs; I disclose 3 (listed in G2). Observation:
  same profile (shell/plumbing + baseline-format assumptions, zero product-code defects found by either run);
  the higher count on my side traces to rebuilding the harness from scratch rather than reusing SG-156's —
  independence trades bugs for correlation.
- **Errors — the near-miss verdict:** my over-strict outer-schema comparison printed a `DRIFT` line for one
  intermediate run before I recognized the baseline's items-on-own-line decomposition. Observation: a
  less careful run could have shipped a false-drift verdict against SG-156's MATCH — the packet's
  "difference is a finding" frame cut the right way here only because the items ref already MATCHed, which
  forced the re-examination. Mechanical comparators need like-for-like granularity checks.
- **Disclosures:** both runs disclose pre-commit harness bugs in-report; neither found a product defect to hide.
  Observation: no behavioral divergence on disclosure norms — the packet's explicit disclosure demand worked
  identically on both selections.
- **Timing/shape:** SG-156 actual 355s all-in; this run's verify leg (33.07s suite) and recheck leg track the
  same shape (expected ~300s). Observation: no selection-dependent duration signal in the work itself.
- **What this suggests:** on a read-only verify-and-compare slice, the two selections converge on verdicts
  (12/12, 2/661 same reds, MATCH) and on process (disclose-early harness fixes); the observable differences
  are harness-depth choices, not conclusions. One genuine extension over SG-156: the orchestrator ranking is
  now independently derived (179 + order), strengthening the T0-PINNED block T1b consumes.

## A5 — guards invoked

| guard | how this slice invoked it |
|---|---|
| `PG-EV-04` | SG-155 tests verified offline by reading imports before running; the only live traffic is the two public GETs, proved keyless by `curl -v` request dumps (0 Authorization headers) |
| `PG-EV-09` | No fix was made → no fail-pre owed; the single verification run is committed as `SG-157_verify.log` (not claimed as fail-then-pass) |
| `PG-SC-03` | No keyed call exists in scope; the missing key is irrelevant and was **not** grounds to stop; both legs answered fresh |
| `PG-IC-01` | No blanket bans in the packet; every criterion named its own action; only reads + two public GETs + three `SG-157_*` worklog files |
| `PG-IC-03` | Stop precedence held: no defect found, so no fix-vs-STOP conflict arose; no re-verify loop |
| `PG-IC-07` | Live clock at each step (`date -u` lines in both logs); no fixed date/time in any command |
| `PG-IC-08` | $0, both directions: no metered call attempted; production writes 0 (no docker, no DB, no `.env` touch, no served-code change) |
| `PG-IC-09` | Every packet premise re-verified against the tree/lane (table above); the one non-confirmation (xhigh caveat) is a finding (F-SG157-1), not an inheritance |

**Vacuity check (loud):** nothing passed vacuously — the suite genuinely collected and ran 663 tests (661
green, 2 named env reds); both GETs genuinely fetched (HTTP 200, byte counts on record, bodies parsed and
mechanically compared); the SG-155 tests genuinely exercise the built request; the harness FAILS (exit 2) on
any empty derived set.

## Findings

- **F-SG157-1** — the packet's CAVEAT (project lane note: the lane refuses `medium`/`xhigh` by name) did not
  fire: `opencode run … --variant xhigh` dispatched and executed end to end with no refusal at trigger or
  in-slice. Either the note describes a different layer (lane conf vs dispatch wrapper) or it is stale after
  the D-1009-9 comparison queue was accepted. Owner call: reconcile the note or record the exception — no
  silent fallback occurred in either direction.
- **F-SG157-2** — `G-L1` still unusable on this host (same as F-SG156-2, re-measured this run): `.rules-cache/`
  absent, `rules_check.sh` exits 3 with `G-L1 UNCHECKED`. Version chain read directly (recorded 0.44.1 ==
  published 0.44.1). Standing item, no new action beyond SG-156's.
- No product-code finding: the SG-155 seam, envelope, and T0-PINNED values stand as committed.

## Timing (publish-before-bound)

Slice start 2026-10-09T14:21:58Z (`RUN_BUDGET_S=2100`, half-bound = 1050s → publish deadline 14:39:28Z).
Reports + receipt publication timestamps and elapsed in the Receipt section below.

## UNCLEAR

- **FIRST READ:** whether "re-derive the shortlist slugs" (G2) demanded re-ranking the orchestrator list or
  re-checking it. Resolved by doing both: re-check of all 10 slugs plus an independent ranking derivation
  that reproduces SG-155's total and order — either reading is now satisfied.
- **DURING EXECUTION:** whether my intermediate `DRIFT` line on `StopServerToolsWhen` was catalogue drift.
  Resolved as harness artifact (baseline logs `items` separately; decomposition-aware comparison MATCHes on
  both parts) — disclosed above, final log line is MATCH.
- **REMAINING:** owner reconciliation of F-SG157-1 (xhigh lane note vs observed acceptance); T1b SG-158
  consumes the T0-PINNED block (unchanged, now triple-confirmed SG-155/156/157).

---

## Receipt — publication evidence (appended by the receipt-evidence commit)

Mechanism: note on `refs/notes/storagegenie-coder-reports` — the ref `run-coder`'s P3 asserts and `dispatch`'s
`receipted()` greps. Published on WORK_HEAD `10940c2` at 2026-10-09T14:24:54Z (elapsed 176s of the 2100s budget;
reports commit pushed at 14:24:47Z, elapsed 169s — publish-before-bound honored against half-bound 1050s).

    $ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-157 | Report: docs/worklogs/SG-157_report.md | Work-HEAD: 10940c27e106bef1a75097a343dadfef0231c1b0" 10940c27e106bef1a75097a343dadfef0231c1b0
    $ git push origin refs/notes/storagegenie-coder-reports
       f388058..f7e85fd  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
    $ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg157-fetched
     * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg157-fetched
    $ git notes --ref=refs/notes/sg157-fetched show 10940c27e106bef1a75097a343dadfef0231c1b0
    Dispatch-ID: SG-157 | Report: docs/worklogs/SG-157_report.md | Work-HEAD: 10940c27e106bef1a75097a343dadfef0231c1b0
    note_show_exit=0

`note=yes` — the note was read back from the **remote** (mapped fetch), not merely from the local store. This
receipt-evidence commit (the tip carrying this section) is annotated with the same note body after it is
committed (dual annotation, SG-092/SG-154/SG-156 precedent); the engine then appends its
`Settings: coder=… model=… effort=…` line and re-proves the note on the remote (P3) before the dispatch is done.

Production writes this slice: **0** (no docker, no DB, no `.env` touch, no served-code change). Spend:
**$0.000000** (four public keyless GET rounds — one discarded harness-bug round + three final — 0 Authorization
headers on every round, re-proven in `docs/worklogs/SG-157_t0recheck.log`).

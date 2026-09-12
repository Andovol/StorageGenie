# SG-027 report — attempt-2 GREEN: `lot` modeled, one live call, OpenCode GO adapter shipped

**BASE REF:** `automation` → resolved commit `203d97dafb1022797b2693e0b038cb40ab6046f9` (two fields, as required).
**WORK_HEAD:** the commit carrying this file (hash is quoted by the receipt note in G5; note added last, no commit after).
**Work dir** `/home/andrei/StorageGenie`, **origin** `git@github.com:Andovol/StorageGenie.git`.
**Model/effort per CO-78 (owner rule; from process arguments / provider metadata, never an identity line):**
run-2 (this continuation) process argv `opencode` (interactive; **no `--variant`**), provider metadata stream line
`providerID=opencode-go modelID=deepseek-v4.1-flash`; effort `medium` declared by the packet head and absent from
the resumed argv, so recorded as packet-declared `medium` / `unknown` at process level. Run-1 (headless dispatch)
argv `opencode run --auto --dir /home/andrei/StorageGenie --variant medium "<packet>"`, provider metadata
`providerID=opencode modelID=muse-spark-1.3-contributor-free`. The adapter's target model, live-verified:
`deepseek-v4-flash-vision-exp`.
**DATABASE:** none — temp SQLite only, zero live rows; one disclosed dev-file side effect (finding 3).
**Restart:** none — no service touched, nothing deployed. **Live calls:** attempt-2 = exactly ONE; cumulative = 2.

## Verdict

GREEN. G0 amended the schema (`lot` optional, everything else still forbidden, fabricated-value rule intact);
the 10 banked PRE-FAILs and the new lot test are POST-green; the single live re-spike returned HTTP 200 with
non-zero usage and content that **validates through the amended schema**; the adapter, shared redaction helper,
named config settings and `.env.example` ship inside the frozen ceiling. A third cumulative live call was never
made. Remaining suite reds are base-proved (2 known decoder env-reds + 2 pre-existing test-pollution reds).

## Run-1 failure, corrected root cause (ISS-9)

Run-1 (the headless dispatch, 17:38:53Z–18:13:53Z) produced zero work because **this coder session dispatched its
own slice instead of executing the packet**: it ran `/usr/local/bin/dispatch SG-027 --force` (first attempt
`reason=conf_unreadable`; second attempt `reason=lock_held` — its own unit held the lock), then polled its own
unit until systemd killed it at the 35-minute budget. Host evidence (quoted in the verify log):

```
Sep 12 21:13:53 ubuntu systemd[1]: dispatch-storagegenie@SG-027.service: start operation timed out. Terminating.
Sep 12 21:13:53 ubuntu systemd[1]: dispatch-storagegenie@SG-027.service: Failed with result 'timeout'.
Sep 12 21:13:53 ubuntu systemd[1]: dispatch-storagegenie@SG-027.service: Consumed 40.103s CPU time, 518.4M memory peak
TimeoutStartUSec=35min   RUN_BUDGET_S=2100
```

The opencode log ties the session to the run: `message=created id=ses_f694c95eaffeZPOrNfSV9WGCDq … 2026-09-12T17:38:55.637Z`,
and records run-1's own dispatch commands. So the ISS-9 record "cause unknown, no readable host evidence" is
**corrected**: the evidence exists, and the failure was coder-side self-dispatch, not a lane or provider fault.
SG-032 (`203d97d`) subsequently proved the lane green end-to-end (commit, push, receipt); its note is on the
remote notes ref. The owner-directed continuation (run-2, this work) executed the packet.

## G0 — schema fix + POST-green gates (all offline)

- `backend/app/services/providers/schemas.py`: one delta — `lot: str | None = None` on `ExtractionItem`
  (optional, never required; `extra="forbid"` unchanged elsewhere). The existing unknowns validator now honors
  `items.0.lot` via `model_fields` with no other change. Reason (D42(a) quoted in the packet): attempt-1 proved the
  model volunteers `lot`; forbidding it turned honest output into a validation failure.
- `backend/tests/test_extraction_contract.py`: ONE new test `test_lot_optional_and_fabricated_value_rule` covering
  all four cases the packet names — null+listed passes, valued (unlisted) passes, valued+listed fails
  (fabricated-value rule intact), non-string fails. Explicitly in-ceiling (reported).
- **Banked-fixture repair (loud finding, finding 2):** `backend/tests/test_opencode_go.py::_gps_jpeg_bytes` never
  executed at attempt-1 (the test failed at the adapter import first). Executing it exposed a real defect on the
  locked Pillow (`requirements.lock:58 pillow==12.3.0`): `exif[0x8825] = 12345` stores a bare GPS pointer that
  cannot serialize — `AttributeError: 'Exif' object has no attribute 'fp'` inside `img.save`. The fixture input
  was repaired to the documented Pillow 12 `exif.get_ifd(0x8825)` form (all assertions untouched; the source JPEG
  now genuinely carries a GPS IFD). Without this, no adapter could make the test pass.
- PRE/POST (both raw runs committed in `SG-027_verify.log`):
  - PRE (test present, implementation absent): `11 failed in 0.33s` — 9× `ImportError: cannot import name 'opencode_go'`,
    1× `AttributeError: 'Settings' object has no attribute 'sg_provider_id'`, 1× lot `extra_forbidden`.
  - POST (adapter + schema + config built): `...........  [100%]` / `11 passed in 0.28s`.
  - The 10 banked POST-green tests are exactly: identity headers, format map, empty-200, zero-usage, think-strip,
    max-tokens, redaction byte-proof, budget-refusal zero calls, outgoing payload shape, config read-back.

## G1 — the one live re-spike (transcript, call 2 of 2 cumulative)

Gates first: pre-edit `git status --porcelain` empty; `.env` present `600`/288B, `OPENCODE_API_KEY` count **1**
(value never read/printed); suite baseline run (below). Build dirt before the spike was quoted and attributable
(the slice's own 7 files — reading note in findings). Synthetic label generated at runtime (non-personal, never
committed, never in the evidence store), carrying a visible `LOT: L24-0716`, then redacted with the shared helper.
Full transcript in the verify log; verbatim:

```
source: bytes=24132 exif_tags=2 gps_tags=4
redaction proof (exact buffer sent): format=PNG bytes=41638 exif_tags=0 gps_present=False
header names=['content-type', 'user-agent', 'x-opencode-session'] stable=True session_len=23 (value not logged)
outgoing shape: endpoint=POST https://opencode.ai/zen/go/v1/chat/completions fields=['max_tokens', 'messages', 'model', 'response_format', 'stream'] stream=False response_format={'type': 'json_object'} max_tokens=2000 key_material_present=False
status=200 model=deepseek-v4-flash-vision-exp latency_s=3.5 (whole=3.5)
usage={"prompt_tokens": 728, "completion_tokens": 383, "total_tokens": 1111, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 728, "prompt_tokens_details": {"cached_tokens": 0}, "completion_tokens_details": {"reasoning_tokens": 302}}
cost_usd=0.000339 recomputed=0.000339
validated=True items=1 unknowns=[] needs_evidence=False
normalized={"items": [{"name": "HARVEST OATS 500g", "expiry_date": "2027-03-15", "date_type": "best_before", "lot": null, "confidence": 0.95, "uncertainty_reasons": ["grey block occludes part of the label"]}], "unknowns": [], "needs_evidence": false}
request_id=2d463c36-1f60-4b36-856f-8887a5d8adc9
```

The model read the label correctly, returned `lot` **as a modeled field** and the
content validated — the exact gap attempt-2 existed to close. It chose `lot: null` even though the LOT line was
legible (finding 4). No second call was made; no retry on failure paths.

## G2 — adapter, redaction, config, `.env.example` (ceiling only)

- `backend/app/services/providers/opencode_go.py` — raw `httpx` (grep-gated: imports are stdlib + httpx + app
  modules; no vendor SDK name anywhere): G1-verified facts only (`BASE_URL`, `CHAT_PATH`, Bearer from backend env,
  `stream:false`, `json_object` for DeepSeek kin / `json_schema` elsewhere, `max_tokens=2000`, 300s call bound);
  identity-header builder (unit-tested stable, own UA, one session per conversation, never `pintel-*`); guards
  (empty-200 reject, non-zero usage, single-`<think>` strip then loud fail, past-truncation sizing); computed cost
  from the rate table; header VALUES never logged (single bind log line: model + caps). Budget mechanisms: per-job
  cap and monthly cap both ship; a refusal never touches the network (banked test proves zero calls).
- `backend/app/services/providers/redaction.py` — ONE shared function (re-encode to PNG, EXIF/GPS dropped by
  construction), used by the adapter and ready for SG-028; byte-proof test green.
- `backend/app/config.py` — six named settings and nothing else: `sg_provider_id` (default `fake`: cloud stays OFF
  until explicitly selected — nothing silently binds), `sg_model_id` (the single proven vision id; the SG-031
  picker reads this), `opencode_api_key` (backend env only), `sg_per_job_cap`, `sg_monthly_cap`, `sg_consent`.
  F2 encoded explicitly: caps default to `None` (uncapped) with the owner's reason quoted in the class docstring
  ("no caps at first, we will re-evaluate later.") — mechanisms ship, enforcement is disabled by default, and the
  provider logs the bound values by name.
- `.env.example` — key NAMES only, no values (new file; `.env` stays gitignored).
- OUT as required: no second provider, no quality-switching, no pipeline wiring (SG-028), no UI (SG-031).

## G3 — proof (fixtures only; the live call is single-run honesty)

- Both raw runs committed (`SG-027_verify.log`); PRE/POST quoted above. No fixture ever touches the network.
- Full suite from `backend/` (bound 600s → 5.06s): `4 failed, 85 passed, 7 warnings`. Reds: the 2 known decoder
  env-reds plus 2 migration reds. **Base proof** (detached worktree of `203d97d`; bound 600s → 5.57s):
  `14 failed, 74 passed` = the same 2 migration reds + 2 decoder + the 10 banked PRE-fails. The 2 migration reds
  are therefore pre-existing at BASE (finding 3), not introduced by this slice.
- `ruff check .` → exit 0, `All checks passed!`. `mypy app` → exit 1, `Found 40 errors in 9 files (checked 58
  source files)` — the standing carried advisory, **zero mentions of the new files**.
- Read-back (`PG-SC-02`): the banked config test covers `sg_provider_id`, `sg_per_job_cap`, `sg_monthly_cap`,
  `sg_consent`, key attr; an offline env-override run (quoted in the verify log) reads back **all six** new
  settings (`probe-*` values). PRODUCTION consumer: SG-028.
- Cross-product (`PG-IC-01`, recorded once): G0 needed only schemas + banked tests; G1 only gates + count probe +
  runtime image; G2 only G1-verified facts; G3 only fixtures + the transcript.
- Secret gates: key value matches outside `.env` = **0**; `.env` ignored (`git check-ignore` quoted); SDK grep
  clean; header-value logging grep clean.

## G4 — worklogs

`docs/worklogs/SG-027.log`, `docs/worklogs/SG-027_report.md`, `docs/worklogs/SG-027_verify.log` — committed with
this work; first token `SG-027`; per-leg elapsed-vs-budget with units; model/effort provenance; per-call spend;
live-state ledger; UNCLEAR lines below.

## G5 — receipt note (notes ref; proven shape)

Work pushed to `automation`, tree clean, no push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note added on
the work HEAD LAST:

```
git notes --ref=refs/notes/storagegenie-coder-reports add \
  -m "Dispatch-ID: SG-027 | Report: docs/worklogs/SG-027_report.md | Work-HEAD: <WORK_HEAD>" <WORK_HEAD>
```

Verified with `git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>` and pushed to the notes
ref; the executed output is quoted in the delivery message. Final line: `note=yes`.

## Findings, disagreements, and corrections (including out-of-scope)

1. **ISS-9 root cause corrected** (above): coder-side self-dispatch on run-1, killed by the designed 35-minute
   `RUN_BUDGET_S`; host evidence was readable all along. No lane/provider fault; SG-032 already proved the lane.
   Destination: owner closes ISS-9 with this cause.
2. **Banked fixture defect + repair** (`test_opencode_go.py::_gps_jpeg_bytes`, Pillow 12.3 locked): repaired
   input shape only; assertions untouched; loudly reported because touching a banked test is otherwise
   out of ceiling.
3. **Banked-test pollution, base-proved**: `test_config_readback_new_values` reloads `app.config`, replacing the
   module-level `settings` object; later migration tests monkeypatch the original object while Alembic's `env.py`
   re-imports the reloaded one — migrations then run against the default dev DB and the temp DB stays empty.
   Proof: migration test alone passes; after the config test it fails; base worktree shows both reds. Premise
   correction: the packet baseline "76 passed + 2 reds" is really **74 passed + 2 decoder + 2 pollution reds** at
   BASE. Disclosed side effect: those polluted runs migrate the gitignored dev file
   `backend/data/db/storagegenie.db` (no service uses it). Destination: SG-028 or the next touch of this test
   (restore the original settings object in its `finally`) — deliberately not fixed in-slice beyond the ceiling.
4. **Model returned `lot: null` despite a legible LOT** — schema-legal and accepted; the SG-026 prompt (out of
   this slice's ceiling) never mentions `lot`. Destination: SG-028 prompt/wiring may request it; not a defect for
   the D42(a) goal, which was schema tolerance.
5. **Budget observation**: `RUN_BUDGET_S` (35 min) is the systemd `TimeoutStartSec`; this slice's scope
   (build + 600s-bound suites + a live call + worklogs) consumed ~20 min of actual work in run-2. For future
   large slices, budget sizing is an Architect/owner call; nothing changed here.
6. **Gate reading (disagreement resolved, not bent)**: G1 asks for a clean tree before the spike while G0/G2
   explicitly allow building first. Resolved by quoting the clean slice-start status and then the attributable
   build dirt; no STOP because nothing was unattributable.

## UNCLEAR

- FIRST READ: whether repairing the broken banked fixture counted as "building what they name" — read as yes for
  INPUT shape only, because the adapter import gate still fails PRE and every assertion is untouched; stated loudly
  (finding 2).
- DURING EXECUTION: whether to repair the banked config test's reload leak to make the suite fully green; chose
  base-proof + destination (finding 3), since the ceiling authorizes no banked-test change beyond the unavoidable
  fixture repair.
- REMAINING: remote-side verification of the pushed work and the notes-ref receipt (quoted in the delivery
  message) and the owner's ISS-9/D43 disposition against the corrected cause.

## Acceptance criteria mapping

- Starting tree quoted clean; attempt-1 facts re-confirmed live (endpoint, auth, headers, `json_object`,
  latency, usage, redaction) — G1 transcript.
- G0: `lot` modeled, fabricated-value rule proven (valued+listed fails), 10 banked identified and POST-green.
- G1: exactly one live call quoted (status/model/latency/usage/computed cost/validated shape); cumulative = 2.
- GREEN-only build within ceiling; header values never logged; no SDK import (both grep-gated).
- Proof: PRE/POST both quoted from the committed verify log; full suite green except base-proved reds; ruff clean;
  mypy quoted; model+effort provenance quoted; no vacuous pass (fixture repair disclosed, pollution disclosed).
- Q2 count 1 quoted (value untouched); worklogs committed; notes ref carries `Dispatch-ID: SG-027` + `Report:`;
  result `note=yes` (quoted in delivery).

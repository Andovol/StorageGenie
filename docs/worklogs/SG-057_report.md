# SG-057 — provision proof: backend-routed metered import E2E, one image

- **Dispatch:** SG-057 (L3 stage D80, consistency batch slice 1 of 4)
- **Coder / effort:** opencode · **medium** (read from process argv `--variant medium`)
- **Model:** `unknown` — argv carries no model id (policy: CLI default IS model); no provider
  metadata exposing the Coder model was observable. `deepseek-v4-flash-vision-exp` in
  `/v1/settings/ai` is the *vision adapter's* model, not the Coder's. Not guessed.
- **Work dir:** `/home/andrei/StorageGenie`; remote `origin git@github.com:Andovol/StorageGenie.git`
- **BASE ref:** `origin/automation` → resolved commit `9db7f23b03902a6c5d7605fb92d0e89aa7230fb1` (two fields)
- **WORK_HEAD:** `<set at receipt>`
- **Contract:** 0.27.0
- **DB:** production SQLite `sqlite:////data/db/storagegenie.db` (import only, rows stay — `PG-PR-10`, D80); no tests run (no code changes)
- **Verdict:** **GO** — backend-routed metered import completed end-to-end.

## G1 — pre-state (read-only, FIRST; no provider call preceded it)

- `git status --porcelain` → **empty** (clean). branch `automation`; HEAD = `9db7f23…`; `origin/automation` = `9db7f23…`.
- Health (deployed): `curl http://localhost:8003/v1/health` →
  `{"status":"ok","db":"ok","storage":"ok"}`
- `GET /v1/settings/ai` → `{"provider_id":"opencode-go","model_id":"deepseek-v4-flash-vision-exp",
  "allowed_model_ids":["deepseek-v4-flash-vision-exp"],"consent":true,"per_job_cap":null,
  "monthly_cap":null,"prompt_category":"food"}`
  → provider + consent confirmed; caps null = uncapped by standing F2 decision.
- **Environment finding (two-field, not a stop):** the packet/AGENTS `{{HEALTH_CMD}}` names
  `http://localhost:8000/v1/health`; the composition publishes `127.0.0.1:8003:8000`
  (`docker-compose.yml:8`) and `:8000` returns `Not Found` from a non-backend app. I probed and used
  **:8003**, the real deployed endpoint. Requested ref `:8000`; resolved `:8003`.
- Blast baseline (prod, counts only):
  `asset=1 candidate=0 job=1 evidence=1 assertion=3 audit_event=6 provider_call=5`,
  plus `asset_evidence=1 job_step=8 observation=2 idempotency_key=2 household=1 user=2`,
  `guardrail_event=0 planning_suggestion=0 review_task=0 source_attribution=0`.
- Toothpaste name (baseline): `Toothpaste` (`asset.id=01a0a467-eb0e-7b83-a227-af122dc9268b`).
- Pre-existing ledger rows (ids): `01a0af39-8d7e-7670-b30e-e456d6ec5cd9`,
  `01a0af39-9a47-7613-b657-907808cdb9b0`, `01a0af3a-5180-7a00-b165-e688d446e8ad`,
  `01a0af3a-5c3d-76a3-94ba-74b356dac7fc`, `01a0af3a-80cb-7bd0-9dab-3fc6bdc2856f` (all `job_id` null).
- Image pick: `backend/eval/corpus/sg029/images/sg029_01_clean_food.png` — **the smallest-bytes FOOD
  image** (9709 B; the only smaller file, `sg029_09…cosmetics.png`, is not food). `sha256=6c4cbf2e…`.
  No other image touched all slice.

## G2 — bound FIRST (`PG-IC-04`, `G-A9` uncalibrated)

Computed in-slice from the **deployed** estimator after the shared redaction the pipeline applies:

```
orig_bytes 9709 · redacted_bytes 10581 · prompt_version extract-food-v2 · prompt_bytes 2710
estimate_usd_per_call = 0.0037227
```

- **Worst-case bound:** 1 call = **$0.0037227**; the single allowed repair makes the logical call
  worst-case 2 metered calls = **$0.0074454**. Import run wall bound 900 s.
- Pre-call refusal path: `per_job_cap=null`, `monthly_cap=null` → no refusal triggered; **nothing was
  refused and nothing was routed around** (`PG-PR-03`). Router `cost_budget=inf`.

## G2 — the import (real HTTP path, loopback)

1. `POST /v1/evidence?household_id=01a0a029-1477-7ca0-b200-bce78a96c679` — multipart
   `sg029_01_clean_food.png` — **201** (0.038 s), `Idempotency-Key: sg057-ev-f59ed209-675d-47b9-b7ee-627be1921595`
   → `{"id":"01a0afaa-145d-7f21-b647-703aaa693f5a","sha256":"6c4cbf2e…","size_bytes":9709,...}`
2. `POST /v1/imports?household_id=01a0a029-1477-7ca0-b200-bce78a96c679` — body
   `{"evidence_ids":["01a0afaa-145d-7f21-b647-703aaa693f5a"],"config":{}}` —
   `Idempotency-Key: sg057-imp-03c0dab8-37d7-452c-b6ba-54f6f6f29723` — **201** (0.014 s)
   → job `01a0afaa-235a-7fe3-8422-1be2b555c921`, state `CREATED`.
3. `POST /v1/imports/01a0afaa-235a-7fe3-8422-1be2b555c921/run?household_id=…` — **200** (4.501 s)
   → state **`AWAITING_REVIEW`**.

Server log for the window (`docker logs … --since 13:59:00Z`) shows exactly the three calls, no errors,
and `grep -c decision` = **0**. Full raw bodies (all three) are pasted in
`docs/worklogs/SG-057_verify.log`.

**Terminal-state establishment (no vacuous pass — the criterion requires ALL):**

- Job state machine observed value: **`AWAITING_REVIEW`** (`AWAITING_REVIEW_STATE`).
- `ANALYZING_WITH_AI` step: `status=ok`, `provider=opencode-go`,
  `model=deepseek-v4-flash-vision-exp`, `prompt_template_version=extract-food-v2`,
  `provider_call_ids=["01a0afaa-3fed-7d43-8adc-5e2976e4544b"]` — the **metered adapter**, not a fake path.
- Candidate `01a0afaa-3ff4-7da0-987a-87f29c73ee5b` `state=proposed`, and each field carries
  `source_type=extraction`, `provider=opencode-go`, `provider_call_id=01a0afaa-3fed-…`
  (extraction provenance). Deliberately **no** `POST /candidates/{id}/decision` — candidate stayed
  `proposed`; proven by the server-log `decision` grep = 0 and `asset` +0.
- Ledger row `01a0afaa-3fed-7d43-8adc-5e2976e4544b`: `provider=opencode-go`,
  `model=deepseek-v4-flash-vision-exp`, **`cost=0.00053505`**, `error_state=NULL`,
  `usage_json={"prompt_tokens":959,"completion_tokens":652,"total_tokens":1611,...}`,
  `latency_ms=4231.27`, `job_id=01a0afaa-235a-…`. Real usage — retires the "silent fallback /
  deterministic-only path" world (`PG-SC-09`).

## G2 — blast delta (diffs, either direction binds)

| table | before → after | delta | expected |
|---|---|---|---|
| job | 1 → 2 | **+1** | +1 ✓ |
| evidence | 1 → 2 | **+1** | +1 ✓ |
| candidate | 0 → 1 | **+1** (all `proposed`) | ≥1 ✓ |
| provider_call | 5 → 6 | **+1** | ≥1 ✓ |
| asset | 1 → 1 | **+0** | +0 ✓ |
| assertion | 3 → 3 | 0 | equal ✓ |
| household | 1 → 1 | 0 | equal ✓ |
| guardrail_event / planning_suggestion / review_task / source_attribution | 0 → 0 | 0 | equal ✓ |
| user | 2 → 2 | 0 | equal ✓ |
| alembic_version | 1 → 1 | 0 | equal ✓ |
| job_step | 8 → 16 | **+8** | see below |
| observation | 2 → 4 | **+2** | see below |
| audit_event | 6 → 10 | **+4** | see below |
| idempotency_key | 2 → 4 | **+2** | see below |

Toothpaste name after: `Toothpaste` (equal). Stored file: `sha256=6c4cbf2e…` at
`storage/…/6c/6c4cbf….png`, 9709 B (hash matches the upload) — +1 file. Two derived thumbnails
(256/512) were also written by the upload path (files, not table rows).

### Delta interpretation (`PG-IC-09` — premise corrected, loudly)

The packet's literal `"all other tables equal"` is **false as stated**: one import unavoidably writes
its own machinery rows. Named, with identifiers:

- `job_step +8` — `create_job` writes one row per step for the new job (`job_service.py:87-96`).
- `observation +2` — `EXTRACTING_DETERMINISTIC_SIGNALS` wrote `ocr`+`phash`
  (`01a0afaa-2f4f-7970-afd9-13e9759f3ebf`, `01a0afaa-2f4f-7970-afd9-13f76627a1a0`).
- `audit_event +4` — `evidence.create`, `job.create`, and two `job.state_transition`
  (`job-runner`) for the new job (`job_service.py:58-67,97-106`). The packet's own `PG-PR-10` scope
  line explicitly names *audit* rows as expected.
- `idempotency_key +2` — the two **fresh** `Idempotency-Key` headers the packet required.

No *un-commanded domain* mutation occurred: no asset, no source_attribution, no review_task, no
planning_suggestion, no guardrail_event. Read per `PG-SC-03`/`PG-IC-09` as inherent machinery of the
one commanded job, not `"anything else created"`; reported as a finding, not silently absorbed. If the
Architect intends the literal reading, this is the single point to rule on.

## Spend (REAL metered $)

- **This slice actual: $0.00053505** (1 metered call, 1611 tokens) — vs worst-case bound
  **$0.0037227** (1 call) / **$0.0074454** (2 calls incl. one repair). Units USD.
- Cumulative household ledger (via job join): **$0.00053505**.
- Every call's real cost/usage row is committed and **LEFT in place** (ISS-11); no row was rolled back.
- Caps null → no pre-call refusal; nothing routed around.

## Constraints check

- No code hunks: diff is confined to `docs/worklogs/SG-057.{log,_report.md,_verify.log}`.
- No migration; no new dependency; network = loopback + the metered provider leg only.
- `docker compose config` **never run**. No push to `storagegenie-evidence`; `{{RECEIPT_CMD}}` **not run**.
- Secret gate: worklogs grepped for key patterns → **0 hits** (quoted in verify log).
- Full test sweep **WAIVED** per `PG-DP-02`; substitute = the quoted live import named here.
- STOP-path spend: $0 (no STOP taken).

## Receipt note (`refs/notes/storagegenie-coder-reports`)

_To be pasted after the note is pushed and re-fetched (M20-corrected block)._

## UNCLEAR

- **FIRST READ:** whether G2's `"all other tables equal"` was meant to forbid the job's own
  job_step/observation/audit/idempotency rows (impossible for any real import) or only un-commanded
  domain mutation. I read it as the latter and reported the machinery rows explicitly.
- **DURING EXECUTION:** why the packet/AGENTS health probe names `:8000` while the composition
  publishes `:8003`. Resolved in-slice by probing both; the documentation is stale.
- **REMAINING:** the Coder's model id is not derivable from process argv (model omitted per policy) or
  observable provider metadata; reported `unknown` rather than a plausible guess.

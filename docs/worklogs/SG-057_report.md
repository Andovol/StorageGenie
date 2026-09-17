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

Commands executed (raw), bound 300 s (completed in a few seconds):

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-057 | Report: docs/worklogs/SG-057_report.md | Work-HEAD: d609a678a2c8b6d4662695aa95ef2dfbc9dc0223" d609a678a2c8b6d4662695aa95ef2dfbc9dc0223
add_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   1e137b4..00dcc36  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-verify
From github.com:Andovol/StorageGenie
   c780487..00dcc36  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-verify
fetch_exit=0
```

`git notes list` emits `<note-blob> <annotated-object>` pairs, not bodies, so the contents were listed by
dereferencing each note blob and grepping the actual body (the packet's `log --grep` warning):

```
$ git notes --ref=refs/notes/storagegenie-coder-reports-verify list | while read -r note obj; do
    body=$(git cat-file -p "$note" | head -1); printf '%s -> %s\n' "$obj" "$body"; done
009bf1145b9ace5f2b73ba7451bc2e9b5e5ba76b -> Dispatch-ID: SG-021 | Report: docs/worklogs/SG-021_report.md | Work-HEAD: 009bf1145b9ace5f2b73ba7451bc2e9b5e5ba76b
0be0315020544c83aff2fb3dec066f0ac68789bb -> Dispatch-ID: SG-027 | Report: docs/worklogs/SG-027_report.md | Work-HEAD: 0be0315020544c83aff2fb3dec066f0ac68789bb
0c3b5702a7fede00cb939b88aa605fdd766b9062 -> Dispatch-ID: SG-042 | Report: docs/worklogs/SG-042_report.md | Work-HEAD: 0c3b5702a7fede00cb939b88aa605fdd766b9062
0c6100f5081d04f0e15f38d69d53132875b64d12 -> Dispatch-ID: SG-044 | Report: docs/worklogs/SG-044_report.md | Work-HEAD: 0c6100f5081d04f0e15f38d69d53132875b64d12
174206cd1c7ac7bc2c4758255b20c164f753f6a3 -> Dispatch-ID: SG-030 | Report: docs/worklogs/SG-030_report.md | Work-HEAD: 174206cd1c7ac7bc2c4758255b20c164f753f6a3
1932f8ac27fca0ffd614e4fa83d1b70a946d3416 -> Dispatch-ID: SG-049 | Report: docs/worklogs/SG-049_report.md | Work-HEAD: 1932f8ac27fca0ffd614e4fa83d1b70a946d3416
1dc63ec26cc531ca88c36f7d240f7b5354fdfb8f -> Dispatch-ID: SG-013 | Report: docs/worklogs/SG-013_report.md | Work-HEAD: 1dc63ec26cc531ca88c36f7d240f7b5354fdfb8f
1e0f5b3d8935c455d9c0c9dba5657eb97e3a9ae2 -> Dispatch-ID: SG-055 | Report: docs/worklogs/SG-055_report.md | Work-HEAD: 1e0f5b3d8935c455d9c0c9dba5657eb97e3a9ae2
203d97dafb1022797b2693e0b038cb40ab6046f9 -> Dispatch-ID: SG-032 | Report: docs/worklogs/SG-032_report.md | Work-HEAD: 203d97dafb1022797b2693e0b038cb40ab6046f9
212cb1c2a982a3afcc7c177cf618349af17f3790 -> Dispatch-ID: SG-045 | Report: docs/worklogs/SG-045_report.md | Work-HEAD: 212cb1c2a982a3afcc7c177cf618349af17f3790
275a62626a0b7d5dfd960b775175ded71b631ad4 -> Negative-Receipt-ID: SG-042
29be0d6bd244d38099b232cba518d980d5b1a26c -> Negative-Receipt-ID: SG-056
307ae8c8698a2950fe22d8f7f04d67be30b16f8f -> Dispatch-ID: SG-043 | Report: docs/worklogs/SG-043_report.md | Work-HEAD: 307ae8c8698a2950fe22d8f7f04d67be30b16f8f
32363ac426cb37ed998846421748c60de3e3fe8b -> Dispatch-ID: SG-041 | Report: docs/worklogs/SG-041_report.md | Work-HEAD: 32363ac426cb37ed998846421748c60de3e3fe8b
3993c369dd8bffd1ecd7f8bd4ae96f9cda726e80 -> Dispatch-ID: SG-023 | Report: docs/worklogs/SG-023_report.md | Work-HEAD: 3993c369dd8bffd1ecd7f8bd4ae96f9cda726e80
40ae5e875cf76840d40aebf7a1a3f86d1bd11af9 -> Dispatch-ID: SG-039 | Report: docs/worklogs/SG-039_report.md | Work-HEAD: 40ae5e875cf76840d40aebf7a1a3f86d1bd11af9
450c85024299fdf57aecf12cbb263ca780b064f7 -> Dispatch-ID: SG-052 | Report: docs/worklogs/SG-052_report.md | Work-HEAD: 450c85024299fdf57aecf12cbb263ca780b064f7
4ad3ff18bb64c9e69571e4f41aa6e9f7006aae2c -> Dispatch-ID: SG-054 | Report: docs/worklogs/SG-054_report.md | Work-HEAD: 4ad3ff18bb64c9e69571e4f41aa6e9f7006aae2c
53abefeb2813f3f8d18a7f32ba9a994d1bb796fe -> Dispatch-ID: SG-028 | Report: docs/worklogs/SG-028_report.md | Work-HEAD: 53abefeb2813f3f8d18a7f32ba9a994d1bb796fe
5429556ef0ce94d10a481e2eba7b2d3e66edb2ff -> Dispatch-ID: SG-026 | Report: docs/worklogs/SG-026_report.md | Work-HEAD: 5429556ef0ce94d10a481e2eba7b2d3e66edb2ff
5a744adee8c74d4f698c372348e135275ecac97f -> Dispatch-ID: SG-033 | Report: docs/worklogs/SG-033_report.md | Work-HEAD: 5a744adee8c74d4f698c372348e135275ecac97f
5d61d43b2708813e25ddca0772da1d43e6021f36 -> Dispatch-ID: SG-014 | Report: docs/worklogs/SG-014_report.md | Work-HEAD: 5d61d43b2708813e25ddca0772da1d43e6021f36
6419c9e1c5e1958b64115842ab0dd690abb451b3 -> Dispatch-ID: SG-053 | Report: docs/worklogs/SG-053_report.md | Work-HEAD: 6419c9e1c5e1958b64115842ab0dd690abb451b3
6456497788720941ba1f35becbe2a41ba4478729 -> Dispatch-ID: SG-056 | Report: docs/worklogs/SG-056_report.md | Work-HEAD: 6456497788720941ba1f35becbe2a41ba4478729
649cedffa1bc86baee5a89ade770acd147db472a -> Dispatch-ID: SG-040 | Report: docs/worklogs/SG-040_report.md | Work-HEAD: 649cedffa1bc86baee5a89ade770acd147db472a
655f75a272aad918e6a2f68c54c910deb472a837 -> Dispatch-ID: SG-047 | Report: docs/worklogs/SG-047_report.md | Work-HEAD: 655f75a272aad918e6a2f68c54c910deb472a837
6a07c62be63248e7a001176f81af8f11c201931d -> Dispatch-ID: SG-029 | Report: docs/worklogs/SG-029_report.md | Work-HEAD: 6a07c62be63248e7a001176f81af8f11c201931d
70e19437c8a8602388b541ee23aa0a4c70f1efee -> Dispatch-ID: SG-011 | Report: docs/worklogs/SG-011_report.md | Work-HEAD: 70e19437c8a8602388b541ee23aa0a4c70f1efee
82312ef1c15639d953df1f70c3c594560affd2eb -> Dispatch-ID: SG-022 | Report: docs/worklogs/SG-022_report.md | Work-HEAD: 82312ef1c15639d953df1f70c3c594560affd2eb
8715d4e5592f52de81b45efe03081c788a02ecca -> Dispatch-ID: SG-015 | Report: docs/worklogs/SG-015_report.md | Work-HEAD: 8715d4e5592f52de81b45efe03081c788a02ecca
9a5f5623cdc1de141dd8fdb9bdbc172757efb6b8 -> Dispatch-ID: SG-024 | Report: docs/worklogs/SG-024_report.md | Work-HEAD: 9a5f562
9e91363efc87c982fda0ab949d9b0f188823aa38 -> Dispatch-ID: SG-034 | Report: docs/worklogs/SG-034_report.md | Work-HEAD: 9e91363efc87c982fda0ab949d9b0f188823aa38
a10083f7f0cb873610322ce2f8f9f774cc733897 -> Dispatch-ID: SG-027 | Report: docs/worklogs/SG-027_report.md | Work-HEAD: a10083f7f0cb873610322ce2f8f9f774cc733897
a2e1f5c972f5ff95b33dfc25be54c4c2de4bc0d0 -> Dispatch-ID: SG-021 | Report: docs/worklogs/SG-021_report.md | Work-HEAD: a2e1f5c972f5ff95b33dfc25be54c4c2de4bc0d0
a8c3958527fe4df5e68e61199af9ecc7b718eb81 -> Dispatch-ID: SG-051 | Report: docs/worklogs/SG-051_report.md | Work-HEAD: a8c3958527fe4df5e68e61199af9ecc7b718eb81
a94397d0d09ce086fba45d37eda8b34c2420cf2d -> Dispatch-ID: SG-038 | Report: docs/worklogs/SG-038_report.md | Work-HEAD: a94397d0d09ce086fba45d37eda8b34c2420cf2d
aeda142dbfbffc3ff3b2509ef7ea0c87de474065 -> Dispatch-ID: SG-025 | Report: docs/worklogs/SG-025_report.md | Work-HEAD: aeda142dbfbffc3ff3b2509ef7ea0c87de474065
b2b9c9383e02ca45e0f8ecf955b3ead11ab8e2e4 -> Dispatch-ID: SG-055 | Report: docs/worklogs/SG-055_report.md | Work-HEAD: b2b9c9383e02ca45e0f8ecf955b3ead11ab8e2e4
b3f73e59985fabeb22737751e83d1fd6998a411b -> Dispatch-ID: SG-036 | Report: docs/worklogs/SG-036_report.md | Work-HEAD: b3f73e59985fabeb22737751e83d1fd6998a411b
b4dcdc8aa791ca5180b7649a31ecf107f1e1ffb1 -> Dispatch-ID: SG-020 | Report: docs/worklogs/SG-020_report.md | Work-HEAD: b4dcdc8aa791ca5180b7649a31ecf107f1e1ffb1
b7bd8635372e98bb12138ecdd837047bef16b533 -> Dispatch-ID: SG-037 | Report: docs/worklogs/SG-037_report.md | Work-HEAD: b7bd8635372e98bb12138ecdd837047bef16b533
b8eee6c0f84db2378f66d269e49952085e8616c4 -> Dispatch-ID: SG-016 | Report: docs/worklogs/SG-016_report.md | Work-HEAD: b8eee6c0f84db2378f66d269e49952085e8616c4
ca70574ac2a1e092fa9a1514234700059cb8bd54 -> Dispatch-ID: SG-049 | Report: docs/worklogs/SG-049_report.md | Work-HEAD: ca70574ac2a1e092fa9a1514234700059cb8bd54
d0f022593b2ea640c04d6eec989701d6c66adb86 -> Dispatch-ID: SG-050 | Report: docs/worklogs/SG-050_report.md | Work-HEAD: d0f022593b2ea640c04d6eec989701d6c66adb86
d25257a94e1edb2a5b007942c4686d3c82cd4b1f -> Dispatch-ID: SG-017 | Report: docs/worklogs/SG-017_report.md | Work-HEAD: d25257a94e1edb2a5b007942c4686d3c82cd4b1f
d609a678a2c8b6d4662695aa95ef2dfbc9dc0223 -> Dispatch-ID: SG-057 | Report: docs/worklogs/SG-057_report.md | Work-HEAD: d609a678a2c8b6d4662695aa95ef2dfbc9dc0223
d70b6f7e9db91d5eb4d37fcd2dfb39170d20f91a -> Dispatch-ID: SG-019 | Report: docs/worklogs/SG-019_report.md | Work-HEAD: d70b6f7e9db91d5eb4d37fcd2dfb39170d20f91a
dafac6ce841b87da1415b0fffc176af37504e293 -> Dispatch-ID: SG-048 | Report: docs/worklogs/SG-048_report.md | Work-HEAD: dafac6ce841b87da1415b0fffc176af37504e293
e060f6c29569d6b043be35e2b879d1eeb6245168 -> Dispatch-ID: SG-046 | Report: docs/worklogs/SG-046_report.md | Work-HEAD: e060f6c29569d6b043be35e2b879d1eeb6245168
e0b5362236f0f90118503beabf84f8f2edd32172 -> Dispatch-ID: SG-009 | Report: docs/worklogs/SG-009_report.md | Work-HEAD: e0b5362236f0f90118503beabf84f8f2edd32172
e9f83797d7e5e854ab0a3b75b832ed9c2f46ccd6 -> Dispatch-ID: SG-010 | Report: docs/worklogs/SG-010_report.md | Work-HEAD: e9f83797d7e5e854ab0a3b75b832ed9c2f46ccd6
ed7abc691dd375efd3247a41fcfcf0d2b811aa06 -> Dispatch-ID: SG-018 | Report: docs/worklogs/SG-018_report.md | Work-HEAD: ed7abc691dd375efd3247a41fcfcf0d2b811aa06
edf3cdcd3832675b2ea3f7a5302a5ff21888e080 -> Dispatch-ID: SG-031 | Report: docs/worklogs/SG-031_report.md | Work-HEAD: edf3cdcd3832675b2ea3f7a5302a5ff21888e080
f0071bafb8572348a7d46fe703fc5079fcf585b7 -> Dispatch-ID: SG-035 | Report: docs/worklogs/SG-035_report.md | Work-HEAD: f0071bafb8572348a7d46fe703fc5079fcf585b7
f0709f7224f8f040967f2716070204d0e154bdfa -> Dispatch-ID: SG-012 | Report: docs/worklogs/SG-012_report.md | Work-HEAD: f0709f7224f8f040967f2716070204d0e154bdfa
fefe3eb42e60410d4e1e206348da822f5e8a715c -> Dispatch-ID: SG-021 | Report: docs/worklogs/SG-021_report.md | Work-HEAD: fefe3eb42e60410d4e1e206348da822f5e8a715c

$ grep -n "SG-057" <note-contents-list>
46:d609a678a2c8b6d4662695aa95ef2dfbc9dc0223 -> Dispatch-ID: SG-057 | Report: docs/worklogs/SG-057_report.md | Work-HEAD: d609a678a2c8b6d4662695aa95ef2dfbc9dc0223
grep_exit=0

$ git notes --ref=refs/notes/storagegenie-coder-reports-verify show d609a678a2c8b6d4662695aa95ef2dfbc9dc0223
Dispatch-ID: SG-057 | Report: docs/worklogs/SG-057_report.md | Work-HEAD: d609a678a2c8b6d4662695aa95ef2dfbc9dc0223
show_exit=0
```

Verified against the fetched ref: `fetch_exit=0`, the note body was listed and grepped (`grep_exit=0`,
hit at line 46), and `show` printed the first line carrying BOTH `Dispatch-ID: SG-057` and
`Report: docs/worklogs/SG-057_report.md` (`CO-97`). No existing note was overwritten (`add_exit=0` on a
fresh hash). **note=yes.**

## UNCLEAR

- **FIRST READ:** whether G2's `"all other tables equal"` was meant to forbid the job's own
  job_step/observation/audit/idempotency rows (impossible for any real import) or only un-commanded
  domain mutation. I read it as the latter and reported the machinery rows explicitly.
- **DURING EXECUTION:** why the packet/AGENTS health probe names `:8000` while the composition
  publishes `:8003`. Resolved in-slice by probing both; the documentation is stale.
- **REMAINING:** the Coder's model id is not derivable from process argv (model omitted per policy) or
  observable provider metadata; reported `unknown` rather than a plausible guess.

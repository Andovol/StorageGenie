# SG-031 report — model-picker UI backed by a safe settings endpoint

**Dispatch-ID:** SG-031 · **Coder:** opencode · **Effort:** medium
**BASE REF:** `automation` → resolved commit `fafe16669718d2acb8f8f254805b6261967cdb77` (two fields, as required).
**WORK_HEAD:** the commit carrying this file; its hash is recorded by the G6 receipt note on `refs/notes/storagegenie-coder-reports` (a committed file cannot contain its own commit hash).
**Work dir** `/home/andrei/StorageGenie` · **origin** `git@github.com:Andovol/StorageGenie.git`.
**DATABASE:** none — temp SQLite only, zero live rows. **Restart:** none — no service touched, nothing deployed. **NETWORK:** none; **spend $0**.

**Model/effort per `CO-78`** — read from process arguments, never an identity line. Parent argv (`/proc/$PPID/cmdline`), quoted verbatim:

```
opencode run --auto --dir /home/andrei/StorageGenie --variant medium # SG-031 — Model-picker UI ...
```

Coder `opencode`, effort `medium` (`--variant medium`), **model `unknown`** — the CLI default IS the model and is omitted per policy; no model id appears in argv or packet, so I write `unknown` rather than a guess.

## Verdict

GREEN. A safe settings endpoint exposes the effective AI subset with the provider key
excluded by rule and proven absent from the response bytes; PUT enforces a tested-models-only
server-side whitelist with an enforced 422; the reader resolves the process-side override at
the provider build site, so the model recorded on an offline extraction call equals the
selection. The Settings screen renders the endpoint's list, PUTs a selection, and re-reads the
backend. `npm run build` is green (the long-queued frontend build proof). Backend suite is green
modulo the 2 known decoder env reds, re-verified at BASE. Ruff clean; secret scan 0; zero network.

## Findings (packet premises verified; differences stated, not bent)

### F-SG031-1 — the packet's second whitelist model is not evidenced (CORRECTION)
The packet names the tested list as `deepseek-v4-flash-vision-exp` **and** `deepseek-v4-flash`
"SG-027run2…SG-030 metered runs". A tree/ratings read contradicts the second id:

```
$ grep -rn "deepseek-v4-flash" *.py *.md *.ts   (tree)
SG-029 report / eval/baseline_sg029.md: all 7 metered calls `model=deepseek-v4-flash-vision-exp`
docs/ratings.md SG-027/028/029/030 "deepseek-v4.1-flash" = the CODER lane model (provider metadata)
docs/launcher-relay/...: `json_object` for `deepseek-v4-flash/_pro` — a vendor output-mode note, no call
```

`deepseek-v4-flash` (no `-vision-exp`) appears in **no metered run** and is not a vision path.
Under the packet's own rule ("tested-models-only") the whitelist is therefore
`ALLOWED_MODEL_IDS = ("deepseek-v4-flash-vision-exp",)`. The unproven id is used as the
**422 negative** in `test_put_unknown_model_is_422_and_selection_unchanged`, so the correction is
proved, not merely asserted.

### F-SG031-2 — the live-health premise does not hold in this environment (unanswered, not routed around)
Packet premise: "live mapped port is 8003 per D20". `docker-compose.yml` does map `"8003:8000"`
(verified), but no stack is running:

```
$ curl -s -m 5 http://localhost:8003/v1/health      -> (no output) exit=7 (connection refused)
$ ss -ltnp | grep -E ':(8000|8003|5173)'
LISTEN 0 4096 127.0.0.1:8000 0.0.0.0:*        # an unrelated listener; /v1/health -> "Not Found"
$ docker compose ps                                   -> NAME IMAGE COMMAND SERVICE CREATED STATUS PORTS  (0 services)
```

No service is running, and the slice's constraint is "no service touched, nothing deployed".
The `CO-92` daemon health probe is therefore reported **unanswered**: start and end are both
"not running" (delta 0), and DB+storage are not proven live. This is the packet's named world
(ship the rest, report the unanswered step); nothing was deployed or started to force a pass.

### Non-vacuity notes
- The UI can never submit an unlisted model (it only renders the endpoint list), so the 422 is
  tested at the backend boundary and the UI test proves a **rejected selection** surfaces the
  error. Stated plainly rather than claiming the UI sends an unknown id.
- Backend override proof sets `sg_model_id` to a **distinct sentinel** (`env-default-model-sentinel`)
  before PUT, so "recorded model == selection" cannot pass because the two happen to coincide.
- The secret-exclusion test asserts the sentinel is absent from `response.content` bytes, and a
  second test reads the route module source and asserts the key name is absent (rule-exclusion).

## G1 — safe settings endpoint

New `backend/app/api/v1/settings.py`, registered in `backend/app/main.py` (`include_router(..., prefix="/v1")`, matching the existing pattern).

- `GET /v1/settings/ai` → `{provider_id, model_id, allowed_model_ids, consent, per_job_cap, monthly_cap, prompt_category}`.
  Effective `model_id` = the runtime override if set, else `settings.sg_model_id`.
- The key (`opencode_api_key`) is **named nowhere** in the module; the response model has no such
  field. Proven by `test_get_exposes_only_safe_subset_and_no_key_bytes` (sentinel key configured,
  asserted absent from `response.content`/`response.text`) and
  `test_response_path_never_names_the_key_rule_exclusion` (source grep).
- `PUT /v1/settings/ai {model_id}` → 200 with the new effective settings for a listed model;
  **422** (RFC 9457 problem+json) for an unknown id, selection unchanged.
- Persistence: the override is a process-side module global in `reader.py`
  (`_runtime_model_id`); settings are env-loaded pydantic with no runtime write path and the
  backend is one process, so **a backend restart resets to the env default** (README line added;
  `test_restart_resets_to_env_default` proves the mechanism).

## G2 — reader honors the runtime selection

`reader.effective_model_id()` is the single resolver; `provider_registry()` builds
`OpenCodeGoProvider(model_id=effective_model_id())` and `run_ai_extraction` uses it as the model
fallback. Proof runs the **real** extraction path with the provider transport replaced in-process
(`_post` double) after `PUT`: captured payload model, step-output model, and every `ProviderCall.model`
all equal the selection while the env default is a different sentinel. A control test proves the env
default is used when no override is set. No network, no key read.

## G3 — Settings UI picker

`SettingsPage.tsx` fetches the endpoint (react-query), renders a `<select>` whose options come from
`allowed_model_ids` (no hardcoded list), displays the effective model, PUTs the selection and
invalidates/refetches — no local mirror. `types.ts` gains `AiSettings`; `client.ts` gains `apiPut`,
`fetchAiSettings`, `updateAiModel` beside the existing helpers.

## G4 — proof (raw runs in `docs/worklogs/SG-031_verify.log`)

| Gate | Result |
|---|---|
| PRE backend `pytest tests/test_settings.py` | **5 failed, 2 errors in 0.87s** (routes 404 / module absent) |
| POST backend `pytest tests/test_settings.py` | **7 passed** in 0.69s |
| PRE frontend `vitest SettingsPage.test.tsx` | **3 failed** ("Unable to find a label … AI model") |
| POST frontend `vitest SettingsPage.test.tsx` | **3 passed** in 0.68s |
| Full backend suite (`pytest -q`, 600s) | **2 failed, 121 passed in 7.91s** |
| BASE `fafe166` — same 2 reds | **2 failed in 0.56s** (pyzbar/libzbar, pytesseract not installed) — base-proved, not inherited |
| `ruff check app tests` | `All checks passed!` |
| `mypy app` | 40 errors in 9 files (baseline 40-in-9 unchanged; none in new/edited files) |
| `npm run build` | green, 93 modules, built in 846ms (dist quoted in verify log) |
| `vitest run` | 9 files, **22 passed** |
| Secret scan | **0** real secrets (worktree-wide); sentinel only in the test; `.env` untracked |
| Health probe `CO-92` | unanswered — no listener on 8003; delta 0 (see F-SG031-2) |

No migration; no prompt diff; no provider switch; no live call; no ignored file staged.

## Budget (actual versus budget)

| Leg | Budget | Actual |
|---|---|---|
| Ordinary probes / single test runs (120s) | 120s | ≤ 0.9s each |
| Backend suite (600s) | 600s | 7.91s |
| `npm run build` (600s) | 600s | 846ms build (plus `tsc` a few s) |
| `vitest run` (600s) | 600s | 1.51s |
| Overall (2400s) | 2400s | well under (single-session, minute scale) |

## Live-state ledger

- Provider spend: **$0** (no live call; `_post` replaced in-process).
- Network attempts: **0** (all proofs in-process; the health probe is the only socket attempt and it was refused).
- Key reads: **0** (only the test sentinel string was assigned to `settings.opencode_api_key`; no real key read or logged).
- Deployments / migrations / restarts: **0**.
- Secrets: names only; sentinel confined to `backend/tests/test_settings.py`.

## Guards

`PG-EV-01` FAIL-then-PASS raw for every new test (verify log) · `PG-EV-02` new files exist and are committed · `PG-EV-03` the 422 is enforced (STOP-of-validation), not satisfied by disclosure; no condition shared with a remediation step (`PG-IC-03`) · `PG-EV-05` property (recorded model == selection) proved, not a command echo · `PG-EV-09` both runs committed raw · `PG-SC-02` allowed list traced endpoint → screen, no UI hardcode · `PG-SC-05` key exclusion by rule + grep · `PG-SC-07` unknown model rejected, selection unchanged · `PG-SC-10` no ignored file staged · `PG-IC-01` cross-product (route+config / reader build site / page+client / proofs) · `PG-IC-07` no fixed dates · `PG-IC-09` premises re-verified, corrections named · `PG-PR-03/04/06/10` scope ceiling, zero live calls, per-leg bounds, disposition.

## Role guard

Coder role only. I did not run any dispatch verb, did not start or poll any unit. No SSH performed.

## UNCLEAR

- FIRST READ: Whether `deepseek-v4-flash` should still appear in the picker as an operator-visible
  option despite having no metered evidence. I read "tested-models-only" as excluding it and used it
  as the 422 negative; the correction is flagged for the Architect to confirm or overrule.
- DURING EXECUTION: The `CO-92` health probe cannot be satisfied because no backend is running in
  this environment and the slice may not deploy one. I reported it unanswered rather than starting a
  service; the Architect may want a stated live-service precondition for probes that need one.
- REMAINING: The `mypy` 40-in-9 baseline is inherited as context; I verified no new file appears in
  the error set but did not attempt to reduce the pre-existing 40, which is outside this ceiling.

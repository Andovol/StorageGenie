# SG-251 — Close-deploy rider: served SG-250 live, proved the served bytes, and reported the served registry's provider ids

SG-251. model=opencode-go/deepseek-v4.1-flash effort=max, read from `/proc/3688251/cmdline` (`opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant max`). Served-model response metadata unavailable (no provider call made); no substitute claimed. dir=`/home/andrei/StorageGenie`; remote=`git@github.com:Andovol/StorageGenie.git`. BASE ref=`origin/automation`; BASE COMMIT (resolved, equals start HEAD)=`21b79d67aa529ae6308b886ed7c0345cee265eb4`. WORK_HEAD=the docs-only commit carrying this report; its hash cannot appear here (CO-55(b)) and is recorded as `Work-HEAD` in the notes receipt and in `docs/worklogs/SG-251_receipt.log`. Terminal class: **NO PRODUCT CHANGE** — one image build, one backend recreate, evidence files only. Target/actual spend: **$0 / $0.000000**; zero provider calls; no key value read by these checks, printed, hashed, stored or transmitted; no `.env` file opened.

Contract echo (`/home/andrei/storagegenie-contract/CODER.md` line 3, verbatim): `**Contract version: 0.53.0** — **echo this line verbatim in your receipt.** It is the only proof that you`

## (a) Issues / deviations / surprises

I1. **Protocol slip, no effect.** My first `docker version` at `19:23:12Z` ran before the lane socket was exported; it used the default endpoint `unix:///var/run/docker.sock`, failed `permission denied`, printed no Server section (rc=1), and changed nothing. The export and the Server-block proof followed at `19:23:49Z` (`docs/worklogs/SG-251_g0.log`). Every docker mutation after that went through the lane socket.

I2. **The pre-serve image was removed from the daemon inside the build/recreate window.** `sha256:97ced17c…` was inspected and its tree copied at `19:24:06Z`; by the G3 control at `19:26:20Z` it no longer exists (`docker images -a` has no `97ced17c`; `docker create` says "No such image"). The window contains the build and the recreate; the exact cause is not established. The pre-serve runtime diff and bundle hashes were captured before the build, so the evidence stands; the G3 non-vacuity control instead greps the git blob the image was built from (`d0a87c6^`), where every removed symbol appears (`docs/worklogs/SG-251_g3_control.log`).

I3. **The packet's "fourteen product files" is 13 runtime files plus one non-runtime file.** SG-250 changed 13 files under `backend/app` and `backend/eval/run.py`. The served-tree diff is exactly the 13; `eval/run.py` is outside runtime and outside `backend/app`, as the packet's own G2 says. Measured set equality: 0 extra, 0 missing (`docs/worklogs/SG-251_g2.log`).

I4. **Contract version label mismatch, not changed (outside the scope ceiling).** The repo `AGENTS.md` records rule-set `0.52.0`; `/home/andrei/storagegenie-contract/VERSION` and `CODER.md` both say `0.53.0`. I read and followed the live `0.53.0` contract and echo that line. The repo label is stale; correcting it is a separate change.

I5. **Two defects in my first pre-state block, both recorded and corrected.** (i) The first Python-tree diff walked all of `backend/` (2181 files) instead of the served tree `backend/app` (100 files); the corrected diff is the SG-240/SG-241 100-file measure. (ii) The first census `docker exec` omitted `-i`, so its stdin here-doc never reached Python and printed nothing; the corrected run uses `-i`. Both corrections are in `docs/worklogs/SG-251_prestate.log` under "G0 correction"; no stale value is used in this report.

I6. **The build was not fully cache-satisfied, and the image was checked anyway.** Nine steps were CACHED (including `npm run build`, consistent with the unchanged frontend); `COPY backend/` and the editable install re-ran. New image `e8c7373577f9…`. Post-build served tree vs worktree: 100/100 Python files, `diff` rc=0.

I7. **The SQLite main-file sha moved** `acf11596…` -> `e4107437…` with the same size (765952 B) while all 29 table counts are identical, including `provider_call=39`. The DB is WAL mode; the old container's stop checkpointed committed WAL pages (same behaviour SG-239/SG-241 measured). No row changed.

I8. **The error scan's only hit was the pass line's `errors=0`.** Re-reading the startup log without that line leaves no `traceback`, `configuration error`, `exception`, `critical`, `failed` or `error` line. The false positive is recorded, not hidden.

I9. **G4's method, stated exactly.** The ids were read by executing the served image's own `provider_registry()` inside the running container, under the same container environment the uvicorn process started with. That function evaluates `settings.opencode_api_key` truthiness to decide registration; I printed only the dict keys, the count, a membership boolean, the `ai_status` reason and the effective provider id name. `/app/.env` is absent from the image, so no `.env` file was opened.

I11. **The remote `automation` branch advanced during the slice.** It moved `21b79d6` -> `7ba4347` (`STATE.md` only, 6 lines; no product, config, schema, dependency or test byte). The first push was rejected non-fast-forward. I rebased this still-unpublished docs-only commit onto `7ba4347` (CO-54 forbids rewriting published history; this commit had not been pushed) and pushed. The product tree verified is still `21b79d6`'s and is unchanged by the new commit.

I10. **`ai_status` returns `enabled`.** With `effective_provider_id=opencode-go`, consent is on and the real provider is registered; the served app is in the real-provider case, so a real call would emit the cost line. This slice still makes no call.

## (b) Actions

Changed paths: `docs/worklogs/SG-251_{g0,prestate,build,deploy,verify,g2,g3_served,g3_control,g4}.log`, `docs/worklogs/SG-251_report.md`, `docs/worklogs/SG-251_receipt.log` (receipt transcript, in the allowed receipt commit). No product, config, schema, migration, dependency or test byte changed. No migration command ran.

G0: lane socket `/run/dispatch-storagegenie-SG-251/docker.sock`; `DOCKER_HOST`/`DOCKER_CONFIG` exported; `docker version` printed a Server block (29.6.2, API 1.55, rc=0). Pre-state: container `6c648f1c…`, image `sha256:97ced17c…`, `Cmd ["uvicorn","app.server:app","--host","0.0.0.0","--port","8000"]`, RestartCount 0, running/healthy; head `20261023_sg233_reminder`; 29 tables.

G1: one `docker compose build backend` (rc=0, 18 s of 600 s) then one `docker compose up -d --no-deps --force-recreate backend` (rc=0, 1 s of 120 s), both through the lane socket. New container `a831fbd0f8d2895d810efc4794f42166d194fa4e31c23403f02a8ff0cc19c2c1`, Created `2026-10-24T19:25:04.308330921Z`, StartedAt `2026-10-24T19:25:05.063123154Z`, image `sha256:e8c7373577f9770bf486ae478e1a867b7ba41165aefa81d5f81d2b1d543d4ec3`, `Cmd ["uvicorn","app.server:app","--host","0.0.0.0","--port","8000"]`, RestartCount 0, running/healthy. Head after: `20261023_sg233_reminder` (unchanged). No other service touched.

External effects (CO-85): build completed (`storagegenie-backend:latest` -> `e8c73735…`); recreate completed (`a831fbd0…` running/healthy); startup daily pass ran and logged once; rows created **0**; counted row changes **0**; migration **0**; provider calls **0**; deployment count **1**.

Durations (box clock, UTC): lane start `2026-10-24T19:23:01Z` (epoch 1792869781); G0 socket proof `19:23:49Z`; pre-state `19:24:03–19:24:27Z`; build `19:24:35–19:24:53Z` (18 s); recreate `19:25:04–19:25:05Z` (1 s); post verification `19:25:37–19:25:44Z`; G3/G4 `19:26:20–19:27:52Z`; G2/census `19:27:33Z`; end health `19:28:07Z`. Report writing began `19:28:07Z` and the amended write ends `19:29:39Z`: **398 s** of the lane's 1200 s bound (33.2%). Retry count 0; test commands 0 (no product change); no command killed; no bound approached.

Highest-impact action: the single recreate to `a831fbd0…`, which made SG-250's cost behaviour the served behaviour.

## (c) Verification

A1 — **PASS (with I1 stated).** The lane socket was exported and `docker version` printed the Server block before any docker *mutation*; the one earlier default-endpoint `docker version` failed without a Server section and changed nothing. Server quote: `Server: Docker Engine - Community / Engine: Version 29.6.2 / API version 1.55`, `docker_version_rc=0` (`SG-251_g0.log`).

A2 — **PASS.** One build rc=0 (18 s), one recreate rc=0 (1 s). Container `a831fbd0…`, image `e8c73735…`, `Cmd ["uvicorn","app.server:app","--host","0.0.0.0","--port","8000"]`, RestartCount 0, health `healthy`. No migration; head `20261023_sg233_reminder` before and after. Health: start `http=200 {"status":"ok","db":"ok","storage":"ok"}`; six post-recreate GETs all `http=200` with the same body; end `http=200 {"status":"ok","db":"ok","storage":"ok"}` (`SG-251_prestate.log`, `SG-251_verify.log`, `SG-251_g2.log`).

A3 — **PASS, with I3's count correction.** The pre-serve-image-to-worktree runtime diff over `backend/app` is exactly 13 files: `api/v1/enrich.py`, `api/v1/settings.py`, `config.py`, `services/analytics/service.py`, `services/chat/service.py`, `services/enrich/snapshots.py`, `services/enrich/synthesize.py`, `services/planning/service.py`, `services/providers/fake.py`, `services/providers/opencode_go.py`, `services/providers/protocols.py`, `services/providers/reader.py`, `services/providers/router.py`; set diff vs SG-250's commit rc=0, extra=0, missing=0. `backend/eval/run.py` is the 14th product file and is not runtime. Frontend bundle byte-identical pre vs post: `index.html` `cec37cf5…` 944 B (cmp rc=0); `index-C07VbG0m.css` `c3b58cda…` 4535 B (cmp rc=0); `index-CWp6nYu6.js` `fe7dff6e…` 326217 B (cmp rc=0). Post-build served tree = worktree: 100/100 Python files, `diff` rc=0.

A4 — **PASS, from the served image's own files** (`SG-251_g3_served.log`; image `e8c73735…`, tree extracted by `docker create`+`docker cp`, no execution):

1. Absences (grep rc=1): `estimate_call_cost|estimate_cost` in served `providers/opencode_go.py` — no match; `cost_budget` in served `providers/router.py` — no match; served `def execute(self, operation: str, *args: Any, **kwargs: Any) -> Any:` carries no cost argument; `_estimate_call|_recorded_spend` in served `providers/reader.py` — no match; `sg_per_job_cap|sg_monthly_cap` in served `config.py` — no match. Control: the same patterns match the pre-SG-250 blob (e.g. `estimate_call_cost` at line 151, `sg_per_job_cap`/`sg_monthly_cap` at lines 48/49, `cost_budget` at line 35, `_estimate_call`/`_recorded_spend` at lines 233/270) — `SG-251_g3_control.log`.
2. The cost line is served: `_log_call` emits `logger.info("provider call: provider=%s model=%s operation=%s status=%s cost=%.8f input_tokens=%d output_tokens=%d latency_ms=%s", ...)` (`opencode_go.py:165-168`), and `compute_cost(usage)` prices the response's real `prompt_tokens`/`completion_tokens` after the call (`opencode_go.py:140-151`), assigned as `cost = compute_cost(usage)` and stored in `ProviderResult` (`opencode_go.py:293-300`).
3. Startup log has no configuration error and no traceback: the four startup lines and the one daily-pass line are the only non-access lines; the only "error" match is the pass line's `errors=0` (I8). Served `config.py:63` is `model_config = {"env_file": ".env", "extra": "ignore"}`; therefore a leftover `SG_PER_JOB_CAP`/`SG_MONTHLY_CAP` in the host environment is ignored rather than rejected. I did not read the environment to test this.

A5 — **PASS.** Served registry ids: `provider_ids=fake,opencode-go`, `provider_count=2`, `real_provider_opencode_go_present=True`, `ai_status_reason=enabled`, `effective_provider_id=opencode-go` (`SG-251_g4.log`). **No key value was read by these checks, printed, hashed, stored or transmitted**; the helper printed names and booleans only. The served app's own `provider_registry()` evaluated key presence as a boolean, exactly as it does in production (I9). `/app/.env` is absent from the image, so no `.env` file was opened.

A6 — **PASS.** Pre and post census both have 29 tables and 32 census lines; `diff` rc=0. `provider_call=39` before and after; `assertion=40`, `asset=7`, `asset_evidence=20`, `audit_event=104`, `candidate=10`, `enrich_snapshot=4`, `evidence=27`, `household=1`, `idempotency_key=11`, `job=11`, `job_step=72`, `reminder=1`, `review_task=9`, `user=2`; every other table unchanged.

A7 — **What changed for the owner in production.** The app no longer estimates a call's cost and no cost check can stop a call: the pre-call estimate, the per-job/monthly caps and the router budget are gone from the served code. Each real provider call now records its **actual** cost — computed after the response from the response's real token usage — in the `provider_call` ledger, and emits exactly one INFO line carrying provider, model, operation, status, actual cost, token counts and latency. The consent switch still gates every cloud call (`ai_status`), and the scene feature's own `SG_SCENE_CAP` stop condition is untouched. The served registry holds `fake` and `opencode-go`, and the effective provider is `opencode-go`, so the next authorised real call is the one that will show the new line live.

G5 — **The cost line's live appearance is NOT claimed.** No provider call was made and none was simulated. The line appears in the served container's log only when a real `opencode-go` call runs the `_log_call` path; that awaits an authorised call. Before such a call, the log correctly shows no cost line.

A8 — **PB-3 vacuity: each check could have failed.** The runtime diff could have shown an extra file (e.g. `server.py` or a test file) or a missing SG-250 file — it showed neither, and the pre-serve image itself is the opposite case (it still contains all five removed symbols). The bundle cmp could have returned nonzero or a moved hash — all three files are byte-identical. The startup scan could have found a traceback or a pydantic configuration error — it found only `errors=0`. The census could have moved `provider_call` (e.g. 39 -> 40) or any table — every count is identical. The registry check could have returned only `fake` with count 1 — it returned both ids and `real_provider_opencode_go_present=True`.

Skipped as unnecessary (CO-103): backend suite — no product byte changed and the slice is deploy-only; lint/type checks — same; browser screenshot — bundle bytes and live health are the evidence; second health/verify pass — no new information; DB backup — no schema change and no write; dispatch/status verb — role guard forbids it; `POST`/`PUT` of any kind — G4 is read-only and no write was authorised.

Budget: lane start `2026-10-24T19:23:01Z` (epoch 1792869781); end as of the amended report write `19:29:39Z` (epoch 1792870179) = **398 s of 1200 s**. Legs: G0 48 s, pre-state 24 s, build 18 s, recreate 1 s, post verify 7 s, G3/G4 92 s, G2/census 0 s, remainder report composition. No command over 60 s; none killed; provider calls 0; spend $0.000000.

INTENT: no behaviour-changing code item (this slice changes no product byte); the recreate serves SG-250's tree, the check expects SG-250's 13 runtime files and unchanged behaviour elsewhere, and the approved packet says exactly that.

UNCLEAR FIRST READ: none; the packet's count "fourteen product files" was read against G2's explicit list and resolved as 13 runtime + `backend/eval/run.py` (I3).

UNCLEAR DURING EXECUTION: why the pre-serve image disappeared from the daemon after the build; the pre-state evidence was captured first and the G3 control used the pre-SG-250 git blob instead (I2).

UNCLEAR REMAINING: the repo `AGENTS.md` still labels rule-set `0.52.0` while the live contract is `0.53.0` (I4); correcting it is outside this slice's ceiling.

Verification: PASS

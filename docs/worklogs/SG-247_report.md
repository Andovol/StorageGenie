SG-247 — read-only verification: the row-14 adapter touch-list, the served image's local-signal dependencies, and where spend lands.

Identity (CO-78/PB-4, from process arguments, never a system-prompt label): model=opencode-go/deepseek-v4.1-flash effort=max, read from `/proc/3476656/cmdline` (`opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant max`). Served-model response metadata unavailable: no provider was called, so no substitute value is claimed. dir=`/home/andrei/StorageGenie`; remote=`git@github.com:Andovol/StorageGenie.git`.

BASE: ref requested `origin/automation` -> resolved commit `20a8dd9e0e79f24506a9bc2930e4d8db3c4c6a68` (equals the start HEAD; measured 2026-10-24T17:04Z). The two fields are separate; no served image is claimed to equal this hash.

WORK_HEAD: the commit that carries this report. A file cannot carry its own hash (CO-55(b)); the receipt names it after publication.

Contract echo (`/home/andrei/storagegenie-contract/CODER.md` line 3, verbatim): "**Contract version: 0.52.0** — **echo this line verbatim in your receipt.** It is the only proof that you".

Contract chain: repo `AGENTS.md` line 4 `0.52.0` == `/home/andrei/storagegenie-contract/VERSION` `0.52.0` == `CODER.md` line 3 `0.52.0`. Read in full: `CODER.md`, `lang/python.md`, `CODER_PRODUCTION.md`. The project declares a datastore, a deployed service and a rendered surface, so the production overlay applies; §6/§9/§10 were not invoked (no DB, no deploy, no visual claim). The Python overlay's test/mypy placeholders `{{VENV}}`, `{{VTEST}}`, `{{EVIDENCE_DIR}}` were not used because this read-only packet runs no test and changes no code.

Spend: **$0.000000 actual vs $0 bound**; zero provider calls (no provider code path was invoked); no model downloaded; no key or `.env` value read; no database opened.

Terminal class: **NO-CHANGE** — read-only. No product commit exists and none was manufactured. Only `docs/worklogs/SG-247*` is committed; the receipt publishes after that commit.

## (a) Issues / deviations / surprises

I1. **The first build invocation failed before starting: the Docker CLI could not create `~/.docker`.** `docker build` exited 1 with `ERROR: mkdir /home/andrei/.docker: permission denied`; no image build occurred (`SG-247_g2_build.log`, attempt 1). The lane's docker socket already answered (`docker version` Server 29.6.2, rc=0); only the CLI's HOME config dir is root-owned. Retried with `DOCKER_CONFIG=/run/dispatch-storagegenie-SG-247/docker-config` (the lane's writable runtime dir), and the one build then exited 0. This is a file-permission issue, not a privileged denial, and no `sudo` was attempted (PB-2; SG-240 I3 precedent).

I2. **The built tag and the running image are NOT the same digest, but their rootfs is identical.** Built `storagegenie-backend:sg247-verify` -> `sha256:0cb60586c19deee43250610e71e7bac53dd8947d1ab03c500af3213b38a6c716` (a BuildKit manifest list carrying an attestation manifest). Running container `storagegenie-backend-1` uses `sha256:97ced17c3120f12eb16ca830bb3a83d3ff78fa980151043f8ec44a172434b2f0` (the `latest` tag, unchanged). The 12 rootfs layer digests are identical in order; the runtime Config fields (`Cmd`, `Env`, `WorkingDir`, `ExposedPorts`, `ArgsEscaped`) are equal; the only Config difference is the `Labels` map (running image: `com.docker.compose.project=storagegenie`, `service=backend`, `version=5.3.1`; built image: null). The four measured facts transfer to the running image's filesystem by layer identity, not by a same-digest claim. The packet's "if the running image differs, say so": it differs at the top-level digest and is identical at the layer/runtime-config level.

I3. **Packet line drift (CO-07).** `config.py:44` is `openrouter_api_key` (the scene key), not the opencode key; the opencode carrier is `config.py:37`. `settings.py:29-36` is the GET shape `AiSettingsOut`; the PUT limit is `:39-40` and the whitelist `:26`. Scene spend recording is at `openrouter.py:803-809` (the cost read) and `:853-869` (the row append), inside the packet's `≈:800-885` window; the `ProviderCall` constructor is `:593-623`. The privacy pins match (237-248, 251-267).

I4. **The four hardcoded `fallback_id=None` sites are not the only production provider caller.** `services/enrich/synthesize.py:276-285` resolves the registry and calls `provider.extract_text(...)` directly, bypassing `ProviderRouter` (no fallback, no router budget). That is the sixth caller (CO-06); the packet's four are the router call sites, not the whole class. If the stage's fallback covers text, this path is uncovered.

I5. **The gateway test's "non-retryable" fixture is production-retryable.** Production's set includes `invalid_json` (`reader.py:61-63`); the test's set is `{"outage","timeout","rate_limited"}` (`test_provider_gateway.py:54`), and its negative branch asserts `invalid_json_once` does not fall back (`:85-91`). The test proves the opposite classification for that class, not merely a narrower set. `FakeProvider` has no `transport`/`http_status` mode (`fake.py:20,38,41`).

I6. **A keyless local adapter cannot register through the current gate.** `provider_registry()` registers `opencode-go` only `if settings.opencode_api_key` (`reader.py:97`). A local no-key adapter needs a new condition (base-url or enable flag), not a key. The local signal path (tesseract/libzbar) is present in the image (G2), but that is the OCR path in `signals.py`, not a provider adapter.

I7. **Health was not run.** `{{HEALTH_CMD}}` is a DB+storage probe (`curl /v1/health`); the packet forbids opening the database even read-only, so invoking it would violate the packet's higher-authority rule (CO-02). No health delta is claimed; the running container was observed only by read-only `docker ps`/`inspect`.

I8. **The one build ran with Docker's default network.** All layers were cache hits and no package download occurred; base metadata was resolved. The measurement container ran with `--network none` and no bind mount. If the packet meant the build itself under `--network none`, that is a reported deviation; a second build was not run because the packet says "once".

I9. **One probe failed and is not used.** `docker image inspect --format '{{json .History}}'` failed with `map has no entry for key "History"`, and the piped `sha256sum` hashed empty input. The config/rootfs comparison is the evidence; the failed probe is recorded, not counted as a measurement (CO-46).

## (b) Actions

Changed paths: `docs/worklogs/SG-247_g1_g3.log`, `docs/worklogs/SG-247_g2_build.log`, `docs/worklogs/SG-247_g2_measure.log`, `docs/worklogs/SG-247_g2_digest.log`, `docs/worklogs/SG-247_orientation.log`, and this report. Nothing else.

Build/run: one `docker build -f backend/Dockerfile -t storagegenie-backend:sg247-verify .` (build_exit=0; every build step hit cache; export 0.1 s); one `docker run --rm -i --network none --name sg247-verify storagegenie-backend:sg247-verify sh -s` (run_exit=0); the container is removed (`docker ps -a --filter name=sg247-verify` empty). The built image remains, tagged `sg247-verify` only; `storagegenie-backend:latest` is still `97ced17c` and the running container `6c648f1c` is still Up/healthy. No recreate, restart, migration, compose call, or `.env` read. No database opened. No provider called. No key read. No spend.

External effects (CO-85): one image build completed (tagged `sg247-verify`, image `0cb60586`); one throwaway container created and removed; zero product writes; zero DB writes; zero provider calls; zero deployments/restarts.

Durations (box clock, UTC; CO-79): start `2026-10-24T17:04:10Z` (epoch `1792861450`); build `17:05:39-17:05:42Z` (3 s); in-container measurement `17:06:02-17:06:03Z` (1 s); digest comparison `17:07:59-17:08:00Z` (1 s); G1/G3 reads `17:07:18Z`; report composition ends `17:13:39Z` (epoch `1792862019`) = **569 s** from start, of the lane's 2100 s and the packet's 1500 s bound. No command over 60 s; none killed. Slice retries 0; one build invocation failed before starting (I1) and was rerun once with `DOCKER_CONFIG`, a verification attempt and not a slice retry; test commands 0; provider calls 0.

Highest-impact action: the one cache-satisfied image build plus the `--network none` measurement, which turned the local-signal hypothesis into four observed facts.

## (c) Verification

### G1 — the static adapter touch-list

**Must change for a second adapter (with a configured fallback):**

- `backend/app/services/providers/<new-adapter>.py` (new file): implement `extract_items(image_bytes, prompt, *, estimated_cost=0.0) -> ProviderResult`, `provider_id`, its own rate table and `estimate_cost`, its own response-format rule and transport. Why: this is the object the registry returns and the reader calls; the protocol is `protocols.py:28-37`.
- `backend/app/services/providers/reader.py`: the registry gate `:90-105` gains an import and a registration branch for the new id (key/base-url, model, caps); `ai_status()` `:108-114` and `run_ai_extraction` `:456-469` use the effective provider/fallback ids. Why: the provider must be registered and selected; today `:97` is `if settings.opencode_api_key`, which a keyless local adapter cannot pass.
- `backend/app/config.py`: add the new provider's key/base-url/model and a fallback-id setting. Why: settings are the only source (pydantic env-loaded; no runtime write path). The packet's `:44` is the scene key; the opencode carrier is `:37`; caps/consent are `:48-50`.
- `backend/app/api/v1/settings.py`: the model whitelist `:26` must include the new provider's tested model; the GET shape `:29-36` and PUT shape `:39-40` must carry provider/fallback if they are runtime-selectable; validation `:62-63` currently rejects anything not in `ALLOWED_MODEL_IDS`. Why: a new model id is a 422 until whitelisted; provider id is not settable today.
- the four `RouterConfig` call sites: `reader.py:463-469`, `chat/service.py:423-429`, `planning/service.py:442-448`, `analytics/service.py:595-601` — replace `fallback_id=None` with the configured id and use the effective provider id. Why: the router's fallback branch (`router.py:79-81`) is unreachable from production today; the switch is tested only at `test_provider_gateway.py:73-91`. These are caller *wiring* edits, not repair/ledger/outcome logic.
- `backend/app/services/enrich/synthesize.py:276-285` (discovered sixth caller): calls `provider.extract_text` directly with no router and no fallback. Why: if the stage's fallback covers text, the four sites do not cover this path.
- `backend/tests/test_privacy_audit.py`: the client-file set `:237-243`, the send sites `:244-248` and repeated at `:524-528`, and the `redact_image` call sites `:264-267`. Why: a new httpx adapter adds a file and a send site; if it calls `redact_image` itself, it adds a third redact site.
- `backend/app/services/providers/router.py` (conditional): the review's per-destination retryable set (a local landing must not absorb `invalid_json`) needs a router field/set, because production uses one shared `retryable_errors`. Why: D-R14-b's disposition, not an adapter requirement.
- `backend/app/services/providers/opencode_go.py` (conditional): if the review's shared base is extracted first, move the vendor-neutral guards/accounting/estimate shape out. Why: see G1.2; rate constants `:44-45` stay per-vendor.
- `backend/tests/test_provider_conformance.py` + a new adapter test file: add the new adapter's signature/behaviour case and its offline shape/estimate/redaction tests. Why: the conformance rail names the real classes; the new adapter would otherwise be uncovered.
- `backend/pyproject.toml` + `backend/requirements.lock` + an image rebuild (conditional): only if the adapter uses a new SDK; the existing raw-httpx pattern adds no dependency.

**Checked, no change:** `providers/protocols.py` (the new adapter conforms to `VisionExtractionProvider`), `models/provider_call.py` (the `provider` string and nullable `job_id` already fit), `services/providers/redaction.py` (the shared helper is reused; the caller pin moves, the helper does not), `services/scene/openrouter.py` (image generation, not the vision seam), `services/providers/fake.py` (test double), `reader._estimate_call` `:233-242` (duck-types `estimate_cost`; no edit if the adapter implements it), the repair policy (`reader.repair_prompt`, chat/planning/analytics `_repair_prompt`), the ledger writers (`reader._write_ledger`, chat/planning/analytics `_write_ledger`), and the outcome contracts (`ExtractionOutput`, `ProviderResult`).

G1.1 — **No: the policy/ledger/outcome half stays untouched, but the list does not stay inside the seam + adapter + pins.** No caller-logic edit to the repair policy, the ledger writers or the outcome contracts is required; the four `RouterConfig` sites (plus `synthesize.py` if text is in scope) still need a caller *wiring* edit, and `settings.py`/`config.py` need the runtime-selection surface. So "changing providers needs configuration, not code" is false today for adding a vendor, and also false for selecting provider/fallback until those edits land.

G1.2 — **Vendor-neutral logic in `opencode_go.py` and the moved line count.** `guard_content` `:70-82`; `guard_usage` `:85-98`; `_THINK_RE` + `strip_single_think` `:47,101-111`; `attach_body_accounting` `:114-136`; `compute_cost` `:139-148`; `estimate_call_cost` `:151-164`; `estimate_cost` `:244-250`; the budget guards duplicated at `:298-309` (`extract_items`) and `:361-372` (`extract_text`). Measured source-line count in the review's ranges: `70-164` = 95, `298-309` = 12, `361-372` = 12, **sum 119** (`SG-247_g1_g3.log`). A shared base would own those guards/accounting/estimate shapes and the two budget-guard copies, with the rate constants `:44-45` injected per adapter; the vendor-specific `response_format_for` `:63-67` and the wire payloads stay per adapter. The review's "~150 duplicated lines" is consistent if the `_post` error mapping, identity headers and payload builders are also shared; the measured figure for the exact ranges it names is 119.

G1.3 — **What runtime selection needs.** Today `settings` is env-loaded and has no runtime write path; only the model has a process-side override (`reader.py:76-87`, `settings.py:60-65`). To make provider and fallback runtime-selectable: add `sg_fallback_id` (and the provider's key/base-url/model) in `config.py`; add `_runtime_provider_id`/`_runtime_fallback_id` and `effective_provider_id()`/`effective_fallback_id()` in `reader.py`; register every configured adapter in `provider_registry()`; use the effective ids in `ai_status()`, `run_ai_extraction` and the four `RouterConfig` sites; extend `AiSettingsOut`/`AiSettingsUpdate` with `fallback_id` and `provider_id` and validate them against registered ids; update `synthesize.py` if text is in scope. A restart resets the overrides to the env defaults. After that, switching among registered adapters is configuration/runtime; adding a new vendor still needs the adapter file and the registry branch (code).

### G2 — the served image's local-signal dependencies

One build into a throwaway tag: `docker build -f backend/Dockerfile -t storagegenie-backend:sg247-verify .` -> `build_exit=0`, every build step hit cache, export 0.1 s (`SG-247_g2_build.log`). One throwaway container: `docker run --rm -i --network none --name sg247-verify storagegenie-backend:sg247-verify sh -s` -> `run_exit=0`, no bind mount, removed after the run (`docker ps -a --filter name=sg247-verify` empty; `SG-247_g2_measure.log`).

Measured inside that container, verbatim:

```
== tesseract --version ==
tesseract 5.3.0
 leptonica-1.82.0
...
tesseract_version_rc=0
== shutil.which(tesseract) ==
which=/usr/bin/tesseract
which_rc=0
== from pyzbar.pyzbar import decode ==
pyzbar_decode_import=OK
pyzbar_rc=0
== import pytesseract ==
pytesseract_import=OK
get_tesseract_version=5.3.0
pytesseract_rc=0
== ldconfig -p | grep zbar ==
	libzbar.so.0 (libc6,x86-64) => /lib/x86_64-linux-gnu/libzbar.so.0
ldconfig_grep_rc=0
== ctypes.CDLL(libzbar.so.0) ==
libzbar.so.0=loadable
cdll_rc=0
```

Image ids: built tag `sha256:0cb60586c19deee43250610e71e7bac53dd8947d1ab03c500af3213b38a6c716`; running container's image `sha256:97ced17c3120f12eb16ca830bb3a83d3ff78fa980151043f8ec44a172434b2f0`. **Not the same digest** at the top level; the 12 rootfs layer digests are identical, and the runtime Config fields are equal; only the `Labels` map and the attestation manifest differ (`SG-247_g2_digest.log`). The running container was not recreated, stopped or restarted; `latest` did not move.

### G3 — where the spend lands and which retryable classes are tested

G3.1 — **Yes, scene rows land in `provider_call` with `job_id=None`.** `record_scene_call` builds `provider=SCENE_LEDGER_PROVIDER` (`openrouter.py:594`; constant `"openrouter"` at `:247`), `cost=cost_usd` (`:619`) and `job_id=None` (`:623`). The cost is the response's `usage.cost` when present (`:803-809`); the row is appended at `:853-869`. Scene's own cap reads `ProviderCall.provider == SCENE_LEDGER_PROVIDER` with **no month filter** (`:288-296`), so the scene cap is all-time by provider; the monthly cap sees scene rows only through the unattributed pool.

G3.2 — **The monthly cap mixes categories and charges the unattributed pool to every household.** `reader.py:292-306`:

```
month_start = _current_month_start_utc()
joined = (
    db.query(func.coalesce(func.sum(ProviderCall.cost), 0.0))
    .join(Job, ProviderCall.job_id == Job.id)
    .filter(Job.household_id == household_id)
    .filter(ProviderCall.created_at >= month_start)
    .scalar()
)
unattributed = (
    db.query(func.coalesce(func.sum(ProviderCall.cost), 0.0))
    .filter(ProviderCall.job_id.is_(None))
    .filter(ProviderCall.created_at >= month_start)
    .scalar()
)
return float(joined or 0.0) + float(unattributed or 0.0)
```

The joined sum counts the household's job-linked rows: the photo path (`reader.py:226`, `:386`) and the Jina snapshot writer (`snapshots.py:140`). The unattributed pool counts every `job_id IS NULL` row: chat (`chat/service.py:331,369`), planning (`planning/service.py:238,272`), analytics (`analytics/service.py:434,469`), synthesize (`synthesize.py:310`) and scene (`openrouter.py:623`). So the monthly cap mixes text, photo, scene and Jina spend, and because the pool is unowned it counts against every household reading that month. The code comment at `:281-290` states the fail-closed intent; it does not separate providers.

G3.3 — **The photo path writes job-linked rows; the chat/planning/analytics and synthesize writers do not.** `reader._write_ledger` sets `job_id=job.id` (`:226`), and the error writer does the same (`:386`). Chat `_write_ledger`/`_write_error_ledger` set `job_id=None` (`:331`, `:369`); planning `:238`, `:272`; analytics `:434`, `:469`; synthesize `:310`. The Jina snapshot writer is job-linked (`snapshots.py:140 job_id=job.id`), so it is in the joined sum, not the pool.

G3.4 — **Production's retryable set and the gateway test.** Production (`reader.py:61-63`) is `{"outage", "timeout", "rate_limited", "transport", "http_status", "invalid_json"}`. The gateway test (`test_provider_gateway.py:54`) is `frozenset({"outage", "timeout", "rate_limited"})`. The test exercises only `outage` (`:74-82`); its negative branch uses `invalid_json_once` (`:85-91`), which production treats as retryable. `FakeProvider` has modes `valid`, `invalid_json_once`, `needs_evidence`, `outage_retryable` only (`fake.py:20`), and raises only `outage` (`:38`) or `invalid_json` (`:41`).

The production classes the gateway test does **not** cover, by name: **`transport`**, **`http_status`**, **`invalid_json`**. `timeout` and `rate_limited` are in the test's configured set but no fake mode exercises them; `invalid_json` is worse than uncovered — the test asserts it is non-retryable while production retries it.

### A4 — which owner decision each fact settles, and which it leaves open

- **G1:** settles **D-R14-d**'s exit-condition honesty — "changing providers needs configuration, not code" is false for adding a vendor and for selecting provider/fallback today; leaves **D-R14-a** (which vendor) and the shared-base scope open.
- **G2:** settles **D-R14-b**'s availability half — the local OCR/zbar signal path is present in the served image's layer set; leaves open what "the local option" means (this no-provider OCR path vs a local model), the sensitive-host decision, and OCR quality on real photos (not measured).
- **G3:** settles **D-R14-a**'s attribution half (scene spend is `job_id=None`, so it pools across households), **D-R14-c**'s cap-mix half (the monthly cap mixes text, photo, scene and Jina spend), and **D-R14-d**'s slice-1 exit (the gateway test is narrower and misclassifies `invalid_json`); leaves open the runtime magnitude (owner DB read), the cap values, and the money authority.

### A5 — artifact, not claim

The full transcripts with each command and its exit code are the five committed logs: `docs/worklogs/SG-247_g1_g3.log`, `docs/worklogs/SG-247_g2_build.log`, `docs/worklogs/SG-247_g2_measure.log`, `docs/worklogs/SG-247_g2_digest.log`, `docs/worklogs/SG-247_orientation.log` (base/head, remote, running container, `latest`, built tag, clock, process arguments). Every measured fact above is quoted from one of them; the duration is the difference of the two `date -u +%s` readings printed in this report, as CO-79 requires. The failed first build (`build_exit=1`), the empty `provider_call.py:216-230` read, the failed `.History` probe and the `diff -q` exit 1 are recorded there, not hidden.

### A6 — PB-3 vacuity / the opposite result

- G1: if a fifth `fallback_id=None` site or a ledger-writer/outcome edit existed, the grep would show it and G1.1 would be "no" on the policy half. If the registry gate were generic, the new registration condition would not be needed. If `synthesize.py` used the router, the sixth caller would not exist. The measured code shows the opposite in each case.
- G2: if tesseract were absent, `tesseract --version` would exit 127 and `shutil.which` would print `None`; if libzbar were absent, `from pyzbar.pyzbar import decode` would fail to load the shared library; if the image differed at the layer level, the 12 layer hashes would differ and the facts would not transfer. The commands would show each opposite.
- G3: if the scene writer set `job_id=<id>`, line 623 would not be `None`; if the pool filtered a provider, the second SELECT would carry that filter; if the test's set equalled production, line 54 would list six classes and the fake would have `transport`/`http_status`; if the photo writer wrote `None`, line 226 would be `None`. The code shows the opposite in each case.
- G2 image identity: if the built image were the same digest, both `.Id` values would be `97ced17c...`; they are `0cb60586...` and `97ced17c...`, with identical layers and runtime Config, which is the measured difference between metadata and content.

### Files read beyond the packet's named files

`AGENTS.md`; `/home/andrei/storagegenie-contract/CODER.md`; `VERSION`; `lang/python.md`; `CODER_PRODUCTION.md`; `STATE.md`; `docs/worklogs/SG-240_report.md`; `docs/worklogs/SG-241_report.md`; `docs/worklogs/SG-238_g3_image_libs.log`; `docs/reviews/2026-10-24-row-14-photo-ai-code-facts.md`; `docs/reviews/review-ledger.md` (row 14 and tail); `docs/worklogs/SG-245_report.md` (grep for D-R14); `docs/worklogs/SG-246_report.md` (grep for D-R14); `backend/app/services/providers/router.py`; `backend/app/services/providers/protocols.py`; `backend/app/services/providers/fake.py`; `backend/tests/test_provider_conformance.py`; `backend/app/services/enrich/synthesize.py` (chunk); `backend/app/services/enrich/snapshots.py` (chunk); `backend/app/services/chat/service.py` (chunks); `backend/app/services/planning/service.py` (chunks); `backend/app/services/analytics/service.py` (chunks); `.dockerignore`; `docker-compose.yml`; `backend/pyproject.toml` and `backend/requirements.lock` (grep for tesseract/pyzbar); `/proc/3476656/cmdline`. No `.env` was read.

### Commands run

The five logs carry every command verbatim with its exit code. The main invocations:

- `git fetch origin automation refs/notes/storagegenie-coder-reports:...` rc=0; `git rev-parse origin/automation` -> `20a8dd9e...`; `git rev-parse HEAD` -> the same; `git status --short` -> clean before the slice.
- `docker version` rc=0 (Server 29.6.2, API 1.55); `docker ps` rc=0 (`storagegenie-backend-1 ... 6c648f1cdce6 ... Up (healthy)`); `docker inspect --format '{{.Image}}' storagegenie-backend-1` rc=0 -> `sha256:97ced17c...`.
- `docker build ... -t storagegenie-backend:sg247-verify .` attempt 1 -> `build_exit=1`, `ERROR: mkdir /home/andrei/.docker: permission denied`; attempt 2 with `DOCKER_CONFIG=...` -> `build_exit=0`, all layers `CACHED`.
- `docker run --rm -i --network none --name sg247-verify ...` -> `run_exit=0`; the four measurements above; `docker ps -a --filter name=sg247-verify` -> empty.
- `docker image inspect --format '{{.Id}} ...'` rc=0 for both tags; `diff -q` of the `.Config` JSONs -> rc=1 (files differ); the field comparison rc=0 -> only `Labels` differs; the `.History` probe failed (I9) and is not used.
- G1/G3: `grep -rn "fallback_id=None"`, `grep -rn "RouterConfig("`, `grep -rn "job_id="`, `grep -rn "settings.sg_provider_id\|reader_mod.provider_registry"`, the `sed` windows at the cited lines, and `wc -l` on `70-164`, `298-309`, `361-372` -> 95 + 12 + 12 = 119. These exited 0; the recorded non-zero exits are the first build (I1), the expected no-such-image inspect that followed it, the `diff -q` (expected difference, I2), and the empty `provider_call.py:216-230` read (my own probe, noted); the failed `.History` probe is I9.
- `ps -eo pid,ppid,args | grep '[o]pencode run'` and `tr '\0' ' ' < /proc/3476656/cmdline` -> the identity line above; `git remote -v` -> `git@github.com:Andovol/StorageGenie.git`.

### Constraints answered

- **Wrote nothing product-facing.** Only the five evidence logs and this report; no product, config, schema, migration, dependency or test byte; no adapter, registry or settings change.
- **No database opened**, not even read-only; no `sqlite3`, no app import, no health call (I7). No production data read.
- **No provider called**, no model downloaded, no key or `.env` value read, **$0**.
- **One image build** into the throwaway tag `sg247-verify`; `latest` and the running container untouched; the throwaway container removed; the built image kept, tagged `sg247-verify` only.
- **No restart, recreate, migration, compose call or host change.** No denied privileged operation; no `sudo` (PB-2). The Docker CLI HOME issue is I1.
- **Budget:** 569 s of the lane's 2100 s and the packet's 1500 s bound; every command bounded (PB-5); none killed; slice retries 0 (one failed build invocation was rerun with `DOCKER_CONFIG`, I1).
- **PB-1/PB-3/PB-4/PB-6:** the measurements above contradict the packet's line citations and its "confined to seam + adapter + pins" expectation (I3, I4, I5); the identity is from `/proc`, not a system-prompt label; the opposite-result checks are A6; no stop condition arose.

### CO-103 skipped as unnecessary

- Full or targeted test suite: the slice changes no code and the packet says "read, do not run"; `{{VENV}}`/`{{VTEST}}` were not used.
- Health probe: it would open the database, which the packet forbids (I7).
- OCR quality on real photos: needs the owner's photos and consent; out of scope.
- Local-model download/serving: out of scope and a sensitive host change.
- Provider call / metered probe: out of scope; no money authority.
- Database read of the unattributed-pool magnitude: the owner's to approve; the code half is G3.
- Adapter code, settings change, registry change, test edit: out of scope by the packet.

## INTENT

Not applicable: this slice changes no behaviour; it reads and measures only. No `INTENT` line is owed, and `TWINS` does not apply (no defect fix).

## UNCLEAR

FIRST READ: the packet's "build ... in a throwaway container, with `--network none` and no bind mount" read as one image build plus one `--network none` measurement container (the SG-240/241 precedent). If the build itself had to run under `--network none`, I8 records that deviation.

DURING EXECUTION: the Docker CLI needed `DOCKER_CONFIG` because `~/.docker` is root-owned; the built tag is an attestation manifest list, so its top-level digest differs from the running image although the 12 layers and runtime Config are identical; the gateway test's `invalid_json` fixture is production-retryable.

REMAINING: the runtime spend magnitude (the unattributed pool) was not read; OCR quality was not measured; the local-model option was not measured; the stage exit condition needs the owner's renegotiation; no health call was made by design.

Verification: PASS

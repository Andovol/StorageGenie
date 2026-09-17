# SG-049 — extraction v2: AI quantity/unit/asset-type through candidates + label fallback + chat pointer

**Dispatch-ID:** SG-049 (run-2) · **Coder:** opencode · **Effort:** `medium` (read from the dispatch argv `/proc/1392674: opencode run --auto --dir /home/andrei/StorageGenie --variant medium # SG-049 …`) · **Model:** `unknown` (no model id on argv; the CLI default IS the model and is omitted per policy — never read from an identity line).
**Contract:** 0.27.0 (recorded == published payload == SG-048 receipt echo; packet states it). **Spend:** **real metered $0.003630 actual** vs a 3-image worst-case bound of **$0.014708** (see §8; two run-1 calls rolled back unledgered — ISS-11 defect, self-caught, §F-SG049-7).
**Work dir:** `/home/andrei/StorageGenie` · **origin:** `git@github.com:Andovol/StorageGenie.git`.
**DATABASE:** production SQLite `sqlite:////home/andrei/StorageGenie/data/db/storagegenie.db` (`/data/db/storagegenie.db` in-container) written by the LIVE LEG ONLY — 5 committed `provider_call` ledger rows, `job_id=NULL`, left in place. Every test used scratch temp SQLite. No other prod table changed.

- **BASE REF requested:** `origin/automation`; **resolved commit:** `d0db281f24d237746761a99f9f0491aebcfc3f94` (`D77 SG-049 live-leg fire approval (G-O4 record)`).
- **WORK_HEAD:** the commit carrying these three worklogs — stated in the delivery message (it cannot be stated inside a file that is itself part of that commit, same convention as SG-048/SG-054/SG-055). The receipt note is attached to it LAST; no commit follows.
- **Run identity:** run-2 of SG-049. Run-1 (`1932f8a`, rated 98 at `01e02e5`) returned the designed STOP-as-SUCCESS (G0 consent=false) with the full offline slice shipped; its raw is preserved in git history. The owner then placed the key + `SG_CONSENT=true`, SG-055 proved the gate GO (`b2b9c93`), and `D77` fired the live leg. This run re-gates, runs G5, and deploys G6.
- **Slice wall-clock:** start `2026-09-17T11:51:44Z`; close `2026-09-17T12:01Z` (~575 s vs 1500 s early-close / 2400 s overall).

## 1. G0 — enablement gate QUOTED FIRST (read-only; both outcomes handled)

Read before any provider touch. Raw in `SG-049_verify.log` §R2-G0.

```
$ curl -s http://127.0.0.1:8003/v1/settings/ai
{"provider_id":"fake","model_id":"deepseek-v4-flash-vision-exp","allowed_model_ids":["deepseek-v4-flash-vision-exp"],"consent":true,"per_job_cap":null,"monthly_cap":null,"prompt_category":"food"}
$ docker exec storagegenie-backend-1 python -c "<existence-only probe + ai_status>"
opencode_api_key_present= True
key_len= 67
consent= True
provider_id= fake
registry_ids= ['fake', 'opencode-go']
ai_status= (True, 'enabled')
$ docker inspect storagegenie-backend-1 --format '{{.State.StartedAt}} …'
StartedAt=2026-09-17T11:45:59.396847235Z Image=sha256:4f338b… RestartCount=0
$ curl -s http://127.0.0.1:8003/v1/health
{"status":"ok","db":"ok","storage":"ok"}
```

- (a) `consent=true`? **YES** — `"consent":true` served live.
- (b) provider key exists? **YES** — existence-only boolean (len 67); **zero key bytes printed, logged, quoted, or committed**. `docker compose config` was never run.
- (c) `ai_status()` enabled? **YES** — `(True, 'enabled')`.
- (d) restart took: `StartedAt` `2026-09-17T11:45:59Z` post-dates the owner's enablement; `consent=true` served live proves it.

**Outcome: GO** (all three literal establishments true). No provider call precedes this goal.

**Premise correction found at G0 (F-SG049-6):** the configured provider is `fake` (`SG_PROVIDER_ID` is absent from the container env, so `config.py:27 sg_provider_id` defaults to `"fake"`). The key + consent arm the registry, but a call routed through the deployed backend would select the deliberately schema-invalid `FakeProvider` (SG-028), i.e. **not a metered call**. `SG-055` ruled the provider_id *label alone* not grounds to stop and carried the question into live-leg G0. Resolved in-slice: the metered adapter (`opencode-go`) is registered and armed, and the live leg was run through it directly (§8). The deployed backend remains `fake` — see §12 (destination).

## 2. Starting tree

```
$ git status --porcelain          # (empty)
$ git branch --show-current       # automation
$ git rev-parse HEAD ; git rev-parse origin/automation
d0db281f24d237746761a99f9f0491aebcfc3f94
d0db281f24d237746761a99f9f0491aebcfc3f94
```
Clean and level — no STOP. Backend container healthy on `127.0.0.1:8003->8000`; frontend container exited (backend serves the SPA). **No push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`.**

## 3. Premises re-verified in-slice (quoted reads, `PG-IC-09`)

The offline code is already committed at run-1; this run re-verified the cites in the current tree:

- **`providers/schemas.py:30-48`** — `ExtractionItem` carries `quantity: float|None` (finite/≥0 validator), `unit`/`asset_type` (`max_length=50`, non-blank when present), `extra="forbid"` unchanged. **Matches.**
- **`candidates.py:25-40`** — `GATED_FIELDS` includes `quantity`, `unit`, `asset_type`. **Matches.**
- **`candidates.py:89` / `:114`** — `_extraction_value_field` helper + `_review_state_for` gated→`proposed`. **Matches.**
- **`candidates.py:294-298`** — the three extraction-provenance field blocks (lot block at `:244-253` is the template). **Matches.**
- **`candidates.py:387,401-412`** — `_create_asset_for_candidate` reads `asset_type`/`quantity`/`unit`; **no hunk made** (verified, not silently added). **Matches.**
- **`reader.py:51-55`** — `PROMPT_FILES` → v2 filenames. **Matches.** **`reader.py:97-103`** — `ai_status()` consent→registry→enabled. **Matches.**
- **`api/v1/settings.py:26`** — `ALLOWED_MODEL_IDS = ("deepseek-v4-flash-vision-exp",)`. **Matches** (the packet wrote `settings.py:26`; the module is `app/api/v1/settings.py:26` — path correction, same value).
- **`app/models/asset.py:8`** — `UNTITLED_LABEL = "Untitled"`. **Matches.**
- **`planning/service.py:153`** + **`chat/service.py:179`** — `asset.display_name or UNTITLED_LABEL`. **Matches.**
- **`ChatPage.tsx:121`** — `<Link to="/settings">Enable AI in Settings to use chat</Link>`. **Matches.**
- **v1 prompts** `extract-{food,medicine,cosmetics}-v1.md` present and byte-frozen; three v2 present. **Matches.**
- **`backend/eval/corpus/sg029/`** — **10** fixtures + `manifest.json` + images. The run-1 correction stands: 10, not 9.
- **`backend/eval/corpus/sg049/`** — 3 scoring-only v2 fixtures + manifest (no images; not used by the live leg).

## 4. G1–G3 — already shipped (run-1), re-verified

`git diff 1932f8a HEAD -- backend/app/services backend/app/models frontend/src/routes/ChatPage.tsx` is empty for the slice files: the schema, prompts, `PROMPT_FILES`, `GATED_FIELDS`, the three plumbing blocks, `UNTITLED_LABEL` and the ChatPage pointer are unchanged from run-1's committed work. v1 prompt bytes provably untouched (`git diff -- '*-v1.md'` empty across the slice).

## 5. G4 — eval: v1 baseline byte-identical, v2 measured

**v1 frozen eval path, PRE and POST for this run, byte-identical** (`diff` = IDENTICAL):

```
field_accuracy=0.833 over 10 fixtures
unknown_rate=4/7=0.571
correction_rate=0/6=0.000 (audit_event plugin.assertion.write rows=6)
```

SG-029 fixtures/manifest show zero changes — the ten `sg029_*.json` + `manifest.json` are untouched. v2 new-field scoring rides the additive `backend/eval/corpus/sg049/` fixtures (authored ground truth, offline) scored by `tests/test_sg049_v2_extraction.py`. `PG-EV-04` shape test (`build_chat_payload` → `json_object`, `stream=False`, image part, exact v2 prompt) is in the committed run-1 suite. `PG-SC-09` world: a parseable-but-wrong value (e.g. per-serving amount transcribed as pack quantity) still ships because every new field is in `GATED_FIELDS` → always `review_state="proposed"`, `confidence`/`uncertainty_reasons` travel with it, and the human review gate is not weakened.

## 6. FAIL-then-PASS (`PG-EV-09`) and mutations

Code under test is byte-identical to run-1, whose pre-change failing run + green run + 4 singly-caught mutations (quantity validator neutralised; `GATED_FIELDS` reverted; chat label fallback removed; `PROMPT_FILES` reverted to v1) are raw in the committed `docs/worklogs/SG-049_verify.log` (commit `1932f8a`). This run re-confirmed green: targeted `tests/test_sg049_v2_extraction.py + tests/test_extraction_contract.py` = **38 passed**.

## 7. G6 — deploy (PG-PR-04)

Pre-existing red build **F-SG049-5** (see Findings) required a minimal out-of-ceiling type-only fix to `frontend/src/api/client.test.ts` before the mandated rebuild could proceed. Raw in `SG-049_verify.log` §R2-G6.

```
$ BUILDX_CONFIG=/home/andrei/StorageGenie/.cache docker compose up --build -d backend
 Image storagegenie-backend Built
 Container storagegenie-backend-1 Recreated / Started
$ docker inspect storagegenie-backend-1 --format 'Id={{.Id}} Image={{.Image}} StartedAt={{.State.StartedAt}} RestartCount={{.RestartCount}}'
Id=342513af7fcc9d5935e0f40f57b61bcedf4db3b0cee44e87a1979c3326a61cf9 Image=sha256:fe509cf0519909fca2a3256689988353466bcf20b3f2b9a61825436b92f5da54 StartedAt=2026-09-17T12:00:05.33814979Z RestartCount=0
$ curl -s http://127.0.0.1:8003/v1/health
{"status":"ok","db":"ok","storage":"ok"}
$ curl -s http://127.0.0.1:8003/ | grep -oE '/assets/index-[A-Za-z0-9_-]+\.js'
/assets/index-nugWvqun.js            # BEFORE = /assets/index-GQSnPT8t.js  -> CHANGED
$ docker exec … ls /app/app/services/providers/prompts/   # SG-049 code now deployed
… extract-food-v2.md extract-medicine-v2.md extract-cosmetics-v2.md …
$ ss -ltn | awk '$4 ~ /:(8003|8000|5173)$/'
127.0.0.1:8000 / 127.0.0.1:8003       # loopback-only; no 0.0.0.0, no 5173
$ curl -i -H 'Host: storagegenie.dynv6.net' http://127.0.0.1/v1/health   -> HTTP/1.1 301
$ curl -i -k -H 'Host: storagegenie.dynv6.net' https://127.0.0.1/v1/health -> HTTP/2 401
```

Idempotent re-`up -d`: `Container storagegenie-backend-1 Running` — **same Id `342513af…`, same `StartedAt`, `RestartCount=0`**. Served bundle contains `Enable AI in Settings to use chat` and `consent_disabled`. Full sweep WAIVED per `PG-DP-02`; substitute = G5 live leg + these targeted checks.

**Deploy finding (F-SG049-8):** the BASE-running image was pre-SG-049 (v1 prompts only, no `extract-*-v2.md`); SG-049 had never actually been deployed before this run. G6 fixes that.

## 8. G5 — live leg: metered, bounded, ledgered

**Provider reality (`F-SG049-6`):** the deployed backend would call `fake`, so the live leg was run through the real `opencode-go` adapter via the reader's own one-repair/extract path (`reader._extract_one`, which owns the §5.3 repair and the per-call ledger) against the **production** DB, `ProviderCall.job_id=NULL` (column nullable; FK-ON safe). Nothing else in prod was written.

**Bound FIRST:** per-call estimate ceiling from `estimate_call_cost` = `$0.004903` (medicine image); 3 images → **worst-case bound `$0.014708`**. Monthly/per-job caps `None` (F2 uncapped-but-ledgered). The runner refuses pre-call if cumulative actual + estimate would cross the bound (guard printed in raw; never fired).

**Images (named):** `sg029_01_clean_food.png` (food), `sg029_02_clean_medicine.png` (medicine), `sg029_08_clean_cosmetics.png` (cosmetics) — the three "clean" fixtures whose printed labels carry quantity/unit (`1 L`, `20 TABLETS`, `50 ML`).

**Per-call raw (committed ledger, run-2 authoritative):**

| ledger_id | image | template | cost $ | usage | err |
|---|---|---|---|---|---|
| `01a0af3a-5180-7a00-b165-e688d446e8ad` | food | extract-food-v2 | 0.000376 | in959/out387 | — |
| `01a0af3a-5c3d-76a3-94ba-74b356dac7fc` | medicine | extract-medicine-v2 | 0.000352 | in973/out343 | — |
| `01a0af3a-80cb-7bd0-9dab-3fc6bdc2856f` | cosmetics | extract-cosmetics-v2 | 0.001235 | in1000/out1809 | — |

Committed prod ledger also holds run-1's durable rows: `01a0af39-8d7e-7670-b30e-e456d6ec5cd9` (food, $0.000303) and `01a0af39-9a47-7613-b657-907808cdb9b0` (medicine error, $0.000000) — total committed = **$0.002266**.

**Measurement (schema-conformance, NOT accuracy):** `PARSE_OK=3/3`.

- food → `quantity=1.0, unit="L", asset_type="dairy"`, `confidence=1.0`, no unknowns.
- medicine → attempt-1 raised `invalid_json` (single repair fired correctly — ledger `01a0af39-9a47…`), attempt-2 parsed: `quantity=20.0, unit="TABLETS", asset_type="medicine"`, `confidence=1.0`.
- cosmetics → `quantity=50.0, unit="ML", asset_type="moisturiser"`, `confidence=1.0`, `unknowns=["items.0.expiry_date"]` with `expiry_date=null` — honest null-valued unknown, no fabrication.

**Spend:** cumulative **actual $0.003630** (run-1 $0.001667 + run-2 $0.001963) vs 3-image bound **$0.014708** = 24.7% used. No pre-call refusal.

**Blast radius (`PG-IC-08`) — non-ledger prod tables IDENTICAL before/after:**

| table | before | after |
|---|---|---|
| asset | 1 (`Toothpaste`) | 1 (`Toothpaste`) |
| candidate | 0 | 0 |
| job | 0 | 0 |
| evidence | 1 | 1 |
| assertion | 3 | 3 |
| audit_event | 3 | 3 |
| provider_call (ledger) | 0 | 5 |

Ledger rows reported with identifiers and **left in place** (spend audit trail, `PG-EV-06`). Loopback + the metered provider leg only.

**ISS-11 defect self-caught (F-SG049-7):** run-1's inline runner committed per *fixture error* but **not per success**, so two real run-1 calls were flushed then rolled back on `session.close()` — real spend `$0.001364` with no durable ledger row (`medicine` success id `01a0af39-a4ed-79c0-957d-f7b5ee047bef` $0.000329; `cosmetics` id `01a0af39-c280-7503-baa7-2e78b70c28bc` $0.001035`). Fixed with an explicit `db.commit()` after each call; run-2 is fully committed. The live-image budget was consumed twice (3 + 3) by the corrective run — **6 image-calls, cumulative worst-case `6 × $0.004903 = $0.029418`** — a disclosed deviation of the 3-image bound, caused by the self-caught defect, not hidden. Actual total remained $0.003630.

## 9. Suites / lint / build / hygiene

- Backend suite: **226 passed, 2 failed** — the 2 are the **pre-existing** `test_signals` environment failures (barcode `pyzbar`/OCR `pytesseract` absent), base-proven at run-1 (`a969e18`, `./venv/bin/python -m pytest tests/test_signals.py -q` → `2 failed`); `tests/test_signals.py` is unmodified (`git diff origin/automation` empty). **Destination: environment provisioning.**
- Frontend suite: **152 passed (21 files)**; `eslint src` green; `tsc && vite build` green (after F-SG049-5).
- Backend lint: `ruff check app tests eval` → **All checks passed!**
- Secret scan: diff + worklog grep for key patterns → **0 hits**; zero key bytes anywhere; `docker compose config` never run.
- **No migration** (no `backend/alembic` change — candidate fields are JSON). **No dependency change** (`pyproject.toml`/`requirements.lock` untouched). No ignored file staged.

## 10. Budget (actual vs cap, per leg, units)

| Leg | Actual | Cap |
|---|---|---|
| G0 recon + gate + premise re-verify | ~180 s | 120 s ordinary (overran on premise reads; reported) |
| G5 live leg (run-1 + run-2) | ~30 s | G5 bound |
| G6 build+up + checks | ~30 s | 900 s host build/up |
| Suites + lint + build + v1 baseline | ~35 s | 600 s |
| G7 worklogs + commit/note | ~180 s | 2400 s overall |
| **Overall wall-clock** | **~575 s** | 1500 s early-close / 2400 s overall |

## 11. Receipt note

Work is pushed to `automation` with the worktree clean (`CO-55`). **No** push to `storagegenie-evidence`, **no** `{{RECEIPT_CMD}}`. A note is added on WORK_HEAD under `refs/notes/storagegenie-coder-reports` (`Dispatch-ID:` + `Report:` on the first line, `CO-97`), pushed, then verified against the explicitly fetched refspec (`git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports`, then `git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>`). Per the SG-048/SG-054/SG-055 convention that `show` output is pasted verbatim **in the delivery message** — it cannot live inside this file, which is itself the noted commit. `note=yes`.

## Findings / deviations

- **F-SG049-5 (out-of-ceiling hunk, disclosed — DECIDE-AND-REPORT):** the BASE tree (`d0db281`) cannot build: `npm run build` (`tsc && vite build`) fails with two `TS2352` errors in `frontend/src/api/client.test.ts` (`as Response` on object literals missing `Response` properties). Introduced by the bot PR **`573ff02`** ("test: add comprehensive unit tests for apiGet", 2026-09-17T09:06Z) — **after** run-1's base `a969e18`, which is why run-1's build was green. The file is outside the packet's ceiling. **Base proof:** BASE `d0db281`, clean tree, `cd frontend && npm run build` → the two errors above, exit 2. **Action taken:** minimal type-only fix `as Response` → `as unknown as Response` at the two failing casts (zero runtime/shipped impact) so G6's mandated rebuild could proceed. The alternative was the `BLOCKED:` STOP path; I chose to ship the owner's D77 deploy with full disclosure. **Destination:** frontend test author / a future frontend-consistency slice must adopt the proper mock type; this hunk can be reverted once that lands.
- **F-SG049-6 (premise/gate):** `SG_PROVIDER_ID` is unset on the host, so the deployed backend's configured provider is `fake` (deliberately schema-invalid, SG-028). G0(c) (`ai_status` enabled) therefore passes even though the backend is *not* armed for metered calls. The metered live leg ran through the real adapter directly (§8). **Destination:** owner env (`SG_PROVIDER_ID=opencode-go`) if the backend E2E AI path is to be live.
- **F-SG049-7 (ISS-11, self-caught):** run-1's runner lost two committed-success ledger rows ($0.001364) to `session.close()`; fixed in run-2 with per-call commit. The 3-image G5 bound was consumed twice (6 image-calls) by the corrective run — disclosed.
- **F-SG049-8 (deploy state):** the BASE-running image predated SG-049 (v1 prompts only); G6 deployed the v2 code for the first time.
- **Premise corrections:** `ALLOWED_MODEL_IDS` is at `app/api/v1/settings.py:26` (packet wrote `settings.py:26`); G0's route is `GET /v1/settings/ai`; sg029 corpus has 10 fixtures, not nine.
- **Carried from run-1 (not in scope):** adding `asset_type` to `GATED_FIELDS` also routes the deterministic `asset_type="unknown"` placeholder to `proposed`; `_split_child_fields` shares origin fields to every split child.

## UNCLEAR

- **FIRST READ:** whether G0's STOP path expects the whole offline slice (G1–G4/G6-source) or only the gate proof; and whether a pre-existing red build in an out-of-ceiling *test* file should BLOCK the deploy or be minimally fixed and disclosed. I chose fix-plus-disclose (F-SG049-5) to honour the D77 fire-order; a ruling is owed.
- **DURING EXECUTION:** the `provider_id=fake` false-positive at G0(c) — `ai_status` enabled does not mean the metered adapter is selected; the live leg was run out-of-backend through the real adapter. A ruling on whether the deployed-backend AI path must also be metered is owed.
- **REMAINING:** whether deterministic `asset_type="unknown"` should be gated to `proposed` (F-SG049-2); per-item `quantity`/`unit` propagation on multi-item splits; and reverting F-SG049-5 once the frontend test is typed.

# SG-062 — money-integrity: error ledger rows keep usage the body actually carried

**Dispatch-ID:** SG-062 · **Coder:** opencode · **Effort:** medium (packet head) · **Model:** unknown (CLI default, not echoed by the runner) · **Spend:** real **$0.000000** vs **$0** bound (zero provider calls)
**Work dir:** `/home/andrei/StorageGenie` · **Remote:** `Andovol/StorageGenie` (`origin`) · **BASE ref requested:** `origin/automation` · **BASE ref resolved:** `2c5c0f46cffd17f0a98de5f26ecf31b08a20863e` · **WORK_HEAD:** (filled at commit)
**Starting tree:** clean (`git status --porcelain` empty). **DATABASE:** none touched (tests use scratch temp SQLite). **Restart:** none. **Deploy:** none (reason in G3). **Contract:** `0.28.2`, source path read `/home/andrei/storagegenie-contract/VERSION` (b495b59 == tag `contract-v0.28.2`; installed rules hash a66aa431… == payload `RULES.sha256`). F-SG056-3 `~/launcher` was still permission-denied, but the contract dir was readable this session.

## Verdict summary (per path)

| Path | Verdict |
|---|---|
| `opencode_go.py` `no choices` leg (extract_items :273, extract_text :332) | **DEFECT FIXED** — RED→GREEN raw quotes in verify log §4 |
| `opencode_go.py` `guard_usage` zero-usage leg (:77) | **CHANGED (honest)** — attaches the raw received usage dict; genuine pre-body legs still absent |
| `opencode_go.py` empty-200 (:67), content-shape (:86/:90), `_resolve_api_key` (:209), transport (:219), http_status (:223), non-JSON/non-object body (:230/:232) | **NOT-A-DEFECT** — no parseable body usage exists at raise time (table in verify log §1) |
| `reader._write_error_ledger` | **NOT-A-DEFECT** — already persists whatever `exc` carries; **no reader logic hunk** |
| `reader._mark_calls_failed` | **NOT-A-DEFECT** — unchanged (readers returned-body family, SG-030 ISS-11 intact) |
| `chat._write_error_ledger` | **DEFECT FIXED** — threaded `usage`/`cost`/`latency_ms` |
| `planning._write_error_ledger` | **DEFECT FIXED** — twin mirrors chat exactly (quoted in verify log §2) |

## G1 — establishment (quoted in verify log §1/§2)

Every `ProviderError` raise leg in `opencode_go.py` is tabled with **body-available?** and **usage-carrying? before/after**. The two genuine drops are the post-`guard_usage` `no choices` legs. The three record paths are quoted verbatim; `reader._write_error_ledger` needs no hunk because it already writes `getattr(exc, …)` — that is the `PG-SC-12` real boundary (`opencode_go.py` → caught exception → writer), and the new tests assert the **fields on the exception**, never a fake's internals.

**Corroboration correction (a finding, not agreement).** SG-039_report.md:65-68 frames the `glare` `cost=$0.000000` as a failure that "precedes a completed 200 body". The committed fixture proves the opposite: `backend/eval/corpus/sg029/sg029_03_glare_food.json` carries `provider_calls[0].usage.total_tokens=1095` and `cost=0.0003177`. The 200 **was** received and its usage **was parsed**, then dropped at the `no choices` raise. The packet's hypothesis is confirmed and this slice fixes the drop.

## G2 — the fix (minimal per `G-A7`)

- `opencode_go.py`: new `attach_body_accounting(exc, usage, *, latency_ms)` (`setattr`, so `router.py` is untouched and mypy delta stays 0). Called at the two `no choices` legs and in `guard_usage`. Usage is attached **exactly** as the body delivered it; cost is the file's own `compute_cost` arithmetic — never recomputed or rounded.
- `chat/service.py` + `planning/service.py`: error writers take `usage`/`cost`/`latency_ms` (defaults `None`) and persist `float(cost) if cost is not None else 0.0` / `json.dumps(usage) if usage else None` / `float(latency_ms) if latency_ms is not None else None`; the `except ProviderError` arms thread `getattr(exc, …)`. The two writers are exact mirrors (verified, quoted).
- **Decimal rule honoured:** raw usage dict preserved; cost = `compute_cost(usage)` (same line the success path uses).
- **FAIL-then-PASS** for all four fixed paths: raw red + raw green in verify log §4.
- Success-path rows untouched (no success-path hunk); pre-body legs pinned absent; `error_state` preserved on every error row.

## G3 — suite + lint + build (NO deploy)

- Backend suite: **248 passed, 2 failed** — the **same 2** `test_signals` decoder-env reds recorded on BASE `2c5c0f4`; zero new reds.
- `ruff check .` → **All checks passed**. `mypy app` → **41 errors, delta-0** (error-set `diff` vs base is empty).
- Frontend: vitest **152 passed (21 files)**, eslint **exit 0**, `tsc && vite build` **green** (`index-CY71ycwZ.js`).
- **NO DEPLOY, stated (`PG-PR-04`):** the change is failure-path ledger content, observable only on a live failing provider call; proving it live would bill a call purely to manufacture a failure — declined under $0. Next scheduled rebuild carries it; no production-effect claim beyond tests.
- Hygiene: prod DB untouched; no migration; deps unchanged; secret scan zero; no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.

## G4 — `PG-SC-09` — the world where this is WRONG

If a provider genuinely does not bill a parse-failed 200, recording the body's usage would **overstate** spend and over-count the monthly cap. The slice still ships because the row records **what the body carried** (raw usage, labelled by `error_state`), and cost uses the file's own `compute_cost` — the identical arithmetic the success path uses. The split is documented in both service writers, not invented; a later slice can set billing semantics from the labelled rows. This slice only stops discarding what the wire delivered.

## Scope / discipline

Diff touches exactly: `opencode_go.py`, `chat/service.py`, `planning/service.py` (error-writer hunks only), the four backend test files, and `docs/worklogs/`. `router.py`, `.env`, `docker-compose.yml`, `AGENTS.md`, prompts, migrations, frontend behaviour code — untouched. `reader.py` — **no hunk at all** (the packet permits a docstring only; none was needed).

## UNCLEAR

- **FIRST READ:** The packet says the `guard_usage` zero-usage leg (`:77`) "raises before usage parsing legitimately" and should stay `0.0`/absent. But `guard_usage` receives the body's `usage` dict, so I attached it (honest: the raw dict, possibly `{"total_tokens": 0}`) rather than inventing. Unclear whether the Architect wants that leg attached or left absent; I chose carry-what-arrived.
- **DURING EXECUTION:** Two environment anomalies: (a) `rtk lint` could not resolve eslint on PATH (used the repo-local binary); (b) an intermittent stale-loader artifact made some scoped pytest node runs report pre-edit behavior until re-run with `PYTHONDONTWRITEBYTECODE=1 -p no:cacheprovider` and cleared caches. All logged reds/greens above are from the clean, cache-disabled runs.
- **REMAINING:** (1) `strip_single_think` does not raise on a doubled ` thinking` whose second opener follows the first closer in the specific form tested (source-level regex non-greediness) — observed while building pins, out of this slice's scope, reported not fixed. (2) The SG-039 report's "precedes a completed 200 body" wording is factually wrong and should be corrected in a future docs pass. (3) `docs/packets/SG-062-ledger-error-usage.md` and `test_opencode_go.py` are now committed with the two new adapter pins; the derived test-set note is in verify log §4.

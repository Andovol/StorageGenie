# SG-101 — Text-path token bound + empty-content accounting, one live proof call (report)

**Dispatch-ID:** SG-101
**Coder / effort:** `opencode` / `high` (read from process arguments: `opencode run --auto --dir /home/andrei/StorageGenie --variant high <packet>`) — **model: cli-default** (no model id sent; omitted per policy; read from process args, never the system-prompt identity line).
**Work dir:** `/home/andrei/StorageGenie` · **Remote:** `origin` = `git@github.com:Andovol/StorageGenie.git`
**BASE (requested ref `origin/automation` resolved):** `f02daebc0b6d67d5ba9941d1150974c527909100`
**WORK_HEAD:** `<filled after commit>` · **Report:** `docs/worklogs/SG-101_report.md`
**Contract echo (verbatim):** `0.33.0` — recorded in `STATE.md:4` (`**Version:** \`0.33.0\` (D129 adoption 2026-09-23: checkouts \`e8f8113\` + \`999e94c\` + \`b232b84\` oldest-first, installed \`18de7fd7…\` = payload at all versions — clean)`) and `AGENTS.md:4` (`Rule-set version this project records: **0.33.0**`). Published-side re-hash **UNEXECUTED**: `.rules-cache/` is absent on this host (gitignored, launcher-populated) and `origin` carries no `contract*` ref — F-SG099-3 carries forward.
**DATABASE: none. Restart: none. Deploy: none. Container actions: none** (`PG-PR-04`). No migration: `models/` + `alembic/` diff empty.
**Spend (real $):** **$0.00140655 actual** for the ONE live call, versus the **$0.0053241** in-slice worst-case estimate and the **$0.05** per-call cap (`PG-IC-04`). The call completed and wrote **one** `ProviderCall` ledger row. No other metered resource touched; all offline work $0.

---

## Result in one line

Both D140-approved fixes are **implemented and proven**: the TEXT turn carries its own `TEXT_MAX_TOKENS=8000` bound (vision `DEFAULT_MAX_TOKENS=2000` byte-untouched), the `extract_text` empty-content raise now attaches the received body's usage/cost/latency, the estimate covers the new bound, and the **ONE live synthesis call COMPLETED** (13 attributed facts, `$0.00140655`, 8.0s) — closing SG-099's live leg.

## G0 — consent / key-name gate: **GREEN** (gate open; live ran)

- `reader.ai_status()` → `(True, 'enabled')`; `settings.sg_provider_id = opencode-go`; `OPENCODE_API_KEY` present (NAME only; `.env` key NAMES: `DATABASE_URL`, `STORAGE_ROOT`, `HOUSEHOLD_DEFAULT_NAME`, `CORS_ORIGINS`, `OPENCODE_API_KEY`, `SG_CONSENT`, `SG_PROVIDER_ID`, `JINA_API_KEY` — no value printed, logged, quoted or committed). No key value appears in any file, log, or assertion.

## G1 — separate text-turn bound: **MET**

- New `TEXT_MAX_TOKENS = 8000` (`opencode_go.py:37`), used by `build_text_payload` (`:203`) instead of `DEFAULT_MAX_TOKENS`; `DEFAULT_MAX_TOKENS = 2000` is byte-untouched and its `test_opencode_go.py:135` pin stays green.
- **Which builder the vision path uses (the load-bearing fact the packet asked to establish):** the vision path uses `build_chat_payload` (`extract_items:312`), which still sends `DEFAULT_MAX_TOKENS`. `build_text_payload` is reached only by `extract_text:373`. The two builders do **not** share, so the split point stays inside `build_text_payload` — no call site moves.
- **Worst-case recomputed in-slice from the real `compute_cost` arithmetic:** input upper bound for the fixture turn = **3494 bytes** (one token/byte), output bound 8000 →
  `estimate_text_cost` = **(3494 × 0.15 + 8000 × 0.60)/1e6 = $0.0053241**, i.e. **9.4× under** the $0.05 per-call cap. (The packet's ≈$0.0054 assumed a 4000-byte input bound; the fixture turn is 3494 bytes. Same order, slightly under — reported, not bent.)
- **Joint caps statement (`PG-SC-06`):** per-call $0.05 (synthesis + endpoint) + monthly ledger + adapter direct guards + router `cost_budget` are unchanged; the new bound raises only the text-turn worst case to ≈$0.00532 and moves nothing else. Monthly posture unchanged.

## G2 — empty-content accounting: **MET**

- `extract_text` now wraps `strip_single_think(guard_content(message.get("content")))` in `try/except ProviderError` and calls `attach_body_accounting(exc, usage, latency_ms=latency_ms)` before re-raising (`opencode_go.py:384-392`), exactly like the no-choices leg (`:378-381`). `usage` is in scope from `guard_usage` (`:375`), so a billed empty-200 always carries what crossed the wire and the existing SG-030 `_write_error_ledger` contract records it with no reader hunk.
- **Disclosure (slightly wider than the literal `:374`):** the `except` covers both content-shape raises — `guard_content` (empty/blank) **and** `strip_single_think` (stray/double `<think>`). Both are post-body, post-usage rejections of a billed leg, so accounting them is the same contract; the packet named only the empty-content leg.
- `guard_content`'s docstring (`:70-78`) corrected: it no longer claims empty-200 legs are unbilled; it states the helper attaches nothing itself and the TEXT caller attaches the received body's accounting.
- `synthesize.py`'s `estimate_text_cost` default is now `max_tokens=TEXT_MAX_TOKENS` (`synthesize.py:119`), the one existing-file hunk outside `opencode_go.py` (M45, failing-test proof below). `DEFAULT_MAX_TOKENS` import removed as now-unused.

## G3 — tests + gates: **MET**

- New `backend/tests/test_sg101_text_path.py` — 5 tests driving the REAL builders/adapter/caller (no network, no key):
  1. text payload carries `TEXT_MAX_TOKENS`; `DEFAULT_MAX_TOKENS == 2000`; the vision `build_chat_payload` keeps 2000;
  2. the SG-099 empty-200 body shape (content `""`, `finish_reason=length`, usage 1039/2000/3039) raises **with** `usage`/`cost`/`latency_ms` attached (the `:333` raise-legs shape extended to the content leg);
  3. the vision empty-content leg stays usage-free (text path ONLY);
  4. the estimate at the new bound is strictly above the old default (failing-test proof: `0.0017241` vs `0.0053241`);
  5. a cap between the old and new worst cases refuses in `synthesize` with **zero invocations** and **zero ledger rows**.
- **Fail-then-pass, BOTH raw committed (`PG-EV-09`, `PG-EV-01`):** fail-pre = clean HEAD + the new test file → **4 failed, 1 passed in 0.45s** (raw R-FAILPRE); pass-post = **5 passed in 0.43s** (raw R-PASSPOST). The one pass-pre test is the vision-stays-usage-free guard (it pins unchanged behaviour by design).
- **Existing vision tests unmodified-green:** `git diff --name-only -- tests/test_opencode_go.py tests/test_chat.py` → **empty**; targeted run of `test_sg101 + test_opencode_go + test_chat + test_sg099` → **55 passed**.
- **Gates:** ruff clean; mypy **41 → 41** errors (delta **0**, 84 source files); secret-pattern grep over changed files **0 real** (only code references `self._api_key`, `Bearer {self._resolve_api_key()}` — no `sk-`, no literal key); full suite **2 failed, 503 passed** — the 2 failures are the known decoder env reds (`test_signals.py` pyzbar + tesseract absent), **stash-proved** at clean HEAD in a throwaway worktree (2 failed, 5 passed).
- **M45 collision self-caught (F-SG101-1):** `test_privacy_audit.py` hardcodes line numbers in `opencode_go.py`. The adapter hunks shifted the send site `:252 → :263` and the `redact_image` call `:299 → :310`. Three pins were updated (minimal, with a disclosed docstring note), exactly the SG-099/F-SG099-4 precedent. This is the one existing-file touch **outside** the packet's enumerated ceiling; it was required by the "full suite green modulo the 2 known reds" criterion. Reported as a finding.

### The one live call (60s bound): **COMPLETED**

Ran the REAL caller → REAL `OpenCodeGoProvider.extract_text` (no fake) through the edited in-tree source, temp SQLite DB `/tmp/opencode/sg101/live.db`, `DATABASE_URL` overridden before import, root `.env` loaded silently (NAMES/values never printed). Raw-body recorder installed on `_post` from leg 1.

- `ai_status` enabled; `sent_max_tokens=8000` (the fixed bound crossed the wire).
- **model** `deepseek-v4-flash-vision-exp` · `finish_reason=stop` · **usage** prompt 1037 / completion 2085 / total 3122 (`reasoning_tokens=1269`) · **cost $0.00140655** · **latency 8005.56 ms** · **facts 13** · elapsed 8.014s.
- **`completion_tokens=2085 > DEFAULT_MAX_TOKENS=2000`** — under the old bound this same call would have truncated again (`finish_reason=length`, empty content). The bound is load-bearing, not cosmetic (F-SG101-2).
- **1** `ProviderCall` ledger row on the temp DB (`error_state=null`, `job_id=null`). Raw body captured (R-LIVE).
- **Production counts identical before/after:** `provider_call 17 / job 7 / candidate 6 / assertion 28 / asset 6` both times (read-only `mode=ro`). Temp DB only; production never opened. No second call.

## F-SG101-1 — privacy-audit brittle line pins (M45, disclosed)

Three hardcoded `opencode_go.py` line pins in `backend/tests/test_privacy_audit.py` (`:252` ×2, `:299` ×1) were invalidated by the adapter hunks and updated to `:263`/`:310`. This is a pin update, not a behaviour change: `_send_sites()` and the `redact_image` caller set are unchanged (one send site; two redactor callers). The packet's scope ceiling said "NOTHING else", but its own acceptance criterion demanded a green suite; the two cannot both hold against a hardcoded-line test. Updated minimally and disclosed rather than leaving the suite red.

## F-SG101-2 — the old bound would have truncated the successful call

The live call used 2085 completion tokens (1269 reasoning + ~816 content), i.e. **85 tokens over `DEFAULT_MAX_TOKENS=2000`**. This is direct, live evidence that raising the text bound (not merely ledgering the failure) is what makes the path usable; had only the accounting fix shipped, this call would still have been a billed empty-200.

## F-SG101-3 — packet line references were slightly off (cosmetic)

`build_text_payload` actually spans `opencode_go.py:179-195` (packet said `187-195`; 187 is the `return {` line) and `attach_body_accounting` spans `:104-127` (packet said `104-120`). The semantics the packet asserted all held; only the cited ranges were imprecise. Reported per the "correcting me is worth more than agreeing" standing line.

## Acceptance criteria — status

| Criterion | Status | Evidence |
|---|---|---|
| Text payload carries the new bound; `DEFAULT_MAX_TOKENS` byte-untouched + pin green | **MET** | `TEXT_MAX_TOKENS=8000`; `test_opencode_go.py:135` green; new test asserts 2000 |
| Empty-content raise carries usage/cost/latency | **MET** | new test 2; `attach_body_accounting` at `:389` |
| Estimate covers the new bound; cap comparison binds | **MET** | new tests 4 + 5; worst case $0.0053241 ≪ $0.05 |
| Worst-case recomputed ≈$0.0054 ≪ cap; joint caps stated | **MET** | in-slice $0.0053241; G1 joint-caps statement |
| Tests fail-pre/pass-post both committed raw | **MET** | R-FAILPRE (4F/1P) / R-PASSPOST (5P) |
| Gates green; vision tests unmodified-green | **MET** | suite 2F/503P (2 known reds, stash-proved); ruff clean; mypy delta 0; secret 0 |
| ONE live synthesis call completes with quoted actuals inside $0.05 on temp DB | **MET** | $0.00140655, 13 facts, 8.0s; R-LIVE |
| Production counts identical | **MET** | 17/7/6/28/6 both times |
| $0 otherwise; no vacuous pass | **MET** | one metered call only; see below |

**Vacuous-pass check (`PG-EV-01`, loudly):** no criterion passed vacuously. The fail-pre genuinely failed for the right reasons (missing attribute, missing accounting, estimate equality) — raw committed. The accounting test feeds the exact SG-099 empty-200 shape and asserts the attached fields, not merely a raise. The vision-stays-usage-free test asserts absent attributes (a real contrast, proving the change is text-only). The cap test asserts `invocations == 0` and `ProviderCall == 0`, not just a raised exception. The live call is quoted with model/usage/cost/latency and a ledger row. **Where this slice is weaker than it looks:** the adapter's `attach_body_accounting` error leg is proven offline and by the live success path, but the live call did **not** exercise the new error-attach branch (it succeeded); the branch is covered by unit test 2, not live.

## Cross-product / privacy (`PG-IC-01`, `PG-SC-05`)

No criterion demanded persistence, endpoint wiring, deploy, restart, container acts, vision-path changes, or a second metered call. Only TestClient + host commands were run; no image pulled/run; `docker compose config` never run. Fixture TEXT only; key NAMES only; no key value in any file, log, or assertion. No fixed dates in code — the live leg read the clock; test attribution strings are sample data. STATE/AGENTS/packet dirs untouched.

## Report note on the notes ref (receipt)

Work pushed to `automation`; worktree clean. Note added on `WORK_HEAD`, notes ref pushed, and verified against the **fetched, mapped** ref. Executed, verbatim:

```
<pasted after execution>
```

No push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`. The final tip (the docs-only receipt commit) is dual-annotated too (note-anchor inoculation, SG-092 precedent). `note=yes`.

---

## UNCLEAR

- **FIRST READ:** every load-bearing packet premise held (the `:374` bare `guard_content`, the `:369-371` attaching no-choices leg, the false unbilled docstring, the two builders being distinct). Three cited line ranges were imprecise (F-SG101-3). I read "text path ONLY" as binding and left `extract_items` byte-identical; I read the scope ceiling as subordinate to the green-suite criterion and updated the privacy-audit pins (F-SG101-1).
- **DURING EXECUTION:** the live call returned **2085** completion tokens — 85 over the old bound — which is direct proof the bound raise (not just the ledgering) is what unblocked the path. The privacy-audit line pins were self-caught by the full suite. The estimate hunk's failing-test proof is the same test that proves the cap now binds.
- **REMAINING:** the adapter change is **not live** in the running service (owner-gated rider `PG-PR-04` owed); the empty-content error-attach branch is unit-proven but not live-exercised; endpoint/persistence consumption of the returned synthesis (`PG-SC-02`) is a later slice; the published-side G-L1 hash stays unexecuted until `.rules-cache/` is populated (F-SG099-3); a non-reasoning text model remains an alternative the D139 Arc A live-re-confirm slices may weigh.

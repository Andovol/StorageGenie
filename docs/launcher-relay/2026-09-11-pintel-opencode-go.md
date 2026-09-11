# OpenCode GO integration — PIP relay (2026-09-11)

**Purpose:** everything the next session needs to build SG-027's GO adapter. **Provenance:** PIP Architect
reply relayed by owner 2026-09-11 (Pintel `6aa4b18` == `origin/main` as fetched that day); vendor docs
(`opencode.ai/go`, `opencode.ai/docs/go`) read same day. PIP-local design-doc claims marked **[PIP record]**.
**Secrets:** NONE in this file — key names and redacted shapes only, by standing rule.

## What GO is (vendor, verified)

- $10/month subscription, API key via Zen console → `/connect` in TUI. One member per workspace subscribes.
- Direct HTTPS per model: `https://opencode.ai/zen/go/v1/chat/completions` (most),
  `/v1/responses` (Grok, Luna, Muse Spark), `/v1/messages` (MiniMax, Qwen-max).
- Listed vision path: `deepseek-v4-flash-vision-exp` (UNPROVEN — listing, not a call).
- Usage posture: dollar caps per window (PIP: $12/5h, $30/week, $60/month from July docs — STALE, re-check).

## What PIP proved live (relayed with paths, re-verify in-slice before building on them)

- **Shape:** raw `httpx`, NO SDK. `POST {base}/chat/completions`, `stream: false`. Only other call:
  `GET {base}/models` (works WITHOUT session header — measured).
- **Call code:** `pintel/llm.py:262-303` (`_call_opencode_go`); schema downgrade `:306-319`; empty-200
  reject `:62-83`; primary→fallback 60s/call `:507-551`; router strips `opencode-go/` prefix `:349-369`;
  one JSON repair retry `:795-817`. Tests: `tests/test_llm_opencode_router.py`,
  `tests/test_p445_opencode_headers.py`. Smoke: `scripts/opencode_smoke.py`.
- **Identity headers REQUIRED** (`pintel/opencode_headers.py:9-69`): non-library `User-Agent` + ONE stable
  `x-opencode-session` per conversation (`pintel-<run_id>-<agent>`). Missing = HTTP 400 `MissingSessionID`
  for ~3h (2026-09-08, `tokens_in=0`). Never `pintel-*`, never random-per-call, never another project's prefix.
- **Per-model output modes** (`pintel/config.py:156-168`): `json_object` ONLY for `deepseek-v4-flash/_pro`
  (`json_schema` = persistent 400); `json_schema` for mimo-2.5/pro, minimax-m3, glm-5.2, qwen3.7-plus/max.
- **Guards:** reject 200-with-empty-content; require non-zero `usage` (an agent once reported success with
  `tokens_in=0`); strip ONE leading `<think>` (minimax-m3) then fail loudly; size `max_tokens` past
  truncation (256 cut off glm-5.3-flash and read as parse failure).
- **Retry shape:** GO function has NO retry decorator — raises on 429/5xx into primary→fallback + one JSON
  repair. Zen function retries 3× exp 2–10s on 429/5xx. No 429 ever seen on GO; 500/503/403/400 seen.
- **Timeouts:** 180s GO call default; 60s fallback wrapper.
- **Money:** PIP's spend figure is list-price ESTIMATE (`config.py:318-329`, `llm.py:85-101`), not billed
  truth; models missing from the table record $0. PIP daily budgets $1.00 desk / $0.50 others, 1.5×
  degrades to flash, 2× refuses (`budgets.py:24-32`). Spend windows `runs.py:339-386`; catalog
  `models_catalog.py:1581-1625`; pricing `config.py:314-329`.
- **Latency:** 1.4–1.6s measured on ZEN FREE tier only. NO GO latency distribution. Cron contention unmeasured.

## Key (names only)

- Env var `OPENCODE_API_KEY` (Zen pay-per-use and GO share it). Pydantic `.env` at repo root; minted by
  owner 2026-07-09, mode 600, never echoed. No rotation recorded. No `.env.example` entry.
- **Trap that broke production:** `.env` at `600 andrei:andrei` killed every scheduled job running as uid
  10000 (Hermes) with `PermissionError` before any write. Fix: group 10000 + mode 640. If the runtime uid
  ≠ file owner, check this FIRST.
- Shared-vs-per-project subscription: UNRESOLVED (PIP backlog "dual subscriptions" open). Box also holds
  CLI creds at `~/.local/share/opencode/auth.json` — unknown if same subscription.
- **StorageGenie decision (Q1/Q2 2026-09-11): SEPARATE subscription; owner places the key in the host
  backend `.env` (600, runtime-group readable) at arc start, never pasted in chat.**

## What PIP never did (our gaps to close ourselves)

- **Vision: NONE.** No `image_url`/`input_image`/`vision` in any request builder; vision-exp id nowhere in
  code or pricing. `mimo-v2-omni` failed a TEXT smoke with 400 "unsupported" (inference only: omni ≈ images).
  Anthropic-compatible base `https://opencode.ai/zen/go` exists but was never called.
- Cross-provider fallback unbuilt (both arms were `opencode-go/`, died together).

## Sharing posture (binding on us)

- Never read/copy PIP's `.env` or key — own key via owner only. Own UA + own session prefix. Caps belong
  to the subscription — IF shared, our pipeline and PIP's 06:30Z desk draw one pool (we are separate per
  Q1, so this is a caution, not a constraint).

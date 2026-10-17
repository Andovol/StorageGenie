# SG-213 — D-18(b): retry `google/gemini-3.1-flash-image` via OpenRouter direct (quota re-check + minimal billed renders, $2.00 worst-case cap)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: disposable test datastore ONLY for call-ledger rows (committed TSV transcript); zero production DB writes — any production write is a STOP.** **Restart: none.**
**Autonomy: L3** (approved queue — runs after SG-212; checkpoints only on `G-K2`/assumption-change/stage end). Authority: owner D-18(b) ("lets try it again") + D-20 ($2.00/day total cap covers this probe). One retry max, root-cause only.

Authoring date (metadata, never a gate): 2026-10-17.

## Why this exists

SG-159 (2026-10-12) blocked this slug twice: Image API → HTTP 429 upstream quota (unbilled), server-tool chat → 200 without artifact. The owner directs a retry — the quota wall may or may not still hold. This probe measures which, then (only if the wall is down) proves the artifact path including the `input_references` leg that cutout/scene depend on.

## Handed-over facts (expected — re-verify at execution, `PB-1`)

- Slug `google/gemini-3.1-flash-image` (Nano Banana 2): SG-209's free controls (2026-10-17) list 3 endpoints with `input_references` 0..14 and token pricing ~6e-05 (Google Vertex / Google AI Studio providers). Re-measure live — catalogue records move.
- SG-159 evidence (the wall being rechecked): two Image-API 429s (`cost=null`, bodies persisted, second after ~100 s backoff) + one chat 200 text-only ($0.000875925). Arc spend then $0.002437125.
- Docs surface (read 2026-10-17, OpenRouter current): `POST /api/v1/images` body `{model, prompt, ...}`; buffered result `data[0].b64_json` + `media_type`; cost `usage.cost`; all-or-nothing billing. Key via the lane's approved tooling ONLY; key/`Bearer` bytes must NEVER reach a log, artifact, or the repo — grep-gate the evidence before commit (SG-209 pattern: word-split gate, exit 1 EMPTY).

## G1 — discovery + quota re-check (free reads first, then ONE minimal billed text-to-image)

- `GET /api/v1/images/models` → confirm slug listed; fetch its endpoints record; commit both bodies; report `supported_parameters` (esp. `input_references`), `pricing[]`, providers. STOP rule: slug absent or endpoints empty → STOP, render legs do not run, cap unspent (PG-SC-03 success).
- Quota re-check: ONE minimal billed text-to-image render (cheapest settings per the endpoint record, `n: 1`, fixed neutral prompt, no customer data). Commit request shape (key redacted) + full response body. 200 + image bytes → wall is DOWN, proceed to G2. 429/quota (quote the body) or 200-without-artifact → STOP with bodies committed; the retry wall stands, reported not fixed. Either outcome is a complete probe.
- Spend guard (fail-closed, computed BEFORE any billed call): worst case from the pricing lines (per-token/image at chosen settings × planned renders) + known spend ≤ **$2.00** AND inside the $2.00/day D-20 cap; else STOP. Actual `usage.cost` vs projection in the report; ledger TSV committed (timestamp, leg, model, HTTP, cost/null-cost, error).

## G2 — reference-path render (only if G1 returns image bytes)

- ONE `input_references` render using a FIXTURE image (committed 256×256 neutral PNG or the SG-209 fixture by copy — never a real asset photo), minimal settings. Proves the cutout/scene precondition end to end. Any failure shape (4xx/5xx/artifact-less 200) STOPS with bodies committed.
- Decode `b64_json` to a committed image; open + disposition it (UI/data: neutral subject, no PII by construction).

## Constraints

- **Money:** ≤$2.00 worst-case projection before any billed call (== the D-20 daily bound; this slice spends only what the guard clears); actual vs projection in the report; monthly cap still undeclared (stated, not needed here).
- **Scope ceiling:** evidence ONLY `docs/worklogs/SG-213_*` (+ fixture if created, same root). Zero product/config/test bytes. Ledger to disposable SQLite + committed TSV; **zero production DB writes** (`PG-EV-06`); no restart; no secret in any artifact (word-split grep-gate, exit 1 required); reads: lane + `openrouter.ai` API only; exactly the planned POSTs, zero otherwise.
- `PG-EV-07`: the reference render uses a real `input_references` data-URL payload, never a mocked leg. `PG-EV-09`: discovery bodies + render bodies + ALL run transcripts committed raw, never prose-only. `PB-2` denial STOPS the whole slice (incl. any key/permission refusal — disclose verbatim, do not route around).
- Hang bounds: reads 120 s; billed calls 600 s each (max 2); idle kill never approached. Expected duration ≈600 s (Architect record, `G-A9` uncalibrated; SG-209's 476 s same shape + one render leg).
- Simplicity: discovery + ≤2 billed renders + ledger; no new machinery. Excluded (stated): cutout/scene implementation (needs this probe green + monthly-cap word if spend recurs); chat-path re-proof beyond the Image-API legs (SG-159 stands unless the Image API forces a revisit); muse (refuted, stays parked).

## Acceptance criteria

- **A1:** discovery bodies committed; slug/endpoints/`input_references`/pricing verdicts with exact JSON paths; quota verdict (200+bytes vs quoted 429/artifact-less) with the body.
- **A2:** 0–2 billed renders per the STOP rules; artifact(s) committed + opened + dispositioned, or quoted error bodies; spend actual vs $2.00 projection; ledger TSV committed; secret-grep empty (command + output committed).
- **A3:** report `docs/worklogs/SG-213_report.md`; elapsed vs ≈600 s; constraints answered on explicit lines; FIRST/DURING/REMAINING; FIRST token `SG-213`.
- **A4:** notes-ref receipt, first line `Dispatch-ID: SG-213 | Report: docs/worklogs/SG-213_report.md`, Work-HEAD recorded, pushed + read back. Never the retired finalizer.

Guards invoked: PG-EV-02/03/05/06/07/09; PG-SC-03/05/09; PG-IC-01/07/08/09; PG-PR-01/03. Stop follows `PB-6`.

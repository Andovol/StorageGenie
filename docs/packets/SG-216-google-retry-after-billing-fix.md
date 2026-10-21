# SG-216 — D-23: retry `google/gemini-3.1-flash-image` after owner billing fix (quota re-check + minimal billed renders, $2/day + $10/mo fail-closed)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: disposable test datastore ONLY for call-ledger rows (committed TSV transcript); zero production DB writes — any production write is a STOP.** **Restart: none.**
**Autonomy: L2** (project default; one retry, root-cause only). Authority: owner D-23 test word 2026-10-21 ("billing is fixed ... do a test") + D-20 ($2.00/day) + D-14 ($10.00/month).

Authoring date (metadata, never a gate): 2026-10-21.

## Why this exists

SG-213 (2026-10-17) re-measured the slug listed with 3 endpoints + `input_references` 0..14 + pricing ~6e-05, then ONE minimal billed POST → HTTP 402 `prepayment credits are depleted` (Google AI Studio surface `https://ai.studio/projects`, cost null, unbilled) → STOP executed, G2 unrun, $0 spent. Owner now reports billing fixed. This probe measures whether the wall is down, then (only if down) proves the artifact + `input_references` legs end to end.

## Handed-over facts (expected — re-verify at execution, `PB-1`)

- Slug `google/gemini-3.1-flash-image`: SG-213 live discovery (bodies `SG-213_g1_models_body.json` 47,720 B + `SG-213_g1_endpoints_body.json`): 3 endpoints (google-vertex/us 6.6e-05/token, google-ai-studio 6e-05, google-vertex/global 6e-05), `input_references` 0..14 on all three, resolution enum 512/1K/2K/4K. Re-measure live — catalogue records move.
- SG-213 wall body (the shape being rechecked): 402 + `prepayment credits are depleted` + billing surface, committed in `SG-213_g1_render_body.json`; ledger `SG-213_ledger.tsv` 3 rows all cost null; arc known spend $0.002437125 then. Re-derive spend live — never inherit a total.
- Docs surface (read 2026-10-17, OpenRouter current; re-read if the driver disagrees): `POST /api/v1/images` body `{model, prompt, ...}`; buffered result `data[0].b64_json` + `media_type`; cost `usage.cost`; all-or-nothing billing. Key via the lane's approved tooling ONLY; key/`Bearer` bytes must NEVER reach a log, artifact, or the repo — grep-gate the evidence before commit (SG-209/SG-213 pattern: word-split gate, exit 1 EMPTY).

## G1 — discovery + quota re-check (free reads first, then ONE minimal billed text-to-image)

- `GET /api/v1/images/models` → confirm slug listed; fetch its endpoints record; commit both bodies; report `supported_parameters` (esp. `input_references`) + `pricing[]` with exact JSON paths. STOP rule: slug absent or endpoints empty → STOP, render legs do not run, caps unspent (`PG-SC-03` success — stopping is a success).
- Quota re-check: ONE minimal billed text-to-image render (cheapest settings per the live endpoints record, `n: 1`, fixed neutral prompt, no customer data). Commit request shape (key redacted) + full response body. 200 + image bytes → wall is DOWN, proceed to G2. 402/429/quota (quote the body) or 200-without-artifact → STOP with bodies committed; the wall stands, reported not fixed. Either outcome is a complete probe.
- Spend guard (fail-closed, computed BEFORE any billed call): worst case from the live pricing lines (per-token/image at chosen settings × planned renders) + known spend (re-read live: arc total + October month total) ≤ **$2.00** (D-20 daily) AND ≤ **$10.00** (D-14 monthly); breach on EITHER cap → STOP before any POST. Actual `usage.cost` vs projection in the report; ledger TSV committed (timestamp, leg, model, HTTP, cost/cost-null, error). Persist each leg's result as it returns; the dry/analysis pass runs the same parsing code (`PG-EV-14` pattern).

## G2 — reference-path render (only if G1 returns image bytes)

- ONE `input_references` render using a FIXTURE image (committed 256×256 neutral PNG — copy the SG-213 fixture by bytes, never a real asset photo), minimal settings. Proves the cutout/scene precondition end to end. Any failure shape (4xx/5xx/artifact-less 200) STOPS with bodies committed.
- Decode `b64_json` to a committed image; open + disposition it (neutral subject, no PII by construction).

## Constraints

- **Money:** both caps bind fail-closed before any billed call (daily $2.00, monthly $10.00); actual vs projection in the report; unbilled 402/429 spends $0 against neither cap (stated).
- **Scope ceiling:** evidence ONLY `docs/worklogs/SG-216_*` (+ fixture copy, same root). Zero product/config/test bytes. Ledger to disposable SQLite + committed TSV; **zero production DB writes** (`PG-EV-06`); no restart; no secret in any artifact (word-split grep-gate, exit 1 required); reads: lane + `openrouter.ai` API only; exactly the planned POSTs (≤2), zero otherwise.
- `PG-EV-07`: the reference render uses a real `input_references` data-URL payload, never a mocked leg. `PG-EV-09`: discovery bodies + render bodies + ALL run transcripts committed raw, never prose-only. `PB-2` denial STOPS the whole slice (incl. any key/permission refusal — disclose verbatim, do not route around).
- Hang bounds: reads 120 s; billed calls 600 s each (max 2); idle kill never approached. Expected duration ≈600 s (Architect record, `G-A9` uncalibrated; SG-213 same shape took 255 s + one render leg if green).
- Simplicity: discovery + ≤2 billed renders + ledger; no new machinery. Excluded (stated): cutout/scene implementation (needs this probe green + recurring-spend word if spend recurs); chat-path re-proof unless the Image API forces a revisit; muse (refuted, stays parked).

## Acceptance criteria

- **A1:** discovery bodies committed; slug/endpoints/`input_references`/pricing verdicts with exact JSON paths; quota verdict (200+bytes vs quoted 402/429/artifact-less) with the body.
- **A2:** 0–2 billed renders per the STOP rules; artifact(s) committed + opened + dispositioned, or quoted error bodies; spend actual vs pre-send projection against BOTH caps; ledger TSV committed; secret-grep empty (command + output committed).
- **A3:** report `docs/worklogs/SG-216_report.md`; elapsed vs ≈600 s; constraints answered on explicit lines; FIRST/DURING/REMAINING; FIRST token `SG-216`.
- **A4:** notes-ref receipt: FIRST line exactly `Dispatch-ID: SG-216 | Report: docs/worklogs/SG-216_report.md` + `Work-HEAD` recorded, pushed + read back. Never the retired finalizer. Exact commands (run after the report commit, on the work HEAD):
  - `git log --format=%H -n 1 HEAD`
  - `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-216 | Report: docs/worklogs/SG-216_report.md" <work-head>`
  - `git push origin refs/notes/storagegenie-coder-reports`
  - `git push origin automation`
  - Read back on the remote (mapped fetch of the notes ref) and commit the verbatim transcript as `docs/worklogs/SG-216_receipt.log`.

Guards invoked: PG-EV-02/03/05/06/07/09/14; PG-SC-03/05/09; PG-IC-01/07/08/09; PG-PR-01/03. Stop follows `PB-6`.

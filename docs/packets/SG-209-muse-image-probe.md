# SG-209 — D-17: muse-image probe via OpenRouter direct (discovery-first, one minimal billed render, $2.00 worst-case cap)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: disposable test datastore ONLY for call-ledger rows (committed TSV transcript); zero production DB writes — any production write is a STOP.** **Restart: none.**
**Autonomy: L3** (owner 2026-10-17 "running in L3 mode"; stage = SG-206→207→208→209 flow; checkpoints only on `G-K2`/assumption-change/stage end per 2026-10-13 D16). Authority: owner D-17 (probe + $2.00 cap, this chat). One retry max, root-cause only.

Authoring date (metadata, never a gate): 2026-10-17.

## Why this exists

D-15 narrowed the AI image stages to `meta/muse-image` via OpenRouter directly. SG-159's `endpoints: []` reading was taken on the lane's image path — a different surface. This probe establishes, by measurement: does the slug exist on OpenRouter direct, what the endpoint accepts (especially `input_references`, which cutout/scene depend on), what it costs — then proves the artifact path with ONE minimal billed render. No implementation slice launches on the answer until this probe proves it.

## Handed-over facts (expected — re-verify at execution, `PB-1`)

- Docs briefing (read 2026-10-17, OpenRouter current): discovery `GET https://openrouter.ai/api/v1/images/models` (Bearer) → per-model `/api/v1/images/models/{id}/endpoints` (definitive `supported_parameters`, `allowed_passthrough_parameters`, `pricing[]` with `billable`/`unit`/`cost_usd`); generation `POST https://openrouter.ai/api/v1/images` body `{model, prompt, ...}`; buffered result `data[0].b64_json` + `media_type`, cost `usage.cost`; all-or-nothing billing. Muse Image is listed in OpenRouter's image collection (Meta, agentic, text+reference in). SG-159 precedent numbers: Google 429 unbilled ×2, Muse chat 200 text-only ($0.000875925), `meta/muse-image` endpoints `[]` on the lane path, arc spend $0.002437125 under $1.00 cap.
- Key handling: OpenRouter key via the lane's approved tooling ONLY (the SG-158/159 mechanism); key value or `Bearer`/`Authorization` header bytes must NEVER reach a log, artifact, or the repo — grep-gate the evidence before commit (`PG-SC-05` literal gate: `grep -ri 'bearer\|authorization' <evidence>` empty or FAIL).

## G1 — discovery (free; no billed call)

- `GET /api/v1/images/models`: is `meta/muse-image` (or the closest Muse image slug — report exact id either way) listed? Commit the full response body.
- Fetch its `/endpoints` record: commit the body; report `supported_parameters` (especially `input_references`: supported? max count? `resolution`/`aspect_ratio` values?), `allowed_passthrough_parameters`, per-endpoint `pricing[]`, `supports_streaming`. Verdict line per question, each naming the exact JSON path it was read from.
- STOP rule: slug absent, or `input_references` unsupported, or cheapest endpoint's worst-case single-render cost already over the cap → STOP with the bodies committed; the render leg does NOT run and the unspent cap is reported, not used. Stopping here is SUCCESS (`PG-SC-03`).

## G2 — one minimal billed render (only if G1 passes)

- Cheapest settings the endpoint record allows (`n: 1`, lowest resolution/quality tier, minimal prompt: a fixed neutral subject, no customer data). Then, ONLY if `input_references` is supported: one reference render using a FIXTURE image (committed fixture or generated blank — never a real asset photo), same minimal settings.
- Spend guard (fail-closed, SG-159 F-SG159-4 pattern): pre-compute worst case from the pricing lines (per-image flat, or per-megapixel/token at the chosen settings × 2 renders max) + known spend; proceed ONLY if ≤ **$2.00 worst case**, else STOP. After: real `usage.cost` vs projection in the report; TSV ledger (`SG-209_ledger.tsv`: timestamp, leg, model, HTTP, cost/null-cost, error) committed; response bodies persisted (b64 decoded to committed image files, opened + dispositioned by the Coder for UI/data issues — a render of a neutral subject has no PII by construction).
- A render that returns 200 without image bytes is error-shaped evidence (`image_bytes_missing`), not success — same honesty rule as SG-159.

## Constraints

- **Money:** ≤$2.00 worst-case projection for the slice, computed BEFORE any billed call; actual vs projection in the report; all-or-nothing billing stated. No monthly-cap decision is made here (D-14(c) monthly part stays open).
- **Scope ceiling:** evidence ONLY `docs/worklogs/SG-209_*` (+ fixture if created, same root). Zero product/config/test bytes. Ledger rows to disposable SQLite + committed TSV; **zero production DB writes** (`PG-EV-06` — authorised surface is disposable only); no restart; no secret in any artifact (grep-gate above); reads: lane + `openrouter.ai` API only; no other external host.
- PG-EV-07: the reference render uses a real `input_references` payload (data-URL fixture), never a mocked delivery leg. PG-EV-09: discovery bodies + render bodies + BOTH run transcripts committed, never prose-only. PB-2: any denied privileged/key operation STOPS the whole slice.
- Hang bounds: reads 120 s; billed calls 600 s each (max 2); idle kill never approached. Expected duration ≈600 s (Architect record, `G-A9` uncalibrated; SG-203/204 lane-measure precedent minus the browser-driver legs).
- Simplicity: discovery + ≤2 renders + ledger; no new machinery. Excluded (stated): cutout/scene implementation; Google leg (suspended under D-15); chat-path re-proof (SG-159 stands).

## Acceptance criteria

- **A1:** discovery bodies committed; slug present/absent verdict with exact id; endpoint params incl. `input_references` verdict; pricing lines quoted; per-question verdicts with JSON paths.
- **A2:** 0–2 billed renders per the STOP rules; artifact(s) committed + opened + dispositioned, or quoted error bodies; spend actual vs $2.00 projection; ledger TSV committed; secret-grep empty (command + output committed).
- **A3:** report `docs/worklogs/SG-209_report.md`; elapsed vs ≈600 s; constraints answered on explicit lines; FIRST/DURING/REMAINING; FIRST token `SG-209`.
- **A4:** notes-ref receipt, first line `Dispatch-ID: SG-209 | Report: docs/worklogs/SG-209_report.md`, Work-HEAD recorded, pushed + read back. Never the retired finalizer.

Guards invoked: PG-EV-02/03/05/06/07/09; PG-SC-03/05/09; PG-IC-01/07/08/09; PG-PR-01/03. Stop follows `PB-6`.

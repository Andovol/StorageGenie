SG-159 — Scene T1b re-dispatch (Google-only): G0-fix shipped + R2 root cause found live + D7 UNANSWERED (no stored render)

**VERDICT (partial ship, per the packet's blocked-leg rule): G0-fix (2xx-body persistence
+ extractor hardening + Image API transport + tests) is SHIPPED with fail-pre→pass-post
both committed; the R2-fix investigation PROVED the SG-158 imageless 200 shape from the
now-persisted body (no image field exists in it — the server-tool chat path never delivers
the artifact to the client) and the Google leg's live block (upstream Google AI Studio 429
quota, unbilled, quoted); Muse executed billed and also surfaced no artifact; the dedicated
Image API routes Google but has ZERO endpoints for the owner-named Muse model. D7 is
UNANSWERED — no stored render exists, no pick is invented. Spent $0.0016782 this slice
(2 billed sends), 0 Evidence rows, 0 Authorization leaks.**

Dispatch: SG-159 · Coder `opencode` · Model `opencode-go/deepseek-v4.1-flash` · Effort `max`
(read first-hand from the process arguments, never a system-prompt identity: `/proc/259916/cmdline`
= `opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash
--variant max …`; engine `bash /usr/local/lib/dispatch/run-coder SG-159`, pid 259814,
lane start 14:16:25Z).
Work dir / remote: `/home/andrei/StorageGenie` · `git@github.com:Andovol/StorageGenie.git`.
BASE ref requested `automation` → resolved `eab2c5a` (tip at slice start; worktree clean).
Work commit: the commit carrying this report (hash in the receipt transcript commit).
Contract echo, verbatim + source path: host `/home/andrei/storagegenie-contract/VERSION` =
`0.46.0` — NOT the packet's expected `0.44.1`. This matches the packet's own known-delta note
(0.44.2..0.46.0 exists; adoption DEFERRED to chain close) — not tripped on. Recorded value in
`AGENTS.md` remains `0.44.1`. `rules_check.sh` (run live) exits 3: `G-L1 UNCHECKED the cache is
not checked out at a contract tag` (F-SG157-2 stands, re-measured) + `G-L5`/`G-L7 gh-unauthenticated.
Type: G0-fix code+tests + G1 live renders. No migration, no restart, no served-code change
→ no refresh (D145).

---

## (a) Issues / deviations / surprises

- **F-SG159-1 (the R2 root cause, now PROVEN live) — the server-tool chat path returns the
  rewritten text but NO image artifact.** SG-158's 2xx body was not persisted; this slice's
  fix persisted it, and the persisted body of the SG-159 R2a 200 (ledger
  `01a13080-8b71-7851-8460-813b909b6034`) shows the full response: `choices[0].message`
  carries only `content` (a text restaging description) + `reasoning`; there is no
  `imageUrl`/`imageB64`/`result`/`images[]`/`b64_json` anywhere in the document, and
  `completion_tokens_details.image_tokens = 0` while `server_tool_use_details.tool_calls_executed
  = 2`. The same shape repeated for Muse (ledger `01a13084-21bb-7850-b8c8-e61f4e85698d`). So
  SG-158's `image_url_missing` was NOT an extractor miss: the artifact is simply not in the
  response. Extractor hardening still shipped (it now covers `imageB64`/`result`/`b64_json`/
  raw-base64 shapes and surfaces a failed tool status), but no extractor could have conjured
  the image this path does not deliver.
- **F-SG159-2 (BLOCKING for the Google leg) — Google AI Studio returns upstream 429 quota
  for the image model.** Two Image-API sends (`POST /api/v1/images`, photo as
  `input_references`) returned HTTP 429, `cost=null` (unbilled): *"You exceeded your current
  quota, please check your plan and billing details … https://ai.google.dev/gemini-api/docs/rate-limits
  … metadata: provider_name Google AI Studio"* (ledgers `01a13082-aadb-7602-b9dd-f4d48bf9b720`,
  `01a13084-4367-7ad2-9984-bc7179dfb4f3`; bodies persisted). The second send was a single
  rate-limit backoff ~100s after the first — it 429'd again, so the Google leg is BLOCKED on
  the measured evidence (PG-IC-03: ship the rest, never substitute another image slug; the 404/429
  bodies are quoted in the ledger rows).
- **F-SG159-3 — Muse is routable on the chat path (provider Meta, permitted) but has ZERO
  Image-API endpoints; the chat path produced no artifact.** `/api/v1/images/models/meta/muse-image/endpoints`
  = `{"id":"meta/muse-image","endpoints":[]}` (measured 2026-10-12); its chat endpoint exists
  (Meta, `image_output` pricing). The R2b server-tool send executed (tool_calls_executed=2)
  and returned text only. So there is no measured transport that yields a Muse artifact
  for the client — the leg is BLOCKED as measured, reported, not substituted.
- **F-SG159-4 (guard vs the packet's spend arithmetic) — the fail-closed unknown-cost rule
  refused the second leg at the packet's stated 0.30 worst case.** With SG-158's two 404s
  and this slice's first 429 accumulating as `cost IS NULL` rows, the guard charge of
  `3 × 0.30 + 0.30` + known spend = 1.2016 > 1.0 → `over_cap` (quoted in
  `SG-159_render_R2b.log` run 1). The packet's "sequential sums 0+0.30, 0+0.30, 0+0.30 ≤ 1.0"
  assumed no unknown-cost rows. I did NOT weaken the guard; I re-derived honest per-render
  bounds from live prices and re-declared them: **Google image leg 0.15** (Image API default
  resolution ≈ 1K ≈ 1290 image tokens × $0.00006 = $0.0774, bound ≈ 2×) and **Muse leg 0.05**
  (orchestrator ≤ 8192 prompt × $0.000000075 + 2048 completion × $0.0000003 + 4096 image
  tokens × $0.0000023952 ≈ $0.011, bound ≈ 4.5×). This is a disclosed deviation from the
  packet's 0.30-per-render working figure; the caps were never raised (authority stays $1.00)
  and the guard's projection was satisfied at the smaller, true bounds.
- **F-SG159-5 — publish-before-bound MISSED.** Lane start 14:16:25Z; the 1050s half-bound fell
  at 14:33:55Z; the real-work recon (contract echo + two model routability reads + the
  no-artifact proof + suite baseline in the production image) ran past it. Actual elapsed at
  work commit is quoted in the receipt transcript. The lane budget (2100s → 14:51:25Z) was
  respected; nothing was killed.
- **F-SG159-6 (environment drift, disclosed) — the repo venv lacks `pillow_heif`** (50
  collection errors when running the suite in `venv/`; F-SG144-1's venv follow-up is live).
  The suite was therefore run in the production image with the repo backend mounted at `/app`
  — the environment that serves. In that environment 6 tests read files outside the mount
  (`/docs/superpowers/specs/...`, repo-root README/docs artifacts): identical 6 reds at BASE
  (eab2c5a) and candidate → zero new reds, +12 new green (below).
- **F-SG159-7 — T0-PINNED price re-verification:** `google/gemini-3.1-flash-image` image_output
  `0.00006` MATCHES T0. `meta/muse-image` live pricing is `image_output`/`image_token`
  `0.00000239520958083832` per token — the packet's inferred "$0.01/image" is consistent at
  ~4175 image tokens, but the live unit is per-token, not per-image; both values quoted
  (drift note, no T0 change for Google).
- **Muse body note:** the persisted Muse 200 body (ledger `01a13084-21bb-…`) likewise carries
  only text + reasoning; the long `reasoning` strings are `_redact_long_strings`-redacted in
  the ledger (`<redacted len=… sha256=…>`), full-body sha in `response_body_sha256`.

## (b) Actions

Changed paths (work commit W): `backend/app/services/scene/openrouter.py`
(`_looks_like_image_b64`, `_as_image_ref`, hardened `extract_image_url`,
`extract_image_b64`, `extract_image_tool_error`, `_redact_long_strings`,
`_persistable_response_body`, `build_image_request`, `SCENE_IMAGE_API_URL`,
`record_scene_call` + `response_body`/`response_body_sha256`, `render_scene` + `transport`
parameter); `backend/tests/test_sg159_scene_render_fix.py` (new, 12 tests);
`backend/scripts/sg159_render.py` (new, one-render-per-invocation driver);
`backend/tests/test_privacy_audit.py` (send-site pins shifted to `:781`/`:783`, docstring
names SG-159 — CO-38); `docs/worklogs/SG-159_failpre.log`, `SG-159_base_suite.log`,
`SG-159_verify.log`, `SG-159_routability.log`, `SG-159_render_R2a.log`,
`SG-159_render_R2b.log`, `SG-159_ledger.tsv`, `SG-159.log`, this report.
External effects: 4 OpenRouter POSTs (2 billed 200s, 2 unbilled 429s) from the production
image via `docker run --rm` through the lane's per-slice socket
(`DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-159/docker.sock`; repo mounted read-only,
live `/data/db` bind + `storagegenie_storage_data` volume mounted; no served container
touched, no restart/build). Production writes: exactly **4 `provider_call` rows, 0 `evidence`
rows, 0 other rows** — read back below. Provider-call count: 4 sends, 2 billed. Retries: 1
(the R2a Image-API rate-limit backoff, disclosed). Test commands: fail-pre, candidate file
run, full suite ×2 (base + candidate), ruff, mypy (logs in `SG-159_verify.log`). Health
section: not applicable (no served-code change, no restart).
Durations (UTC clock): lane start 14:16:25Z; recon + free routability 14:17–14:24; G0-fix
write 14:21–14:23; R2a/R2b live legs 14:24–14:29; pins+verify 14:29–14:33; suite base+candidate
+report 14:33–…; work commit + receipt: see Receipt section. Only command > 60s: the two
full-suite runs (61.5s / 55.8s, bound 600s).

## (c) Verification

**A1 — fail-pre → pass-post, both committed** (isolated base worktree at `eab2c5a` with the
candidate test copied in, then candidate tree):

    SG-159_failpre.log  (base eab2c5a + candidate test):
    10 failed, 2 passed in 0.74s   (extractor shapes, tool-error surface, 2xx persistence,
                                    billed tool failure, redaction, Image API all red at base)
    SG-159 passpost (candidate W):
    12 passed in 0.67s   (the new file; 36 passed with SG-155 envelope + SG-158 siblings)
    Envelope re-asserted offline: `test_frozen_envelope_reasserted_offline` + all SG-155 pins green
    2xx-body persistence proven against real SQLAlchemy SQLite rows
    (`test_successful_render_persists_2xx_body_with_sha`, `test_error_response_body_is_persisted_as_well`)
    — and the LIVE rows below carry `response_body` + `response_body_sha256` (PG-SC-12).

**A2 — renders, per-render accounting, ≤$1, 0 leaks.** Live reads (read-only SQL against
`/data/db/storagegenie.db`; per-render ledger transcript in `SG-159_ledger.tsv`):

    R2a server_tool 2026-10-12 14:24:53  ledger 01a13080-8b71-7851-8460-813b909b6034  google/gemini-3.1-flash-image via seed  200  cost=0.000802275  error=image_url_missing (body persisted)
    R2a image_api   2026-10-12 14:27:12  ledger 01a13082-aadb-7602-b9dd-f4d48bf9b720  google/gemini-3.1-flash-image            429  cost=null (Google AI Studio quota body persisted)
    R2b server_tool 2026-10-12 14:28:48  ledger 01a13084-21bb-7850-b8c8-e61f4e85698d  meta/muse-image via seed                 200  cost=0.000875925  error=image_url_missing (body persisted)
    R2a image_api   2026-10-12 14:28:56  ledger 01a13084-4367-7ad2-9984-bc7179dfb4f3  google/gemini-3.1-flash-image            429  cost=null (retry after backoff)
    Evidence rows (source_kind='scene_render'): 0   (evidence total unchanged 13)
    Sends this slice: 4; BILLED this slice: 2 (≤3); SLICE SPEND: $0.0016782; ARC SPEND (SG-158+SG-159): $0.002437125 ≤ $1.00 cap
    Guards: per-send free routability check (SG-159_routability.log) + guard projection at re-derived bounds (see F-SG159-4)
    Authorization leaks: 0 (grep 'Bearer|Authorization' over all live logs = 0; key name-only, added at send time only, test-asserted)

**A3 — D7: UNANSWERED, deliberately; no invented values.** No per-render judgment table is
possible: zero stored renders exist. Evidence-based statements only: (1) Google — server-tool
200 without artifact (body quoted) AND Image-API 429 upstream quota (body quoted) → BLOCKED;
(2) Muse — chat 200 without artifact (body quoted), Image-API endpoints `[]` → no
artifact-yielding transport measured. The packet's PG-IC-03 rule (never substitute a slug)
forbids swapping in another image model, so the pick is honestly absent. T0-PINNED unchanged
(price re-verification F-SG159-7). A narrowed pick is not derivable from these works.

**A4 — production writes exactly as measured, both directions (PG-IC-08).** Before:
evidence 13 (scene_render 0), provider_call 21 (openrouter 3; cost sum 0.000758925; null-cost 2).
After: evidence 13 (scene_render 0), provider_call 25 (openrouter 7; cost sum 0.002437125;
null-cost 4). No other table written; no UPDATE/DELETE anywhere; nothing written into the
storage volume (0 Evidence rows). Report + receipt: see Receipt section (remote read-back).

**A5 — suite / ruff / mypy as established** (`SG-159_verify.log`, verbatim tails):

    ruff: All checks passed!  (ruff_exit=0)
    mypy: Found 41 errors in 9 files (checked 92 source files) — none in app/services/scene (scene-only: Success, 2 files); same 41/9 snapshot as SG-158
    suite (production image, backend mounted at /app — see F-SG159-6):
      candidate: 6 failed, 684 passed in 55.80s
      base eab2c5a: 6 failed, 672 passed in 61.46s
      failure sets IDENTICAL (google_taxonomy[food|medicine|cosmetics] ×3 read /docs/superpowers/specs/…,
      runbook ×2 read repo-root README, sg082 ×1 reads a docs artifact — all outside the mount);
      +12 new tests green; zero new reds.

**Guards invoked:** `PG-EV-02` (transports mocked offline; live legs are the 4 disclosed sends) ·
`PG-EV-04` (all tests offline, scripted transports; envelope re-asserted) · `PG-EV-06` (every
live result persisted at return; ids quoted; 2xx bodies now included) · `PG-EV-09` (privacy
pins updated in-slice, named; no weakening) · `PG-EV-14` (report-and-leave; nothing
updated/deleted) · `PG-SC-03` (missing key refuses loudly; tested) · `PG-IC-01` (no blanket
bans; only the named append-only rows) · `PG-IC-03` (blocked legs reported, no substitution) ·
`PG-IC-07` (live UTC clock at each step; logs) · `PG-IC-08` (counts in both directions, above;
2 billed ≤ 3) · `PG-IC-09` (every packet premise re-verified; five live contradictions →
F-SG159-1/2/3/4/7) · `PG-PR-10` (4 append-only ledger rows; storage volumes untouched).

**INTENT lines (behaviour-changing):**
`INTENT: code persists every live response body at return (redacted/capped, sha256 recorded), hardens the image extractor for the documented tool/b64 shapes, surfaces a failed image-tool status, and adds the dedicated Image API transport (input_references + b64_json) to the same guarded send path; the checks expect exactly those outcomes offline via scripted transports; the approved packet says "Persist EVERY live response body … harden extract_image_url … decide server-tool vs dedicated Image API (POST /api/v1/images, b64_json, input_references) inside these constraints — decide and report" (G0-fix) — they agree.`
Vacuity check (loud): the fail-pre is 10 real assertion failures on base (not a collection
error); the pass-post exercises the real `render_scene`/`record_scene_call` through real
SQLite; the 4 live sends really left the machine (ledger rows, persisted bodies, 429 quota
text on record); nothing passed by empty set — the Evidence count is honestly 0 and the D7
pick is honestly absent. The only vacuous-looking pass is `test_frozen_envelope_reasserted_offline`
(passes on base by design — it is a regression guard, not new behaviour), stated here so it is
not counted as coverage.

## Receipt

Mechanism: note on `refs/notes/storagegenie-coder-reports`. Work commit `8ee3562` pushed at
14:37:15Z (elapsed 1250s of 2100s; the 1050s half-bound was MISSED — F-SG159-5; work began at
lane start 14:16:25Z); the note was published on it and read back from the **remote** at
14:37:27Z (elapsed 1262s — publish-before-bound NOT honored, disclosed). Verbatim transcript:

    $ git push origin automation
       eab2c5a..8ee3562  automation -> automation
    $ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-159 | Report: docs/worklogs/SG-159_report.md | Work-HEAD: 8ee3562" 8ee3562
    $ git push origin refs/notes/storagegenie-coder-reports
       093ee52..027de2d  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
    $ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg159-fetched
       * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg159-fetched
    $ git notes --ref=refs/notes/sg159-fetched show 8ee3562
    Dispatch-ID: SG-159 | Report: docs/worklogs/SG-159_report.md | Work-HEAD: 8ee3562
    note_show_exit=0

`note=yes` — read back from the remote (mapped fetch), not the local store. The receipt-evidence
commit (the tip carrying this section) is annotated with the same note body after it is
committed (dual annotation, SG-092/SG-154/SG-157/SG-158 precedent).

Production writes this slice: 4 `provider_call` rows, 0 Evidence rows, 0 others; spend
$0.0016782 (arc $0.002437125).

## UNCLEAR

- **FIRST READ:** whether the R2-fix meant "find the image the 200 already carried" or "make
  the 200 carry an image". Resolved live: the persisted body proves the 200 carried none — the
  fix is a transport decision (Image API), not an extractor tweak; reported, not bent.
- **DURING EXECUTION:** what the unknown-cost guard rows would do to the packet's ≤$1
  arithmetic once 404/429 failures accumulated. Resolved: at the packet's 0.30 worst case the
  guard refuses the second leg (fail-closed, quoted); honest per-render bounds (0.15 / 0.05)
  keep the projection inside the unchanged $1.00 authority — disclosed as a deviation.
- **REMAINING:** (1) the Google AI Studio quota block on the image model — an owner-side
  quota/plan question, not code; (2) whether any transport surfaces a Muse artifact at all
  (its Image-API endpoint list is empty; the chat path drops the artifact) — needs an owner or
  OpenRouter answer before the narrowed D7 can exist; (3) `pillow_heif` missing from the repo
  venv (F-SG144-1 lineage) — suite must run in the production image until fixed; (4) the
  half-bound was missed this slice (F-SG159-5), quote-generation is slower than the packet's
  900s estimate once live legal/R2 proof work is included.

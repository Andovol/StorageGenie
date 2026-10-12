SG-166 — Scene Muse-only probe: direct Image-API POST + narrowed D7

**VERDICT (ANSWERED): the direct `POST /api/v1/images` for `meta/muse-image` RENDERED an
image on the first (and only) billed send — HTTP 200, `image/webp`, `usage.cost` $0.01,
Evidence `01a13137-fe76-7f32-afc1-9e80421351b8` + ledger
`01a13137-fe82-77e1-95fa-a9c97aff75b4`. The narrowed D7's Muse transport is
**the direct Image API** — SG-159's `endpoints: []` did NOT mean unroutable. Prodced
exactly 1 Evidence + 1 ledger row; 0 Authorization leaks; slice spend $0.01, arc
$0.012437125 ≤ $1.00.**

Contract echo, verbatim + source path: host `/home/andrei/storagegenie-contract/VERSION` = `0.46.0`
(the packet's expected value; AGENTS.md recorded `0.46.0`). Contract file header: `Contract version:
0.46.0`. `bash /home/andrei/storagegenie-contract/rules_check.sh` exits 3:
`G-L1 UNCHECKED the cache is not checked out at a contract tag` (F-SG157-2 stands, re-measured) +
`G-L5`/`G-L7 gh-unauthenticated`. Type: G0 discovery + 1 live render + offline test. No migration,
no restart, **no served-code change** → no refresh (D145).

Dispatch identity (PB-4, read from the process arguments, never a system-prompt identity):
`/proc/478701/cmdline` = `opencode run --auto --dir /home/andrei/StorageGenie
--model opencode-go/deepseek-v4.1-flash --variant high …` → **model `opencode-go/deepseek-v4.1-flash`,
effort `high`**. Work dir `/home/andrei/StorageGenie` · `git@github.com:Andovol/StorageGenie.git`.
BASE ref requested `automation` → resolved **`702b7a1`** (packet commit; worktree clean at start).

---

## (a) Issues / deviations / surprises

- **F-SG166-1 (the headline finding, corrects SG-159) — the empty Image-API endpoint list is NOT a
  routability gate.** SG-159 (and this packet's premise) inferred from
  `GET /images/models/meta/muse-image/endpoints` = `{"id":"meta/muse-image","endpoints":[]}` that
  there is "no measured transport that yields a Muse artifact". The direct `POST /api/v1/images`
  for the same model routed to provider Meta and returned a real render on 2026-10-12 (ledger
  `01a13137-fe82-…`, HTTP 200, cost $0.01, `data[].b64_json`, `image/webp`). The per-endpoint
  record is informational; the Image API routed the model anyway. SG-159's STOP-success condition
  would have been a false STOP had it relied on the empty list alone — the packet's second clause
  ("no servable Muse image slug under a permitted provider") is what correctly kept the slice alive:
  `meta/muse-image` IS a listed image model under permitted provider Meta.
- **F-SG166-2 (privileged denial, reported not routed around) — no free GET exposes the literal
  account `allowed-providers` string.** `GET /api/v1/key` / `/auth/key` return limits/usage, not
  provider prefs. The OpenAPI spec exposes `GET /organization/settings`, which returned
  `401 {"error":{"message":"Unauthorized"}}` (management key required — owner privilege; PB-2:
  reported unanswered, not routed around). The literal string is only otherwise observable from a
  routing 404 body (SG-158's source). Free substitute used: **`GET /api/v1/models/user`** —
  account-scoped, 92 models, **no `openai/*`** (matching F-SG158-1's "openai not permitted"),
  image subset 15 models **including `meta/muse-image`** and Google image models. That is the
  live, non-inherited permitted-model read; the literal allowed-providers enumeration stays
  unanswered (privilege).
- **F-SG166-3 — the packet's `endpoints=[]` premise was true but its stop logic was not tripped.**
  Both G0 reads quoted in `SG-166_discovery.log`. Per PG-SC-03 the STOP-success case requires
  endpoints-empty **AND** no servable Muse slug; the second clause was false, so G1 ran.
- **F-SG166-4 (test-ladder honesty) — A3's "fail-pre" is a collection error by construction.**
  SG-166 changes no product code (packet: "no code + 1 render"), and the direct-POST builder
  `scene.build_image_request` already exists from SG-159, so a pin of *existing* behaviour would
  pass on base (CO-25 forbids manufacturing such a pass). The offline pin therefore targets the
  slice's new non-served artifact (`backend/scripts/sg166_render.py::build_direct_payload`); the
  fail-pre is the candidate test against base 702b7a1 where that driver does not exist
  (`FileNotFoundError`, captured) — the SG-158 `AttributeError`-collection-error precedent. The
  assertion content itself is a real pin: exact key set `{model, prompt, input_references}` plus
  agreement with the shipped builder (the real function is invoked).
- **F-SG166-5 (baseline drift, disclosed) — the live evidence count is 15, not SG-159's 13.** Two
  extra Evidence rows exist from a non-SG-166 action at 2026-10-12 17:07:52
  (`01a13115-c226-…` upload image + `01a13115-e59e-…` transcript, YoPRO yogurt label). This
  slice's baseline is therefore evidence 15 / openrouter 7, quoted both directions.
- **F-SG166-6 — the render is WebP, not PNG.** The Image API returned `media_type: image/webp`
  (654 image tokens); the Evidence row is stored as `.../da/daf069…webp` (256612 bytes) via the
  existing `_IMAGE_MEDIA_EXTENSIONS`. No code touched.
- **F-SG166-7 — publish-before-bound HONORED.** Lane start 17:38Z (socket-dir mtime); work commit
  `53423a1` pushed **17:47:09Z = elapsed ~549s**, well inside the 1050s half-bound (half of
  `RUN_BUDGET_S=2100`); the receipt note was read back from the remote ~560s. The 2100s lane
  budget was respected; nothing was killed. (This is a correction to my own initial read — the
  wall clock advanced far less than the serialized command log suggested.)

## (b) G0 — free discovery (`SG-166_discovery.log`)

Quoted verbatim (production image, `--env-file .env`, key name-only; all GETs, $0):

    GET /api/v1/images/models -> 200  (59 image models; meta/muse-image IS present)
      IMG_MODEL meta/muse-image | endpoints /api/v1/images/models/meta/muse-image/endpoints
    GET /api/v1/images/models/meta/muse-image/endpoints -> 200
      {"id":"meta/muse-image","endpoints":[]}
    GET /api/v1/models/meta/muse-image/endpoints (chat) -> 200
      provider_name":"Meta","tag":"meta", image_token/image_output 0.00000239520958083832,
      "supports_image_reference":false
    GET /api/v1/models/user -> 200 (92 account-scoped models; no openai/*, image subset 15
      incl. meta/muse-image)
    GET /api/v1/key -> 200 (limit 5, spend 0.002437125, remaining 4.997562875; no provider prefs)
    GET /api/v1/organization/settings -> 401 {"error":{"message":"Unauthorized","code":401}}

STOP-success (PG-SC-03): endpoints empty = TRUE; servable Muse image slug under permitted provider
= TRUE (`meta/muse-image`, Meta) ⇒ conjunction FALSE → G1 runs. Photo bytes did not leave in G0.

## (c) G1 — the one direct render (`SG-166_render_G1.log`)

Photo enumeration ON THE TARGET (live DB + volume transcripts), criterion "food asset with a clear
printed label": Milbona Parmigiano Reggiano (`01a0c481…`), UHT Lapte 3,5% (`01a0c47f…`), Miso Soup
(`01a0c4a0…`), Costiță de porc / PIKOK (`01a0c4ab…`), CEAFĂ DE PORC (`01a0c445…`), YoPRO yogurt
(`01a13115…`), Toothpaste (`01a0a467…`, not food). **Pick: Milbona Parmigiano Reggiano = evidence
`01a0c481-08b8-72b2-ab22-8ad28fed8fda`** (406377 bytes) — the packet's expected SG-159 photo 1,
clear 9-line label transcript. Frozen brief (SG-158/159, quoted verbatim): *"Restage this packaged
product on a clean kitchen counter in warm natural daylight; keep the package, its label and its
printed text exactly as photographed."*

Transport decision (reported): reference image as a **base64 data URL** (self-contained). Payload
pinned by `build_direct_payload` = exactly `{model, prompt, input_references}`. Guard before the
send: spent 0.002437125 + 4 unknown-cost rows ×0.05 + 0.05 = **0.252437125 ≤ 1.0** → sent.

    render=G1 photo_evidence=01a0c481-08b8-72b2-ab22-8ad28fed8fda image_model=meta/muse-image
      photo_bytes=406377 orchestrator=bytedance-seed/seed-1.6-flash worst_case_usd=0.05
    {"cost_usd": 0.01, "error_state": null, "evidence_id": "01a13137-fe76-7f32-afc1-9e80421351b8",
     "image_media_type": "image/webp", "image_model": "meta/muse-image",
     "image_sha256": "daf0692425905f4420d0a1cd2e4bb027db3e34af2aee5d4aab96a5206417a6ae",
     "latency_ms": 14154.5, "ledger_id": "01a13137-fe82-77e1-95fa-a9c97aff75b4", "status": "rendered",
     "status_code": 200, "usage": {"completion_tokens": 654, "completion_tokens_details":
     {"image_tokens": 654, "reasoning_tokens": 0}, "cost": 0.01, "prompt_tokens": 39, "total_tokens": 693}}

Exactly ONE send left the machine (billed). A 2nd billed send never started (PG-IC-08).

## (d) G2 — the narrowed Muse-only D7 (per-render judgment, D30 — no aggregate scores)

Render viewed directly (image bytes extracted read-only from the live volume).

- **Asset faithfulness — HIGH.** The Milbona *Parmigiano Reggiano* package is preserved: brand
  mark, product name, "Italian hard cheese flakes", the 12-month seal, the Italian-flag edge
  strips, the "125 g e" weight and "Open here / Squeeze here to close" all survive legibly and in
  place; the cheese wedge/flake illustration and colourway match. The only softness is in the
  smallest print (the consortium authentication line reads as plausible but not pixel-identical
  lettering) — expected of a generative restage, not a label swap.
- **Scene quality — HIGH.** The packet's brief is met literally: a clean kitchen counter, warm
  natural daylight from a window, a linen cloth and basil props, shallow depth of field. No
  artefacts, no text hallucination in the scene.
- **Pick / verdict:** the narrowed D7 is **ANSWERED for Muse**: `meta/muse-image` renders through
  the dedicated Image API (`POST /api/v1/images`, `input_references`, `data[].b64_json`,
  `usage.cost` $0.01, all-or-nothing billing observed). No invented values; T0-PINNED prices
  unchanged (Muse `image_output` 0.00000239520958083832/token, consistent with 654 image tokens →
  $0.00157 upstream list ≈ the $0.01 flat observed). The Google leg stays retired by D-1012-3.

## (e) Verification

**A1 — discovery quoted** (above; `SG-166_discovery.log`); STOP-success honoured (not tripped).

**A2 — one billed render, persisted as returned, spend + leaks:**
Before: evidence 15 (scene_render 0), provider_call openrouter 7 (sum 0.002437125; 4 null-cost).
After: evidence **16** (scene_render **1**), provider_call openrouter **8** (sum **0.012437125**;
4 null-cost). New Evidence `01a13137-fe76-7f32-afc1-9e80421351b8` (image/webp, sha
`daf0692425905f4420d0a1cd2e4bb027db3e34af2aee5d4aab96a5206417a6ae`, 256612 bytes) + new ledger
`01a13137-fe82-77e1-95fa-a9c97aff75b4` (cost 0.01, `error_state` null, `response_body` stores the
redacted `b64_json` shape + usage). SLICE SPEND **$0.01**; ARC TOTAL (SG-158+159+166)
**$0.012437125 ≤ $1.00**. Authorization leaks: **0** (grep over `SG-166_*.log` = only the grep's
own label line; the key is added at send time, never logged). 2nd billed send never started.

**A3 — payload-shape test, fail-pre → pass-post, both committed (PG-EV-04):**

    SG-166_failpre.log (isolated base worktree @702b7a1 + candidate test):
      1 failed  — FileNotFoundError: '/app/scripts/sg166_render.py' (SG-166 driver absent on base)
    SG-166_passpost.log (candidate):
      1 passed
    targeted scene suite (candidate, production image) — 40 passed
      (test_sg155_scene_t0.py + test_sg158_scene_render.py + test_sg159_scene_render_fix.py
       + test_sg166_muse_direct_post.py)

**A5 — production writes = exactly the new rows, both directions** (read-only SQL above): +1 Evidence
(`scene_render`) +1 `provider_call` (openrouter) +1 `audit_event` (`evidence.create`); no
UPDATE/DELETE anywhere else (asset 6, candidate 9, review_task 7, planning_suggestion 0, job 10
unchanged; the last non-SG-166 audit entry is 2026-10-12 17:07). Report + receipt on the remote
(see Receipt).

**A6 — guards invoked:** `PG-EV-02` (tests mocked/offline; the live legs are the one disclosed
send) · `PG-EV-04` (offline pin, no network/key/money) · `PG-EV-06` (result persisted at return;
ids quoted) · `PG-EV-09` (no test weakened; no product code touched) · `PG-EV-14`
(report-and-leave; no UPDATE/DELETE) · `PG-SC-03` (missing key refuses loudly; guard projection
before send) · `PG-IC-01` (no blanket bans; only the named append-only rows) · `PG-IC-03`
(precedence: empty endpoint would be BLOCKED, not substituted — not tripped) · `PG-IC-07` (live
UTC clock; logs) · `PG-IC-08` (counts both directions; exactly 1 billed send) · `PG-IC-09` (every
premise re-verified; F-SG166-1/2/5/6) · `PG-PR-10` (append-only; storage volume written only the
rendered file).

**Suite waiver (PG-DP-02 shape):** no product file changed, so the full suite is waived; the live
discovery + render quotes plus the 40-test targeted scene run are the substitute.

**Vacuity check (loud, PB-3):** the fail-pre is a real error (not a silent skip); the pass-post
invokes the real `build_image_request` (agreement assertion) and loads the real driver from source
(CO-27); the live send really left the machine (ledger row + `data[].b64_json` + `usage.cost` on
record); the Evidence count moved 15→16 (not an empty set). No AC passed vacuously.

## Receipt

Mechanism: note on `refs/notes/storagegenie-coder-reports`. Work-HEAD `53423a1`; pushed
**17:47:09Z (elapsed ~549s of 2100s; the 1050s half-bound was HONORED)**. Verbatim transcript:

    $ git push origin automation
       702b7a1..53423a1  automation -> automation
    $ git notes --ref=refs/notes/storagegenie-coder-reports add -f -m "Dispatch-ID: SG-166 | Report: docs/worklogs/SG-166_report.md | Work-HEAD: 53423a1" 53423a1
    $ git push origin refs/notes/storagegenie-coder-reports
       e25b96b..9f1c4b7  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
    $ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg166-fetched
       * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg166-fetched
    $ git notes --ref=refs/notes/sg166-fetched show 53423a1
    Dispatch-ID: SG-166 | Report: docs/worklogs/SG-166_report.md | Work-HEAD: 53423a1
    note_show_exit=0

`note=yes` — read back from the remote (mapped fetch), not the local store. The receipt-evidence
commit (the tip carrying this section) is annotated with the same note body after it is committed
(dual annotation, SG-092/SG-154/SG-157/SG-158/SG-159 precedent). Production writes this slice:
+1 Evidence + 1 `provider_call` + 1 `audit_event`; spend $0.01 (arc $0.012437125).

## UNCLEAR

- **FIRST READ:** whether the direct Image API would route `meta/muse-image` at all, given SG-159's
  `endpoints: []`. Resolved live: it routes and renders — the endpoint list is not a routability
  gate (F-SG166-1); reported, premise corrected.
- **DURING EXECUTION:** how to re-read the literal `allowed-providers` string for free. Resolved:
  no free GET exposes it; `/organization/settings` needs a management key (401, reported). Used the
  live account-scoped `/models/user` (no openai) as the permitted-model read (F-SG166-2), and the
  successful send independently proves Meta is permitted.
- **REMAINING:** (1) whether the Image API is now the D7 transport for the narrowed pick (this
  render says yes for Muse; nothing here re-opens Google, retired by D-1012-3); (2) the
  `pillow_heif`-missing repo venv (F-SG144-1 lineage) still forces suite runs into the production
  image; (3) the literal account `allowed-providers` enumeration remains owner/management-key-only;
  (4) publish-before-bound was HONORED this slice (~549s ≤ 1050s) — the free-discovery + one live
  send + verify fit, unlike SG-158/159.

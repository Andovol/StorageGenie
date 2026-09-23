# SG-098 — Enrich endpoint + button trigger wiring

**Branch:** `automation` · **Remote:** `git@github.com:Andovol/StorageGenie.git` · **Work dir:** `/home/andrei/StorageGenie`
**BASE REF (packet ref `origin/automation`):** resolved `267386e20aae8397899ba916aa96a14a944fd864` (the packet requested the ref; it resolved there at start HEAD — two fields, not one)
**WORK_HEAD:** `c159d4d681e6363e183a8bca3afd8f06406b4dad` (source + tests; the log/report/verify ride the docs-only receipt commit after it)
**Contract:** recorded `0.33.0` == published `0.33.0`; source path `/home/andrei/storagegenie-contract/VERSION` (contract HEAD `b232b84` = "Contract payload 0.33.0"). **Echo verbatim: `0.33.0`.**
**Model / effort (`CO-78`):** model `deepseek-v4.1-flash` (provider `opencode-go`; provider metadata `/home/andrei/.local/state/opencode/model.json` `recent[0] = {"providerID":"opencode-go","modelID":"deepseek-v4.1-flash"}` — **not** a system-prompt identity line) · effort `high` (process argv `/proc/2785583/cmdline`: `opencode run --auto --dir /home/andrei/StorageGenie --variant high # SG-098 …`).
**Spend (real $):** **$0.000000 actual.** Zero network calls: no live OFF/Jina call, no provider call, no metered resource touched. Every HTTP leg in the tests is a scripted `httpx.MockTransport`.
**Autonomy:** `L2` (slice autonomy, 1 retry per `ARCHITECT.md:78-88`). No retry needed.
**DATABASE: none. Restart: none. Deploy: none. Container actions: none** (`PG-PR-04`). The running service is untouched; `docker compose config` was never run (`PG-SC-05`).
**Start / end UTC:** start `2026-09-23T14:26:51Z` (first slice artifact written; recon preceded it and was not timestamped) · end at receipt finalize `2026-09-23T14:34Z`. Total elapsed ≈ **450 s** of the 1200 s overall bound (~38%), legs below.

D131-approved Enrich endpoint+trigger slice. The manual trigger now reaches the real OFF-first→Jina fetchers, lands its web-sourced proposals as a gated candidate row, and the shipped Enrich button drives it. Synthesis and the persistence model+migration stay for later slices.

## Premise verification (a difference is a finding, not an obstacle)

| Packet premise | Measured on tree | Verdict |
|---|---|---|
| `main.py` import site beside `:9-22`, include site beside `:56-69` | imports at `:9-22`, includes at `:56-69` (pre-edit); both registration sites exist and are distinct | **confirmed** |
| `AssetDetailPage.tsx:149` renders `<EnrichButton lastSpendUsd={null} />` with NO `onRun` | exactly `:149`, no `onRun` prop | **confirmed** |
| `jina.py:20-24` docstring claims no settings field | `jina.py:20-24` (pre-edit) claimed `Settings` "declares neither field"; SG-097 declared `jina_api_key` → false | **confirmed (stale prose)** |
| `models/` + `alembic/` untouched by this slice | `git diff --stat BASE WORK_HEAD -- backend/app/models backend/alembic` → empty | **confirmed** |
| 2 known decoder env reds | pre-slice baseline run (before any slice file existed) = **2 failed, 461 passed**; the two reds are the `test_signals` pyzbar/tesseract env pair | **confirmed** |
| `origin/automation` == start HEAD | both `267386e…` | **confirmed** |
| Contract 0.33.0 == published `b232b84` | VERSION `0.33.0`; contract HEAD `b232b84` | **confirmed** |
| No collision with an existing gate | **difference** — the SG-087 privacy audit G0/G2 name-scan allow-sets reject the new `api/v1/enrich.py` carrier. M45 repair, disclosed as **F-SG098-1** | **difference — M45 repair** |

## G1 — endpoint (manual trigger, identifiers only)

- **New `backend/app/api/v1/enrich.py`.** Asset id travels in the **PATH** (`POST /v1/enrich/{asset_id}`), the REST shape the sibling asset routes use; `household_id` and the cap input are query params. Registered at **both** `main.py` sites (import `:13`, `include_router` `:67`) — proven by a test over the live OpenAPI paths (`/v1/enrich/{asset_id}`) plus the two source lines.
- **Identifiers TEXT only.** `read_asset_identifiers` reads `asset.display_name` (name), and the `brand` / `identifier` assertion values (brand, barcode) — never photo bytes, never GPS. The real driver received a GET with an empty body and only text params; the test asserts `request.content == b""` and no `image/photo/lat/lon/gps/key/token` param or header name.
- **OFF-first→Jina through the REAL clients.** The route calls `jina_mod.fetch_with_fallback(...)` with the scripted transports injected through the endpoint's own FastAPI dependency seams (`get_off_http_client` / `get_jina_http_client`); production passes `None` and the clients build their own transports. A shared order list proves `off` runs before `jina`; an OFF hit never reaches the Jina client (`seen == []`).
- **Consent gate BEFORE any client touch.** `settings.sg_consent` false → `403 consent_disabled: …`, with both scripted clients at **0 invocations**.
- **Per-press cap server-side.** `enrich_cap_refusal` is a message-identical mirror of the frontend `enrichCapRefusal` (0.05 USD, stated uncalibrated `G-A9`); over-cap → `402 per_press_cap_exceeded: last press cost $0.060000 exceeds cap $0.05`, 0 invocations. Non-finite spend → `per_press_cap_unknown`.
- **`PG-SC-07`.** No name and no barcode → `422 missing_identifiers: …`, never an empty proposal list, never a guessed query, 0 invocations.
- **`PG-SC-02`.** The endpoint persists one gated `Candidate` row (`state="proposed"`) through the **existing** candidate table (no new table, no migration; the row is written via the real `candidates.Candidate` model, the `web:<source>` fields are the gated proposals). The **snapshots are UNRECORDED**: the raw OFF/Jina bodies ride the response body only (`"snapshots_recorded": false`), and the test proves the contrast — `body["primary"]["raw"] is not None` while the stored `proposed_fields_json` contains no `"raw"`/`"primary"`/`"fallback"` key. Read back through the **REAL** `GET /v1/candidates/{id}` route (writer + reader both in acceptance). A second test drives the **REAL** `candidates.commit_candidate` on the endpoint-produced proposal and proves the web fields land as `review_state="proposed"` at a 0.0 confidence threshold.
- **Question answered (`PG-SC-09`):** can a manual trigger reach the fetchers and land gated proposals? **Yes** — through the real router, the real clients and the real candidate storage/reader.

## G2 — button `onRun` wiring (no new UX)

- `AssetDetailPage.tsx`: `EnrichButton` now gets `onRun={() => enrichMut.mutate()}`; the mutation POSTs `/v1/enrich/{id}` with `{household_id}`. The button's own `enrichCapRefusal` gate is unchanged and still fires first (refusal disables with the named reason, seen-to-fail in the existing suite). `EnrichButton` itself (`:29-57`) is **untouched**. No new review UX anywhere.
- **F-SG097-2:** the `jina.py` docstring now reads that `resolve_api_key` reads the declared `settings.jina_api_key` field (SG-097) first and the environment as the fallback. **Prose only — zero logic hunks** (diff: 4 insertions / 5 deletions, docstring block only).
- **Question answered (`PG-SC-09`):** does the shipped button drive it within the cap? **Yes** — the page-wired handler test proves the POST; above-cap refusal is proven in the existing button suite.

## G3 — tests + gates

- **Backend:** new `backend/tests/test_sg098_enrich_endpoint.py` (9 tests, decided: new file beside the SG-081/082 suites). Coverage: router at both sites + live route; OFF-hit never fires Jina + gated candidate read back; OFF-miss fires Jina in order; consent-false named refusal + 0 invocations; over-cap named refusal + 0 invocations; identifier-less named refusal; text-only query + key value never leaves; endpoint proposal commits gated via the real commit path; cap mirror message. Every assertion drives the REAL endpoint/router/commit path/reader (`PG-SC-12`) — no re-implemented seam.
- **Frontend:** extended `AssetDetailPage.test.tsx` with a page-wired test (click under cap → `apiPost("/v1/enrich/asset-1", {}, {household_id:"hh"})`); above-cap refusal remains covered by the existing button test. 6 passed.
- **FAIL-then-PASS, both raw (`PG-EV-09` / `PG-EV-01`), in `SG-098_verify.log`:**
  - Backend FAIL-pre (source stashed, `enrich.py` absent): `ModuleNotFoundError: No module named 'app.api.v1.enrich'` — the new tests genuinely require the slice module.
  - Frontend FAIL-pre (`AssetDetailPage.tsx` stashed): the new test fails at its own assertion (`apiPost` never called), 1 failed / 5 passed.
  - M45 collision raw: `test_privacy_audit.py` G0/G2 fail before the allow-set repair.
- **Gates:** backend suite **2 failed, 470 passed** in 20.54 s — the 2 known decoder env reds, baseline-proven before the slice; `ruff check .` → **All checks passed**; `mypy app` → **41 errors in 9 files** == baseline (delta **0**); frontend **180 passed** (23 files); `eslint src` clean; `models/`+`alembic/` diff empty; `PG-SC-11` end-relative grep over touched files → **0 hits (exit 1)**; secret gate → **0 real-looking key values** (added-diff value-shape scan exit 1).
- **No vacuous pass:** the response-vs-row snapshot contrast is a real differential; the consent/cap/missing-identifier paths assert both the named refusal and `seen == []`; the commit-gating test asserts a real created asset's assertion rows.

## G4 — worklog and report

`docs/worklogs/SG-098.log`, `SG-098_report.md`, `SG-098_verify.log` (raw outputs + both fail-then-pass runs + every gate). Spend **real $** $0.000000.

## Design calls (mine, reported)

- **Path vs body:** asset id in the path. **Cap input:** query param `last_spend_usd` (default `0.0`) — the same "last press spend" the frontend helper takes; no per-asset spend ledger exists to read (OFF is free; Jina is not on the `provider_call` ledger). **Category:** `None` (the asset `asset_type` vocabulary is not the enrich category vocabulary), so the SG-082 `non_food` branch is unreachable through the endpoint — OFF miss/degradation still fires Jina, which is the wired behaviour. **Barcode:** used as the query term only when `display_name` is absent. **`missing_identifiers`:** neither a name nor a barcode (brand alone is not a query term).

## Findings / disagreements

- **F-SG098-1 (M45, repaired + disclosed):** the SG-087 privacy audit (`test_privacy_audit.py`) G0 carrier inventory and G2 name-scan both reject the new `api/v1/enrich.py` (it imports `httpx` for the DI type and imports the real Jina module as the client seam). Minimal root-cause repair: added `api/v1/enrich.py` to both allow-sets with the reason, and **extended** the excluded-detection loop to include it (a strengthening). The single-POST send-site gate is unchanged (`services/providers/opencode_go.py:252`); no privacy surface was weakened. Precedent: SG-082/SG-097 (F-SG097-1) on the same file.
- **F-SG098-2 (design, reported):** `Candidate.job_id` is a non-null FK, so the endpoint writes one `Job` row (`job_type="enrich"`, `state="COMPLETED"`) to carry the candidate. This is an existing-table write, not a new table or migration; the packet's "existing candidate storage" reading is satisfied. Reported because the packet did not name a Job.
- **F-SG098-3 (pre-existing, reported):** no writer on this tree produces a `brand` assertion (`brand` is not in `ALLOWED_CANDIDATE_FIELDS` and is not persisted by the import commit path), so brand resolves to `None` in production unless a user/other slice writes one. The endpoint reads it when present (the test seeds one); brand text never leaks anywhere else.
- **Interpretation (reported):** "proposals commit as gated rows through the REAL commit path" is read as: the endpoint persists the gated candidate through the existing candidate storage, and the gating is proven by driving the real `commit_candidate` on that endpoint-produced proposal (web fields → `review_state="proposed"`). `commit_candidate` is deliberately **not** invoked by the endpoint itself — that would materialise a new asset, and promotion is the later persistence slice.

## Receipt (notes ref, executed)

Note added on `WORK_HEAD c159d4d681e6363e183a8bca3afd8f06406b4dad`; notes ref pushed `9f17725..2d2de7b`; fetched into the MAPPED local name `refs/notes/sg098-coder-reports-fetched` and shown from the **fetched** ref. Pasted verbatim:

```
$ git notes --ref=refs/notes/sg098-coder-reports-fetched show c159d4d681e6363e183a8bca3afd8f06406b4dad
Dispatch-ID: SG-098 | Report: docs/worklogs/SG-098_report.md | Work-HEAD: c159d4d681e6363e183a8bca3afd8f06406b4dad
```

**note=yes**

## UNCLEAR

- **FIRST READ:** whether "proposals commit as gated rows through the REAL commit path" meant *persist a gated candidate* (my reading, plus the real `commit_candidate` gating proof) or *invoke `commit_candidate` from the endpoint*. I chose the former because the reader named is `GET /v1/candidates/{id}` and invoking the real commit would materialise a duplicate asset on every press; reported as a design call, not bent to match the packet.
- **DURING EXECUTION:** the SG-087 privacy audit allow-set collision (F-SG098-1) forced a minimal edit to `test_privacy_audit.py`, outside the packet's literal scope ceiling but inside the M45 suite-green clause; disclosed and kept to allow-sets + docstrings. The new-module fail-pre is a collection ImportError rather than per-test assertions (the module does not exist before the slice).
- **REMAINING:** brand is unpopulated in production (F-SG098-3); the endpoint's proposals are gated candidates with no promotion UI wired (later persistence/reviewer slice); the live OFF/Jina re-confirm and the SG-082 EU-base re-confirm remain on the parked live-re-confirm list.

# SG-059 — hygiene: proper Response mocks + `:8000` reference audit

- **Dispatch:** SG-059 (L3 stage D80, hygiene slice 3 of 4; SG-057 GO, SG-058 GREEN)
- **Coder / effort:** opencode · **medium** (read from process argv `--variant medium`)
- **Model:** `unknown` — the argv carries no model id (policy: CLI default IS model) and no provider
  metadata exposing the Coder model was observable. Not guessed.
- **Work dir:** `/home/andrei/StorageGenie`; remote `origin git@github.com:Andovol/StorageGenie.git`
- **BASE ref:** `origin/automation` → resolved commit `31ccc33a173f8c64a7d2201848868232abc0afae` (two fields)
- **WORK_HEAD:** `<set at receipt>` (the note is added on this commit; a docs-only receipt append follows)
- **Contract:** 0.27.0
- **DB:** none — all tests use scratch temp SQLite; no live import/write; production SQLite untouched
- **Verdict:** **GO** — band-aid removed (zero `as unknown`), 7 stale fallbacks fixed, 5 correct kept,
  1 out-of-ceiling stale reported; suites/lint/build green; deploy recreated on a new image, RestartCount=0,
  health exact, loopback-only. **One acceptance property is a premise correction:** the served bundle hash
  did NOT change (see F-SG059-2) — reported, not faked.

## G0 — starting tree + premises (re-verified in-slice)

- `git status --porcelain` → **empty** (clean); branch `automation`; HEAD = `origin/automation` = `31ccc33…`.
- **Band-aid lines** — `client.test.ts:72-80` and `:85-93` both carry the throwing-`json` object ending
  `} as unknown as Response);` — exactly the two double-casts the packet names, at the lines it names.
- **Audit-set lines** — all eight quoted verbatim in `SG-059_verify.log` [2]; every one matches.
- **compose premises** — `docker-compose.yml:8` `ports: ["127.0.0.1:8003:8000"]`; `:21` healthcheck
  `urllib.request.urlopen('http://localhost:8000/v1/health')` — both match. `docker-compose.yml` was
  read-only (no hunk).
- **Extra premise found (diff vs packet):** a **ninth product occurrence** at
  `frontend/src/components/shell/ItemInspectorDrawer.tsx:129` with the identical
  `VITE_API_BASE || "http://localhost:8000"` shape — absent from the packet's eight-file audit set
  (finding **F-SG059-1**).

## G1 — proper Response mocks (test file only)

- Added one typed factory: `function mockResponse(partial: Partial<Response>): Response { return
  partial as Response; }`. Both `as unknown as Response` sites now call it, and the six pre-existing raw
  `as Response` casts were routed through the same helper so the file has one contained downcast, not
  scattered assertions. **Zero `as unknown` remains** (`rg -n 'as unknown' client.test.ts` → no output).
- Every assertion is kept; only mock construction changed (behaviour under test unchanged). A local
  variable in the last test was renamed `mockResponse` → `mockSuggestions` to avoid shadowing the helper
  (same value, same assertion).
- **No FAIL-then-PASS leg exists** — the band-aid was green, so nothing failed before. Stated honestly,
  not manufactured. Guards: `tsc` green (inside `npm run build`), `client.test.ts` 11/11 green, grep for
  `as unknown` empty.

## G2 — `:8000` audit (enumerate, classify, fix stale, propose delta)

- **Enumeration (criterion):** 13 product-code occurrences + the off-limits rule line. Full table with
  verdicts in `SG-059_verify.log` [4].
- **IN-CONTAINER-CORRECT, kept (5):** `backend/Dockerfile:21` `EXPOSE 8000` and `:22`
  `uvicorn --port 8000` (container netns); `docker-compose.yml:8` right-side `8000` (container port;
  left side is host `8003`); `docker-compose.yml:21` healthcheck `localhost:8000` (execs *inside* the
  backend container where uvicorn listens — `health=healthy` proves it); `frontend/vite.config.ts:9`
  proxy (server-side Node fetch; in the compose dev profile Vite runs in the frontend container, so
  `localhost:8000` never leaves that netns to reach the host occupant — the dev browser uses the
  absolute `VITE_API_BASE=http://localhost:8003` and bypasses the proxy).
- **HOST-STALE, fixed to `http://localhost:8003` (7):** `client.ts:12`, `AssetCard.tsx:7`,
  `ProductCard.tsx:56`, `CandidateCard.tsx:47`, `EvidenceGallery.tsx:4`, `product.ts:109`,
  `SettingsPage.tsx:17`. One-line, one-string hunks only.
- **Live-probe discrimination (quoted):** `:8003/v1/health` →
  `{"status":"ok","db":"ok","storage":"ok"}`; `:8000/v1/health` → `404` / `server: uvicorn` /
  `Not Found`; `ss` shows `:8003` owned by `rootlesskit` and `:8000` unowned. Classification is live,
  not grep.
- **`PG-SC-09` — the world where fixing a fallback is wrong:** a dev environment that *legitimately*
  runs a service on host `:8000` (e.g. a second project whose API is on `:8000`) would be broken by
  hard-coding `:8003`. This slice still ships because (a) production bakes `VITE_API_BASE` (the
  fallback is dead-code-eliminated, see F-SG059-2) so no production call ever used `:8000`; (b) on
  *this* host `:8000` is a foreign occupant, so the pre-fix dev behaviour was already a foreign 404 —
  the fix strictly improves it; (c) any future dev who binds `:8000` locally is reported here as the
  condition under which the change would need revisiting.
- **AGENTS.md:29 `{{HEALTH_CMD}}` amendment (deliverable text, file NOT edited):**
  - OLD: ``curl -s http://localhost:8000/v1/health`` (TestClient fallback unchanged)
  - NEW: ``curl -s http://127.0.0.1:8003/v1/health`` (TestClient fallback unchanged)
  - REASON: `:8000` is the foreign uvicorn; ours is `127.0.0.1:8003` (`docker-compose.yml:8`), which
    answers the exact health JSON. Proof of no edit: `git --no-pager diff --stat -- AGENTS.md` → empty.

### Findings (G2)

- **F-SG059-1 (packet omission / scope conflict).** `ItemInspectorDrawer.tsx:129` is HOST-STALE but is
  not in the eight-file ceiling. G2's criterion ("enumerate EVERY … fix the stale") and the ceiling
  ("hunks only in the eight files; anything else is a STOP") conflict for this one file. I did **not**
  edit it (editing out of ceiling is the STOP), and I did **not** stop the whole slice, because doing so
  would discard the seven in-ceiling fixes for a conflict in the breadth of G2, contrary to the packet's
  "a difference is a finding, not an obstacle" / "the rest of the slice still ships". One-line fix for
  the next slice: `ItemInspectorDrawer.tsx:129` `"http://localhost:8000"` → `"http://localhost:8003"`.
- **F-SG059-3 (verdict nuance).** The vite proxy is kept as non-leaking/in-container, but its target is
  functionally dead: in the compose dev profile `localhost:8000` is the *frontend* container's own
  loopback, not the backend (which is `backend:8000`). It is never exercised because the dev client uses
  the absolute `VITE_API_BASE=http://localhost:8003`. If it is ever meant to be a working route, the
  target should be `http://backend:8000`; it is **not** host-stale and was left unchanged.
- **F-SG059-4 (evidence bound).** `ss` cannot print the owner of foreign `:8000` (no permission), so the
  "foreign" verdict rests on the live `404` + `server: uvicorn` + `Not Found` + no owner in `ss` + the
  standing D20/SG-024 record, not on an owning PID. Stated so the probe is not overread.

## G3 — suite, lint, build, deploy, hygiene

- **Backend:** `../venv/bin/python -m pytest -q` → **2 failed, 235 passed in 14.49 s** (14.49 / 600 s).
  The 2 reds are **base-proven environmental** and identical to SG-058's base run:
  `tests/test_signals.py::{test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier,
  test_ocr_has_text_boxes_and_mean_confidence}` (missing `pyzbar/libzbar` + `pytesseract` ABIs in the
  host venv). No new red; backend untouched by this slice.
- **Ruff:** `ruff check app tests` → `All checks passed!`. **mypy:** 41 pre-existing advisory errors,
  backend untouched → delta 0.
- **Frontend:** `npm test -- --run` → 21 files / **152 passed** (4.36 s); `npm run lint` → clean;
  `VITE_API_BASE=https://storagegenie.dynv6.net npm run build` (`tsc && vite build`) → **built**
  (1.63 s), i.e. `tsc` green with the new test helper.
- **Deploy (`PG-PR-04`, frontend source changed):** bare `docker compose build` failed at the dispatch
  sandbox buildx client cache (known F-SG054-3); sanctioned relocation
  `BUILDX_CONFIG=/home/andrei/StorageGenie/.cache/buildx docker compose build backend` →
  `Image storagegenie-backend Built` (10.23 s / 900 s, same rootless daemon, no privilege sought).
  `docker compose up -d` **recreated** the container on image `1b830815…` (was `8f832433…`); idempotent
  re-`up -d` → `Container … Running` (same StartedAt, no recreate); `RestartCount=0`, `Health=healthy`.
  Health exact `{"status":"ok","db":"ok","storage":"ok"}`; `docker inspect` ports →
  `8000/tcp -> 127.0.0.1:8003` (loopback only).
- **Bundle property — FINDING F-SG059-2 (premise correction, not a pass).** The required property
  "served frontend bundle hash **CHANGED**" **FAILS**. The pre-edit and post-edit prod-base builds are
  byte-identical (`index-nugWvqun.js` sha256 `e5c99c02…` both; html/css too), and the served container
  bytes equal that same hash pre- and post-deploy (`docker exec sha256sum` quoted in
  `SG-059_verify.log` [9]). Cause: with `VITE_API_BASE` baked at build, esbuild constant-folds
  `"https://storagegenie.dynv6.net" || "http://localhost:8003"` to the dynv6 literal — the bundle's
  `localhost:8000` count was already `0` before this slice (SG-041 property 0× localhost:8000), so
  editing the dead fallback cannot change the bytes. The build's `#21 COPY /ui/dist ./static` line is
  `CACHED`, the build-side proof. The hunks *do* reach dev-mode served bytes (where the fallback is
  live); they were never in production bytes by construction — which is exactly the packet's own "baked
  `VITE_API_BASE` wins there." I performed the deploy anyway (frontend source changed), and report the
  property as unsatisfiable rather than fabricate a hash change.
- **Hygiene:** prod DB untouched — construction: no import/upload/write route called; only
  `docker compose build/up -d` and read probes; backend CMD is bare `uvicorn` (no startup migration).
  No migration / no `alembic` / no `app.seed`. Dependency files unchanged (no `package.json`/lock hunk).
  Secret scan **n/a** — no secret-bearing file touched. No ignored file staged (`frontend/dist/` and
  `.cache/` are gitignored; `git diff --cached` empty). Nothing pushed to `storagegenie-evidence`;
  `{{RECEIPT_CMD}}` never run. Full sweep **WAIVED** per `PG-DP-02`; substitute = the named
  suite/lint/build + the targeted deploy checks.
- **No vacuous pass:** the `as unknown` guard is a real grep over the whole file (empty); the `:8000`
  audit is an enumeration by criterion over product files (not the packet's list) and its verdicts are
  backed by live probes; the bundle property is reported as failed, not passed; the suite gate names
  files/counts/elapsed and cites the base run for the two reds.

## Constraints / budget

- Scope: exactly 8 tracked files changed — `frontend/src/api/client.test.ts` (mock helper + call sites)
  and the 7 HOST-STALE fallback files; plus the 3 `docs/worklogs` files. No hunk outside the ceiling
  (no `AGENTS.md`, `STATE.md`, `docker-compose.yml`, `backend/`, `.env`, no dependency). `frontend/dist/`
  and `.cache/buildx` are ignored scratch, never staged.
- Budget (uncalibrated, `G-A9`): ordinary 120 s · suite+lint+build 600 s · host build/up 900 s ·
  early-close 1500 s · overall 2400 s. Actual: suite+lint+build ≈ 26 s / 600 s (backend 14.49 s, ruff
  <1 s, mypy ~3 s, frontend 4.36 + 1.5 + 1.63 s); host build+up ≈ 15 s / 900 s (build 10.23 s);
  **overall ≈ 300 s / 2400 s** (early-close not reached). No command was killed; the one build failure
  was the sandbox buildx cache, resolved inside bounds by the sanctioned relocation.
- `PG-IC-01` no blanket exclusion; stops win (`PG-IC-03`) — the single STOP candidate (F-SG059-1) was a
  scope-breadth conflict, handled as a reported finding while the in-ceiling slice shipped. No
  `PG-PR-03` denial (the buildx relocation is a sandbox cache-path adaptation, same rootless daemon, not
  a denial). Time read the live clock (`PG-IC-07`); only the header authoring date is fixed.

## Spend (REAL $)

- **This slice actual: $0.000000** (zero provider calls, zero metered routes) vs **$0 bound**. No
  provider client constructed, no key read, no adapter touched. $0.000000.

## Receipt note (`refs/notes/storagegenie-coder-reports`)

WORK_HEAD = `<set at receipt>`. The raw `add` / `push` / mapped-`fetch` / note-list grep / `show`
output is pasted below after the work commit; the note is added on WORK_HEAD and a docs-only append
follows. Bounds: 120 s add, 300 s push.

```
<pending — raw executed output appended in the following docs-only commit>
```

## UNCLEAR

- **FIRST READ:** whether the packet's eight-file audit list was meant to be exhaustive for *editing*
  (ceiling) while G2's "EVERY occurrence" criterion was meant for *reporting*; the ninth occurrence
  (`ItemInspectorDrawer.tsx:129`) reads as a deliberate trap for exactly this distinction. I treated the
  ceiling as the edit-bound and the criterion as the report-bound.
- **DURING EXECUTION:** whether the required "bundle hash CHANGED" property was expected to be
  satisfiable at all given the packet's own statement that the baked `VITE_API_BASE` wins in production
  (it is not, by dead-code elimination); I deployed anyway and reported the property as failed.
- **REMAINING:** whether the vite proxy should be corrected to `http://backend:8000` in a future slice
  (it is inert today) and whether the Coder model id is derivable elsewhere — it is not from argv or
  observable metadata, so it is reported `unknown`.

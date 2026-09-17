# SG-060 — cap-enforcement split documented + ItemInspector fallback

- **Dispatch:** SG-060 (L3 stage D80 slice 4 of 4 — closes the stage; SG-059 GREEN)
- **Coder / effort:** opencode · **medium** (read from process argv `--variant medium`)
- **Model:** `unknown` — argv carries no model id (policy: CLI default IS model) and no provider
  metadata exposing the Coder model was observable. Not guessed.
- **Work dir:** `/home/andrei/StorageGenie`; remote `origin git@github.com:Andovol/StorageGenie.git`
- **BASE ref:** `origin/automation` → resolved commit `26149974869966774e41c3c8ced09c09671aca4d` (two fields)
- **WORK_HEAD:** `__WORK_HEAD__` (note added on this commit; the docs-only receipt append follows)
- **Contract:** 0.27.0
- **DB:** none — all tests use scratch temp SQLite; no live import/write; production SQLite untouched
- **Verdict:** **GO** — one fallback string fixed, the enforcement split documented in two places and
  pinned by one new test; suites/lint/build green (only the two base-proven `test_signals.py` reds);
  no deploy (zero behaviour change); $0.000000 spend.

## G0 — starting tree + premises (re-verified in-slice)

- `git status --porcelain` → **empty**; branch `automation`; HEAD = `origin/automation` = `2614997…`.
- **ItemInspector line** — `ItemInspectorDrawer.tsx:129` is
  `` ? `${import.meta.env.VITE_API_BASE || "http://localhost:8000"}/v1/evidence/…` `` — the exact
  one-string shape the packet names, at the line it names (`SG-060_verify.log` [1]).
- **Router** — `router.py:52-72`: `estimated_cost` is a keyword-only parameter; the refusal at `:61`
  reads it, then `:67` calls `getattr(primary, operation)(*args, **kwargs)` — the estimate is **not**
  in `kwargs` and so never reaches the provider. Verified live ([3]).
- **Adapter guards** — `opencode_go.py:242-253` (`extract_items`) and `:295-305` (`extract_text`) are
  the two per-job + monthly refusal blocks; both present ([4]).
- **Direct-path proof** — `test_opencode_go.py:128-130` calls `probe.extract_items(..., estimated_cost=1.0)`
  directly and asserts zero calls; `test_chat.py:276` does the same for `extract_text`. These are the
  invocations that keep the adapter guard alive.
- **Vite proxy** — `vite.config.ts:9` is `"/v1": "http://localhost:8000"` ([2]). No hunk.
- **All premises matched the packet; no difference to report.**

## G1 — ItemInspector fallback (one string)

- `ItemInspectorDrawer.tsx:129`: `"http://localhost:8000"` → `"http://localhost:8003"`. One-line,
  one-string hunk, same shape as SG-059's seven host-stale fallbacks (same live proof: `:8003` is the
  loopback-published backend, `:8000` is a foreign occupant / the front-end port under the dev profile).
- **`vite.config.ts:9` — NO HUNK, verified unchanged.** Inertness in my own words from the live read:
  the proxy only serves requests the browser sends to the Vite dev server's own origin; the dev client
  we ship builds every API URL from the absolute `VITE_API_BASE` (baked at build time), so requests go
  straight to the absolute host and never traverse this proxy. Retargeting the proxy to `backend:8000`
  would encode a dev-topology assumption (Vite running inside the compose frontend container on the
  same netns as `backend`) that this slice does not establish — M17 family, left untouched.

## G2 — enforcement split documented + pinned

- **Router docstring (`router.py:52`)** — added a paragraph stating that `estimated_cost` is consumed
  *here* for the pre-call refusal and is **not forwarded** (only `*args, **kwargs` travel, so the
  adapter always receives its `estimated_cost` default), with the reason: one enforcement point per
  routed call. Points at the pin test by name.
- **Adapter docstrings (`opencode_go.py`)** — `extract_items` gained a docstring and `extract_text`'s
  docstring gained a paragraph: the guard enforces for **DIRECT invocations only** (tests, eval
  harnesses) and is **shadowed but harmless** on the routed path, where the router + reader own
  enforcement. **Zero logic hunks** — the guard bodies are byte-identical; the diff is docstrings only.
- **Pin test: NEW `test_router_consumes_estimate_and_shadows_adapter_guard`** in
  `backend/tests/test_provider_gateway.py`. Chosen over extending
  `test_budget_exceeded_refuses_precall_with_zero_invocations` because the existing test covers only
  half (a); a distinct name documents half (b), and the adjacent placement keeps router enforcement in
  one file. A **local recording double** (`_RecordingProvider`, no network, no key, no adapter
  construction) records the `estimated_cost` it receives:
  - (a) `estimated_cost=5.0` over a `cost_budget=1.0` → `BudgetExceededError`, `invocations == 0`;
  - (b) `estimated_cost=0.5` → provider invoked once with `seen_estimates == [0.0]`, proving the router
    consumed-and-dropped the estimate — the documented shadowing, in executable form.
- **No FAIL-then-PASS leg exists** — nothing failed before this slice. Stated honestly, not
  manufactured. Guards: the pin test green and the suites green.

## G3 — suite + lint + build + hygiene (NO deploy)

| Gate | Command | Result |
|---|---|---|
| Pin | `pytest tests/test_provider_gateway.py -q` | **6 passed** (0.36s) |
| Backend suite | `pytest -q` | 2 failed / 236 passed (19.60s) |
| Backend lint | `ruff check .` | All checks passed! |
| Frontend test | `npm test -- --run` | 21 files / **152 passed** (6.10s) |
| Frontend lint | `npm run lint` | clean |
| Frontend build | `npm run build` (tsc && vite build) | OK, 1960 modules (1.73s) |

- **The only reds** are `test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier`
  and `::test_ocr_has_text_boxes_and_mean_confidence`. **Base-proven:** a detached worktree at BASE
  `26149974869966774e41c3c8ced09c09671aca4d` ran the same file and produced the **identical 2 failed /
  5 passed** (`SG-060_verify.log` [8]). Not new; no destination owed.
- **NO DEPLOY, with reason:** this slice changes no behaviour — two docstrings, one dev-fallback string,
  one test. `PG-PR-04` binds packets demanding live proof of *new code*; there is none. The fallback
  literal is constant-folded from prod bytes when `VITE_API_BASE` is baked (SG-059 F-SG059-2), so the
  next scheduled rebuild carries it automatically. Full sweep WAIVED per `PG-DP-02`, substitute named:
  suite + lint + build + the pin test.
- **Prod DB untouched** by construction: no app boot, no `DATABASE_URL` change, no migration; every
  test uses scratch temp SQLite via `TestClient`. **No migration. Dep list unchanged** (no
  `package.json` / `pyproject.toml` hunk). **Secret scan n/a** — no secret-bearing file touched.
  **No ignored file staged** (`PG-SC-10`): only the four tracked files are modified. **Nothing pushed
  to `storagegenie-evidence`.** **No vacuous pass** — the pin test invokes the real
  `router.execute`/`getattr` path with a real double and asserts on observed invocations.
- **Served bundle NOT rebuilt by this slice** — no deploy ran and the container/image is untouched; the
  local `frontend/dist` artifact was regenerated by the mandated build gate only and is gitignored
  (not staged).
- **`PG-SC-09` — the world where documenting-not-forwarding is wrong:** a future direct caller assumes
  that going *through* the router gives them the adapter's monthly-cap protection as well. It does not:
  the router only checks its own `cost_budget`, and a routed call never carries the estimate into the
  adapter, so the adapter's monthly guard is inert there. **Why the slice still ships:** the docstrings
  now state exactly which layer protects which path (router `cost_budget` + reader ledger-durable
  monthly check on the routed path; adapter guard on direct calls), and the pin test locks that
  statement in executable form, so the next reader cannot re-derive the "dead path" confusion.

## G4 — worklog and report

- `docs/worklogs/SG-060.log`, `docs/worklogs/SG-060_report.md`, `docs/worklogs/SG-060_verify.log`.
- First token `SG-060`; elapsed-vs-budget per leg: pin+ruff ~2s/120s, backend suite ~20s/600s,
  frontend ~9s/600s, overall ~140s/1800s (early-close 1200s not reached). No command killed.
- **MODEL unknown, effort medium** — from process argv, not a prompt identity line.
- **Spend: real $ $0.000000 actual vs $0 bound** (zero provider calls; no metered route touched).

## Receipt — notes ref

(pending execution; raw output pasted on completion)

## UNCLEAR

- **FIRST READ:** whether `estimated_cost` was being forwarded — the packet's claim that the adapter
  "always sees 0.0" was checkable only at `router.py:67`; the live read confirmed `*args, **kwargs`
  excludes it, so the claim holds.
- **DURING EXECUTION:** whether extending the existing router budget test would be cleaner than a new
  one; chose new for a distinct name and a self-contained (a)+(b) assertion, and said why.
- **REMAINING:** none architectural — the only open reds are the two base-proven `test_signals.py`
  environmental failures, outside this slice's ceiling and unchanged by it.

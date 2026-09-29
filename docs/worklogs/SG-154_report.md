# SG-154 — close-out deploy rider (standing directive: rebuild + exactly ONE recreate + verify)

**Dispatch:** SG-154 · **Coder:** opencode · **Model:** `opencode-go/deepseek-v4.1-flash` · **Effort:** `high`
(from process arguments — `/proc/1191616/cmdline` = `opencode run --auto --dir /home/andrei/StorageGenie
--model opencode-go/deepseek-v4.1-flash --variant high`; wrapper `bash /usr/local/lib/dispatch/run-coder SG-154`).
**Work dir:** `/home/andrei/StorageGenie` · **Origin:** `git@github.com:Andovol/StorageGenie.git`.
**BASE ref requested:** `origin/automation` → **resolved commit:** `b16d0670db5f1803bc385256e23801a4f71ac311`
(== local HEAD at start, worktree clean). **WORK_HEAD:** the evidence commit (SG-154_verify.log).
**Authoring date (metadata):** 2026-09-29. Live clock reads below.
**Type:** DEPLOY RIDER. Production restart authorized by the standing close-out directive (`AGENTS.md` Close-out
row; `G-K2` covered, not new). **Zero product hunks expected — and zero produced.**

**Contract echo (verbatim):** `0.40.0` — source path `/home/andrei/storagegenie-contract/VERSION`.
Contract HEAD `f26dbd32e3c4bd7cf878333fba719a6ca1d10c3c`; `RULES.md` sha256
`5b65629377bbac9e40bfa7e2f4d4e42a5667b3a08ec786beb47c6a677d9ac33c` (== the installed payload hash recorded
in `AGENTS.md` for 0.39.0+0.40.0). **Recorded == published (D4).** `.rules-cache/` is absent on the host
(SG-145 F-SG145-1); the live contract checkout is the source path.

**Money posture (REAL $):** **$0.000000 USD actual**, **zero metered calls** — no USD-metered provider/model
path exists anywhere in this slice (image rebuild + container recreate + local reads). Per-leg budget table below.

---

## What this slice did

Served everything committed since the last live deploy (image `76917528…` at SG-143): SG-148 offline-SQL chain
(migration offline branches only), merge batches A–D (CORS lockdown, evidence bulk paths, schemas tests,
independents) — all rated 98/99 with receipts. The slice is **rebuild + exactly one recreate + verify only**.
No product, test or config byte was edited: the diff ceiling is the three `docs/worklogs/SG-154*` files.

How the code became live (`PG-PR-04`): `BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend`
(one rebuild) + `docker compose up -d --no-deps backend` (exactly one recreate) + verify.

---

## G0 — rebuild (one) + exactly one recreate

**BEFORE (read-only, 2026-09-29T15:13:06Z):**

| field | value |
|---|---|
| container | `55d398ed7625cf637f587d863d60c0d114355ca9312b554becdfccd59e71a4de` |
| image | `sha256:76917528f28bc92a89029dc7ef08bb94cdf8682852a003bd7c53470343601303` |
| RestartCount / Created | `0` / `2026-09-29T09:49:22.387840497Z` (SG-143 generation) |
| health | 6× 200 `{"status":"ok","db":"ok","storage":"ok"}` |
| gate | http:80 **301** / https:443 **401** |
| alembic | `20260924_sg114_relation (head)` |

**BUILD (exactly one):** `BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend` → `BUILD_EXIT=0`,
**12 s** (`15:13:52Z → 15:14:04Z`). Image **`sha256:76917528…` → `sha256:c6fc45abbd1e7725ccf6ef33027ce63fa0bd6192e6f39ea3094b83ff4acdee4f`** (new).
The `BUILDX_CONFIG` relocation is the documented EROFS-sandbox workaround (SG-132/SG-142/SG-143 precedent).

**RECREATE (exactly one):** `docker compose up -d --no-deps backend` → `REC_EXIT=0`, **1 s**
(`15:14:18Z → 15:14:19Z`), one `Recreate/Recreated/Starting/Started`.

| field | BEFORE | AFTER |
|---|---|---|
| container id | `55d398ed7625…` | **`596e7d7a35d2c0ec6483cb2a418419394c0ba383ea84a73d427f823f7c1a5f40`** |
| image | `sha256:76917528…` | **`sha256:c6fc45ab…`** |
| RestartCount | 0 | 0 |

`PG-EV-08` satisfied: BEFORE ids/health/counts/alembic captured before the change; the recreate is proven by the
**container-id change** (`M42`), never by `RestartCount` (a recreate replaces the container; the counter resets 0→0).

---

## G1 — verify live (state change by post-state, `PG-EV-02`)

- **Health ×6 exact** through `{{HEALTH_CMD}}` (`curl -s http://127.0.0.1:8003/v1/health`) at `2026-09-29T15:14:46Z`:
  all six bodies `{"status":"ok","db":"ok","storage":"ok"}` at HTTP 200 (quoted in the verify log).
- **Gate:** http:80 **301** (`https://storagegenie.dynv6.net/`) / https:443 **401** — both unmoved.
- **Alembic:** `20260924_sg114_relation (head)` == BEFORE (unmoved; no migration run).
- **Counts — delta 0 on every table:** 28/28 BEFORE == AFTER (full dynamic set; see F-SG154-1). None moved.
- **CORS live proof, ZERO writes** (OPTIONS preflight only; no PATCH/POST/PUT/DELETE sent):
  - `OPTIONS /v1/assets` `Origin: http://localhost:5173` `Access-Control-Request-Method: PATCH`
    `Access-Control-Request-Headers: If-Match` → **200**, `allow-headers: …If-Match…` (lockdown list live).
  - `OPTIONS` with `Access-Control-Request-Method: TRACE` → **400** `Disallowed CORS method`.
  - `OPTIONS` with `Access-Control-Request-Headers: X-Evil-Header` → **400** (was 200 pre-lockdown).
  - `allow-methods: GET, POST, PUT, PATCH, DELETE, OPTIONS` (old `*`-expanded list included `HEAD`; now gone).
  - (Actual HTTP `TRACE /v1/assets` → 405 Method Not Allowed, read-only — see F-SG154-3.)
- **Bundle note:** served entry **UNCHANGED** — `index-CTQCofuO.js`
  `d9dbdef301177ad9f82f0b1dd290336eb5e10dd47b6d68836eebf14d3cbeb12c` (318152 B) and `index-DO0gjGV6.css`
  `37b25dbd…` are byte-identical BEFORE and AFTER. Direction **stated**: unchanged, because
  `git diff 66497c6..HEAD -- frontend/` is EMPTY (F-SG154-2). The packet predicted it would move; it did not.
- **Pages:** `/capture` `/inbox` `/catalog` → **200** each through the fresh server.

---

## Findings (premise corrections; reported, not bent)

- **F-SG154-1 — the "24-count baseline" is stale.** The live SQLite schema has **28 user tables + 1 view**
  (`asset_fts_content`). The 24-table list predates SG-100 (`enrich_snapshot`), SG-113 (`location`,
  `asset_location`) and SG-114 (`asset_relation`). Counting only 24 would have narrowed the check; the full
  28-table set was enumerated at runtime and compared. All delta 0.
- **F-SG154-2 — bundle direction was the opposite of the packet's premise.** The packet says "backend changed →
  it moves". Measured: the served JS+CSS are **byte-identical**. Reason: no `frontend/` commit exists between the
  SG-143 build (`66497c6`) and HEAD, so the deterministic Vite output is unchanged. Direction stated explicitly.
- **F-SG154-3 — TRACE semantics.** The packet's "TRACE → 400" is the **preflight** form
  (`Access-Control-Request-Method: TRACE` → 400 `Disallowed CORS method`, SG-150 precedent). A literal HTTP
  `TRACE` request reaches the router and returns **405 Method Not Allowed**. Both were captured (read-only).
- **Note (not a finding):** the BEFORE header line "worktree: 1 modified entries" is the verify log being
  created by `tee` at that instant (self-reference). BASE was clean before capture; no pre-existing dirt.

**No vacuous pass:** every criterion drives a real observation — the rebuild is evidenced by a changed image ID
(one build), the recreate by a changed container ID (`M42`), health by six quoted bodies, counts by a full
28-table re-read on both sides, and CORS by live OPTIONS preflights with zero writes. Nothing was averaged away,
no gate skipped, no mutating live request sent.

---

## Acceptance criteria — question answered

| criterion | question | result |
|---|---|---|
| rebuilt | is the image ID new (one build)? | YES — `76917528…`→`c6fc45ab…`, exactly one build, `BUILD_EXIT=0` |
| recreated | container ID new, exactly one generation (`M42`)? | YES — `55d398ed…`→`596e7d7a…`, one `Recreated` line |
| live | health ×6, gate 301/401, alembic `sg114`, counts delta 0, preflight green, zero writes? | YES — all green; zero writes |
| clean | is the diff exactly worklogs? | YES — `docs/worklogs/SG-154.{log,report.md,verify.log}` only |

---

## Budget — actual vs bound, per leg (units stated)

| leg | bound | actual |
|---|---|---|
| recon + BEFORE capture | 120 s | ~60 s |
| rebuild (rebuild class) | 600 s | **12 s** |
| recreate | 120 s | **1 s** |
| AFTER verify (health/gate/counts/preflight) | 120 s | ~30 s |
| G2 worklog + receipt | 300 s class | see below |
| **overall** | **2400 s** (lane `RUN_BUDGET_S=2100`) | **~200 s** |

No command hit its bound; nothing was killed; no command needed a retry. **Spend: REAL $0.000000 USD + zero
metered calls.**

---

## Receipt

Push of the work to `automation`, receipt note on the notes ref, mapped-ref fetch and pasted `show` output are
recorded in `docs/worklogs/SG-154.log` (final receipt block) after execution. No push to `storagegenie-evidence`,
no `{{RECEIPT_CMD}}`.

---

## UNCLEAR

- **FIRST READ:** whether "24 counts" was a literal table list or shorthand for "all tables". Resolved by
  re-reading the live schema (28 tables) and counting all of them; disclosed as F-SG154-1.
- **DURING EXECUTION:** whether the unchanged bundle was a deploy failure. Resolved by checking
  `git diff 66497c6..HEAD -- frontend/` (empty) — the build is deterministic and no frontend byte changed; the
  new image is proven live by the CORS lockdown behavior, not by the bundle.
- **REMAINING:** the owner's visual verdict on the deployed UI (hue screenshots of Inbox/Capture/Catalog) and
  the still-open desk items (F-SG150-2, Desk #69/#70) remain outside this rider's scope.

**RECOMMENDED-NEXT:** hue screenshots (Inbox / Capture / Catalog post-deploy) for the owner verdict.

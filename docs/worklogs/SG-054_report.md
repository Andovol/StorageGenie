# SG-054 — shell unification + sourceless fallback icon + table overflow + count grammar

**Dispatch-ID:** SG-054 · **Coder:** opencode · **Effort:** medium (read from process args: `opencode run --auto --dir /home/andrei/StorageGenie --variant medium # SG-054 …`) · **Model:** `unknown` (no model id on argv; CLI default per policy — not guessed from any identity line).
**Contract:** 0.27.0. **Spend:** `$0` metered (AI OFF, no provider calls).
**Work dir:** `/home/andrei/StorageGenie` · **origin:** `git@github.com:Andovol/StorageGenie.git`.

- **BASE REF requested:** `origin/automation`; **resolved commit:** `9fb738b9df29fef696a9ed74f607e2a41b8b14a4` (`SG-054 packet + feedback triage + D71-D73 approvals (L2)`).
- **WORK_HEAD:** the commit carrying these three worklogs — **stated in the delivery message** (it cannot be stated inside a file that is itself part of that commit, same as SG-053). The receipt note is attached to it LAST; no commit follows.
- **Slice wall-clock:** start `2026-09-16T18:29:02Z`; report frozen `2026-09-16T18:36:00Z` (~7 min / 420 s vs 2100 s overall cap).

## 1. Starting tree (clean expected; dirt = STOP first)

```
$ git status --porcelain=v1 -b
## automation...origin/automation
$ git rev-parse HEAD ; git rev-parse origin/automation
9fb738b9df29fef696a9ed74f607e2a41b8b14a4
9fb738b9df29fef696a9ed74f607e2a41b8b14a4
```
Clean and level: no STOP. The final tree carries exactly 6 modified product/test files + the 3 worklogs; no new files outside `docs/worklogs`.

## 2. Premises re-verified in-slice (quoted reads, `PG-IC-09`)

- **Legacy nav** `App.tsx:11-47`: `Nav()` background at `:22` is `background: "#f9fafb"` hard-coded; six `NavLink`s at `:26-43` (Catalog/Capture/Settings/Inbox/Planning/Chat) + wordmark `Link` `:23-25`; `Phase 0 · local-first` `:44`. Root `:51` `background: "white"`. **Matches.**
- **Token shell** `AppShell.tsx:44-63` (`bg-background text-foreground`, sticky top `:45`) + `AppHeader.tsx:37-112` (`bg-card border-border`); count pill `:56-63` with `aria-label="Total loaded items: N"`, `title="Items loaded on this page, not the household total"`, text `Total: {loadedCount} items`. **Matches.**
- **Empty media branches:** `ProductCard.tsx:136-144` renders `null` when `!media || broken`; `TableThumb` `ProductGrid.tsx:71-97` same. **Matches.**
- **Table:** `COLUMNS` `ProductGrid.tsx:41-49` fixed widths (56+200+140+130+120+110+48 = 804 px); bare `<table>` at `:113`, no scroll wrapper. **Matches.**
- **lucide-react** `1.46.0` already installed (`frontend/package.json:14`). Glyph export established by grep of the installed package **before** choosing: `dist/lucide-react.d.ts` has `declare const Package`; `dist/esm/lucide-react.mjs` maps `index_Package as Package`. Chose **`Package`** (parcel/box). No new dependency.
- **Pills** (G3 check): `CatalogToolbar.tsx:81-92` row is `display:flex; flexWrap:"wrap"` — pills already wrap, no page-level pill overflow. **No pill restyle** (reported either way as required).

## 3. Route enumeration (G1)

Routes declared `App.tsx:54-61`: `/`, `/capture`, `/assets/:id`, `/settings`, `/inbox`, `/planning`, `/chat`, `/review/:candidateId` (8). **Criterion:** `pathname === "/"` renders no legacy `Nav`; every other pathname renders it byte-identical. Implementation `App.tsx:51` `{pathname === "/" ? null : <Nav />}`. Difference found: **none** — all 8 routes are covered by this one conditional (`/assets/:id` and `/review/:candidateId` fall to the `else`). App-level test proves `/` (one wordmark, no `Phase 0 · local-first`) and `/capture` (nav present + Capture page).

## 4. Goal outcomes

- **G1** — catalog route renders the token shell as the single header; legacy `Nav` untouched/unchanged for the other seven routes. `App.tsx` diff is the conditional hunk only.
- **G2** — `Package` glyph tile for sourceless/broken media in **both** densities, `data-testid="product-fallback-icon"`, `className="text-muted-foreground"`, `aria-hidden`, size 28 (grid well) / 20 (table thumb). Failed-state visuals untouched: the fallback is gated `!failed` in the grid well, so the `failed` badge / `AlertTriangle` / rose hairline are exactly as before (`catalog.test.tsx` failed-state test still green).
- **G3** — `<table>` wrapped in a labelled scroll region `ProductGrid.tsx:120-125`: `<div data-testid="table-scroll" role="region" aria-label="Product results table" style={{overflowX:"auto"}}>`. Columns stay reachable by container scroll; page no longer has a fixed 804 px table child. Pills not restyled (already wrap).
- **G4** — `AppHeader.tsx:62` `Total: {loadedCount} {loadedCount === 1 ? "item" : "items"}`. `aria-label` (`Total loaded items: N`) and `title` semantics unchanged. `PG-SC-11` hits named: `shell.test.tsx:176` (pre-existing, `Total: 4 items` — N=4 plural, still correct, left as-is), `shell.test.tsx:320` (new singular), `shell.test.tsx:321` (new: `Total: 1 items` asserted absent). No other count-text assertion exists in the tree.
- **G5** — see §5.
- **G6** — see §6 (deployed and proven live, one packet-premise finding).
- **G7** — this file, `SG-054.log`, `SG-054_verify.log`.

## 5. Tests / FAIL-then-PASS / mutation (`PG-EV-01`, `PG-EV-09`, `PG-EV-02`)

Raw runs are committed to `SG-054_verify.log`.

- **Pre-change (new tests, old code): 6 failed / 131 passed / 21 files, 4.07 s, exit 1.** The 6 failures are exactly the new/changed assertions:
  1. `catalog` broken-image → fallback glyph absent;
  2. `catalog` fallback glyph shows only for sourceless (fails on the sourceless half);
  3. `catalog` sourceless table-thumb fallback absent;
  4. `catalog` `table-scroll` container absent;
  5. `shell` one-wordmark on `/` (got 2 wordmarks);
  6. `shell` `Total: 1 item` absent (code said `Total: 1 items`).
- **Green (post-change): 21 files / 137 passed, 3.89 s, exit 0.** Re-confirmed after all mutations were reverted (137 passed).
- **Lint:** `eslint src` exit 0 (2 s). **Build:** `tsc && vite build` exit 0 (4 s).
- **Mutation proof (post-change, each caught singly, reverted clean, raw in verify.log):**
  - **M1 fallback branch** `(!media || broken) → (!media && broken)` → **caught by 2** tests (broken-image + sourceless-fallback).
  - **M2 grammar branch** ternary → hard-coded `items` → **caught by 1** test (singular).
  - **M3 scroll wrapper** `overflowX:"auto" → "hidden"` → **caught by 1** test (scroll container).
  After each revert, `git status` shows only the 6 intended modified files.
- **Vacuity note:** the "vanishes when media exists" half of the fallback test cannot fail-first (there was never a fallback); it is a *guard* against over-rendering. To avoid a vacuous pass it is bundled in the same test whose second half (sourceless → glyph) genuinely fails pre-change. Similarly the scroll test's ancestor-walk is a structural assertion (jsdom cannot measure layout); it is non-vacuous because the `table-scroll` element itself is absent pre-change.

## 6. Live deploy (`PG-PR-04`, `PG-EV-08`, `PG-DP-03`; authority D71)

Raw before/after in `SG-054_verify.log`.

**BEFORE:** health `{"status":"ok","db":"ok","storage":"ok"}`; served asset `assets/index-CuxlcH9v.js`; `f9fafb` present; blessed counts **exactly** `household=1, user=2, asset=1 Toothpaste, evidence=1, assertion=3, audit_event=3` (== packet, no `PG-IC-08` stop); 8003 loopback-only; gate 301 (http) / 401 (https); container `244465492ac0`, image `sha256:86f7436d5a61`.

**REBUILD + UP:** `docker compose build backend` first failed at the **buildx client cache** (`/home/andrei/.docker/buildx/activity/...: read-only file system`) because this Coder session runs inside the dispatch systemd sandbox (`ProtectSystem=strict`, `ProtectHome=read-only`). The wrapper's `confine()` leaves `XDG_RUNTIME_DIR=/run/user/1000` read-write and the **rootless** docker endpoint `unix:///run/user/1000/docker.sock` reachable (it only makes `/var/run/docker.sock` and `/run/docker.sock` inaccessible). Redirected only the client cache: `BUILDX_CONFIG=/run/user/1000/sg054-buildx docker compose build backend` → exit 0, 9 s, **same rootless daemon, no sudo, no privilege escalation**, base layers served from the local builder cache (no registry pull, no new runtime). Image `86f7436d5a61 → b619f62b5336`. `docker compose up -d backend` recreated the container `244465492ac0 → dac0bf5c60a4`.

**AFTER:** health exact; served asset **CHANGED** to `assets/index-DQSbiXPE.js`; new code proven live in the served bundle — `product-fallback-icon` `0→2`, `table-scroll` `0→1`; blessed counts re-read **EQUAL**; 8003 loopback-only; gate 301/401; idempotent `up -d` → `Running`, **same container id**, `RestartCount=0`. Full e2e sweep **waived** per `PG-DP-02` (restart-gated slice); substitute = the targeted checks above.

## 7. Findings / disagreements

- **F-SG054-1 (packet premise defect — headline).** G6 requires the *"legacy marker ABSENT from the served bundle"* (the "legacy hard-coded value" is `#f9fafb`, per `docs/feedback/2026-09-16-live-UI-feedback.md:15`). This is **unsatisfiable as written** together with G1, which mandates the legacy nav stay **byte-identical on every non-catalog route**. A Vite SPA bundle is whole-app: the `Nav` component (and its `#f9fafb` literal) remains compiled in because seven routes still render it. Measured: `f9fafb` **before=1, after=1** (the same single occurrence). The Architect's model — that removing the catalog's nav would drop the value from the build — does not hold for a route-conditional runtime render. This is reported per *"a difference is a finding, not an obstacle"* and *"correcting me is worth more than agreeing"*; it is **not** treated as a blocking constraint, because the underlying requirement (G1: one header on `/`) is implemented and test-proven, and the rest of G6 passes. **Substitute live evidence that the new build is actually served:** asset hash changed `index-CuxlcH9v.js → index-DQSbiXPE.js`, and new-only markers `product-fallback-icon` (0→2) and `table-scroll` (0→1) now appear in the served bytes. A browser-level DOM check of `/` is not possible on-box (no browser; network limited to loopback) — see UNCLEAR #1.
- **F-SG054-2 (pre-existing, out of scope).** Foreign `127.0.0.1:8000` still bound, serving `404` at `/` (SG-053 `F-SG053-1`). Not ours; our publish is `127.0.0.1:8003:8000` only (`docker-compose.yml:8`). No action.
- **F-SG054-3 (sandbox adaptation).** `docker compose build` cannot write its buildx client cache under this dispatch's read-only `~/.docker`; worked around by pointing `BUILDX_CONFIG` at the writable `XDG_RUNTIME_DIR`, same rootless daemon. No privilege was sought or obtained. Worth the Architect's awareness for future deploy slices.
- **Doc nit.** `AGENTS.md` maps `{{HEALTH_CMD}}` to `http://localhost:8000/v1/health`; on this box port 8000 is the foreign service (above) and the StorageGenie health endpoint is `http://127.0.0.1:8003/v1/health` (compose publish). Health was taken from 8003.

## 8. Guards invoked (0.27.0) — evidence

| Guard | Status |
|---|---|
| `PG-EV-01` gate-seen-failing | MET — 6 failing pre-change raw; each mutation caught singly. |
| `PG-EV-02` artifact-exists | MET — rendered DOM (tests), served bundle bytes, committed logs; never exit codes. |
| `PG-EV-05` property-not-command | MET — one wordmark on `/`; glyph shows with no media in both densities; page has no fixed-width table child; `1 item` vs `N items`. |
| `PG-EV-08` before-capture | MET — before state captured read-only before any write. |
| `PG-EV-09` both-runs-committed | MET — pre-change + green + mutations raw in `SG-054_verify.log`. |
| `PG-SC-05` exclude-by-rule | MET — `git diff --name-only \| grep '^backend/'` = 0; no backend file touched. |
| `PG-SC-10` no-ignored-commit | MET — only intended files; `.cache/`, `data/`, `.env` stay ignored and unstaged. |
| `PG-SC-11` end-relative-assertions | MET — count-text hits named in §4. |
| `PG-IC-01` cross-product | MET — G6 restart shares no condition with any remediation step; no blanket exclusion. |
| `PG-IC-07` no-fixed-dates | MET — relative dates via injected `nowMs`; authoring date is the only fixed date. |
| `PG-IC-09` premises-live | MET — every premise re-read live in-slice, quoted in §2. |
| `PG-PR-04` code-becomes-live | MET — compose rebuild+up; served bundle changed and carries new markers. |
| `PG-DP-02` no-sweep-in-restart-slice | MET — e2e sweep waived; targeted checks named. |
| `PG-DP-03` live-repro | MET — before/after on the live box, raw committed. |

## 9. Acceptance criteria

- [x] Starting tree clean and quoted; premises re-verified with quoted reads incl. installed lucide glyphs.
- [x] One wordmark on `/`, legacy nav intact elsewhere; no restyle outside the ceiling (6 files, all in-scope).
- [x] FAIL-then-PASS honest: pre-change failing run + green run + 3 mutation runs, all raw committed; live before/after raw committed.
- [x] Suite + lint + build green; secret scan 0 matches on the diff; no `backend/` diff; no migration; dep list unchanged (`package.json`/`package-lock.json` untouched); blessed counts equal; nothing to `storagegenie-evidence`; no vacuous pass (§5).
- [~] G6 "legacy marker ABSENT" — **unsatisfiable** as written (F-SG054-1); substitute evidence provided.

## 10. Budget (actual vs cap, per leg, units)

| Leg | Actual | Cap |
|---|---|---|
| Pre-change suite | 4.07 s | 600 s (suite+lint+build) |
| Green suite | 3.89 s (+4 s re-confirm) | 600 s |
| Lint / Build | 2 s / 4 s | 600 s |
| Mutations (3 × single-file) | a few seconds each | — |
| Host build / up / re-up | 9 s / 1 s / 1 s | 900 s |
| Overall wall-clock | ~420 s | 2100 s (early-close 1500 s) |

## 11. Receipt note

Work is pushed to `automation` with the worktree clean (`CO-55`). **No** push to `storagegenie-evidence`, **no** `{{RECEIPT_CMD}}` (this packet's M20-corrected block). A note was added on WORK_HEAD under `refs/notes/storagegenie-coder-reports`, then pushed, then verified against the explicitly fetched refspec (`git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>`). Per the convention used by SG-053, that `show` output is pasted verbatim **in the delivery message** — it cannot live inside this file, which is itself the noted commit. `note=yes`.

## UNCLEAR

- **FIRST READ:** G6's "legacy marker ABSENT from the served bundle" vs G1's "legacy nav stays byte-identical elsewhere" read as mutually exclusive for an SPA — I could not satisfy both, and chose G1 (the real user-facing requirement) while reporting the mismatch (F-SG054-1).
- **DURING EXECUTION:** whether redirecting `BUILDX_CONFIG` into the writable `XDG_RUNTIME_DIR` was the Architect's intended deploy path under the dispatch sandbox, or whether deploy slices are expected to run outside the confine; I judged it a cache-path relocation (same rootless daemon, no privilege), not a route around a denial.
- **REMAINING:** the definitive live proof of "one wordmark on `/`" is a browser/DOM render; on-box there is no browser and network is loopback-only, so that property is proven by the App-level React test plus the served-bundle marker evidence, not by a live DOM fetch.

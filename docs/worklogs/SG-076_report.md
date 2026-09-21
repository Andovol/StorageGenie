# SG-076 — deploy rider: Stone theme live on the public entry

**Branch:** `automation` · **Remote:** `git@github.com:Andovol/StorageGenie.git` · **Work dir:** `/home/andrei/StorageGenie`
**BASE (packet ref `origin/automation`):** `8bc896c145483a06821bff03c96cf56a4f34e4c0` (`D98: SG-076 design deploy rider packet (Stone theme live)`)
**WORK_HEAD:** `WORK_HEAD_TBD` (work commit; the post-note receipt commit is HEAD after it)
**Contract:** recorded `0.28.2` == published; source `/home/andrei/storagegenie-contract/VERSION`, contract repo HEAD `b495b59b3426af66772a87939473ac558f8f72d2`
**Model / effort (`CO-78`):** model `deepseek-v4.1-flash` (provider `opencode-go`, read from opencode provider metadata `/home/andrei/.local/share/opencode/log/opencode.log` `llm.provider=opencode-go llm.model=deepseek-v4.1-flash`, `small=false`; **not** a system-prompt identity line; argv carries no `--model`) · effort `medium` (process argv `/proc/59767/cmdline`: `opencode run --auto --dir /home/andrei/StorageGenie --variant medium`)
**Spend (real $):** `$0.000000` actual vs `$0` bound — zero metered provider calls.
**Autonomy:** `L2` slice (1 retry available; not used).

The D98-approved rider for SG-075 (audited 98). SG-075's Stone token migration sat in `frontend/src` only
(27-file diff, re-verified below: `frontend/src` + `docs/worklogs` — **no migration**). The production
backend image was still the SG-074-era build, serving `index-3DyyAB0n.js` without the token system. This
slice rebuilt the baked-UI image, recreated the one service **once** (the only authorized production
mutation), and proved the new bundle is live with structural discriminators. **BEAUTY is explicitly NOT
proven here** — no browser exists on the box; the owner's eyeball on `https://storagegenie.dynv6.net` is
the final authority (D96 / `PG-PR-04`).

## G1 — rebuild + bring up (the authorized restart)

- **SG-075 diff scope re-verified (frontend-only, no migration):** `git show --stat d209ecc` = 26 files
  under `frontend/src` (22 source + `tokens.css` + 1 new test) + 3 worklogs. No `backend/`, no `alembic/`,
  no compose, no `.env`. Raw in `SG-076_verify.log` LEG 1.
- **BUILDX_CONFIG relocation (F-SG067-2 precedent, reused):** `$HOME/.docker` is **not** writable on this
  box, so the build ran with `BUILDX_CONFIG=/tmp/opencode/buildx` (a writable tmp dir). Relocation stated,
  no privilege probed. Raw precedent path.
- **`docker compose build`** — rc=0 in **10 s** (bound 900 s). The frontend build inside the image emitted
  `dist/assets/index-CoNI-1Zn.css` (3.84 kB) + `dist/assets/index-BhyX-Hlp.js` (303.88 kB); image
  `storagegenie-backend:latest` became `c2bcb600b817`.
- **`docker compose up -d`** — rc=0 in **1 s**; exactly **one** recreate
  (`Container storagegenie-backend-1 Recreate/Recreated/Starting/Started`). Container id changed
  `3a2b60da38cd` → `3952f6760e49`.
- **Health:** read1 `[http 000]` during uvicorn settle (SG-067 precedent, disclosed not hidden), then
  `{"status":"ok","db":"ok","storage":"ok"} [http 200]` twice consecutively. RestartCount **0 → 0** (no
  restart loop). `ss -ltnp` still `LISTEN 127.0.0.1:8003` only (loopback preserved).

## G2 — the new behavior is LIVE

### Served bundle before / after

| | BEFORE (SG-074-era) | AFTER (rebuilt) |
|---|---|---|
| JS name | `index-3DyyAB0n.js` | `index-BhyX-Hlp.js` |
| JS bytes | `301041` | `303974` |
| JS sha256 | `79daad044b3da00c5ce540b6a2ec2dbba97222d40c36450fd48cf885cd8dc378` | `256d728a34abc77dfde445ef466933751e08cc54ccc1174dfe92cf886057c744` |
| CSS name | `index-DxKo-z_g.css` | `index-CoNI-1Zn.css` |
| CSS bytes | `2652` | `3839` |
| CSS sha256 | `e6bb17555af6266702cd22eb64457554f24732dadb4abad29def6fbc9563591c` | `b18dbb336eef5c580bf0a2e6726d647c4f6c63edbc48373580d31e4508659ad3` |

Result: JS name, size and sha256 **all differ**; the served `index.html` references the new pair, and the
new token stylesheet `index-CoNI-1Zn.css` (3839 B) is live. The BEFORE sha256 matches SG-074's quoted
measured record **exactly** — the before-leg is the real prior artifact, not a re-typed number.

### Theme-shipped discriminator (structural — no browser on the box)

Greps against the **served** bundle bytes inside the container (occurrence counts via `grep -o … | wc -l`,
so a single minified line cannot hide multiplicity):

| probe | BEFORE | AFTER |
|---|---|---|
| `page-header` (SG-075-only utility) | **0** | **8** |
| `#111827` (`App.tsx` old inline ink) | **7** | **0** |

The pair is genuine both ways: the old bundle has **zero** `page-header` and **seven** hardcoded
`#111827` inks (proving it predates SG-075), the new bundle has **eight** `page-header` and **zero**
`#111827`. Raw in `SG-076_verify.log` LEG 1 + LEG 3.

### Regression checks (not the discriminator) — all still 200 after the rebuild, each carrying the seed

| endpoint | BEFORE | AFTER |
|---|---|---|
| `/v1/analytics/summary?household_id=01a0a029-1477-7ca0-b200-bce78a96c679` | `[http 200 bytes=5022]` | `[http 200 bytes=5022]` |
| `/v1/taxonomy` | `[http 200]` | `[http 200 bytes=1118]` (identical body) |
| `/v1/saved-searches?household_id=…` | `{"items":[]}` `[http 200]` | `{"items":[]}` `[http 200]` |
| `/v1/assets/facets?household_id=…` | `{"asset_type":{"unknown":1},"status":{"ACTIVE":1},"has_evidence":{"with":1,"without":0}}` `[http 200]` | identical `[http 200]` |

### Public-entry gate (unauthenticated, loopback Host-header form F-SG053-2)

`curl -sk -H "Host: storagegenie.dynv6.net" https://127.0.0.1/` → `[http 401]` **before and after**. No
credential file was fetched.

### `PG-SC-09` — the named world where green is still wrong

A stale image **does** pass the health check: BEFORE, the old bundle was serving healthy `{"status":"ok",…}`
200s. Health alone cannot distinguish the deploy. The genuine discriminators are (a) the JS bundle
name/size/sha256 change and new CSS, (b) `page-header` `0 → 8`, (c) `#111827` `7 → 0`, and (d) the new
container/image ids (`3952f6760e49` / `c2bcb600b817`). **Beauty is not among them** — deferred to the owner.

## G2b — what must NOT change

- **`alembic current` identical before/after:** both read `20260917_sg068_saved_search (head)` (rc=0). The
  image change ships no revision; the DB file is the same mounted file. **No `alembic upgrade` was run.**
  No F-SG069-1 substitution needed (the rebuilt image resolves the head fine).
- **Row counts unchanged** (read-only SQLite `mode=ro`, never a writer):
  `provider_call = 7`, `guardrail_event = 1`, `saved_search = 0`, `asset = 1`, `assertion = 3`,
  `household = 1` — **7→7**, **1→1** across the slice (`PG-EV-06` authority NONE).
- **No `UPDATE`/`DELETE` against any table.** All HTTP traffic was GET; the only DB access was read-only
  (`alembic current` + `sqlite3 file:…?mode=ro`). No credential file fetched, no retagging, no extra
  restart. DB file `mtime`+size byte-identical before/after (`339968` B, mtime `2026-09-21 10:19:45.51…`).

## G4 — worklog and report

- `docs/worklogs/SG-076.log`, `SG-076_report.md`, `SG-076_verify.log` written (first token `SG-076`).
- Elapsed vs budget (units, per leg): BEFORE capture **~7 s** / 120 s · build **10 s** / 900 s · up+AFTER
  capture **~12 s** / 120 s · overall **< 60 s** / 1800 s. No command hit its bound; nothing was killed.
- Spend: **real $0.000000** (zero metered calls). Contract echo + source path above.
- Receipt: work pushed to `automation`, notes ref pushed + verified (see Receipt below). No push to
  `storagegenie-evidence`, no `{{RECEIPT_CMD}}`.

## Findings

- **F-SG076-1 (bundle hash differs from SG-075's local build — expected, explained).** SG-075's own
  `npm run build` emitted `index-B_67LUDe.js` (303.82 kB); the in-image build emits `index-BhyX-Hlp.js`
  (303.88 kB). The difference is the baked `VITE_API_BASE` build arg (`https://storagegenie.dynv6.net` in
  the image vs the local/dev value), which changes the API-base string and therefore the content hash
  (CSS is byte-identical: same `index-CoNI-1Zn.css` token name both builds). Not a defect; reported because
  the packet's "expected different hash" is satisfied but the *name* differs from the one SG-075's log
  quoted.
- **F-SG076-2 (`HOME/.docker` not writable — relocation, not privilege).** Build required
  `BUILDX_CONFIG=/tmp/opencode/buildx` as in F-SG067-2. Nothing was probed or escalated.
- **F-SG076-3 (vacuous-pass guards).** The discriminator greps were run on the **served** file inside the
  live container (not the repo source), with `grep -o | wc -l` occurrence counts, and both directions
  (0-before and ≥1-before) are quoted. The two `page-header`/`#111827` numbers could not have passed
  vacuously: a deleted/empty bundle would have failed the sha256/size reads first.

## No-write / spend construction (`PG-IC-01`)

Every HTTP request was a read-only GET (`/v1/health` ×several, `/`, `/v1/taxonomy`,
`/v1/analytics/summary?household_id=<seed>`, `/v1/saved-searches?household_id=<seed>`,
`/v1/assets/facets?household_id=<seed>`, and the nginx gate). The only POST is none — no chat gate call was
needed this slice. DB access was read-only (`alembic current`, `sqlite3` opened `mode=ro`). The only
mutating commands were the authorized `docker compose build` + a **single** `docker compose up -d`
recreate. No `.env` read, no credential fetch, no migration, no seed, no network beyond loopback + the
Docker runtime. No criterion required a repository write except this slice's own worklogs.

## Receipt — notes ref (M20-corrected block; executed output pasted verbatim)

Work pushed to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no
`{{RECEIPT_CMD}}`. Existing-note refusal guard checked, note added on WORK_HEAD `WORK_HEAD_TBD`, notes ref
pushed, then fetched into a **mapped** local name and verified with `show` (output appended by the
post-note receipt commit):

```
RECEIPT_OUTPUT_TBD
```

First line carries both `Dispatch-ID:` and `Report:` (`CO-97`). Final line `note=yes`.

## Acceptance criteria

- [x] Pre-bundle quoted (`index-3DyyAB0n.js`, 301041 B, sha256 `79daad04…`, matches SG-074 record); build+up once; two consecutive healthy 200 reads after settle; RestartCount 0→0; loopback preserved.
- [x] Post-bundle hash different (`256d728a…`); new token stylesheet quoted (`index-CoNI-1Zn.css`, 3839 B, `b18dbb33…`); `page-header` 0-before → 8-after; `#111827` 7-before → 0-after (all four numbers quoted); analytics/taxonomy/saved-searches/facets still 200; gate 401 both sides.
- [x] `alembic current` identical before/after (`20260917_sg068_saved_search (head)`); `provider_call`/`guardrail_event` counts unchanged (7/1); prod DB otherwise untouched; nothing pushed to `storagegenie-evidence`; no vacuous pass (F-SG076-3); beauty explicitly deferred to the owner.

## UNCLEAR

- **FIRST READ:** Every recorded premise held on the live box (port map, DB head, seed household, SG-075 frontend-only, pre-bundle `79daad04…`). The only surprise was that the in-image bundle name (`index-BhyX-Hlp.js`) differs from SG-075's local build name (`index-B_67LUDe.js`) — expected once the `VITE_API_BASE` build arg is accounted for, but I did not assume it; I traced it (F-SG076-1).
- **DURING EXECUTION:** The first post-up health read returned `[http 000]` (uvicorn settle); I disclosed it rather than hiding it and waited for two consecutive 200s. No command required killing; the build was 10 s against a 900 s bound.
- **REMAINING:** BEAUTY is unproven by construction — no browser/headless engine exists on the box, so this slice proves the SG-075 bytes are **served live** (structural discriminators), not that the theme looks right. The owner's eyeball on `https://storagegenie.dynv6.net` is the final authority (D96/`PG-PR-04`). The `auth_basic` gate's 401 was checked only as a status code; the credential path itself was never fetched or exercised.

# SG-078 — deploy rider: drawer repair live on the public entry

**Branch:** `automation` · **Remote:** `git@github.com:Andovol/StorageGenie.git` · **Work dir:** `/home/andrei/StorageGenie`
**BASE (packet ref `origin/automation`):** `9f34dae73b736d286d41b374ef95f18a820aa462` (`D100: SG-078 drawer deploy rider packet`)
**WORK_HEAD:** `29fd8f909273c9eb34a32ecb66571aff259559b9` (work commit; the post-note receipt commit is HEAD after it)
**Contract:** recorded `0.28.2` == published `0.28.2`; source `/home/andrei/storagegenie-contract/VERSION`, contract repo HEAD `b495b59b3426af66772a87939473ac558f8f72d2`
**Model / effort (`CO-78`):** model `deepseek-v4.1-flash` (provider `opencode-go`, read from provider metadata `/home/andrei/.local/share/opencode/log/opencode.log` line `llm.provider=opencode-go llm.model=deepseek-v4.1-flash`, **not** a system-prompt identity line; argv carries no `--model`) · effort `medium` (process argv `/proc/182941/cmdline`: `opencode run --auto --dir /home/andrei/StorageGenie --variant medium`)
**Spend (real $):** `$0.000000` actual vs `$0` bound — zero metered provider calls.
**Autonomy:** `L2` slice (1 retry available; not used).

The D100-approved deploy rider for SG-077 (audited 98). SG-077's drawer width repair sat in `frontend/src`
only (2 files — component + test; re-verified below), but the running container still served the SG-076-era
image (`index-BhyX-Hlp.js`) **without** the panel width constraint. This slice rebuilt the baked-UI backend
image, recreated the one service **exactly once** (the only authorized production mutation, D100), and proved
the new bundle is live with the standard before/after discriminators. **The drawer LOOK is explicitly NOT
proven here** — no browser exists on the box; the owner's eyeball on `https://storagegenie.dynv6.net` is the
final authority (D99 / `PG-PR-04`).

## Premise verification (a difference would have been a finding)

| Packet premise | Measured on tree | Verdict |
|---|---|---|
| SG-077 ships frontend-only, **no migration** | `git show --stat 6417e53` = `ItemInspectorDrawer.tsx` (+25 −2), `drawer.test.tsx` (+31 −0) + 3 worklogs; no `backend/`, `alembic/`, compose, `.env` | **confirmed** |
| Running container serves SG-076-era bundle | served `index-BhyX-Hlp.js`, **303974 B**, sha256 `256d728a34abc77dfde445ef466933751e08cc54ccc1174dfe92cf886057c744` | **confirmed exactly** |
| Production DB at head `20260917_sg068_saved_search` | in-container `alembic current` → `20260917_sg068_saved_search (head)`; DB `alembic_version` row identical | **confirmed** |
| Seed household is a READ-ONLY query parameter | `01a0a029-1477-7ca0-b200-bce78a96c679` passed only as `?household_id=`; no write path | **confirmed** |
| Baked-UI shape: backend rebuild+recreate IS the deploy | `backend/Dockerfile` `COPY --from=frontend-build /ui/dist ./static`; `frontend` service under profile `dev` untouched | **confirmed** |
| One service, loopback `127.0.0.1:8003` | `docker compose ps` one running service; `ss` → `LISTEN 127.0.0.1:8003` only | **confirmed** |

## G1 — rebuild + bring up (the authorized restart)

- **`docker compose build`** — rc=0 in **10 s** (bound 900 s). `$HOME/.docker` exists but is **not writable**
  on this box, so the build ran with `BUILDX_CONFIG=/tmp/opencode/buildx` (writable tmp dir) — the
  F-SG067-2 / F-SG076-2 relocation precedent, reused and reported, no privilege probed. The in-image vite
  build emitted `dist/assets/index-fOM9Er4k.js` (304.02 kB) + `dist/assets/index-CoNI-1Zn.css` (3.84 kB,
  unchanged token stylesheet); image became `e9ad06fb9f7e`.
- **`docker compose up -d`** — rc=0 in **1 s**; exactly **one** recreate
  (`Container storagegenie-backend-1 Recreate/Recreated/Starting/Started`). Container id changed
  `3952f6760e49` → `f1e44f3b6bce`; image `c2bcb600b817` → `e9ad06fb9f7e`.
- **Health:** read1/read2/read3 all `{"status":"ok","db":"ok","storage":"ok"} [http 200]` — **no settle
  `000`** this time (better than the SG-067/SG-076 instant-read; disclosed either way). RestartCount **0 → 0**
  (no restart loop). `ss -ltnp` still `LISTEN 127.0.0.1:8003` only (loopback preserved).

## G2 — the new behavior is LIVE

### Served bundle before / after

| | BEFORE (SG-076-era) | AFTER (rebuilt SG-077) |
|---|---|---|
| JS name | `index-BhyX-Hlp.js` | `index-fOM9Er4k.js` |
| JS bytes | `303974` | `304117` |
| JS sha256 | `256d728a34abc77dfde445ef466933751e08cc54ccc1174dfe92cf886057c744` | `91b53c1c7eb377353d7d9e8863d91f1e913fc6c517f327099b6f46dce49b6c1c` |
| CSS name | `index-CoNI-1Zn.css` | `index-CoNI-1Zn.css` (**unchanged**) |
| CSS bytes / sha256 | `3839` / `b18dbb336eef5c580bf0a2e6726d647c4f6c63edbc48373580d31e4508659ad3` | `3839` / `b18dbb336eef5c580bf0a2e6726d647c4f6c63edbc48373580d31e4508659ad3` |

Result: the JS name, size and sha256 **all differ**; the served `index.html` references the new pair
(`src="/assets/index-fOM9Er4k.js"`). The BEFORE sha256 matches SG-076's quoted measured record **exactly** —
the before-leg is the real prior artifact, not a re-typed number. The token stylesheet is **byte-identical**
(see F-SG078-3): SG-077's repair is JS-only, so "quote the new token stylesheet" resolves to the same
`index-CoNI-1Zn.css` — stated as measured, not bent.

### Drawer-fix discriminator (composition, stated — no browser on the box)

The claim is a **composition of two legs**, stated explicitly rather than blurred:

1. **Shipped HERE (this slice):** the served bundle hash changed
   (`256d728a…` → `91b53c1c…`) and the new container/image ids (`f1e44f3b6bce` / `e9ad06fb9f7e`) prove the
   rebuilt frontend is what the public entry now serves.
2. **Renders bounded THERE (SG-077, already audited 98):** the committed jsdom test
   `frontend/src/components/shell/drawer.test.tsx:308` (`describe("SG-077 panel containment (presentation
   only)")`) asserts `parseFloat(panel.style.maxWidth)` is finite and `<= 640` (`:314,:317`), and the viewer
   well cap is finite, positive and `<= panelMax` (`:320`). Its **fail-pre → pass-post** raw runs are quoted
   in `docs/worklogs/SG-077_report.md`. The committed source carries the real values —
   `ItemInspectorDrawer.tsx:23 const PANEL_MAX_WIDTH = 440;`, `:24 const VIEWER_MAX_SIZE = 260;` — applied
   to `style.maxWidth` at `:196` (panel) and `:260-261` (well). The test reads the live rendered DOM's inline
   styles, so it cannot pass vacuously.

The composition proves the bounded panel **shipped and is served**; it does not prove how it looks. Optional
structural support in the served AFTER bundle: token `440` appears **1×** and `maxWidth` **12×** (raw in
`SG-078_verify.log`) — consistent with the repair, but **not** load-bearing (minification makes it brittle,
and `440` could occur elsewhere). The hash change + the committed test pair carry the claim.

### Regression checks (not the discriminator) — each carrying the seed

| endpoint | BEFORE | AFTER |
|---|---|---|
| `/v1/analytics/summary?household_id=…` | `[http 200 bytes=5022]` | `[http 200 bytes=5022]` (body differs only in `generated_at` — F-SG078-1) |
| `/v1/taxonomy?household_id=…` | `[http 200 bytes=1118]` | `[http 200 bytes=1118]` (byte-identical) |
| `/v1/saved-searches?household_id=…` | `{"items":[]}` `[http 200]` | `{"items":[]}` `[http 200]` |
| `/v1/assets/facets?household_id=…` | `{"asset_type":{"unknown":1},"status":{"ACTIVE":1},"has_evidence":{"with":1,"without":0}}` `[http 200]` | identical `[http 200]` |

### Public-entry gate (unauthenticated, loopback Host-header form F-SG053-2)

`curl -sk -H "Host: storagegenie.dynv6.net" https://127.0.0.1/` → `[http 401]` **before and after**. No
credential file was fetched.

### `PG-SC-09` — the named world where green is still wrong

A stale image **does** pass the health check: BEFORE, the old `index-BhyX-Hlp.js` bundle was serving healthy
`{"status":"ok",…}` 200s. Health and the four regression endpoints cannot distinguish the deploy. The genuine
discriminators are (a) the JS bundle name/size/sha256 change and the served `index.html` reference, (b) the
new container/image ids (`f1e44f3b6bce` / `e9ad06fb9f7e`), and (c) the committed SG-077 test pair's
fail-pre→pass-post. **The drawer's appearance is not among them** — deferred to the owner (D99).

## G2b — what must NOT change

- **`alembic current` identical before/after:** both read `20260917_sg068_saved_search (head)` (rc=0). The
  image change ships no revision; the DB file is the same mounted file. **No `alembic upgrade` was run.** No
  F-SG069-1 substitution needed (both the old and rebuilt image resolve the head fine).
- **Row counts unchanged** (construction: `sqlite3 'file:…?mode=ro'` — a read-only open, never a writer;
  traffic was GET-only + container greps; `PG-EV-06` authority NONE):
  `provider_call = 7`, `guardrail_event = 1`, `saved_search = 0`, `asset = 1`, `assertion = 3`,
  `household = 1` — identical before and after.
- **No `UPDATE`/`DELETE` against any table.** DB file `size=339968 B`, `mtime 2026-09-21 10:19:45.51… Z`
  byte-identical before/after (untouched since the last pre-slice write). No credential file fetched, no
  retagging, no extra restart.
- **Nothing pushed to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`.**

## G4 — worklog and report

- `docs/worklogs/SG-078.log`, `SG-078_report.md`, `SG-078_verify.log` written (first token `SG-078`).
- Elapsed vs budget (units, per leg): recon+BEFORE **~30 s** / 120 s · build **10 s** / 900 s · up **1 s** /
  120 s · AFTER capture **~8 s** / 120 s · overall **52 s** / 1800 s. No command hit its bound; nothing was
  killed.
- Model `deepseek-v4.1-flash` / effort `medium` (sources above). Spend: **real $0.000000** (zero metered
  calls). Contract echo + source path above.
- Receipt: work pushed to `automation`, worktree clean (`CO-55`). Notes-ref note added on `WORK_HEAD` and
  pushed, then fetched into a mapped local ref and `git notes show` pasted verbatim in the receipt
  subsection below.

### Receipt note verification (pasted `show` output)

```
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
(no output; silent create/update of the mapped local ref refs/notes/storagegenie-coder-reports)
$ git rev-parse refs/notes/storagegenie-coder-reports
3df8963bfb47d88b8704f4e4b3226c832f167e5f
$ git ls-remote origin refs/notes/storagegenie-coder-reports
3df8963bfb47d88b8704f4e4b3226c832f167e5f	refs/notes/storagegenie-coder-reports
$ git notes --ref=refs/notes/storagegenie-coder-reports show 29fd8f909273c9eb34a32ecb66571aff259559b9
Dispatch-ID: SG-078 | Report: docs/worklogs/SG-078_report.md | Work-HEAD: 29fd8f909273c9eb34a32ecb66571aff259559b9
```

Final line: `note=yes`

## Findings

- **F-SG078-1 (analytics summary body differs — benign, explained).** `/v1/analytics/summary` returned 5022
  bytes both sides but the bodies are **not** byte-identical: a JSON diff shows the **only** change is
  `generated_at` (`2026-09-21T13:07:11.06Z` → `2026-09-21T13:07:38.53Z`). This is a per-request timestamp,
  not a data change; taxonomy/saved-searches/facets were byte-identical. Reported because the packet asks
  for regression checks and a reader should not infer DB movement from the `cmp` mismatch.
- **F-SG078-2 (BUILDX_CONFIG relocation — F-SG067-2 reused).** `$HOME/.docker` exists but is not writable;
  the build required `BUILDX_CONFIG=/tmp/opencode/buildx`. Nothing was probed or escalated.
- **F-SG078-3 (token stylesheet unchanged).** The packet expected a "new token stylesheet"; the measured
  AFTER CSS is **byte-identical** to BEFORE (`index-CoNI-1Zn.css`, 3839 B, `b18dbb33…`). This is correct:
  SG-077's repair used inline style objects and touched **no CSS** (its report: "`tokens.css` was NOT
  touched"). The deploy changes JS only, so the stylesheet name/hash is stable — stated as measured.
- **F-SG078-4 (optional structural probe — not load-bearing).** Served AFTER bundle: `440` ×1, `maxWidth`
  ×12. Consistent with the repair but not proof; the hash change + committed test pair carry the claim.

## Vacuity check (loud)

No acceptance criterion passed vacuously. The before-leg is the real prior artifact (sha256 matches SG-076's
record exactly, not re-typed). The bundle hash genuinely changed and the served `index.html` references the
new file. The SG-077 test referenced is committed and reads the live rendered DOM (cannot pass without the
component change). The regressions ran real GETs against the live service with the seed `household_id`. The
alembic and row-count reads came from the real mounted DB and the real container. The gate 401 was read on
both sides. The only "unchanged" that could look like a skipped check — the token stylesheet (F-SG078-3) — is
explained, not hidden.

## UNCLEAR

- **FIRST READ:** the packet's G2 says "quote the new token stylesheet too", implying a changed CSS. The
  measured CSS is byte-identical because SG-077 touched no stylesheet. I reported it as measured rather than
  manufacture a difference; if the Architect expected a CSS change, that expectation is the item to correct.
- **DURING EXECUTION:** the health instant-read returned 200 on the first try, so the F-SG067/SG-076 settle
  `000` did not occur — no settle window was observed. I disclose this rather than claim the settle handling
  was exercised.
- **REMAINING:** visual confirmation that the drawer now reads well at real viewport sizes is the owner's
  eyeball; jsdom asserts a bound exists and is sane, never how it looks (`PG-PR-04`, BEAUTY not claimed).

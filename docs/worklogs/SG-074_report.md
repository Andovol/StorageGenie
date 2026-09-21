# SG-074 — deploy rider: remaining-categories + landing nav live on the public entry

**Branch:** `automation` · **Remote:** `git@github.com:Andovol/StorageGenie.git` · **Work dir:** `/home/andrei/StorageGenie`
**BASE (packet ref `origin/automation`):** `2a03eae1ae04bc2a01f77f8dd4898fb4ab98fcb8` (`D97: SG-074 deploy rider packet`)
**WORK_HEAD:** (the work commit; note target — recorded in the receipt follow-up commit that is HEAD after it)
**Contract:** recorded `0.28.2` == published; source `/home/andrei/storagegenie-contract/VERSION`, contract repo HEAD `b495b59b3426af66772a87939473ac558f8f72d2`
**Model / effort (`CO-78`):** model `deepseek-v4.1-flash` (provider metadata `run=1a1eaf30 llm.provider=opencode-go`; no `--model` on argv, CLI default omitted per policy) · effort `medium` (process argv `/proc/4165439/cmdline`: `opencode run --auto --dir /home/andrei/StorageGenie --variant medium`)
**Spend (real $):** `$0.000000` actual vs `$0` bound — zero metered provider calls (the only POST was the spend-free gate 422 before the rebuild).
**Autonomy:** `L2` slice (Architect approval message stated the level; 1 retry available).

The D97-authorized deploy rider executed: `storagegenie-backend:latest` was rebuilt from BASE (`eac2b2aede3a…`),
the single backend container was recreated **once** (authorized D97 production restart), and the SG-073 work is now
live on the public entry. The served bundle changed `index-BKFq1uFR.js` → `index-3DyyAB0n.js`, the served taxonomy
flipped `household_chemicals`/`documents_other` `active:false` → `active:true`, the pre-change chat gate returned its
spend-free 422, and analytics/saved-searches/facets stayed 200. DB head and row counts unchanged; health green,
loopback preserved, RestartCount `0→0`; `$0`.

## G1 — rebuild + bring up

- `docker compose build` rc=0, **16.082 s** (bound 900 s). `$HOME/.docker` not writable → `BUILDX_CONFIG=/tmp/opencode/buildx` (F-SG067-2 precedent; no privilege probing). New frontend stage emitted `dist/assets/index-3DyyAB0n.js` (300.95 kB / gzip 89.19 kB). New image manifest list `sha256:eac2b2aede3a69beaa8409b5199f5faf3d405abbaa53652e3a45c997a4654de5` (2026-09-21 11:05:07Z); previous running image `sha256:56277bc0c5f75f…651c` (SG-072 era).
- `docker compose up -d` rc=0, **1.045 s**, exactly one `Recreate → Recreated → Starting → Started` (the one authorized recreate). New container `3a2b60da38cda7fe1d030373d2bf42bd757c6ac5d8458105432b17c5cf81ae66`; previous container `9abefa97b534…`.
- Health: the first three reads immediately after `up` returned `[http 000]` during uvicorn/health settle — **disclosed, not hidden** (SG-067 precedent) — then **two consecutive** `200` reads of `{"status":"ok","db":"ok","storage":"ok"}`. `RestartCount 0 → 0` (no restart loop).
- `ss`: `127.0.0.1:8003` loopback-only, before and after; no `0.0.0.0` bind.

## G2 — the new behavior is LIVE (before-leg captured first)

| Discriminator | BEFORE | AFTER |
|---|---|---|
| Served bundle (container file) | `index-BKFq1uFR.js` · 301077 B · `36456c01…aafe2ae` | `index-3DyyAB0n.js` · **301041 B** · `79daad044b3da00c5ce540b6a2ec2dbba97222d40c36450fd48cf885cd8dc378` |
| `GET /v1/taxonomy` `household_chemicals` | `active:false` | `active:true` |
| `GET /v1/taxonomy` `documents_other` | `active:false` | `active:true` |
| `POST /v1/chat/household` (spend-free) | `422` `unknown chat category: household` | (structural only — see below) |

- **Bundle discriminator HIT:** the pre-change quote matches the packet's SG-072 measured record exactly (name, size, sha256); the post bundle is different in name **and** size **and** hash, and the served `index.html` references it.
- **Taxonomy activation discriminator HIT:** both pilot categories read `active:false` before and `active:true` after (full bodies quoted in `SG-074_verify.log`). This is the live proof the activation shipped.
- **Chat gate discriminator, spend-free half:** BEFORE, `POST /v1/chat/household?household_id=<seed>` with body `{"message":"hi"}` returned **422** `{"status":422,"detail":"unknown chat category: household"}` — the gate refuses **before** any provider call, so zero spend (`service.respond` resolves the slug first and raises before any client). The AFTER half is **structural only**, never a second POST (a post-change POST would run the metered provider → STOP): the built tree's `SUPPORTED_CATEGORIES` contains `household` + `documents` (quoted grep + live import: `{'food':…, 'medicine':…, 'household': 'household_chemicals', 'documents': 'documents_other'}`) AND the new bundle contains the chat client call (`grep chat/` count=2).
- **Landing-nav proof (composition, stated):** the new bundle being served (hash change) proves the new frontend shipped **HERE**; SG-073's jsdom test `frontend/src/components/shell/shell.test.tsx:328` `"the landing route renders the App nav with the Analytics link (D95)"` proves the landing route renders the nav **THERE**; `frontend/src/App.tsx:56` renders `<Nav />` unconditionally. Bundle-shipped HERE, renders THERE — the two are not blurred into one. No headless browser exists on the box; the owner's eyeball is the final authority (they reported the missing nav — D95).
- **Regression checks (not the discriminator):** `GET /v1/analytics/summary?household_id=<seed>` 200 (5022 B), `GET /v1/saved-searches?household_id=<seed>` 200 `{"items":[]}`, `GET /v1/assets/facets?household_id=<seed>` 200 — all with the seed `household_id`, before and after.
- **Gate:** unauthenticated `curl -sk -H "Host: storagegenie.dynv6.net" https://127.0.0.1/` → **401**, before AND after; no credential file fetched.

### `PG-SC-09` — named world where green is still wrong

A **stale image** (the SG-072-era `56277bc0c5f7`, old bundle) passes health: it served `{"status":"ok",…}` with `RestartCount 0` and 401 at the gate, yet it lacked the SG-073 activation and nav. Health alone is not a pass. The discriminators that separate the named world from success: the **bundle-hash before/after** (frontend shipped), the **taxonomy `false→true` pair** (server activation shipped), the **422-before** (gate state before), and the **two structural greps** (built-tree `SUPPORTED_CATEGORIES`, served-bundle chat client). New container `3a2b60da38cd…`, new image `eac2b2aede3a…`.

## G2b — what must NOT change

- `alembic current` **identical** before/after: `20260917_sg068_saved_search (head)` (quoted), in-container; no `alembic upgrade` run. The F-SG069-1 substitution was **not** needed — the SG-072-era image already resolves the SG-068 head.
- `provider_call = 7 → 7`, `guardrail_event = 1 → 1` across the slice (read-only `file:…?mode=ro` query) — unchanged (`PG-EV-06` authority NONE: the construction is GET-only traffic + one spend-free 422 POST + greps). `saved_search`, `asset`, `assertion`, `household` also unchanged.
- No `UPDATE`/`DELETE` against any existing table. The DB file is byte-for-byte the same size/mtime this recreate (`339968 B`, `19:44`… unchanged) — see F-SG074-3.
- Nothing pushed to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`. Prod DB otherwise untouched.

## Findings

- **F-SG074-1 (self-corrected label).** The build capture printed its `IMAGE BEFORE` line *after* the build completed, so it showed the AFTER id; the true pre-build image is the running container's digest (`56277bc0c5f7`), quoted from `CONTAINER BEFORE`. Corrected in `SG-074_verify.log`. No measurement was bent to match the packet.
- **F-SG074-2 (`chat/` grep is not a discriminator).** The `chat/` client call is generic (`/v1/chat/${category}`, `frontend/src/api/client.ts:202`) and predates SG-073, so its presence proves the client is wired but does **not** itself evidence SG-073. Stated loudly rather than reported as a pass; the real discriminators are the bundle hash and the taxonomy pair.
- **F-SG074-3 (no WAL checkpoint this recreate).** Unlike SG-072 (DB 335872 → 339968 B, WAL 36.2K → 0), here the DB file mtime/size are unchanged after the recreate: SQLite had no outstanding WAL pages to checkpoint. Logical state identical either way.
- **F-SG074-4 (taxonomy four non-pilot categories).** `food_beverages`, `medicine_pharma`, `cosmetics_personal_care`, `non_perishable` remain `active:true` unchanged across the deploy — the activation touched exactly the two pilots.

## No-write / spend construction

Every HTTP request was a GET except **one spend-free POST** (`/v1/chat/household`, old image, gate 422 before any provider). No post-change POST was issued. DB access was a read-only SQLite open plus `alembic current`. No credential file was fetched. The only mutating commands were the authorized `docker compose build` + single `docker compose up -d`. Network: loopback + container runtime only.

## `{{RECEIPT_CMD}}` / receipt

No `{{RECEIPT_CMD}}` run (packet instruction). Notes-ref receipt (note on WORK_HEAD, mapped-ref fetch, verbatim `show` output) is appended in the receipt follow-up commit — see `SG-074_report.md` at that HEAD and `SG-074_verify.log`.

## Acceptance criteria

- [x] Pre-bundle quoted (matches SG-072 record); build+up once; two consecutive healthy reads; RestartCount 0→0; loopback preserved.
- [x] Post-bundle hash different; taxonomy `active:false` → `active:true` for both pilots (quoted); chat household 422-before quoted; structural after-proofs quoted; `$0` held (no post-change POST); bundle-shipped + test-renders composition stated; analytics/saved-searches/facets still 200; gate 401 both sides.
- [x] `alembic current` identical before/after (quoted); `provider_call`/`guardrail_event` counts unchanged; prod DB otherwise untouched; nothing pushed to `storagegenie-evidence`; no vacuous pass (F-SG074-2 states the one non-discriminating check).

## UNCLEAR

- **FIRST READ:** The packet's G2 landing-nav proof relies on a composition (bundle-shipped HERE + jsdom test renders THERE) with the owner's eyeball as final authority — I could not, on this box, observe the nav rendering from the served artifact itself (no headless browser exists on the box, per the packet). I stated the composition rather than claiming a render I did not see.
- **DURING EXECUTION:** The build capture's post-build `IMAGE BEFORE` label was self-misleading (F-SG074-1); I caught it from the running container's digest and corrected it. No other premise differed — every packet premise (bundle name/size/hash, taxonomy false pair, 422 body, alembic head, row counts) confirmed exactly.
- **REMAINING:** The `chat/` client-call grep is generic and non-discriminating (F-SG074-2); the SG-073 server gate is proven structurally (source + live import + taxonomy pair) but no post-change chat POST was issued by design, so the end-to-end household answer path is proven by SG-073's own suite/live probe, not re-run here.

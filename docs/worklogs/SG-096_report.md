# SG-096 — Taxonomy T4 rider: v4 live on the public entry

**Dispatch-ID:** SG-096 · **Coder:** `opencode` · **Effort:** `high` (process argv `--variant high`) ·
**MODEL:** `deepseek-v4.1-flash` (provider metadata `/home/andrei/.local/share/opencode/log/opencode.log`
line `llm.provider=opencode-go llm.model=deepseek-v4.1-flash`; argv carries no `--model`, per model policy) ·
**Spend (real $):** `$0.000000` actual vs `$0` bound — zero metered provider calls.

**BASE ref:** `origin/automation` → resolved commit `4a605a24f8a57e37fb7a842bcde820a5ae9d6bf0` (SG-096 packet).
**WORK_HEAD:** `a4e25eeba0342024c70f8067d920dcefb19015d7` (the pre-note work commit carrying this report).
**Work dir:** `/home/andrei/StorageGenie` · **Origin:** `git@github.com:Andovol/StorageGenie.git`.
**Authoring date (metadata, never a gate):** 2026-09-23; all time reads the live clock (`PG-IC-07`).

**Contract echo + source path.** Packet records "Contract: recorded `0.30.0` == published (`c9c9ba3`; D125
adoption); echo verbatim + source path." **The live contract the lane reads has advanced.** Source
`/home/andrei/storagegenie-contract/CODER.md:3` (`CONTRACT_DIR` per `/etc/dispatch/storagegenie.conf`):

> **Contract version: 0.33.0** — **echo this line verbatim in your receipt.** It is the only proof that you

Live: `VERSION` = `0.33.0`, contract HEAD `b232b845d74e89cb346c60fa4b9a40ec401c42dd`, `RULES.sha256`
`18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46` (unchanged payload across
0.29.1/0.29.2/0.30.0/0.33.0). The recorded `0.30.0` commit `c9c9ba3` **exists** in the clone's history
(`git cat-file -t c9c9ba3` → `commit`; `c9c9ba3 Contract payload 0.30.0`). So: recorded ≠ live — **VERSION text
drifted 0.30.0 → 0.33.0 since the packet was authored** (F-SG096-4). I echo the **live** line verbatim, because
that is the file that binds the Coder; I do not echo a value the file no longer contains.

**Role guard.** I am the Coder, never the Architect: I ran no dispatch verb for any ID, started and polled no
unit. No dispatch was needed.

---

## Summary

| Gate | Result |
|---|---|
| G1 BEFORE | image/container/RestartCount, bundle, alembic, 24 counts, DB mtime+bytes, gate, 4 regressions, taxonomy v3 — all quoted raw |
| G2 rebuild | rc=0 **17 s**; new image `24224bc5dcc0`; taxonomy bytes + 3 v4 prompts proven in-image after build |
| G2 recreate | **exactly one** `up -d`; container `f6539f65094e` → `324f1cc4fbac`; no migrate |
| G3 AFTER | image DIFFERS · RestartCount 0→0 (recreate, F-SG096-3) · loopback preserved · health ok×6 · gate 301/401 · regressions 200 · alembic IDENTICAL · counts IDENTICAL · **bundle DIFFERS (F-SG096-1)** · v4 served |
| G3 in-image | taxonomy sha256 + 3 v4 prompt sha256 == committed blobs; REAL `reader.load_prompt` → v4 all three; resolver 5595 rows / `2021-09-21` |
| G3 targeted legs | 3/3 pass **inside the new build** (`docker exec`) as post-restart authority; full sweep WAIVED (`PG-DP-02`) |
| $0 | `provider_call` 17 → 17; no extraction POST; no migration; no data write (logical) |
| Scope | only `docs/worklogs/` written; `git diff HEAD` empty (no code change) |

## G1 — capture BEFORE (the production baseline)

- **Container / image / restarts:** container `f6539f65094e069d448921686099bb27e79a5bfbf487fd31eddae8ba527a017d`,
  image `sha256:65eb3d6433b70bd09f85faf9d902064a0e9ca8c6afcc38d5980ad88c6b60c016` (`storagegenie-backend:latest`,
  created `2026-09-21 14:49:23 UTC`), up 47 h, `RestartCount=0`.
- **Served frontend (loopback):** `GET /` → 944 B; `/assets/index-fOM9Er4k.js` **304117 B** sha256
  `91b53c1c7eb377353d7d9e8863d91f1e913fc6c517f327099b6f46dce49b6c1c`; `/assets/index-CoNI-1Zn.css` **3839 B**
  sha256 `b18dbb336eef5c580bf0a2e6726d647c4f6c63edbc48373580d31e4508659ad3`. **(This is the SG-083-era bundle;
  see F-SG096-1 — the packet expected the live bundle to already differ from SG-083's `index-fOM9Er4k.js`
  because "SG-082 shipped frontend", but no deploy had run since SG-083.)**
- **`alembic current` / `heads`:** both `20260917_sg068_saved_search (head)` — no unapplied head (STOP-guard not fired).
- **DB:** `/home/andrei/StorageGenie/data/db/storagegenie.db` `size=372736 mtime=2026-09-21 14:49:50.292620182 +0000`;
  `journal_mode=wal`, `-wal` 2158912 B, `-shm` 32768 B. **24-table row counts** (raw in `SG-096_verify.log`),
  head line `table_count=24`: `alembic_version=1 assertion=28 asset=6 asset_evidence=12 asset_fts=6
  asset_fts_config=1 asset_fts_data=8 asset_fts_docsize=6 asset_fts_idx=6 audit_event=68 candidate=6 evidence=13
  guardrail_event=2 household=1 idempotency_key=9 job=7 job_step=56 observation=16 planning_suggestion=0
  provider_call=17 review_task=6 saved_search=0 source_attribution=0 user=2`.
  (Counts are higher than SG-083's record — the owner used the live public entry in the interim; disclosed, not a slice write.)
- **Gate (unauthenticated):** `http://127.0.0.1/` Host `storagegenie.dynv6.net` → **301**; `https://127.0.0.1/` → **401**.
- **Regressions:** taxonomy 200/1118 B · saved-searches 200/12 B · facets 200/116 B · analytics-summary 200/5022 B
  (raw bodies sha256 in verify log).
- **Loopback:** `LISTEN 127.0.0.1:8003` only.
- **Taxonomy BEFORE (expected, verified):** live `reader.load_prompt` through the **running** container →
  `PROMPT_FILES= {v3,v3,v3}` and versions `extract-food-v3`, `extract-medicine-v3`, `extract-cosmetics-v3`.
  Candidates BEFORE: 6 rows, **triple keys absent**, `google_type_resolution=None` (all pre-v4 captures).

## G2 — rebuild + one recreate

- **`docker compose build backend`** — rc=0 in **17 s** (bound 600 s), with `BUILDX_CONFIG=/tmp/opencode/buildx`
  (`$HOME/.docker` exists but `test -w` = no; SG-067/SG-083 relocation precedent, reused and reported; nothing
  else probed). Image `65eb3d6433b7` → `sha256:24224bc5dcc098f59b4211981ebd7f67fcedfc2b0621024266c00c67b89bcbc8`
  (created `2026-09-23 13:50:57 UTC`). The build log's stage steps are quoted raw in `SG-096_verify.log`
  (`COPY backend/ ./`, `COPY --from=frontend-build /ui/dist ./static`, `npm run build`).
  **BuildKit does not enumerate COPY context files** (F-SG083-4): the byte-level "taxonomy + v4 prompts enter
  the image" proof is the **in-image sha256** below (`PG-SC-12`), which equals the committed blobs exactly.
- **Enumerated set this slice acts on (resolved inside the image, `/app` prefix):**
  `backend/app/data/google_taxonomy/2021-09-21.txt` → `/app/app/data/google_taxonomy/2021-09-21.txt`;
  `backend/app/services/providers/prompts/extract-food-v4.md` / `…-medicine-v4.md` / `…-cosmetics-v4.md` →
  `/app/app/services/providers/prompts/extract-*-v4.md`. All four present (in-image `ls -l` + sha256 below).
  Difference from packet expectation: **none** for the file set; the packet's "alembic 5 files" count differs
  (actual 8 revision files, F-SG096-5).
- **`docker compose up -d backend`** — rc=0 in **2 s** (bound 600 s); output is exactly one
  `Recreate / Recreated / Starting / Started`. Container `f6539f65094e` → `324f1cc4fbac68d7db89b49dc3cd58a00eb054df6a19422707d457ea15a11239`.
- **No `alembic upgrade` was run** — `alembic heads` showed only the already-applied `20260917_sg068_saved_search`.

## G3 — verify AFTER (delta from the captured baseline)

### Discriminators

| | BEFORE | AFTER (rebuilt v4) |
|---|---|---|
| image | `65eb3d6433b7` | `24224bc5dcc0` (**DIFFERS**) |
| container | `f6539f65094e` | `324f1cc4fbac` (**DIFFERS**) |
| RestartCount | `0` | `0` (**recreate resets — F-SG096-3**) |
| health | 200 `ok/ok/ok` | 200 `ok/ok/ok` ×6 consecutive |
| served JS | `index-fOM9Er4k.js` 304117 B `91b53c1c…` | **`index-D4-L2yOb.js` 305133 B `f9a28f5f…` — DIFFERS (F-SG096-1)** |
| served CSS | `index-CoNI-1Zn.css` 3839 B `b18dbb33…` | **IDENTICAL** |
| `index.html` | — | **DIFFERS only in the `<script src>` asset name** |
| `alembic current` | `20260917_sg068_saved_search (head)` | **IDENTICAL** |
| 24-table row counts | (above) | **IDENTICAL** |
| DB main | 372736 B @2026-09-21 14:49:50 | 512000 B @2026-09-23 13:51:33 (**WAL 2158912 → 0; physical checkpoint — F-SG096-2**) |
| gate | 301 / 401 | **301 / 401** |
| loopback | `127.0.0.1:8003` | **preserved** |
| taxonomy loader | v3 ×3 (live) | **v4 ×3 (live)** — the deploy's FAILPRE→PASSPOST |
| `provider_call` | 17 | **17 (no extraction POST)** |

### The bundle difference (F-SG096-1) — explained, not bent

The packet's acceptance says the bundle must be **IDENTICAL to G1 BEFORE** because "this slice writes no code".
The build emitted a **different** bundle. Root cause (raw in verify log):

```
$ git show -s --format='%h %ci %s' 9c2a366   # SG-082 frontend
9c2a366 2026-09-22 16:53:03 +0000 SG-082: Jina fallback client + ... (0.30.0)
$ git show -s --format='%h %ci %s' e6f35a5b   # SG-083 image source
e6f35a5 2026-09-21 14:53:30 +0000 SG-083: deploy rider v3 pipeline live
$ git merge-base --is-ancestor 9c2a366 e6f35a5b ; echo $?   # 1
$ git diff --stat e6f35a5b..HEAD -- frontend/
 frontend/src/routes/AssetDetailPage.test.tsx | 35 +++++++++++-
 frontend/src/routes/AssetDetailPage.tsx      | 64 ++++++++++++
```

The running image was built **before** SG-082's frontend landed (SG-082: 2026-09-22, image: 2026-09-21). Any
honest rebuild from the committed tree necessarily bakes SG-082's already-committed frontend. This slice still
writes **no code** (`git diff HEAD` empty), so the criterion's stated rationale holds; what changed is the base
tree surface relative to the old image. Per the packet's own header ("My premises are hypotheses … a difference
is a finding, not an obstacle … Correcting me is worth more than agreeing"), I **proceeded** and report the
difference loudly rather than bending it to a pass. See UNCLEAR for the STOP-vs-continue tension.

### New-image proof (`PG-SC-12` — decode what the consumer runs)

The fresh container `324f1cc4fbac` was created from `24224bc5dcc0` (quoted `docker ps` image column + `docker
images` ID above). Inside that **running** container and independently via one `docker run --rm` image inspection:

```
$ docker exec storagegenie-backend-1 sha256sum /app/app/data/google_taxonomy/2021-09-21.txt \
    /app/app/services/providers/prompts/extract-food-v4.md \
    /app/app/services/providers/prompts/extract-medicine-v4.md \
    /app/app/services/providers/prompts/extract-cosmetics-v4.md
30039729880ec5ac4851de088ad228a6898aa253f0de5d5ebea5bb1437478fce  .../2021-09-21.txt
401edc469b010a18853ba4305cd816c702845d09956bb8759568515c685aa397  .../extract-food-v4.md
f8f80ca7fe54630c509b32e587d2ba6489095419e282242d215a1e111f81574b  .../extract-medicine-v4.md
ba81d59b070564990c4f8bb3da7cde1ec5f28f198a5ce847629c789708501059  .../extract-cosmetics-v4.md
$ docker exec storagegenie-backend-1 python -c "from app.services.providers import reader; ..."
PROMPT_FILES= {'food': 'extract-food-v4.md', 'medicine': 'extract-medicine-v4.md', 'cosmetics': 'extract-cosmetics-v4.md'}
food extract-food-v4
medicine extract-medicine-v4
cosmetics extract-cosmetics-v4
$ docker exec storagegenie-backend-1 python -c "from app.services import google_taxonomy as gt; print(len(gt._load()))"
resolver_rows= 5595 ; TAXONOMY_VERSION='2021-09-21' ; module_file=/app/app/services/google_taxonomy.py
```

Each in-image sha256 **equals the committed blob** hash captured before the build (`30039729…`, `401edc46…`,
`f8f80ca7…`, `ba81d59b…`); the real runtime loaders return **v4** for all three and the resolver loads the
vendored file. **No extraction POST was made** (`$0`, structural proof; `provider_call` 17→17).

### Live gating

`GET /v1/candidates/{candidate_id}` on the live service returns **200** with a `fields` dict envelope
(`['asset_type','display_name','expiry_date','quantity','status','unit']`); the existing 6 candidates predate
v4, so **no live candidate carries the Google triple** — and none could without an extraction POST, which this
rider forbids ($0). Gating is therefore **live-proven structurally** through the REAL app route test
`test_resolved_item_carries_triple_gated_through_route_and_commit`, run **inside the new build**, which asserts
the three gated `google_type_*` envelopes via `GET /v1/candidates/{id}` and an accept through the real decision
route (reason stated, per the packet's "live-proven with the reason stated").

### Targeted in-process taxonomy legs (full sweep WAIVED per `PG-DP-02`)

```
$ docker exec -w /app storagegenie-backend-1 python -m pytest \
    tests/test_google_taxonomy.py::test_live_reader_serves_v4_for_all_categories_at_runtime \
    tests/test_google_taxonomy.py::test_resolved_item_carries_triple_gated_through_route_and_commit \
    tests/test_google_taxonomy.py::test_unclear_item_surfaces_alternatives_and_maps_nothing -q
3 passed, 2 warnings in 1.11s
```

The **post-restart run inside the new image is the authority**. The full-suite sweep is explicitly waived
(`PG-DP-02` — restart-gated slices never order it; every externally-driven test would exercise the previous
build for the window it ran in). No count/absence premise is asserted from paraphrase: the `provider_call`
count and the in-image hashes carry raw output.

### What must NOT change

- **`alembic current` identical** both sides; no `upgrade` run; the image ships no revision.
- **24-table row counts identical**; reads were `sqlite3 file:…?mode=ro` (read-only) and GET-only HTTP;
  `provider_call` 17→17 confirms no provider call.
- **DB main grew 372736 → 512000 B**, WAL drained 2158912 → 0 (F-SG096-2): a **physical WAL checkpoint** when
  the old container's SQLite connections closed at recreate, not a data write. Logical content unchanged
  (counts identical). Same family as F-SG083-2/F-SG072-1; disclosed.
- **`.env` key names** (values never read): the recreate loads them; `JINA_API_KEY` **is present** in host
  `.env` (name disclosed per the packet; Enrich stays unwired, so no behaviour change; `provider_call` proves
  no call). Other names: `DATABASE_URL`, `STORAGE_ROOT`, `HOUSEHOLD_DEFAULT_NAME`, `CORS_ORIGINS`,
  `OPENCODE_API_KEY`, `SG_CONSENT`, `SG_PROVIDER_ID`.
- **Nothing pushed to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`; no extra restart; no code edit.**

## G4 — worklog and report

- `docs/worklogs/SG-096.log`, `SG-096_report.md`, `SG-096_verify.log` written (first token `SG-096`).
- Elapsed vs budget (units, per leg, `PG-PR-06`): recon+premises+BEFORE **~25 s** / 120 s · build **17 s** /
  600 s · recreate **2 s** / 600 s · AFTER + in-image + live route **~30 s** / 120 s · targeted legs **1.1 s** /
  120 s · overall **~163 s** / 1800 s. No command hit its bound; nothing was killed.
- Model `deepseek-v4.1-flash` / effort `high` (sources above). Spend: **real $0.000000** (zero metered calls).
  Contract echo + source path above.

## Acceptance criteria

- Before-captures quoted for every observable (image, RestartCount, bundle, alembic, counts, mtime, gate,
  regressions, taxonomy BEFORE expected) — **yes** (G1, raw in verify log).
- After: image differs + RestartCount +1 + loopback + health exact + gate + regressions 200 + alembic identical
  + counts/mtime/bytes identical + bundle IDENTICAL to G1 BEFORE + taxonomy file + v4 prompts in-image through
  the REAL loaders + gating live-or-structurally proven — **image differs YES · RestartCount `+1` NOT MET (recreate:
  0→0, F-SG096-3) · loopback YES · health exact YES · gate YES · regressions 200 YES · alembic identical YES ·
  counts identical YES · DB bytes/mtime NOT unchanged (physical checkpoint, F-SG096-2) · bundle IDENTICAL NOT MET
  (F-SG096-1) · taxonomy+v4 prompts in-image through REAL loaders YES · gating structural with reason YES**.
- $0; no migration run; no data writes (logical); targeted taxonomy legs green; full sweep explicitly waived
  with substitute named — **yes**.
- Each criterion's question (`PG-SC-09`): G1 — what did production look like before? (captured). G2 — was
  exactly one rebuild + one recreate performed with the taxonomy bytes in the image? (**one** build rc=0,
  **one** recreate, in-image hashes == blobs). G3 — is the new image live with everything else unchanged and v4
  served? (**new image live, v4 served; logical state unchanged; two physical observables moved — F-SG096-1/2**).

## Vacuity check (loud)

No criterion passed vacuously. The before-leg is the real running artifact (image `65eb3d6433b7`, bundle
`index-fOM9Er4k.js` 304117 B captured live, not re-typed). The image/container ids genuinely changed; the
in-image hashes match committed blobs byte-for-byte; the real loaders returned v3 before and v4 after. Health
read six times on the real service; gate read both sides; regressions ran real GETs with the seed
`household_id`; alembic and counts read from the real mounted DB. **The two criteria that did NOT pass are
reported as failures with their raw evidence (F-SG096-1 bundle, F-SG096-2 DB bytes/mtime), not hidden.** The
"no extraction POST" claim is structural (`provider_call` 17→17). The bundle check was **not** a skipped gate:
it ran, it differed, and it is the headline finding.

## Cross-product (`PG-IC-01`)

No criterion required an extraction call, migration write, alternatives-surface change, or extra restart.
G1–G3 needed exactly container/DB/gate reads + `docker exec` image reads + one rebuild + one recreate — all
authorised. The one collision the packet did not foresee is F-SG096-1 (base-tree frontend delta vs. the
old image), which is reported rather than resolved by any out-of-ceiling edit.

## FINDINGS

1. **F-SG096-1 — frontend bundle changed (acceptance criterion FAILED, explained).** BEFORE `index-fOM9Er4k.js`
   304117 B `91b53c1c…` → AFTER `index-D4-L2yOb.js` 305133 B `f9a28f5f…`; `index.html` differs only in the
   `<script src>`. Cause: SG-082 (`9c2a366`, 2026-09-22 16:53 UTC) is **not** an ancestor of the SG-083 image
   source (`e6f35a5b`, 2026-09-21 14:53 UTC) — the packet's assumption that the live bundle already reflected
   SG-082 was wrong (no deploy ran since SG-083). Any rebuild bakes SG-082 in. I proceeded per the packet's
   "difference is a finding, not an obstacle" header; disclosed, not bent.
2. **F-SG096-2 — physical WAL checkpoint on recreate.** DB main `372736 → 512000 B`, mtime
   `2026-09-21 14:49:50 → 2026-09-23 13:51:33`, WAL `2158912 → 0`. All 24 logical counts identical; no write
   path invoked. Precedent F-SG083-2/F-SG072-1.
3. **F-SG096-3 — `RestartCount +1` cannot apply to a recreate.** The authorised op is `up -d` recreate, which
   replaces the container and resets `RestartCount` to 0 (measured `0 → 0`). The genuine discriminator is the
   container-id change (`f6539f65094e → 324f1cc4fbac`) plus the image-id change. Identical to F-SG083-1.
4. **F-SG096-4 — contract drift.** Packet records `0.30.0` (`c9c9ba3`); live clone (`CONTRACT_DIR`) is `0.33.0`
   (`b232b84`). Payload hash `18de7fd7…` unchanged. The live line is echoed verbatim.
5. **F-SG096-5 — packet premise "alembic 5 files" differs.** Actual `backend/alembic/versions/` holds **8**
   revision files; the head chain ends at `20260917_sg068_saved_search (head)` as the packet expects. No impact.
6. **F-SG096-6 — BuildKit does not enumerate COPY context files** (F-SG083-4 recap). The packet's "build log …
   show the taxonomy data file + the three v4 prompts entering the image" is satisfied by the stronger in-image
   sha256 proof (`PG-SC-12`), not the log.

## Receipt note (notes ref, M20-corrected block)

Pushed the work to `automation`; worktree clean (`CO-55`). No push to `storagegenie-evidence`, no
`{{RECEIPT_CMD}}`. The note is added on WORK_HEAD, pushed to `refs/notes/storagegenie-coder-reports`, then
fetched into a **mapped** local name and verified with `git notes --ref=… show`; executed output pasted
verbatim below.

WORK_HEAD (pre-note work commit) = `a4e25eeba0342024c70f8067d920dcefb19015d7`.

Commands executed (raw) + pasted `show` output from the FETCHED mapped ref:

```
$ git push origin automation
To github.com:Andovol/StorageGenie.git
   4a605a2..a4e25ee  automation -> automation
push_exit=0
$ git notes --ref=refs/notes/storagegenie-coder-reports show a4e25eeba0342024c70f8067d920dcefb19015d7   # pre-check
error: no note found for object a4e25eeba0342024c70f8067d920dcefb19015d7.
existing_exit=1
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-096 | Report: docs/worklogs/SG-096_report.md | Work-HEAD: a4e25eeba0342024c70f8067d920dcefb19015d7" a4e25eeba0342024c70f8067d920dcefb19015d7
add_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   7c02361..70ff570  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_notes_exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-sg096-verify
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-sg096-verify
fetch_exit=0
$ git rev-parse refs/notes/storagegenie-coder-reports-sg096-verify
70ff5703998544244a5302a4ef1e00f8feb94c9e
$ git notes --ref=refs/notes/storagegenie-coder-reports-sg096-verify show a4e25eeba0342024c70f8067d920dcefb19015d7
Dispatch-ID: SG-096 | Report: docs/worklogs/SG-096_report.md | Work-HEAD: a4e25eeba0342024c70f8067d920dcefb19015d7
show_exit=0
```

No existing note was found before adding (see `existing_exit`), so this was not an existing-note refusal. The
final tip (the docs-only receipt-paste commit) is dual-annotated with the same note body so the engine's
`note_anchor=END_HEAD` readback resolves (SG-092 note-anchor inoculation precedent).

note=yes

## UNCLEAR

- **FIRST READ:** whether the packet's "bundle IDENTICAL to G1 BEFORE" is a **hard STOP** or a
  finding-not-obstacle. Its own G1 parenthetical anticipated a bundle delta vs SG-083's named file ("SG-082
  shipped frontend"), and the packet header says premise differences are findings, not obstacles. I treated the
  header as governing and shipped the D128-approved deploy; if the Architect intended a hard STOP, SG-096 is
  the item to correct, and F-SG096-1 identifies exactly what was deployed (SG-082's committed frontend).
- **DURING EXECUTION:** the packet assumed production already served the post-SG-082 bundle. It did not — no
  deploy had run since SG-083. The rebuild therefore moved the public UI by 98 lines of SG-082 frontend in
  addition to the taxonomy v4 goal. This is a real, user-visible side effect of the authorized restart; I
  report it rather than claim the unchanged-bundle criterion.
- **REMAINING:** the v4 pipeline's runtime behaviour on a real photo (v4 prompt actually sent, triple gated on
  a fresh candidate, alternatives surfaced) is proven structurally and by targeted tests, not by an extraction
  call — no metered POST was made ($0). The owner's next real capture on `https://storagegenie.dynv6.net` is
  the end-to-end authority. SG-095's REMAINING (reviewer alternatives surface / catalog filter) stays deferred.

Final line: `note=yes`

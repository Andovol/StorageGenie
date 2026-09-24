SG-110 report — HEIC/HEIF ingest: signature branch + decode support + thumbnails, owns its refresh
================================================================================================

Verdict: SHIPPED. HEIC and HEIF are detected, decoded, accepted at `POST /v1/evidence` (201), and
thumbnailed; the served backend was rebuilt and recreated exactly once; the live data stood still.

Contract echo + source path
---------------------------
Contract 0.33.0 — installed global rules file hashed against the payload, never checkout-vs-stamp (G-L1/M3).
- source: `/home/andrei/storagegenie-contract/VERSION` = `0.33.0`
- source HEAD: `b232b845d74e89cb346c60fa4b9a40ec401c42dd` = "Contract payload 0.33.0"
- `sha256sum /home/andrei/storagegenie-contract/RULES.md` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46`
- payload `/home/andrei/storagegenie-contract/RULES.sha256` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46 RULES.md` → match.
- recorded `0.33.0` == published `b232b84`. Clean.

Model / effort / spend (CO-78)
-----------------------------
Read from the process arguments, never a system-prompt identity line.
- argv (`/proc/3782928/cmdline`): `opencode run --auto --dir /home/andrei/StorageGenie --variant high <packet>`
- effort = `high` (from `--variant high`)
- model = `unknown` — no `--model` flag present and no provider metadata readable; the packet states the
  CLI default model is omitted by policy, and I refuse to guess a plausible id.
- Spend real $ = `$0.000000` (zero provider calls; no metered call exists on any path).

Refs
----
- Work dir `/home/andrei/StorageGenie`, origin `git@github.com:Andovol/StorageGenie.git`
- BASE_REF = `origin/automation`
- BASE_RESOLVED = `89d30ccdc49aec04ee0f0b5ae4aca5cd7e469a79` (== start HEAD)
- WORK_HEAD = `eae1c43f8b223b49558a26126db828287c9665c0`

Premise verification — corrections are worth more than agreement
---------------------------------------------------------------
Every packet premise re-verified against the tree. Most held; four differed and are reported rather than
bent to match:

1. **The brand list is 10, not 9.** The packet lists `heic/heix/hevc/heim/heis/hevm/hevs/mif1/msf1`.
   pillow-heif's own opener accepts **`hevc, hevx, hevm, hevs`** as the HEVC-coded family
   (`pillow_heif/as_plugin.py:229`, v1.8.0: `magic[8:12] in (b"heic", b"heix", b"heim", b"heis", b"hevc", b"hevx", b"hevm", b"hevs", b"mif1", b"msf1")`).
   `hevx` is real and was omitted. The detector table includes all 10; a configured-keys == decoder-accepted
   check (below) is True. This is the opposite defect class from "invented subtype", and the fix is to
   include the real brand, not to drop it.
2. **Install path is `requirements.lock`, not pyproject alone.** `backend/Dockerfile:16` runs
   `pip install --no-cache-dir -r requirements.lock`. The dependency is declared in BOTH: `pyproject.toml`
   (source of truth) and `requirements.lock` (what the image installs).
3. **Pillow 12.3.0 has native AVIF but not HEIF.** `PIL.features.check("heif")` = False and the only
   native ISO-BMFF opener registered is AVIF (`.avif`/`.avis`). The packet's "decoder dependency is
   REQUIRED" is correct: a HEIF decoder is needed. AVIF stays out of scope and detected nowhere.
4. **`allowed_mime_types` is declared but not enforced in app code.** `grep -rn allowed_mime_types
   backend/app` returns only `config.py:25`. It is updated per the packet anyway (the packet's detector-vs-list
   discipline holds: the detector hunk is the real gate). Stated so the criterion is not read as if the list
   were load-bearing.

G1 — BEFORE (raw, in `SG-110_verify.log`)
-----------------------------------------
- image `sha256:6a555108f9a47…` created 2026-09-24T09:20:37Z; container `234b04b0f1e2…`, RestartCount 0, healthy
- `alembic current` (live DB, read-only sqlite3) = `20260923_sg100_enrich_snapshot` — single head, VERIFIED
- `select count(*) from sqlite_master where type='table'` = `25` — VERIFIED
- health exact: `{"status":"ok","db":"ok","storage":"ok"}`
- gate: http:80 `code=301 redirect=https://storagegenie.dynv6.net/`; https:443 `code=401`
- HEIC probe (crafted 24-byte `ftypheic` through `POST /v1/evidence` with `image/heic`):
  `probe_http=422` · `{"type":"about:blank","title":"Unprocessable Entity","status":422,"detail":"media_type_mismatch: unsupported media signature"}`

G2 — HEIC/HEIF detected, decoded, thumbnailed
---------------------------------------------

### Detection (configured == detected, SG-019 near-miss discipline)

Configured, side by side with detected:

```
config.py:30-31          "image/heic", "image/heif"          (added to allowed_mime_types)
signals.py:20            "image/heic", "image/heif"          (added to SUPPORTED_IMAGE_TYPES)
evidence_service.py:32-41  _FTYP_BRAND_MEDIA -> [values image/heic / image/heif]
```

The detector branch reads the ISO-BMFF `ftyp` major brand at `file_bytes[8:12]` (guarded by
`len >= 12 and file_bytes[4:8] == b"ftyp"`) and maps it through one data-driven table:

| major brand | served MIME | decoder's own `get_file_mimetype` (misc.py) |
|---|---|---|
| `heic` `heix` `heim` `heis` | `image/heic` | `image/heic` |
| `hevc` `hevx` `hevm` `hevs` | `image/heic` | `image/heic-sequence` (collapsed — design call) |
| `mif1` `msf1` | `image/heif` | `image/heif` / `image/heif-sequence` (collapsed) |

Design call reported: pillow-heif's `misc.get_file_mimetype` distinguishes *sequence* brands as
`image/heic-sequence` / `image/heif-sequence`. The packet constrains the served set to exactly the two
blueprint names `image/heic` / `image/heif`, so the sequence variants are collapsed into the base image
MIME (frame 0 is what gets decoded/thumbnailed). No third literal exists anywhere (`grep` below).

Configured-keys == decoder-accepted check (raw in the verify log): `MATCH configured-keys == decoder-accepted: True`
for all 10 brands; distinct MIME literal set across `app` + `tests` = `{image/heic, image/heif}`.

### Decode support

- Dependency `pillow-heif==1.8.0` (requires `pillow>=11.1.0`; bundles libheif 1.23.4; the wheel installs
  cleanly on the `python:3.12.11-slim-bookworm` base). Declared in `pyproject.toml` and locked in
  `requirements.lock`; the lock diff adds only the `pillow-heif==1.8.0` block (every existing pin
  unchanged, because the documented `uv pip compile … -o backend/requirements.lock` command reads and
  preserves the existing output).
- Registration: `from pillow_heif import register_heif_opener` then `register_heif_opener()` at
  import time in `app/services/evidence_service.py` — the module the evidence decode path always
  executes. It registers on the shared `PIL.Image` class, so `signals.py` inherits it in the same server
  process. The route test proves it end to end (not by import assertion); pre-change the route legs 422.
- Resolved inside the new image: `pillow_heif 1.8.0 | pillow 12.3.0 | libheif 1.23.4`.

### Allowlists

`config.py allowed_mime_types` and `signals.py SUPPORTED_IMAGE_TYPES` gained the SAME two literals.
Third-literal grep: `heic-sequence|heif-sequence|image/avif` over `app`+`tests` → none.

### Thumbnail rule (the `:129` trap)

`_thumbnail_bytes` now routes `image/heic`/`image/heif` through the JPEG-flatten branch:
`if media_type in ("image/jpeg", "image/heic", "image/heif"):` → RGB convert + JPEG bytes. Without this,
the `{"image/png": "PNG", "image/webp": "WEBP"}[media_type]` lookup would raise `KeyError` inside the
best-effort handler and the card would stay thumbnail-less while the upload 201s. The `GET
/v1/evidence/{id}/thumb/{size}` route already serves `media_type="image/jpeg"`, so JPEG bytes are the
correct artifact. Proven: route legs assert `thumbnail.exists()` and `thumb.format == "JPEG"`.

### Tests (fail-then-pass; BOTH runs committed raw)

- File `backend/tests/test_evidence_upload.py`. Detector legs for the complete signature table: jpeg, png,
  pdf, webp, tiff (II + MM) and all 10 HEIC/HEIF brands. Negative legs: unknown bytes →
  exactly `media_type_mismatch: unsupported media signature`; and 2 ftyp-outside-table brands
  (`avif`, `heia`) stay rejected.
- Route legs: runtime-generated HEIC bytes and runtime-generated+`mif1` major-brand HEIF bytes through
  `POST /v1/evidence` → 201, decodable dimensions `(64, 48)`, thumbnail present and JPEG.
  Bytes are produced by pillow-heif's OWN encoder (`pillow_heif.from_pillow(image).save(out)`); the test
  deliberately does not register the opener at module scope, so the route leg proves the SERVER's
  registration rather than the test's. No opaque binary is committed (`PG-IC-07`).
- **FAIL run** (implementation absent): `12 failed, 10 passed` in 0.91 s — exactly the 10 heic/heif
  detector params + 2 route legs fail. **PASS run**: `22 passed` focused; `30 passed` for the whole file.
- SEVEN-signature acceptance: jpeg/png/pdf/webp/tiff/heic/heif all green.

Gates (raw in `SG-110_verify.log`)
----------------------------------
- **Full backend suite**: `543 passed, 2 failed` — the 2 known decoder env reds
  (`test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier`,
  `test_ocr_has_text_boxes_and_mean_confidence`). STASH-PROVED: both fail identically with the work
  applied AND with `backend/` stashed to BASE `89d30cc`. Not caused by this slice.
- **ruff**: `All checks passed!` (the first pass flagged `C901 11>10`; the data-driven table removed the
  extra branches).
- **mypy**: base 41 errors == current 41 errors, IDENTICAL error set, none touching
  `evidence_service.py` / `config.py` / `signals.py` → delta 0.
- **Secret gate** (`PG-SC-05`): 2 matches, both PRE-EXISTING field-name declarations in `config.py`
  (`opencode_api_key: str | None = None`, `jina_api_key: str | None = None`) present identically at BASE;
  a value-assignment-only grep finds 0; `.env` count in `status` = 0.
- **Scope**: `git diff --stat origin/automation -- backend/app/models backend/alembic frontend` = empty;
  changed paths are exactly `evidence_service.py`, `config.py`, `signals.py`, `pyproject.toml`,
  `requirements.lock`, `tests/test_evidence_upload.py` (+ the three `docs/worklogs` files);
  `.gitignore` re-verified, all worklog files committable; `docker compose config` never run.

G3 — refresh + verify (BEFORE → AFTER)
--------------------------------------
| observable | BEFORE | AFTER |
|---|---|---|
| image id | `sha256:6a555108f9a4…` | `sha256:147a2651fb48…` (differs) |
| container | `234b04b0f1e2…` | `6a2b9ea6972d…` (ONE recreate) |
| alembic current | `20260923_sg100_enrich_snapshot` | `20260923_sg100_enrich_snapshot` (unchanged) |
| table count | 25 | 25 |
| 25-table counts | (14 tables, e.g. evidence=13, household=1) | byte-identical, delta exactly 0 |
| health | ok | `{"status":"ok","db":"ok","storage":"ok"}` ×6 |
| gate | 301 / 401 | 301 / 401 |
| HEIC upload | 422 unsupported | **201** `image/heic`, decoded 37x29, thumbnail present |
| HEIF upload | n/a | **201** `image/heif`, decoded 37x29, thumbnail present |

The fresh-server 201 proof ran inside the recreated container on a **temp DB**
(`DATABASE_URL=sqlite:////tmp/sg110verify/db.sqlite`, `STORAGE_ROOT=/tmp/sg110verify/storage`), so the
live DB was untouched (`evidence=13 household=1` before and after, temp dir removed).

Post-restart sweep waived (`PG-DP-02`, restart-gated). Substitute authority: in-process suite
pre-restart + post-restart live probes + the fresh-container 201s. No browser-driven tests exist on this
path — the derived set is empty and differed nowise.

Issues / disagreements / unanswered
-----------------------------------
- Corrected above: 10 brands (not 9), `requirements.lock` is the install path, Pillow-12 AVIF-not-HEIF,
  `allowed_mime_types` is unenforced.
- Minor observation (outside slice, reported not fixed): a HEIC thumbnail is written as
  `<sha>_thumb256.heic` (the pre-existing `thumbnail_path` keeps the source suffix) while its bytes are
  JPEG. The serve route hardcodes `media_type="image/jpeg"`, so this is cosmetically odd but correct on
  the wire. Changing the naming/path scheme is out of this slice's ceiling.
- `model` is reported `unknown` (no `--model` in argv, no provider metadata). Not a failure, a refusal to guess.
- No privileged operation was denied; nothing was left unanswered.

Receipt (notes ref)
-------------------
Work pushed to `automation` (`89d30cc..eae1c43`), worktree clean. No push to `storagegenie-evidence`,
no `{{RECEIPT_CMD}}`. Note added on WORK_HEAD `eae1c43f8b223b49558a26126db828287c9665c0`; notes ref
`refs/notes/storagegenie-coder-reports` pushed (`f69e686..274f598`) and read back from a MAPPED fetch
(`refs/notes/storagegenie-coder-reports-sg110-fetched`). Pasted executed output:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports show eae1c43f8b223b49558a26126db828287c9665c0
Dispatch-ID: SG-110 | Report: docs/worklogs/SG-110_report.md | Work-HEAD: eae1c43f8b223b49558a26126db828287c9665c0
```

Full raw transcript (precheck, add, push, mapped fetch, show) is in `SG-110_verify.log` →
`RECEIPT NOTE VERIFY`. The final tip (this receipt commit) is dual-annotated with the same note
(SG-092 inoculation). final line: `note=yes`.

Three UNCLEAR lines
-------------------
- FIRST READ: whether "exactly `image/heic` / `image/heif`" meant to collapse pillow-heif's sequence brands
  (`image/heic-sequence`) — I collapsed them into the base image MIME; the alternative was to reject them.
- DURING EXECUTION: whether the G3 "HEIC upload 201 through the FRESH server" write was permitted against
  the live DB; the packet also says a write of any kind is a STOP, so I ran the 201 proof on a temp DB
  inside the fresh container and kept the live DB byte-identical.
- REMAINING: model id (CLI default, not readable from argv/metadata); and whether the `_thumb256.heic`
  filename-for-JPEG-bytes naming should be normalised in a later slice.

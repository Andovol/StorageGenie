# SG-128 — Orphan thumbnail cleanup: BLOCKED (delete leg denied by read-only filesystem)

**Dispatch-ID:** SG-128 · **Verdict:** BLOCKED — G0 (enumerate) COMPLETE and non-vacuous; G1 (delete) DENIED as an unanswered privileged step; G2 (serve) is a non-result; G3 (this report) shipped.
**First token:** `SG-128`. **Work dir:** `/home/andrei/StorageGenie`. **Origin remote (as on host):** `git@github.com:Andovol/StorageGenie.git`.
**BASE** (`origin/automation` resolved at start): `eb3d4fa5900a243de32db821161a7785eb013f46` · **WORK_HEAD:** `5524e9f93e91a0fb195317f63aebfffc6da27002` (the BLOCKED work commit holding these 3 worklogs). A docs follow-up tip carries the pasted receipt (noted in the receipt subsection).
**Settings (CO-78, from process arguments / provider metadata — never the identity line):** coder `opencode`; **effort `high`** from process argv `opencode run --auto --dir /home/andrei/StorageGenie --variant high` (pid 1350401 `/proc/<pid>/cmdline`); **model `opencode-go/deepseek-v4.1-flash`** from provider metadata (`~/.local/share/opencode/log/opencode.log`: `providerID=opencode-go`, `modelID=deepseek-v4.1-flash`). **Spend: real $0.000000** (zero metered calls).
**Contract echo (verbatim):** recorded `0.37.0` == published (`1acd773`, D15 adoption). **Source path:** `AGENTS.md` line 3 — "Rule-set version this project records: **0.37.0**". **Finding F-SG128-1:** the contract cache `.rules-cache/` named by `AGENTS.md` Loading is **ABSENT** at `/home/andrei/StorageGenie/.rules-cache` (verified) — the echo is grounded on `AGENTS.md`, not on a live fetch. Not load-bearing for this slice.

## The three criterion questions (PG-SC-09)

- **enumerate — exactly which files are orphans, and why does the rule hold for each?** 14 of the 16 `*_thumb*` files: all are `_thumb<256|512>.png` under 7 PNG evidence. The rule (suffix ≠ `.jpg`) holds for each; the 2 `.jpg` thumbs (one JPEG evidence) are LIVE and excluded. Suffix distribution `{'png': 14, 'jpg': 2}` — non-vacuous.
- **delete — is every deleted path a rule-member and is anything else untouched?** **Zero paths were deleted** — the write was denied (EROFS). No path was touched; 13/13 originals byte-identical (sha256). "Every deleted path is a rule-member" is vacuously true at zero; the non-vacuous check is the 14/14 enumeration classification.
- **serve — did any served status move?** No, but **trivially**: nothing was deleted, so `BEFORE == AFTER` cannot evidence the rule's safety. Reported as a **non-result**, not a pass (anti-vacuity).

## G0 — enumerate by rule (COMPLETE)

Volume resolved read-only (`docker volume inspect storagegenie_storage_data`) → mountpoint `/home/andrei/.local/share/docker/volumes/storagegenie_storage_data/_data`. Full 16-hit `*_thumb*` enumeration with per-file verdicts, sizes and suffix distribution is quoted verbatim in `SG-128_verify.log`. **14 ORPHAN candidates (all `.png`, 904,254 bytes), 2 LIVE `.jpg`, 0 unlisted suffix classes, 0 expected-orphans-that-are-`.jpg`** — the `PG-IC-08` rule gate did not trip.

**Reader premise re-verified in-tree (holds):** `backend/app/storage/local_store.py:10-16` `thumbnail_path` returns `<stem>_thumb<size>.jpg`; `backend/app/api/v1/evidence.py:117` feeds only that resolver to `FileResponse(tp, media_type="image/jpeg")` (`:120`); no other route serves the storage root (`backend/app/main.py` static fallback serves only `SG_STATIC_DIR=/app/static`). The reader resolves **only** the `.jpg` path, so deleting non-`.jpg` rule-members cannot flip a served status.

## G1 — delete exactly the set (BLOCKED / unanswered)

All 14 exact-path `rm -v` commands were prepared (no globs at delete time; full list in `SG-128_verify.log`). The **first executed** command returned:

```
rm: cannot remove '/home/andrei/.local/share/docker/volumes/storagegenie_storage_data/_data/01a0a029-1477-7ca0-b200-bce78a96c679/05/052a5f7b47d0556aace108ea32fbd67f8641c9e940f4a7ef69e1cc92e75a1a45_thumb256.png': Read-only file system
```

**Root cause (finding F-SG128-2):** this Coder process runs in an execution sandbox whose `/` mount is `ro` (`findmnt -T <DATA>` → `/ /dev/vda1 ext4 ro,nosuid,...`); only `/home/andrei/StorageGenie` is bind-mounted `rw`. `touch <DATA>/__wtest` → `Read-only file system` (exit 1), while a touch inside the worktree succeeds. It is **not** a Unix ownership problem (files are `andrei:andrei 644`). The live volume is EROFS to this process. Per the packet's standing line this denied step is reported **unanswered**, and **not routed around** — no `docker exec`, no `sudo`, no re-mount (the packet also sets *Container actions: none*). **Deleted paths: 0. Bytes reclaimed: 0.** Volume listing AFTER is identical to BEFORE (29 files, 6,035,868 bytes; 14 orphans remain).

**Originals untouched (PG-EV-06 spirit):** sha256 of all 13 non-thumb files before vs after → `IDENTICAL`.

## G2 — served regression check (non-result)

GET `/v1/evidence/{id}/thumb/{size}?household_id=…` for all 8 image evidence × {256,512}: 7 PNG → `404` both sides; 1 JPEG → `200` both sides. No `200→404` flip. **Loud caveat:** because no delete occurred, this equality is guaranteed and proves nothing about the rule's safety; the pre-existing PNG `404`s (legacy-PNG gap, F-SG127-2) are quoted as unchanged behaviour, never as proof. `PG-EV-02` is satisfied only in the trivial sense.

## Budget (actual vs bound; units)

| Leg | Actual | Bound | Note |
|---|---|---|---|
| G0 enumerate + reader read | ~129 s | 120 s ordinary | first recon batch slightly over the ordinary bound; no hang |
| G1 delete attempt | <1 s | 120 s | denied immediately (EROFS) |
| G2 served GETs (16) | ~3 s | 120 s | — |
| G3 docs + commit + receipt | ~75 s | 600 s overall | — |

Overall 600 s budget not approached. **Real metered spend $0.000000** (zero calls; no path constructs a metered call).

## Findings / disagreements

- **F-SG128-1** — `.rules-cache/` absent (contract echo grounded on `AGENTS.md`). Not load-bearing.
- **F-SG128-2 (BLOCKING)** — the live volume is read-only to the Coder sandbox; the packet's `STORAGE` leg cannot execute here. The enumeration (the blast radius) is complete and non-vacuous, so the Architect has everything needed to either (a) re-run the delete from a writable context, or (b) authorise a specific alternate mechanism. I did not choose a workaround.
- **F-SG128-3** — G2 is structurally unable to prove the safety case when the delete is denied; flagged rather than reported green.
- No code change, migration, rebuild, recreate, key, DB write, `.tmp` interaction, or metered call occurred. Product diff for this slice is limited to the 3 `docs/worklogs/SG-128.*` files (no `backend/`, `frontend/`, config, or DB change).

## Receipt (notes ref)

Executed, in order (all within bound):

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-128 | Report: docs/worklogs/SG-128_report.md | Work-HEAD: 5524e9f93e91a0fb195317f63aebfffc6da27002" 5524e9f93e91a0fb195317f63aebfffc6da27002
note-add-exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   34ccfa1..4737f96  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
note-push-exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg128-verify
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg128-verify
fetch-exit=0
$ git rev-parse refs/notes/sg128-verify
4737f96a493d21c0804fd420628ad107f78f00f6
$ git notes --ref=refs/notes/sg128-verify show 5524e9f93e91a0fb195317f63aebfffc6da27002
Dispatch-ID: SG-128 | Report: docs/worklogs/SG-128_report.md | Work-HEAD: 5524e9f93e91a0fb195317f63aebfffc6da27002
show-exit=0
```

`note=yes`. Work pushed to `automation` (worktree clean); no push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`. The final docs tip was **dual-annotated** (same message) and its note pushed on the same ref; the fetched-ref `show` above is the executed proof for the work HEAD.

## UNCLEAR

- **FIRST READ:** whether the Coder process could write the live volume at all — the packet's `STORAGE` DELETE grant (`PG-PR-10`) assumes host-path write access, but the sandbox mounts the volume `ro`; resolved at execution as BLOCKED.
- **DURING EXECUTION:** whether to use the container (which mounts the volume `rw`) to perform the delete — decided **NO** per the packet's "denied … never route around it" + "Container actions: none" lines.
- **REMAINING:** the 14 orphan `*_thumb*.png` files are still present (904,254 bytes); the deletion leg needs a writable execution context or an explicit alternate mechanism from the Architect.

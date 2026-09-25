# SG-129 — Orphan thumbnail delete via the container (writable context): probe, delete the 14, prove serving

**Dispatch-ID:** SG-129 · **Verdict:** COMPLETE — G0 re-verified (identical to SG-128) + writability probe PASS; G1 deleted 14/14 exact paths through `docker exec`; G2 BEFORE == AFTER (non-vacuous); G3 this report + worklogs + notes receipt.
**First token:** `SG-129`. **Work dir:** `/home/andrei/StorageGenie`. **Origin remote (as on host):** `git@github.com:Andovol/StorageGenie.git`.
**BASE** (`origin/automation` resolved at start): `0cc8d35c59b2db3fe3aa41f6f43e76f80eeeee06` · **WORK_HEAD:** `<filled in receipt follow-up>` (the work commit holding these 3 worklogs).
**Settings (CO-78, from process arguments / provider metadata — never the identity line):** coder `opencode`; **effort `high`** from process argv `opencode run --auto --dir /home/andrei/StorageGenie --variant high` (pid 1357930 `/proc/1357930/cmdline`); **model `opencode-go/deepseek-v4.1-flash`** from provider metadata (`~/.local/share/opencode/log/opencode.log`: `providerID=opencode-go`, `modelID=deepseek-v4.1-flash`). **Spend: real $0.000000** (zero metered calls).
**Contract echo (verbatim):** `> Rule-set version this project records: **0.37.0** (D15 adoption 2026-09-25: checkout `1acd773` tag `contract-v0.37.0` published …)`. **Source path:** `AGENTS.md:4`. Recorded `0.37.0` == published (`1acd773`, D15). **Finding F-SG129-1:** `.rules-cache/` is **ABSENT** at `/home/andrei/StorageGenie/.rules-cache` (persists F-SG128-1) — the echo is grounded on `AGENTS.md`, not a live fetch. Not load-bearing.
**Grant invoked:** `PG-PR-10` — volume `storagegenie_storage_data` at in-container `/data/storage`, D17, delete of the enumerated set only. Container actions: `exec` for delete + probe only; no restart, no pull, no recreate.

## The three criterion questions (PG-SC-09)

- **enumerate — does SG-128's list still match the volume exactly?** YES. The container's `*_thumb*` listing is byte-for-byte the SG-128 set: 16 hits, 14 `.png` ORPHAN (904,254 B), 2 `.jpg` LIVE; suffix distribution `{'png': 14, 'jpg': 2}`; zero new/missing/suffix delta. Non-vacuous (14 candidates).
- **probe — can this context delete?** YES. `touch` + `rm` of `.__sg129_wtest` in the same `docker exec` leg succeeded (exit 0), proving the volume is RW through the container (the host path is EROFS to the Coder process, per SG-128 F-SG128-2 — not re-proven).
- **serve — did any served status move?** NO. 8 image evidence × {256,512} thumb GETs: BEFORE == AFTER (tag-stripped `diff` exit 0); JPEG 6050ed6f 200→200; 7 PNG 404→404; zero 200→404 flip. Unlike SG-128, this is **non-vacuous** because 14 files were actually removed between the two captures.

## G0 — re-verify enumeration + writability probe (COMPLETE)

Container `storagegenie-backend-1` mounts volume `storagegenie_storage_data` **RW=true** at `/data/storage`. Host↔container mapping quoted: `/home/andrei/.local/share/docker/volumes/storagegenie_storage_data/_data` == `/data/storage`. Full 16-hit enumeration with per-file verdicts and sizes is quoted verbatim in `SG-129_verify.log`. **Enumeration diff vs SG-128: identical — the `PG-IC-08` gate did not trip.** Reader premise re-read and holds: `backend/app/storage/local_store.py:11` `thumbnail_path` returns `<stem>_thumb<size>.jpg`; `backend/app/api/v1/evidence.py:117-120` feeds only that resolver to `FileResponse(..., media_type="image/jpeg")`; the reader resolves **only** `.jpg`, so deleting non-`.jpg` rule-members cannot flip a served status. Writability probe create+remove quoted, exit 0.

## G1 — delete exactly the set (COMPLETE)

14 exact in-container `rm -v` paths (no globs at delete time), each `rm_exit=0`; full list + per-path sizes in `SG-129_verify.log` (sum 904,254 B). Volume **29 → 15 files**, **6,035,868 → 5,131,614 bytes**, bytes reclaimed **904,254**. After-listing shows only the 2 LIVE `.jpg` thumbs. Probe file was created and removed within its own leg and is never counted. `PG-EV-06` spirit: originals sha256 BEFORE == AFTER (13/13 identical). `PG-IC-08` is non-vacuous (14 paths actually removed).

## G2 — served regression check (COMPLETE, non-vacuous)

Status BEFORE and AFTER tables are quoted in `SG-129_verify.log`. `diff` of the tag-stripped tables returned **exit 0** (identical). 200-rows 2 = 2. **No 200→404 flip.** Pre-existing PNG 404s (legacy-PNG gap, F-SG127-2) stayed 404 and are quoted as unchanged, never as proof. **Anti-vacuity:** because 14 files were removed between captures, this equality genuinely exercises the rule — it is not the trivial equality SG-128 could only report.

## Budget (actual vs bound; units)

| Leg | Actual (wall-clock approx.) | Bound | Note |
|---|---|---|---|
| G0 recon + container enumeration + reader read + probe | ~90 s | 120 s ordinary | no leg over bound; no hang |
| G1 exact-path delete (14) | <2 s | 120 s | all `rm_exit=0` |
| G2 served GETs (16) | ~20 s | 120 s | incl. corrected rerun |
| G3 docs + commit + notes receipt | ~90 s | 600 s overall | — |

Leg times are wall-clock approximations from tool-call boundaries. Overall 600 s budget not approached. **Real metered spend $0.000000** (zero calls; no path constructs a metered call).

## Findings / disagreements

- **F-SG129-1** — `.rules-cache/` absent (contract echo grounded on `AGENTS.md:4`). Persists F-SG128-1. Not load-bearing.
- **F-SG129-2 (method, self-caught)** — my first G2 compare returned a false `CHANGED` because the compared string included the `BEFORE`/`AFTER` tag field, and `printf '%s'` without a trailing newline made `while read` drop the last evidence (`f9d71a40`), yielding 14 not 16 rows. Corrected by tag-stripping and a proper newline; rerun over 8 evidence gave `diff` exit 0. No status actually moved. Flagged because a false `CHANGED` would have been a false STOP and the dropped evidence a partially-vacuous table.
- **Observation (not a slice finding)** — the container runs as root, so `docker exec` deletes on this root-owned volume bypass the Coder's Unix ownership; the D17 grant is what bounds the blast radius to the enumerated set. Stated so the mechanism is on record.
- No code change, migration, rebuild, recreate, key, DB write, `.tmp` write, host-path write, or metered call occurred. Product diff for this slice is limited to the 3 `docs/worklogs/SG-129.*` files (`git status --porcelain` empty at G2).

## Cross-product check (PG-IC-01)

G0 needs exec listing + reader read + probe; G1 needs exact-path exec deletes; G2 needs route GETs; nothing else. No criterion demands a rebuild, a DB touch, a key, or any metered call; no cell collides — stated so the check exists on paper.

## Receipt (notes ref)

Commands are executed **after** the work commit; the `show` output is pasted in the receipt follow-up commit (SG-128 precedent). **Status: PENDING — see the follow-up tip for the pasted executed output.** If this subsection reaches the final tip without pasted `show` output, the receipt was not executed and must be reported as such.

<!-- RECEIPT-PASTE-ANCHOR -->

## UNCLEAR

- **FIRST READ:** whether `docker exec` on `storagegenie-backend-1` (root, RW volume) was the intended writable context vs. a workaround — the packet names the container explicitly as the mechanism, D17-authorized; resolved as intended.
- **DURING EXECUTION:** whether a delete that removes files a `.png`-only reader never served could still flip a status — resolved by the BEFORE/AFTER GET tables and the `.jpg`-only resolver read; no flip.
- **REMAINING:** none blocking. Residual: the 7 PNG evidence still return pre-existing 404 thumbs for a **separate** reason (no `.jpg` thumb was ever written for them — the legacy-PNG gap F-SG127-2), untouched by this slice and out of scope.

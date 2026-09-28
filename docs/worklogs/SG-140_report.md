SG-140 — Close-out deploy rider: serve everything landed (rebuild + one recreate + verify)

**GREEN — the landed queue is now served.** Rebuild green, exactly one recreate, health ×6 exact,
gates held, alembic head unchanged, live counts delta 0, served bundle hash moved, live smoke 200.
This is the re-ride of SG-140; the first ride was correctly BLOCKED on a red frontend build and
SG-141 repaired the defect (PRE-1 / F-SG140-1 below).

Settings (CO-78, from process arguments / provider metadata — never the identity line): coder
`opencode`; **model `opencode-go/deepseek-v4.1-flash`** and **effort `high`** read from process argv
`/proc/169935/cmdline`: `opencode run --auto --dir /home/andrei/StorageGenie --model
opencode-go/deepseek-v4.1-flash --variant high`. **Spend: real $0.000000 USD** (zero metered calls).
Work dir `/home/andrei/StorageGenie`; origin `git@github.com:Andovol/StorageGenie.git`.
**BASE** (`origin/automation` requested; resolved): `486d0b4754c15fcdf41ba86bd7e04ef269d596cf` ·
**WORK_HEAD:** `fb72d8362735617376d485ef33f40cfc50517471` (the worklogs commit; this report lives in
the following receipt-paste commit, so it does not carry its own hash — CO-55b).
Gates: **DATABASE** read-only (`alembic current` + mode=ro counts; no write) · **Restart** exactly
ONE `docker compose up -d --force-recreate backend` (the standing close-out grant, `PG-PR-10`;
production restart named plainly per `G-K2`) · **Deploy** that recreate only.
Role guard held (Coder only; no dispatch verb, no unit started/polled).
Contract echo `0.40.0` verbatim; source path `/home/andrei/storagegenie-contract/VERSION`
(host link echoed by SG-138).

> **Premise delta (loud).** (1) The packet's "unserved queue" list stops at SG-138 and does not
> name SG-141; SG-141 is in the tree at BASE and **is the reason this ride can build at all**.
> (2) The packet's product-diff/asks assume a *fresh* dispatch; SG-140 already ran and was rated 98
> as a correct STOP. This is a `--force` re-ride; the worklog paths collide with the blocked ride's
> files, which I supersede in the working tree while citing their commits (PRE-1) — history and the
> notes-ref note on `6494164` are untouched. (3) The stored expectation `20260924_sg114_relation`
> matched exactly, so no STOP.

## G0 — nothing to serve but the queue (reads only): PASS

- Empty product diff vs BASE at start — **quoted empty** (`git diff --stat/--name-only
  origin/automation...HEAD` → no output), worktree clean (`git status --porcelain` empty).
- `alembic current` head **quoted**: `20260924_sg114_relation (head)` — **equals the packet's
  expectation**; newest `.py` in `backend/alembic/versions/` is `20260924_sg114_relation.py`, so no
  migration landed since the last image. No upgrade run.
- Pre-rider baseline: image `sha256:ca29a3dc9a07…` (2026-09-25 — SG-135…139 were indeed unserved);
  container `40a117eaff0c…` Up 2 days (healthy); health exact-shape ×2
  `{"status":"ok","db":"ok","storage":"ok"}` HTTP 200; served entry `/assets/index-DXSEg7CT.js`
  (**sha256 `f435cbc1…`**, 318414 bytes), index.html sha256 `89c1f993…`.
- Gate baseline: `http:80 Host=storagegenie.dynv6.net → 301 https://storagegenie.dynv6.net/`;
  `https:443 → 401`.

## G1 — rebuild + ONE recreate + verify (in this order — `PG-PR-04`): PASS

- **Rebuild** (`BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend`; 300s bound, 18s
  actual): `BUILD_EXIT=0`; new image id **`sha256:995b20df6b705c82bfe5c21c745a7a10d61d0aa8e59b1b7a54c5862ef796a43a`**
  (created 2026-09-28 19:13:36 UTC). The identical command failed at 8s on the first ride — the
  green build is the SG-141 fix taking effect.
- **Exactly ONE recreate** (300s bound, 1s actual): `docker compose up -d --force-recreate backend`,
  `REC_EXIT=0`, log line `Container storagegenie-backend-1 Recreated`. **Container-id change quoted
  (M42 — the proof, never `RestartCount`)**: `40a117eaff0c…` → **`2e623765ce226dc779defcdc67b05820f33ecee5e81d6ac4162e08df5d1057fa`**.
  No second recreate, no restart-loop, no `down -v`.
- Verify: **health exact-shape ×6** = `{"status":"ok","db":"ok","storage":"ok"}` HTTP 200 each;
  **gate** `301` / `401`; **alembic head UNCHANGED** `20260924_sg114_relation (head)`; **live counts
  delta == 0** on all 9 read tables (provider_call 18, job 9, enrich_snapshot 4, candidate 8,
  evidence 13, guardrail_event 2, audit_event 68, asset 6, household 1); **served bundle hash moved**
  `f435cbc1…` (318414 B) → **`fc696d21a99543369424b904395e7f2a55364b76ddcad8294c08dac142cd581a`**
  (318415 B), index.html sha256 `89c1f993…` → `63731edd…`, etag `67e80638…` → `b9ad6305…` (the new
  `HouseholdSelector`/`client.test.ts`-era bundle, quoted by hash — bytes, not rendering).
- **Live smoke through the real seam** (`PG-EV-07`): `GET /v1/assets?household_id=01a0a029-…` →
  **200**, 6 items, `next_cursor:null`; served frontend `GET /` → **200**, 944 bytes.

## G2 — worklog and report: PASS

`docs/worklogs/SG-140.log`, `SG-140_report.md`, `SG-140_verify.log` (G0 proofs, image/container
ids, health ×6, gate, alembic before==after, bundle hashes, counts, smoke). First token `SG-140`.
No secret in any committed artifact (`CO-100` — health bodies carry status strings only).

### Actual-versus-budget per goal (units)
| Goal | Budget | Actual | Note |
|---|---|---|---|
| G0 reads | ≤120s ordinary | ~45s | diff/head/ids/health/bundle/gate/counts |
| G1 rebuild | ≤300s | **18s** | `tsc && vite build` exit 0 |
| G1 recreate | ≤300s | **1s** | exactly one `--force-recreate` |
| G1 verify + smoke | ≤120s ordinary | ~30s | health ×6, gate, counts, bundle, smoke |
| G2 worklogs + notes | ≤120s / 300s push | ~60s | 3 files + note |
| Overall | ≤2400s | well under | no command killed, no hang |
| Spend | $0.000000 USD | **$0.000000 USD** | zero metered calls |

### Official guards (reviewer copies to the rating row)
`PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06` ·
`PG-PR-10` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09`.

### Product-diff ceiling proof (end)
`git diff --stat origin/automation...HEAD -- backend frontend Makefile docker-compose.yml` → empty;
non-product writes are the three `docs/worklogs/SG-140_*` files only.

### Receipt note (M20-corrected block; executed output pasted verbatim)
```
$ git push origin automation
To github.com:Andovol/StorageGenie.git
   486d0b4..fb72d83  automation -> automation
$ git notes --ref=refs/notes/storagegenie-coder-reports add \
    -m "Dispatch-ID: SG-140 | Report: docs/worklogs/SG-140_report.md | Work-HEAD: fb72d8362735617376d485ef33f40cfc50517471" \
    fb72d8362735617376d485ef33f40cfc50517471
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   ad6afbe..4b73661  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg140-r2-fetched
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg140-r2-fetched
$ git notes --ref=refs/notes/sg140-r2-fetched show fb72d8362735617376d485ef33f40cfc50517471
Dispatch-ID: SG-140 | Report: docs/worklogs/SG-140_report.md | Work-HEAD: fb72d8362735617376d485ef33f40cfc50517471
```
Verified against the FETCHED mapped ref (`refs/notes/sg140-r2-fetched`), not the local notes ref.
note=yes (the executed `show` output above is pasted verbatim). The final-tip dual-annotation and
its fetched `show` output are pasted in `SG-140.log`.

### Issues / disagreements (including outside this slice's scope)
- **PRE-1 / F-SG140-1 (resolved):** the first SG-140 ride (6494164, rated 98) stopped on
  `WebAlternates.test.tsx` TS2739 ×3 landed by SG-135 PR #18; SG-141 repaired it; this ride serves.
  The re-dispatch reuses the SG-140 ID, so the three worklog paths collide — superseded in-tree,
  prior commits and note preserved.
- **F-SG140-2 (premise delta, no impact):** the packet's unserved-queue list omits SG-141 and
  presumes a first run; both corrected above.
- **F-SG140-3 (container-vs-image serving proof):** the production UI is baked into the backend
  image (`backend/Dockerfile:20`), so the single backend recreate ships API **and** UI; the
  `frontend` compose service is `profiles: ["dev"]` and its container `1aabf2905704` has been Exited
  ~2 weeks. One recreate is therefore sufficient, as the packet's grant assumes.

### No vacuous pass — stated loudly
- The "empty product diff" is a quoted `git diff` with no output, plus a byte-scoped re-check.
- The recreate is evidenced by a **changed full container id**, not by `RestartCount`.
- Health is the **exact body plus status**, six times.
- The bundle claim is a **sha256 + byte count move**, not a filename change alone.
- The smoke is a **status + item count** (6 == baseline), not a 200 alone.
- A green build is a real `BUILD_EXIT=0` from the same command that failed red on the first ride.

### UNCLEAR
- **FIRST READ:** whether a re-dispatch of an already-rated ID should carry a new worklog path
  rather than overwrite the blocked ride's files; the packet names SG-140's paths, so I followed
  the packet and preserved the prior record by citing its commits.
- **DURING EXECUTION:** none material — build/recreate/verify all behaved exactly as the packet's
  order prescribes; the `--force-recreate` flag is the explicit form of the authorised single
  recreate.
- **REMAINING:** whether the Architect wants the SUPERSEDED blocked ride's worklog files restored
  to their blocked content (e.g. under a `SG-140a` name) for audit convenience; the originals remain
  one `git show 63b37a0:docs/worklogs/SG-140_report.md` away.

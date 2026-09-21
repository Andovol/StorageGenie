# SG-084 — SG-080 failure probe: why the unit exit-coded with no receipt (read-only)

**Branch:** `automation` · **Remote:** `git@github.com:Andovol/StorageGenie.git` · **Work dir:** `/home/andrei/StorageGenie`
**BASE (packet ref `origin/automation`):** `3c84ec2a92fc280b798b3cb16025a10f1804de86` (`D104 recorded (SG-080 failure probe + conditional re-fire)`)
**WORK_HEAD:** `f2f974f4f5e995d45a9a5367c1565a8d9667ecab` (docs commit carrying this report; the post-note, docs-only receipt commit is HEAD after it)
**Contract:** recorded `0.28.2` == published `0.28.2`; source `/home/andrei/storagegenie-contract/VERSION`
**Model / effort (`CO-78`):** model `deepseek-v4.1-flash` (provider `opencode-go` — read from provider metadata: SG-084 dispatch log header `> build · deepseek-v4.1-flash` and `.local/state/opencode/model.json` `recent[0]`; **argv carries no `--model`**, model is the CLI default) · effort `medium` (process argv `/proc/483139/cmdline`: `opencode run --auto --dir /home/andrei/StorageGenie --variant medium`)
**Spend (real $):** `$0.000000` actual vs `$0` bound — zero metered provider calls.
**Autonomy:** `L2` slice (1 retry available; not used).
**Guards:** `PG-EV-02` · `PG-EV-05` · `PG-EV-06` (authority: NONE) · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-01` · `PG-PR-03`.

D104-approved read-only probe (SG-071/D91 verification-first precedent). Role guard honoured: the Coder ran
**no dispatch verb for any ID**, started/polled/retried **no unit**, made no launch change. Root of SG-080's
failure is established below; verdict is **GO** for re-firing `SG-080 --force`.

## Premise verification (a difference is a finding, not an obstacle)

| Packet premise | Measured on 2026-09-21 host | Verdict |
|---|---|---|
| "SG-080's dispatch died BEFORE any Coder work" | SG-080 ran reconnaissance (9 reads + 1 grep) then the LLM provider failed | **difference — F1** |
| "trigger `result=no_receipt`" | `negative_receipt=published`; no positive note on `15f7dd4`; `P3_note=FAIL note=no` | **confirmed (positive receipt absent)** |
| "unit exit-code, status verb `failed`" | `Active: failed (Result: exit-code)`; `run-coder SG-080 code=exited status=1` | **confirmed** |
| "notes ref has no SG-080 note" | no *positive* receipt, but a *negative* `Negative-Receipt-ID: SG-080` IS present | **difference — F2** |
| "`origin/automation` tip untouched at the packet commit" | at failure `START=END=15f7dd4`; **now** tip `3c84ec2` (2 commits ahead) | **difference — F3 (post-failure)** |
| Contract recorded == published | `/home/andrei/storagegenie-contract/VERSION` = `0.28.2` | **confirmed** |

## G1 — host tree + packet presence

- `git status --porcelain` → **empty** (clean; no dirt). Raw output in `SG-084_verify.log`.
- `git rev-parse HEAD` = `git rev-parse origin/automation` = `3c84ec2a92fc280b798b3cb16025a10f1804de86` (equal — no gap).
- `git log --oneline -3`:
  ```
  3c84ec2 D104 recorded (SG-080 failure probe + conditional re-fire)
  e06dc0b D104: SG-084 probe packet (SG-080 unit failure, conditional re-fire on GO)
  15f7dd4 SG-080: ingest pipeline on v3 packet (D101 track slice 2)
  ```
- **Commits AFTER the packet commit `15f7dd4` (finding):** `e06dc0b` and `3c84ec2`. Both are the Architect's
  D104 probe-metadata commits; `git diff --stat 15f7dd4..HEAD` touches only `STATE.md` and
  `docs/packets/SG-084-sg080-failure-probe.md`. Neither touches the SG-080 packet or any product file.
- **Packet presence/content:** `docs/packets/SG-080-ingest-pipeline-v3.md` exists at the checked-out tip
  (`rw-r--r--`, 14.0K), sha256 `d5e537eaa0baf0ef07a857d097cd400601d1f5edabfeaabb15e3f40efaa30afd`. Last commit
  touching it is `15f7dd4`; `git diff 15f7dd4..HEAD -- <packet>` is **empty** → content is byte-identical to
  the dispatched content. No `packet_missing`-class cause.

## G2 — launch preconditions + unit failure evidence

- **Disk (`df -h / /tmp /home`)** — all on `/dev/vda1`:
  ```
  Filesystem      Size  Used Avail Use% Mounted on
  /dev/vda1       232G  110G  122G  48% /
  /dev/vda1       232G  110G  122G  48% /tmp
  /dev/vda1       232G  110G  122G  48% /
  ```
  Not full (122G avail). Not a disk-space failure.
- **Docker daemon (read-only):** `docker info` → `29.6.2 containers=2 images=2` (exit 0);
  `docker images -q | wc -l` → `2`. Daemon reachable; deny-free. No build/pull/run/exec/inspect performed.
- **Unit (`systemctl status dispatch-storagegenie@SG-080.service`):**
  ```
  × dispatch-storagegenie@SG-080.service - Confined Coder slice SG-080
       Loaded: loaded (/etc/systemd/system/dispatch-storagegenie@.service; static)
       Active: failed (Result: exit-code) since Mon 2026-09-21 14:24:59 UTC
      Process: 480953 ExecStart=/usr/local/lib/dispatch/run-coder SG-080 (code=exited, status=1/FAILURE)
  ```
- **Journal (`journalctl -xeu ...`)** — earliest error line (line 56 of the unit journal):
  ```
  run-coder[480953]:   Error: Upstream request failed: [server_error] Upstream response was not valid JSON
  ```
  **It attributes the failure to the upstream LLM provider** — not packet fetch, not worktree dirt, not the
  runner, not lane tooling. Preceding lines: `contract_sync=refresh version=0.28.2` then the Coder's recon
  reads. The final dispatch block:
  ```
  DISPATCH_RESULT id=SG-080 coder=opencode exit=1 head=15f7dd466794b2476c0c8240af2a38aafe5f099e note=no moved=no rewrite=no dirty=no elapsed=21s budget=2100s
  P1_moved=FAIL count=0
  P2_rewrite=PASS behind=0
  P3_note=FAIL note=no
  P5_receipt=FAIL
  P6_dirty=PASS dirty=no
  negative_receipt=published
  ```
  The Coder exited on the provider error after ~21s of recon; `moved=no`/`count=0` → zero commits, so no
  positive receipt. The runner correctly published a **negative** receipt instead.
- **Negative receipt (raw evidence):** on `refs/notes/storagegenie-coder-reports`, object
  `97dec23030d0419570cd8d23752e2753bd43f96f`:
  ```
  Negative-Receipt-ID: SG-080
  utc=2026-09-21T14:24:56Z
  DISPATCH_RESULT id=SG-080 coder=opencode exit=1 head=15f7dd4... note=no moved=no rewrite=no dirty=no elapsed=21s budget=2100s
  ...
  ```
  Confirmed on the **remote** notes ref via a mapped fetch (`refs/notes/sg084-notes-check`), so F2 is a
  remote fact, not a local-only artifact.
- **Dispatch residue — criterion and result.** Criterion: any path matching `*SG-080*`/`*sg-080*` under
  `/home/andrei`, `/run`, `/tmp`, `/var/tmp`, `/var/lib`, `/var/lock` (maxdepth 5, excluding
  `StorageGenie/.git`). My expectation: none outside version control. Actual:
  ```
  /home/andrei/StorageGenie/output/dispatch/SG-080.launcher.sh
  /home/andrei/StorageGenie/output/dispatch/SG-080.log
  /home/andrei/StorageGenie/docs/packets/SG-080-ingest-pipeline-v3.md
  ```
  The two `output/dispatch/` files are **untracked, gitignored residue** (`output/dispatch/.gitignore` = `*`);
  they are the launcher script and the Coder's terminal log, with no claim/lock semantics. No per-ID claim
  marker or lock file was found under `/run`, `/var/lib` (`/var/lib/dispatch` and `/run/dispatch` do not
  exist), `/tmp` or `/var/lock`. Residue is therefore inert and does not block a re-fire.

## G3 — verdict

**GO** for re-firing `SG-080 --force`.

One-line reason: **the unit died on a transient upstream LLM-provider error with zero commits, and every
re-fire precondition holds — tree clean, SG-080 packet byte-identical to the dispatched content, disk 48%,
daemon reachable.**

Blocker class: **none in-repo; external/transient provider.** There is no Architect-fixable packet change and
no desk-side (unit/journal) defect: the runner's confinement, receipt and negative-receipt machinery all
behaved correctly. If the provider error recurs, the class is **owner-side** (provider reliability), not a
rule or tree defect — no follow-up slice is required.

Literal-criterion note (`PG-EV-05`): the criterion "tip == packet commit" is **not literally met** — the tip
is `3c84ec2`, two commits ahead of `15f7dd4`. Those two commits are the probe's own D104 metadata commits
(`e06dc0b`, `3c84ec2`); the packet file is unchanged since `15f7dd4`. At failure time `START=END=15f7dd4`, so
the dispatch target was the packet commit then. The literal condition can never re-hold once the probe packet
is committed; I record the deviation and still return GO on the substantive conditions. **No auto-retry was
performed.**

## Acceptance criteria

- Tree state quoted (porcelain empty + HEAD == origin/automation + log -3) — **done**.
- Packet presence/content verdict quoted (sha256 + empty diff vs `15f7dd4`) — **done**.
- Disk + daemon outcomes quoted; unit status/journal tail quoted (not `unanswered`); residue enumeration with
  criterion + difference reported — **done**.
- GO/NO-GO with one-line reason and blocker class; no auto-retry — **done**.
- $0; no writes outside `docs/worklogs`; no vacuous pass — **done** (all 3 worklog files written; every
  criterion exercised against real fetched/executed output; the empty-porcelain result is quoted, not
  inferred).

## Receipt note (M20-corrected block)

Work pushed to `automation` (`3c84ec2..f2f974f  automation -> automation`), worktree clean at commit
time. No push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`.

Added the note on work HEAD `f2f974f4f5e995d45a9a5367c1565a8d9667ecab` (120s bound), pushed the notes ref
(300s bound): `e93d7b4..fa22ef2  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports`.
Verified against a **mapped** fetch (`refs/notes/storagegenie-coder-reports:refs/notes/sg084-verify`), then
`git notes --ref=refs/notes/sg084-verify show f2f974f...` — executed output pasted verbatim:

```
$ git notes --ref=refs/notes/sg084-verify show f2f974f4f5e995d45a9a5367c1565a8d9667ecab
Dispatch-ID: SG-084 | Report: docs/worklogs/SG-084_report.md | Work-HEAD: f2f974f4f5e995d45a9a5367c1565a8d9667ecab
```

A pre-add existence check returned `error: no note found for object f2f974f...` (no existing-note
refusal). Final line: `note=yes`.

## UNCLEAR

- **FIRST READ:** whether "no receipt" meant *no positive receipt* (the negative receipt is present) — the
  packet's phrasing could be read as "no note at all", which the notes ref contradicts.
- **DURING EXECUTION:** the failure reproduced the exact provider message; I could not confirm whether the
  trigger's `result=no_receipt` classifier distinguishes a provider death from a runner death without reading
  the dispatch engine's trigger source, which is outside this slice's read ceiling (not attempted).
- **REMAINING:** whether re-firing `SG-080 --force` will hit the same transient provider error; unanswerable
  read-only and unmeasured here (no retry performed, per the role guard).

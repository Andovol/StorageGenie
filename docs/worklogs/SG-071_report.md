# SG-071 — dispatch probe: why did the SG-066 unit fail at launch

**Dispatch:** SG-071 · coder: opencode · effort: medium (read from process argv `--variant medium`)
**Model:** `deepseek-v4.1-flash` — **provider metadata**, source `~/.local/share/opencode/log/opencode.log` run=`d497a8d9` line `llm.provider=opencode-go llm.model=deepseek-v4.1-flash`. No `--model` on argv (CLI default, omitted per policy); not read from any system-prompt identity line.
**Contract:** recorded `0.28.2` == published (`0.28.2`); source path `/home/andrei/storagegenie-contract/VERSION`; contract repo HEAD `b495b59b3426af66772a87939473ac558f8f72d2` (`contract-v0.28.2`).
**Work dir:** `/home/andrei/StorageGenie` · **origin:** `git@github.com:Andovol/StorageGenie.git`
**BASE ref:** `origin/automation` · **resolved:** `cc4a53151ae364d4615d7c2532a7132f773ecf55`
**Work HEAD (BASE):** `cc4a53151ae364d4615d7c2532a7132f773ecf55` · **WORK_HEAD:** see Receipt below (docs-only work commit).
**Spend:** real **$0.000000** (zero metered calls; read-only probe).

---

## Outcome (one line)

**The packet's premise is wrong: SG-066's unit did NOT fail before any Coder work.** The Coder launched and ran **299 s**, wrote **11 files / +1776 lines**, ran the backend suite (15 passed, 2 failed), and was mid-fix when the opencode CLI terminally aborted with `Error: Upstream request failed: [server_error] Upstream response was not valid JSON`. Exit 1, no commit, no receipt → the engine published a Negative-Receipt and quarantined the debris. **Verdict: GO** to re-fire `SG-066 --force`.

---

## Legs — actual vs budget (units per leg)

| Leg | Actual | Bound | Margin |
|---|---|---|---|
| Recon G1 (status/HEAD/packet/log) | ~8 s | 60 s | under |
| G2 disk + docker (read-only) | ~4 s | 60 s | under |
| G2 residue enumeration (engine state, unit, journal, quarantine, note) | ~35 s | 60 s | under |
| G3 root-cause assembly + report | ~55 s | 60 s | under |
| **Overall (unit start 09:59:59Z → final commit)** | **~200 s** | 300 s | under |

No command was killed; no interactive command was run.

---

## G1 — host tree + packet presence

- `git status --porcelain` → **(empty)** (tree clean; not dirty).
- `git branch --show-current` → `automation`.
- `git rev-parse HEAD` → `cc4a53151ae364d4615d7c2532a7132f773ecf55` **==** `git rev-parse origin/automation` → `cc4a53151ae364d4615d7c2532a7132f773ecf55`. **Equal — expected.**
- `git log --oneline -3`:
  ```
  cc4a531 D91: SG-071 dispatch probe packet (SG-066 launch failure)
  65536de D90: SG-066 analytics Insight Agent packet (split scope)
  c8b11e1 D89 bot branch policy + opencode.json gitignore + SG-066 priority
  ```
- The only commit after the SG-066 packet commit `65536de` is `cc4a531` (D91 — this very probe packet, authored intentionally). **No unexplained mid-window bot merge.**
- **Packet present with dispatched content:** `docs/packets/SG-066-analytics-insight-agent.md` exists, 12938 B. `git diff 65536de HEAD -- <packet>` → **empty**; blob `HEAD:` = `b3af8c09f2864963726714cafb70847f732f5596` **==** `65536de:` = `b3af8c09f2864963726714cafb70847f732f5596`. Packet is byte-identical to the dispatched commit. **Not a `packet_missing`-class failure.**

## G2 — launch preconditions (read-only, non-mutating)

- **Disk:** `df -h /home/andrei/StorageGenie` and `/tmp` both `/dev/vda1 232G 109G 124G 47%`. **124 GB free — not full.**
- **Docker (read-only):** `docker info --format '{{.ServerVersion}} {{.Containers}} {{.Images}}'` → `29.6.2 2 2`; `docker images -q | wc -l` → `2`. **Daemon reachable.** No build/pull/run/exec/inspect performed.
- **Residue enumeration.** *Criterion:* per-ID durable state the dispatch engine leaves readable for an ID whose unit failed at launch. *Expectation stated:* none expected under the legacy wrapper's runtime dir, and I also enumerate the live engine's per-ID state.
  - Legacy `$STATE=/run/user/1000/storagegenie-dispatch` → **absent** (`No such file or directory`). Matches expectation.
  - **Actual residue (live engine `/usr/local/bin/dispatch` + `run-coder`):**
    - `output/dispatch/SG-066.launcher.sh` (224 B) + `output/dispatch/SG-066.log` (130.9 K) — gitignored (`output/dispatch/.gitignore:*`).
    - systemd unit `dispatch-storagegenie@SG-066.service` **loaded failed / failed** (retained).
    - `refs/quarantine/SG-066-20260921T095958Z` = `ae29ca495209d4e278ea4d5b1569d32b58cd663a` — "quarantine: debris from SG-066 (no receipt)", 11 files / +1776.
    - Note object `852f055f4488ddd43f29f6e51fb40ecf321de1ae` in `refs/notes/storagegenie-coder-reports`: `Negative-Receipt-ID: SG-066`.
    - `.git/dispatch_last_id` = `SG-071` (this run; `SG-066` before it); `.git/dispatch.lock` present (this run holds it); `.git/dispatch_known_hosts` present.
    - `~/.local/state/opencode/locks/` empty (see finding).

### Root cause of the SG-066 failure (the slice's deliverable)

The live engine is **not** `/opt/storagegenie-dispatch/dispatch_coder.sh` (that wrapper whitelists only `grok|codex` and is stale — a filing error in `AGENTS.md`'s Wrapper row). The storagegenie forced command is `DISPATCH_CONF=/etc/dispatch/storagegenie.conf /usr/local/bin/dispatch`; `run-coder` reads `coder:`/`effort:` **from the packet head**, so `coder: opencode` was honored and the launcher was written as:

```
exec opencode run --auto --dir /home/andrei/StorageGenie --variant medium "$(cat "$PROMPT_FILE")"
```

Evidence that the Coder **did work**, contradicting the premise:

- journal `DISPATCH_RESULT id=SG-066 coder=opencode exit=1 … elapsed=299s`; `P1_moved=FAIL`, `P3_note=FAIL`, `P5_receipt=FAIL`, `P6_dirty=FAIL dirty=yes`; `negative_receipt=published`; `advisory_failed=P1_moved,P3_note,P6_dirty`.
- The engine's dirty-tree gate then preserved the debris as `refs/quarantine/SG-066-20260921T095958Z` (`ae29ca4`, 11 files, +1776 — the analytics service/tests/UI).
- `output/dispatch/SG-066.log` (the exact launch artifact) shows the full session: it generated code, ran `pytest` (`2 failed, 15 passed`), and was mid-edit on `backend/tests/test_analytics.py` when the last line fired:
  ```
  Error: Upstream request failed: [server_error] Upstream response was not valid JSON
  ```

**Terminal cause: a transient upstream provider fault** (the model API returned non-JSON — `[server_error] Upstream response was not valid JSON`), which aborted the CLI mid-slice at 299 s. It is **not** a launch precondition and **not** deterministic. No commit → no receipt → Negative-Receipt.

**Secondary environment finding (non-fatal, Architect-fixable):** the opencode process also logged, at launch (09:49:01Z), `EROFS: read-only file system, mkdir '/home/andrei/.local/state/opencode/locks/<hash>.lock'`. The unit's `ReadWritePaths` grants `/home/andrei/.local/share/opencode` but **not** `/home/andrei/.local/state/opencode`; `CODER_STATE_DIR` in `/etc/dispatch/storagegenie.conf` lists only the former. The run continued 299 s after this error, so it was **not** the terminal cause, but it silently denies opencode its lock/kv state. **Follow-up (Architect):** add `/home/andrei/.local/state/opencode` to `CODER_STATE_DIR` and re-emit the drop-in via `run-coder --emit-dropin`.

**Premise correction (notes ref):** "notes ref has no SG-066 note" is **not exactly true** — there *is* a note (`Negative-Receipt-ID: SG-066`). It is a Negative-Receipt, not a `Dispatch-ID:` receipt, so the replay guard correctly does not treat it as a receipt. Reporting the distinction rather than the absolute.

## G3 — verdict

**GO** to re-fire `SG-066 --force`.

One-line reason: every packet-stated GO condition holds (tree clean; `HEAD == origin/automation == cc4a531`; SG-066 packet present and byte-identical to the dispatched blob `b3af8c0`; disk 124 GB free; docker daemon reachable), and the prior failure was a **transient upstream provider error**, not a launch or precondition defect — with the debris preserved on a host-local quarantine ref so re-firing destroys nothing.

**Blocker classification (for the record, none gating the GO):**
- No blocker to the GO.
- Architect-fixable (optional follow-up): the `~/.local/state/opencode` EROFS gap (add to `CODER_STATE_DIR`; re-emit drop-in).
- Desk-side: stale `AGENTS.md` Wrapper row naming `/opt/storagegenie-dispatch/dispatch_coder.sh` (actual = `/usr/local/bin/dispatch` via `/etc/dispatch/storagegenie.conf`); `dispatch_last_id`/lock live in `.git/`, not the named wrapper.
- Owner-side: none identified.

**Vacuous-pass check:** every criterion is a **read**; there is no test/suite whose function could go uninvoked, no diff to be empty, and no skipped gate. The one premise that could have been reported vacuously ("notes ref has no SG-066 note") is explicitly refuted above, not passed.

**Guards invoked:** `PG-EV-02` · `PG-EV-05` · `PG-EV-06` (authority: NONE) · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-01` (enumerate with non-mutating forms only) · `PG-PR-03`.

---

## Receipt — notes-ref note on WORK_HEAD (executed; output pasted verbatim)

**Work HEAD (note target):** `015d63214bf6d6ec9fffa0006ad4ef316bf79cdc`

Executed commands and their verbatim output:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add \
    -m "Dispatch-ID: SG-071 | Report: docs/worklogs/SG-071_report.md | Work-HEAD: 015d63214bf6d6ec9fffa0006ad4ef316bf79cdc" \
    015d63214bf6d6ec9fffa0006ad4ef316bf79cdc
rc=0

$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   350bf8e..eaf2bc6  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
ok refs/notes/storagegenie-coder-reports

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-sg071-verify
ok fetched (1 new refs)

$ git notes --ref=refs/notes/storagegenie-coder-reports-sg071-verify show 015d63214bf6d6ec9fffa0006ad4ef316bf79cdc
Dispatch-ID: SG-071 | Report: docs/worklogs/SG-071_report.md | Work-HEAD: 015d63214bf6d6ec9fffa0006ad4ef316bf79cdc
rc=0
```

Fetched ref tip: `refs/notes/storagegenie-coder-reports-sg071-verify` = `eaf2bc6d12de638da102538962ca7c3d58b401db`; `grep -c "Dispatch-ID: SG-071"` = 1; first line carries both `Dispatch-ID:` and `Report:` (`CO-97`).

**note=yes**

---

## UNCLEAR

- **FIRST READ:** The packet said the unit "failed BEFORE any Coder work"; the first read of the tree (dirty=yes, a quarantine commit holding 1776 lines of analytics code, and a 299 s `DISPATCH_RESULT`) made it clear the opposite was true. The premise was the single largest uncertainty at entry.
- **DURING EXECUTION:** Two engine facts had to be discovered by reading, not from the packet: (1) the live dispatch path is `/usr/local/bin/dispatch` + `/etc/dispatch/storagegenie.conf`, not the `AGENTS.md`-named wrapper; (2) the opencode `EROFS` on `~/.local/state/opencode` is a real (non-fatal) confinement gap. Both shift blame away from "launch" and toward a transient provider error.
- **REMAINING:** Whether re-firing will hit the same `Upstream response was not valid JSON` is unknowable from here (transient vs recurring provider behaviour); and whether the opencode `~/.local/state` EROFS silently degrades any success path (session state/kv) is unproven — both need a future slice, the latter an Architect drop-in fix.

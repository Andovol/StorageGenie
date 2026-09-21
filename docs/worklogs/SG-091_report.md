# SG-091 — SG-088 failure probe: read-only diagnosis of the 221s exit-1 with zero commits and a dirty tree

**Dispatch-ID:** SG-091
**Work dir:** `/home/andrei/StorageGenie`
**Origin remote (as on host):** `git@github.com:Andovol/StorageGenie.git` (fetch+push)
**BASE (start HEAD):** `339bf4e9eaf22b6938b71bb8522708f9a40c9cfb` = `origin/automation`
**WORK_HEAD:** `TBD` → filled by the docs commit carrying this report (see Receipt subsection; pre-note docs commit).
**Contract:** recorded `0.28.2` == published `b495b59` — source path `/home/andrei/storagegenie-contract/VERSION`; `git -C /home/andrei/storagegenie-contract rev-parse HEAD` = `b495b59b3426af66772a87939473ac558f8f72d2`.
**Model / effort (CO-78, from process arguments):** model `unknown` (argv carries no `--model`; CLI default); effort `medium` (argv `--variant medium`). Source: ancestor process `opencode run --auto --dir /home/andrei/StorageGenie --variant medium …`. The SG-088 lane's own provider banner (raw, from `output/dispatch/SG-088.log:2`) is `> build · deepseek-v4.1-flash` — quoted as observed metadata, not used as the identity of this process.
**Spend:** **$0.000000 actual** — zero provider calls; containment per `PG-PR-04` stated: nothing live exists to contain.
**Live clock at open:** `2026-09-21T17:48:41Z`.

## Verdict (G4): **GO** — transient-shaped death, re-fire is warranted

SG-088 was killed by a provider-side upstream failure, not any runner-side or repo-side fault. The
launcher, CLI, packet resolution and base state all check out. The debris is fully attributable to the
failed slice and the attribution classification the packet predicted is confirmed — the dirt gate
**already** quarantined it (commit `dd13458`) before this probe ran. One caveat is stated loudly in
G2/G4: the residue is a **mix** of *partial work* (the slice's two own target files) and *scratch logs*,
not scratch-only.

---

## G0 — packet + base resolution on the host (could the slice run at all?)

**Packet resolution (exactly-one).** `docs/packets/SG-088-*.md` resolves to exactly one file:

```
664  SG-088-derived-registry.md  10.2K
```

Dispatch-params head, quoted raw (`docs/packets/SG-088-derived-registry.md:3-5`):

```
**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium
```

**Reachability of `dd2bb9c` (ancestor form — never `HEAD ==`, `PG-IC-07`):**

```
$ git merge-base --is-ancestor dd2bb9c origin/automation; echo ancestor_exit=$?
ancestor_exit=0
$ git log --oneline -1 dd2bb9c
dd2bb9c SG-088 packet: derived table registry, remove EXPECTED_TABLES static copy (tests-only, D107 slice 4)
```

`dd2bb9c` is an ancestor of `origin/automation`; the check is an ancestor check, not an equality. PASS.

## G1 — unit journal (what killed it?)

Bounded read, 120s: `timeout 120 journalctl --no-pager -u dispatch-storagegenie@SG-088.service -n 200`.
Journal was readable (no privilege denial). The decisive runner line, raw:

```
Sep 21 17:46:49 ubuntu run-coder[591863]: DISPATCH_RESULT id=SG-088 coder=opencode exit=1 head=dd2bb9c1a179513b50c5772a19befa24214f5dd8 note=no moved=no rewrite=no dirty=yes elapsed=221s budget=2100s
```

This matches the Architect's quoted negative receipt exactly (utc 17:46:49Z, exit=1, head=dd2bb9c,
note=no, moved=no, rewrite=no, dirty=yes, elapsed=221s, budget=2100s). The runner-side audit:

```
P1_moved=FAIL count=0
P2_rewrite=PASS behind=0
P3_note=FAIL note=no
P5_receipt=FAIL
P6_dirty=FAIL dirty=yes
negative_receipt=published
...
files: count=0
DIRTY
status:
   M backend/tests/test_plugin_taxonomy.py
   M backend/tests/test_postgres_dialect.py
  ?? docs/worklogs/SG-088.log
  ?? docs/worklogs/SG-088_verify.log
```

The runner's captured `log_tail` ends with the causal line (raw from the journal):

```
Sep 21 17:46:52 ubuntu run-coder[591863]:   Error: Upstream request failed: [server_error] Upstream response was not valid JSON
```

**`run_coder=fail reason=` presence/absence, raw count:** **0**.

```
$ timeout 120 journalctl --no-pager -u dispatch-storagegenie@SG-088.service | grep -c 'run_coder=fail'
0
$ ... | grep 'run_coder='
(no output; exit=1)
```

So no explicit `run_coder=fail reason=` line exists; the failure is carried by the lane log's terminal
`[server_error]` line and the `DISPATCH_RESULT … exit=1` audit line. There is exactly one
`DISPATCH_RESULT id=SG-088` line (`grep -c` = 1), and `negative_receipt=published` is present.

## G2 — CLI smoke + debris inventory (does the Coder start, and what was left?)

**CLI smoke (bound 120s):**

```
$ timeout 120 opencode --version
1.17.19
cli_exit=0
```

The CLI starts and exits 0. **Finding (out of scope):** `AGENTS.md` records OpenCode CLI `1.18.31`
(measured 2026-09-17); the host now reports `1.17.19`. Either a downgrade or a stale doc entry — named
here, not acted on.

**Debris inventory (current tree, raw) — DIVERGES FROM THE PACKET PREMISE.** The packet states the
dispatch left the tree DIRTY and that the dirt gate *will* quarantine it. At probe time the tree is
**clean**:

```
$ git status --porcelain
(empty)
status_exit=0
```

`git status --porcelain --ignored` shows only standard ignored caches/venvs (`data/`, `output/`,
`venv/`, `__pycache__`, `.env`, …) — no tracked modification and no untracked source.

**The quarantine the packet predicted has ALREADY happened.** Reflog, raw:

```
339bf4e HEAD@{0}: reset: moving to origin/automation
dd2bb9c HEAD@{1}: reset: moving to HEAD~1
dd13458 HEAD@{2}: commit: quarantine: debris from SG-088 (no receipt)
dd2bb9c HEAD@{3}: reset: moving to origin/automation
```

```
$ git show --stat --oneline dd13458
dd13458 quarantine: debris from SG-088 (no receipt)
 backend/tests/test_plugin_taxonomy.py  |   5 +-
 backend/tests/test_postgres_dialect.py |  34 +---
 docs/worklogs/SG-088.log               |  46 ++++++
 docs/worklogs/SG-088_verify.log        | 282 +++++++++++++++++++++++++++++++++
 4 files changed, 338 insertions(+), 29 deletions(-)
$ git branch --contains dd13458
(no output; not on any branch - dangling quarantine commit)
```

**Attribution classification confirmed:** all four entries are traceable to SG-088's own target files
plus its own worklogs, matching the failed slice exactly. No rogue/unknown state exists. Classification
per entry:

| Entry | Class | Basis |
|---|---|---|
| `M backend/tests/test_postgres_dialect.py` | **partial work** | SG-088's own target file (the static `EXPECTED_TABLES` copy); edits interrupted mid-slice |
| `M backend/tests/test_plugin_taxonomy.py` | **partial work** | SG-088's own consumer/target file (`:25` import); edits interrupted mid-slice |
| `?? docs/worklogs/SG-088.log` | **scratch log** | SG-088's own worklog (46 lines) |
| `?? docs/worklogs/SG-088_verify.log` | **scratch log** | SG-088's own verify log (282 lines) |

**Loud caveat (no vacuous pass):** the GO predicate's words "the debris is scratch-class" hold only for
the two worklogs; the two modified test files are *partial work*, not scratch. I do **not** call the
whole set scratch. What matters for re-fire is that nothing here is unexplained or persistent — every
entry is attributable to SG-088 and the quarantine already captured it. Verdict remains GO on that basis.

Base state confirms the debris was reverted (not silently retained): the removed static set is back at
HEAD, so SG-088's edits did not land — consistent with `P1_moved=FAIL count=0`:

```
backend/tests/test_postgres_dialect.py:35:EXPECTED_TABLES = {
backend/tests/test_postgres_dialect.py:59:    assert metadata_tables == EXPECTED_TABLES
backend/tests/test_postgres_dialect.py:65:    assert set(ddl) == EXPECTED_TABLES
backend/tests/test_plugin_taxonomy.py:25:from tests.test_postgres_dialect import EXPECTED_TABLES
backend/tests/test_plugin_taxonomy.py:62:    assert before == EXPECTED_TABLES
backend/tests/test_plugin_taxonomy.py:83:    assert after == before == EXPECTED_TABLES
```

Nothing was moved, deleted, or touched by this probe; the closing re-list is identical to the opening
(status empty → status empty).

## G3 — launcher artifact (what exactly ran?)

Path hypothesis verified on target: `output/dispatch/SG-088.launcher.sh` exists. Raw:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd /home/andrei/StorageGenie
PROMPT_FILE=docs/packets/SG-088-derived-registry.md
exec opencode run --auto --dir /home/andrei/StorageGenie --variant medium "$(cat "$PROMPT_FILE")"
```

Exact `opencode` argv: `opencode run --auto --dir /home/andrei/StorageGenie --variant medium "<packet text>"`.

Lane log `output/dispatch/SG-088.log` (1026 lines). Provider/model banner (line 2, raw):

```
> build · deepseek-v4.1-flash
```

LAST line (raw, `tail -c 300 | cat -v`; ANSI stripped in the final line shown):

```
Error: Upstream request failed: [server_error] Upstream response was not valid JSON
```

Both artifacts were readable; no refusal occurred.

## G4 — verdict GO vs NO-GO

**GO.** Discriminating lines, all quoted above:

- Packet resolved exactly-one and `dd2bb9c` reachable (G0) — the slice *could* run.
- CLI starts: `opencode --version` → `1.17.19`, exit 0 (G2).
- Death is transient-shaped / provider-side: `Error: Upstream request failed: [server_error] Upstream response was not valid JSON` (the terminal line of both the lane log and the journal's captured `log_tail`). This is the same failure shape SG-090 diagnosed for SG-085 (upstream `server_error`).
- No runner-side fault: `run_coder=fail reason=` count = 0; `P2_rewrite=PASS`; `product_touch=no`; `sql_touched=no`; the failure occurred *after* the Coder had been working (writing `docs/worklogs/SG-088.log` at 17:46:30Z) while mid-verification.
- Debris is attributable and already quarantined (`dd13458`), with no unexplained/rogue state.

**Fix home on NO-GO:** not applicable — verdict is GO. Had it been NO-GO, the persistent root would be
the upstream provider transport, and the owner would be a transport/provider-policy slice (the
`ISS-6` provider-unproven line), **not** a code slice inside `backend/tests`. `SG-088 --force` is
therefore cleared to fire on this probe's GO.

**No vacuous pass.** The one place a GO could pass on a hole — "debris is scratch-class" — is explicitly
narrowed: two of four entries are partial work, and I say so rather than report a clean scratch-only
pass. All other legs are backed by pasted raw output.

**Negative-receipt path note:** this probe is *not* a zero-commit probe — it commits this report and its
log, so the positive notes-ref receipt path applies (Receipt subsection). Had the commit been forbidden,
the receipt subsection would be replaced by an explicit negative-receipt statement, never left silent.

## Constraints / cross-product (`PG-IC-01`)

- Writes: `docs/worklogs/SG-091_report.md` and `docs/worklogs/SG-091.log` only.
- Reads: host packet file, unit journal, `opencode --version` smoke, `git status`/reflog/ls inventory,
  run-dir launcher/log. No container image pull/run.
- No provider call, no `--force`, no re-trigger, no quarantine invocation, no restart, no deploy, no
  production contact. Nothing moved or deleted (`PG-PR-04` — nothing live stated; nothing live exists).
- Simplicity (`G-A7`): four reads + inventory + verdict + worklog; no fix attempt.

## Receipt

Push work to `automation`; worktree clean. No push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`.
Note added on the work HEAD, pushed to `refs/notes/storagegenie-coder-reports`, then fetched into a
mapped local ref and shown verbatim:

<!-- RECEIPT-SHOW-BEGIN -->
_(filled after commit+push+note; pasted `git notes show` output goes here)_
<!-- RECEIPT-SHOW-END -->

## Acceptance criteria → question answered (`PG-SC-09`)

- Packet resolution (exactly-one) + reachability verdict quoted — G0: could the slice run at all? **Yes.**
- Journal tail raw quoted; `run_coder=fail` raw count 0 — G1: what killed it? **Upstream `server_error`.**
- CLI smoke raw; launcher argv + banner + last line quoted — G2/G3: does the Coder start, what ran? **Yes; quoted.**
- Debris inventory raw with per-entry classification; NOTHING moved/deleted proven by identical re-list — G2: what was left? **Partial work + scratch logs, already quarantined.**
- GO/NO-GO carried by quoted evidence; fix home named on NO-GO — G4: **GO (re-fire); fix home N/A.**
- Worklog committed; $0.000000; no vacuous pass — **met.**

## UNCLEAR

- **FIRST READ:** whether SG-088's debris was still present. The packet's future tense ("will … quarantine") read as if the residue were live; it was already quarantined (`dd13458`) and reset away, leaving a clean tree. The packet's dirt-gate premise was stale at authoring-vs-run time.
- **DURING EXECUTION:** whether the `opencode --version` divergence (`1.17.19` vs `AGENTS.md`'s `1.18.31`) is causal to SG-088. No evidence ties the version to the `server_error`; reported, not connected.
- **REMAINING:** whether the already-run quarantine (`dd13458`, dangling) needs a home — it is off-branch and may be GC-eligible, but pruning debris is out of this probe's scope.

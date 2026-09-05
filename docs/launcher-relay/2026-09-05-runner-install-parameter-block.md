# 0.18.1 runner install — parameter block for the Launcher desk (sign-off A GIVEN)

**Date:** 2026-09-05. **From:** StorageGenie Architect (OpenCode, Class 4).
**Owner approval:** sign-off A GRANTED 2026-09-05 — plan P1–P5 plus decisions D1–D5,
all approved in one pass ("Okay to all"). Next gate is **sign-off B before any host
write**; steps 6–9 stay with this project, and step 6/7 wait for sign-off C (serialised,
one project at a time — `ISS-81`).

**Do NOT install from the 0.18.0 payload** — it re-installs the `ISS-58` hole (missing
engine). Install from the 0.18.1 tree (`dispatch` + `run-coder` + unit template).

## Conf values (shell-quoted per `ISS-94` — the conf is `source`d by bash)

```sh
PROJECT='storagegenie'
ROOT='/home/andrei/StorageGenie'
BRANCH='automation'
NOTES_REF='refs/notes/storagegenie-coder-reports'
PACKET_DIR='docs/packets'
ID_PATTERN='^SG-[0-9]{3}(r[0-9])?$'
LOCK='/home/andrei/StorageGenie/.git/dispatch.lock'
CODER='codex'
DISPATCH_USER='andrei'
RUN_BUDGET_S='2100'
CODER_STATE_DIR='/home/andrei/.codex /home/andrei/.grok'
# XDG_RUNTIME_DIR intentionally UNSET (owner decision D2 — least privilege; no
# opencode Coder on this project). DISPATCH_PATH must include
# /home/andrei/.grok/bin (measured gap from SG-001).
```

## Decisions behind the values (owner-approved, recorded in our `STATE.md`)

- **D1** `NOTES_REF='refs/notes/storagegenie-coder-reports'` — convention-conformant,
  verified collision-free locally. Receipts move here; the evidence branch stays history.
- **D2** `XDG_RUNTIME_DIR` unset — see above.
- **D3** `CODER='codex'` — standing `m0106` + L3 bounds; our `AGENTS.md` Coder field now
  reads `codex` (`m0083` grok kept as history).
- **D4** `RUN_BUDGET_S=2100` (only budget proven on this estate — LNR slices),
  `LOCK` beside the receipt marker in `.git/` (persists — `ISS-96`/`ISS-97`),
  anchored `ID_PATTERN` (`ISS-69`).
- **D5** Proof slice: **SG-009** (committed + pushed `64eee1f`), run through the new
  runner at step 6/8 — only after sign-off C.
- **`ISS-107` acknowledged:** confinement coverage is point-in-time (39/68 measured).
  No sibling-extension needed from us; the step-4 `blocked_count=` line is the evidence,
  and the drop-in is re-emitted when the host gains directories.

## Project state the desk should know

- Recorded rule-set version stays **`0.17.2`** until the proof passes — the version flips
  with the receipt, never before (`G-A1`).
- `reference/vps-info.md` is ABSENT from our tree (whole-tree glob, 2026-09-05) although
  our `AGENTS.md` cites it — values above come from `AGENTS.md` instead. Flagged as our
  finding F1; not a blocker.
- `0.18.1` self-handles `ISS-60` (`run-coder:90` writes `output/dispatch/.gitignore`,
  marker in `.git/`), so no `.gitignore` change from us.
- Verb stays transitional (`SG-<nnn> <coder> [effort]`) until the runner is live (`ISS-77`).
- Our tree is clean on `automation` and in sync with `origin/automation`; SG-010 packet is
  still untracked and stays out of this handoff.

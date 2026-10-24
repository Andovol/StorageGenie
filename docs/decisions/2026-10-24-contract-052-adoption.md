# 2026-10-24 — Contract adoption 0.52.0 (D-1024-1)

Question put: adopt contract 0.52.0 or stay on 0.51.0 — the session-start command reported **BEHIND** on every installed harness copy and on the version line; `G-L1` + `D502` (new in 0.52.0) require that a behind rule set be raised to the owner as a decision.

Owner approval, quoted byte-identical (2026-10-24, this chat): "Approved now: - Adopt contract 0.52.0: check out tag contract-v0.52.0, update AGENTS.md:4 and STATE.md:6, re-run the start command, record docs/decisions/2026-10-24-contract-052-adoption.md."

## Start-command read before the change (`G-L1` — the written line)

```
G-L1 claude   BEHIND installed=795851b0f882 /c/Users/popes/.claude/CLAUDE.md
G-L1 codex    BEHIND installed=795851b0f882 /c/Users/popes/.codex/AGENTS.md
G-L1 opencode BEHIND installed=795851b0f882 /c/Users/popes/.config/opencode/AGENTS.md
G-L1 VERSION  BEHIND adopted=0.51.0 shared=0.52.0
```

BEHIND, not FORKED: the installed copies already carried the newer payload's bytes, so nothing had diverged and nothing was overwritten.

## Delta review (tag `contract-v0.52.0` read-only before checkout; adoption note quoted verbatim)

"Contract payload 0.52.0 / PROJECT ADOPTION: - **Nothing to change in your files.** Behaviour changes to apply from your next message: when the owner must start a session, hand ONE paste-ready prompt (`G-O1`, `D493`); an improvement unrelated to the owner's current goal gets one line after that goal's next step (`G-M11`, `D501`); a behind rule set is raised to the owner as a decision, per newer tag (`G-L1`, `D502`). - **Coder reports end with a `Verification:` line** (`CO-104`); the runner will refuse a restart marker without a PASS once `LNR-183` is installed."

Doc diff 0.51.0 → 0.52.0 (12 files): `RULES.md` reworked (`RULES.sha256` `8048dd35…` → `795851b0…`), `RATIONALE.md` +18, `CLOSE.md`, `CODER.md`, `CODER_PRODUCTION.md`, `PACKET.md`, `SECOND_OPINION.md`, `VERSION`, `coder_models.tsv` re-measured (136 lines), lane `dispatch` +158 and `run-coder` +194.

## What ran

1. `git -C .rules-cache fetch -q --depth 1 origin tag contract-v0.52.0` then `git -C .rules-cache checkout -q contract-v0.52.0` — the approved **tag**, never the moving branch. Cache `VERSION` now `0.52.0`; `git -C .rules-cache status --porcelain` empty (no hand-edit drift before or after).
2. Grep of the OLD version string `0.51.0` across the project: two **live pointers** updated (AGENTS.md:4, STATE.md:6); every other hit is history (decision files, packets, worklogs, ratings rows) and stays byte-identical.
3. Re-ran the start command — see the read after the change.

## Start-command read after the change

```
G-L1 claude   CLEAN installed=795851b0f882 /c/Users/popes/.claude/CLAUDE.md
G-L1 codex    CLEAN installed=795851b0f882 /c/Users/popes/.codex/AGENTS.md
G-L1 opencode CLEAN installed=795851b0f882 /c/Users/popes/.config/opencode/AGENTS.md
G-L1 VERSION  CURRENT adopted=0.52.0 shared=0.52.0
```

Cold-start bytes: `total[opencode]=29659` (AGENTS.md 6709 B + CLAUDE.md 11 B + installed rules copy 22939 B). R15 headroom: codex combined 29648 of 131072; grok AGENTS.md 6691 of 10000 characters.

## Live-pointer updates

- `AGENTS.md:4` — `0.51.0` → `0.52.0` (the version record line).
- `STATE.md:6` — `0.51.0` → `0.52.0` (adoption D-1024-1, 2026-10-24).
- No Coder-rulebook pointer lives in this repo; the Coder reads its own copy on the server.

## Reconciliation against the project's own rules (`G-L1`, first half)

The project file was compared against the 0.52.0 globals: **no duplicate, no conflict.** The upload cap, the no-second-copies pointer, the declared sensitive surfaces, the restart rule and the health probe are either project-specific or narrower than a global rule; none forbids an action a global rule allows, and none excuses one a global rule requires.

## Behaviour that applies from the next message

- `G-O1` + `D493` — the owner runs zero commands: hand ONE paste-ready prompt when the owner must start a session.
- `G-M11` + `D501` — an improvement unrelated to the current goal gets one line after that goal's next step, never a pitch in its place.
- `G-L1` + `D502` — a behind rule set is raised to the owner as a decision (this session did exactly that).
- `CO-104` — Coder reports end with a `Verification:` line; the SG-235 packet asks for `Verification: PASS` or `Verification: FAIL — <check>`, and the runner refuses a restart without a PASS once `LNR-183` is installed.

## ID note

This session's approvals are recorded as `D-1024-1` … `D-1024-4` (date-qualified). Plain `D4` and `D5` already exist in this repo (2026-10-13 recovery grants; 2026-10-16 density scope) and are not reused (`G-P4`).

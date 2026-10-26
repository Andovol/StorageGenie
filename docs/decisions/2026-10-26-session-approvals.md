# 2026-10-26 — Session approvals (D1, D2)

Recorded the moment each was issued (`G-O4`). This file is the owner-quote owner for both; the W1 packet and `STATE.md` point here rather than restating the quotes.

## D1 — the W1 slice, approved

Owner, 2026-10-26 (this chat), verbatim: **"D1 - approved. Run in L3 mode"**

**Scope approved:** the W1 slice as put to the owner — one slice that stops the two always-red host signal tests from taxing every suite run. It marks the two library-dependent tests with one pytest marker, guards each by the exact capability it needs, makes `make backend-test` run the host suite **and** the image proof and fail if the proof fails, builds the prover image from the current worktree (not the stale `:latest`), and runs the one whole-suite image trial. The review's third fix also applies: **the pure-Python EAN validation splits out so the host keeps it** (`SG-243` disposition, `docs/reviews/review-ledger.md`).

**Autonomy:** L3 — the owner approved the stage; the Architect packets, dispatches, audits and rates this slice without asking.

**What it does not touch:** the host's packages, the live container, the database, the dispatch key, and any privilege. Local Docker only; no spend; no app runtime code, so no deploy.

**Prior review:** the two-phase second opinion ran before the owner saw the item — SG-242 (blind) and SG-243 (critique), recorded in `docs/reviews/review-ledger.md`: D (the image route as the tests' home) kept with three fixes, A (move the whole suite into the image) deferred to the one measured trial, B (a sudo install on the host) rejected because D-1024-6's fallback condition never fired.

## D2 — contract 0.53.0 adopted

Owner, 2026-10-26 (this chat), verbatim: **"D2 - approve"**

**Question put:** adopt 0.53.0 or stay on 0.52.0. The start command reported every installed rule copy and the version line **BEHIND**, and the dispatch checklist requires recorded == published before any product work — so the approved W1 slice could not dispatch on 0.52.0.

**Start-command read before the change (`G-L1` — the written line):**

```
G-L1 claude   BEHIND installed=536046ae3aac /c/Users/popes/.claude/CLAUDE.md
G-L1 codex    BEHIND installed=536046ae3aac /c/Users/popes/.codex/AGENTS.md
G-L1 opencode BEHIND installed=536046ae3aac /c/Users/popes/.config/opencode/AGENTS.md
G-L1 VERSION  BEHIND adopted=0.52.0 shared=0.53.0
```

BEHIND, not FORKED: the installed copies already carried the newer payload's bytes; nothing had diverged and nothing was overwritten.

**Delta review (tag `contract-v0.53.0`, adoption note quoted verbatim):**

> Contract payload 0.53.0
>
> No adoption steps: check out this tag and record 0.53.0 as your rule-set version.

Doc diff 0.52.0 → 0.53.0: 13 files, +1014/−17. `RULES.sha256` `795851b0…` → `536046ae…`. Behaviour that applies from the next message: the roadmap carries three sections — Accepted (ordered work, each with its close `verify:`), Proposed, Rejected — plus `last_product_round:` (`ARCHITECT.md` §2b, `D513`/`D517`); a close starter names the Accepted item it serves; the Coder contract header moves to 0.53.0; a model-comparison decision rule (`D518`); a one-command guard index (`D511`); the artifact-emission clause in `PG-EV-07` (`D525`); the branch-range gate fix in `PG-IC-07` (`D522`); the ID format rule in `G-M6` (`D521`). Three scripts ship — `rule_index.sh`, `packet_check.sh`, `dispatch_preflight.sh` — and nothing requires them now.

**What ran:**

1. Guard first: `git -C .rules-cache status --porcelain` empty and `describe --tags --exact-match` = `contract-v0.52.0`.
2. `git -C .rules-cache checkout -q contract-v0.53.0` — the approved **tag**, never the moving branch. Cache `VERSION` = `0.53.0`; `RULES.sha256` = `536046ae3aac…`; `status --porcelain` empty after.
3. `AGENTS.md:4` — `0.52.0` → `0.53.0` (the only live version pointer; this repo has no `STATE.md` version line).
4. Re-ran the start command — see the read after the change.
5. Reconciliation: the project file compared against the 0.53.0 globals — **no duplicate, no conflict**. The upload cap, the no-second-copies pointer, the declared sensitive surfaces, the restart rule and the health probe are project-specific or narrower; none forbids an action a global rule allows, and none excuses one a global rule requires.

**Start-command read after the change:**

```
G-L1 claude   CLEAN installed=536046ae3aac /c/Users/popes/.claude/CLAUDE.md
G-L1 codex    CLEAN installed=536046ae3aac /c/Users/popes/.codex/AGENTS.md
G-L1 opencode CLEAN installed=536046ae3aac /c/Users/popes/.config/opencode/AGENTS.md
G-L1 VERSION  CURRENT adopted=0.53.0 shared=0.53.0
```

**Cold-start bytes:** `total[opencode]=30876` (AGENTS.md 7825 + CLAUDE.md 11 + installed rules copy 23040). R15 headroom: codex combined 30865 of 131072; grok AGENTS.md 7793 of 10000 characters.

**Live-pointer updates:** `AGENTS.md:4` only. Every other hit of the old string is history (decision files, packets, worklogs, ratings rows) and stays byte-identical.

## ID note

This session uses plain `D1`, `D2` per `G-M6`'s session-local identifiers; the repo's date-qualified decision numbers (`D-1024-…`, `D-1026-…`) are for records that outlive the session and are not reused here. `D1` and `D2` map to the W1 approval and this adoption only.

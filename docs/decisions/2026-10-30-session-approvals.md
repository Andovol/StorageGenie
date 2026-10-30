# 2026-10-30 — Session approval (D6) and contract 0.56.0 adoption

Recorded the moment the owner issued it (`G-O4`). This file is the owner-quote owner for D6; the stage packet and `STATE.md` point here rather than restating the quote.

## D6 — the household-and-document stage, approved

Owner, 2026-10-30 (this chat), verbatim: **"d6 - approved"**

**Scope approved:** the stage as put to the owner — adopt rule set **0.56.0**, then run **SG-258** (the household-and-document work) and **SG-259** (its own deploy rider). The outcome: a Household chemicals or Documents/other item can be classified, given a date, seen in the Expiry page and reminded at its category windows; documents gain their 60/30-day reminder windows; an accepted date can be corrected; reclassification does not lose a date. No migration; no production data write by the deploy; no provider call.

**Autonomy:** L3 — the owner approved the stage; the Architect packets, dispatches, audits and rates the slices without asking.

**What it does not touch:** the app database schema, the dispatch key, the host packages, and any provider. The rider is the only host action (one build, one recreate, read-only census, health checks). The new controls write the owner's data only when the owner uses them after the rider.

**Process note (0.56.0):** the new `SECOND_OPINION.md` T3 trigger (a packet introducing a design choice no earlier review covered) binds every project. A blind pass runs before the SG-258 packet is committed; its review ID and disposition go into the packet, the review ledger and the next report. The pass is advisory, never a veto.

**Second opinion (SG-260 blind · SG-261 critique, `muse-spark-1.3-contributor`):** picked **A1 / B1 / C1 / D1**, agreeing with the Architect. Strongest objection — a document's OCR date can be an issue date, and flipping the flag forces a date record on keepsakes — **accepted** by suppressing the observed-date proposal for documents, adding the category hint (keepsakes under Non-perishable) and keeping the owner's approved documents outcome. The critique's other six findings are accepted as refinements: optional `If-Match` on the classify/manual/clear routes, accepted-only date preservation plus a reverse-move clear, the classification-profile gate and exact-field/latest-`created_at` read, Clear parity with D4, and a `valid_until` date type. The keepsake scope risk is **noted**, not reopened; the owner's D6 approval is the decision. Full record: `docs/reviews/review-ledger.md`.

## D6a — contract 0.56.0 adopted

**Question put:** adopt 0.56.0 or stay on 0.53.0. The start command reported every installed rule copy and the version line **BEHIND**, and the dispatch checklist requires recorded == published before any product work — so the approved stage could not dispatch on 0.53.0.

**Start-command read before the change (`G-L1` — the written line):**

```
G-L1 claude BEHIND installed=8d2f20c41ff4 /c/Users/popes/.claude/CLAUDE.md
G-L1 codex BEHIND installed=8d2f20c41ff4 /c/Users/popes/.codex/AGENTS.md
G-L1 opencode BEHIND installed=8d2f20c41ff4 /c/Users/popes/.config/opencode/AGENTS.md
G-L1 VERSION BEHIND adopted=0.53.0 shared=0.56.0
```

BEHIND, not FORKED: the installed copies already carried the newer payload's bytes; nothing had diverged and nothing was overwritten.

**Delta review (tag `contract-v0.56.0`, adoption note quoted verbatim):**

> Contract payload 0.56.0
>
> No adoption steps: check out this tag and record 0.56.0 as your rule-set version.

Doc diff 0.53.0 → 0.56.0: 18 files, +895/−98. `RULES.sha256` `536046ae…` → `8d2f20c4…`. Project-facing changes: the **T1/T3 blind-pass triggers** (`SECOND_OPINION.md`, `D555`; T2/T4 remain opt-in, default `none`); a fast failure is attributed by a second model (`DISPATCH.md`, `D552`); the owner's `openai/gpt-6.1-sol` effort ceiling at `medium` (`CODERS.md`, `D551`); packet premises name the file and line that would prove them (`PACKET.md`, `D535`); moved code counts as changed code for the test set (`D547`); `PG-EV-15` gate-path coverage (`D547`); `CO-106` a failed production post-check is a STOP (`D547`); the reply wake re-arms on any owner message (`CLOSE.md`, `D570`); `RECIPES.md` §13 shells and interpreters (`D556`); a second-opinion pick is a recommendation, never a decision (`SECOND_OPINION.md`, `#96`/`D537`); a model judge needs controls (`D549`); `G-M6` decision numbering (`D547`); `G-M5` the asking message arms the reply wake (`D569`); the Coder contract echoes **0.56.0** and carries the `Verification:` last line (`CO-104`). Three dispatch scripts ship updated; nothing requires them now.

**What ran:**

1. Guard first: `git -C .rules-cache status --porcelain` empty and `describe --tags --exact-match` = `contract-v0.53.0`.
2. `git -C .rules-cache checkout -q contract-v0.56.0` — the approved **tag**, never the moving branch. Cache `VERSION` = `0.56.0`; `RULES.sha256` = `8d2f20c4…`; `status --porcelain` empty after.
3. `AGENTS.md:4` — `0.53.0` → `0.56.0` (the only live version pointer; this repo has no `STATE.md` version line).
4. Re-ran the start command — see the read after the change.
5. Reconciliation: the project file compared against the 0.56.0 globals — **no duplicate, no conflict**. The upload cap, the no-second-copies pointer, the declared sensitive surfaces, the restart rule and the health probe are project-specific or narrower; none forbids an action a global rule allows, and none excuses one a global rule requires. The project's second-opinion lane is set (`opencode-go/muse-spark-1.3-contributor`, `agent=plan`); `second_opinion_triggers` is unset, so T2/T4 stay `none` and T1/T3 bind.

**Start-command read after the change:**

```
G-L1 claude CLEAN installed=8d2f20c41ff4 /c/Users/popes/.claude/CLAUDE.md
G-L1 codex CLEAN installed=8d2f20c41ff4 /c/Users/popes/.codex/AGENTS.md
G-L1 opencode CLEAN installed=8d2f20c41ff4 /c/Users/popes/.config/opencode/AGENTS.md
G-L1 VERSION CURRENT adopted=0.56.0 shared=0.56.0
```

**Cold-start bytes:** `total[opencode]=31347` (AGENTS.md 7825 + CLAUDE.md 11 + installed rules copy 23511). R15 headroom: codex combined 31336 of 131072; grok AGENTS.md 7793 of 10000 characters.

**Live-pointer updates:** `AGENTS.md:4` only. Every other hit of the old string is history (decision files, packets, worklogs, ratings rows) and stays byte-identical.

## ID note

This session uses plain `D6` per `G-M6`'s session-local identifiers; the repo's date-qualified decision numbers (`D-1024-…`, `D-1026-…`) are for records that outlive the session and are not reused here. `D6` maps to the stage approval and `D6a` to this adoption only.

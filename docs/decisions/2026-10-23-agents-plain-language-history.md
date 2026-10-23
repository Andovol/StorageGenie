# 2026-10-23 — Configuration history moved out of AGENTS.md (plain-language pass)

This file holds every decision number, superseded value, and history line removed from `AGENTS.md` on 2026-10-23 so the configuration reads in plain words. The live values live in `AGENTS.md`; nothing here is live.

## Rule-set version history

- Recorded version 0.51.0 adopted 2026-10-23 (adoption D3; checkout tag `contract-v0.51.0`; delta = Roadmap-if-none + G-M5 numbered Actions + G-M3 plain words + G-O5 + harness-plugin check + ARCHITECT/CLOSE/CODER/DISPATCH/ONBOARDING/PACKET/RATIONALE/RECIPES/RULES/SECOND_OPINION doc updates + lane run-coder/dispatch rework; supersedes 0.50.0).
- Recorded version 0.50.0 adopted 2026-10-15 (adoption D2; checkout tag `contract-v0.50.0`, commit `1723165` per tag log; delta = ARCHITECT stage-definition + SECOND_OPINION routing + AUDIT slowest-waste + CODER CO-103 + CODERS plan-agent + DISPATCH agent-setting + LEDGER 12th column + ONBOARDING reviewer value + PACKET waste-cutting/D443 + lane run-coder rework; RULES.md hash unchanged `49338e39a574…`; supersedes 0.47.0, chain D-1012-2 preserved).

## Field history

- Workspace: local is `automation` branch; host authority is the contract's VPS guide.
- Repository: default branch `automation`, evidence ref `refs/heads/storagegenie-evidence` (per CO-86).
- Host project path: owner directive m0045.
- Credential: naming `<project>-architect-dispatch` per PROVISIONING.md:129.
- Coder: owner directive D29 (2026-09-11) chose opencode going forward; supersedes m0106 (codex high, kept as history). Effort per catalogue row for opencode (deepseek rows low/high/max; muse-spark rows minimal..xhigh, xhigh proven live SG-157 — validity was always per-model, F-SG157-1) via `--variant` (explicit per trigger per D120/D15, uncalibrated per G-A9; the Coder default max is NOT taken). Catalogue `coder_models.tsv` (0.44.1, re-measured 2026-10-08): high listed for `opencode-go/deepseek-v4.1-flash` — engine-checked strictly, trigger effort (D266/D302). Hard ceiling: packet file stays far under the 128 KiB single-argv limit. Provider partially unproven (ISS-6); entry-point run-2 owed (ISS-7).
- Dispatch verb: settings ride the trigger, any subset (D302); a packet `coder:`/`model:`/`effort:` line is refused `packet_settings_retired`. `agent=plan` for second-opinion reviews (0.50.0/D451). `--force` bypasses replay guard only, `--quarantine` per DISPATCH.md section 2 (D331).
- Harness: owner directive 2026-09-12 to use the `job_spawn` spawner (supersedes the Start-Process + blocking-wait chunking).
- Wrapper: measured 2026-09-21 by SG-071 (journal + launch artifact); supersedes the stale `/opt/storagegenie-dispatch/dispatch_coder.sh` path (legacy grok-codex-only whitelist).
- Model policy: owner directive D-1012-15 (2026-10-12); catalogue-valid low/high/max row; max uncalibrated vs D120/D15-high. Supersedes the omit-model row (D302 subset still contract-legal; explicit chosen per owner). Coder default proven live SG-120.
- Second opinion: owner D-7 approved 2026-10-17 (`docs/decisions/2026-10-17-d5-d6-d7-answers-l4-window.md`); supersedes the explicit value recorded 2026-10-15.
- Autonomy L2 (slice autonomy, 1 retry, per ARCHITECT.md 60-72 section 6) — escalates to L3 only after clean stage.
- Close-out: standing owner directive 2026-09-28 (live deploy before every close, G-O4 record).

## Values history

- Worklog dir per CO-57; health probe per CO-92; receipt via notes-ref (live lane; SG-092/SG-156 precedent); legacy `/opt/storagegenie-dispatch/finalize_dispatch_report.sh` (v0.17.2 evidence-ref) refused `candidate_not_remote` on this lane — retired 2026-10-09 (F-SG156-1).
- Production database: blueprint page 14 local-first; CODER_PRODUCTION.md not bound until datastore declared.
- Default branch: current branch; evidence `storagegenie-evidence`.
- Dispatch key: Layer A forced-command.

## Narrowings history

- Budget cap corrected 2026-09-17 by SG-061 (was config page 11, now page 20).
- Duplicate pointer: `docs/decisions/2026-08-28-phase-0-approvals.md:33-41` Launcher block duplicates global rules — keep global, project copy is a pointer.
- Sensitive surfaces declared per PRODUCTION.md trigger; every decision touching one goes to owner individually at every autonomy level.

## Loading history

- Session start version check FIRST (run `bash .rules-cache/rules_check.sh` per D339, never checkout-vs-stamp, M3).
- Cutover: pinned pre-conversion state `26e9e8b` (local `automation` head chain); disposition m0064 — 40 obligations dispositioned keep/covered/retire, zero conflict.

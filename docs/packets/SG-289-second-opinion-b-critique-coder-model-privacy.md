# SG-289 — Second opinion Phase B (critique): which Coder model may read the live host and the owner's data

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one. This lane's snapshot has no `.git`: state `unknown` once and carry on.
**DATABASE: none.**
**Restart: none.**

## Why this exists

Phase A ran (`docs/worklogs/SG-288_report.md`) and stopped itself: a search spilled excerpts of `docs/decisions/` into its context. **The Architect's pick was not in the repository then** (it is first written here), so that pass stays blind to the pick; the ledger records the spill. This is **Phase B — the critique.** Attack the pick below. It is the Architect's **recommendation, not a decision**; model choices are the owner's.

**Known gap:** this lane's `.contract/` holds `CODER.md` but not `CODERS.md`, `SECOND_OPINION.md` or `coder_models.tsv` (SG-288). The context pack quotes the two rule lines verbatim; treat those quotes as the evidence.

## The pick, verbatim

> **R1, recommended: C2, Haiku 5.5 `high` for every builder slice on this lane, starting with SG-286, until the owner chooses otherwise.**
> - The contract's lane default already says so for a lane with a `.env` or personal data, and this lane has both (`docker-compose.yml:17-18`; `backend/app/config.py` loads `.env` on import, per SG-288).
> - C3 is rejected: a "code-only" slice still runs with settings that load `.env`, and the repository holds a household-name literal (`docker-compose.yml:15`, SG-288), so "reads nothing private" is not established.
> - C1 is rejected: once a value reaches a model whose provider trains on it, nothing takes it back; packet wording limits what is written, not what is read (`.contract/CODER.md:271-274`, per SG-288).
> - **Mitigations kept either way:** packets still forbid printing environments and owner values, compare secrets by hash, and keep scratch containers off `env_file`.
> - **Risk accepted:** Haiku 5.5 has never run on this lane. SG-286 is an operations slice with hard stop rules, so a weaker build model shows up as a stop, not as a silent defect. The first Haiku slice's rating is compared with Muse's recent ratings in `docs/ratings.md` before SG-271, the first code slice.

## G1 — Read

`AGENTS.md`'s top section, `docs/reviews/2026-11-07-coder-model-privacy-context.md`, `docs/worklogs/SG-288_report.md`, `docs/packets/SG-286-recovery-image.md`, and the files they name. **Do not read `STATE.md` or `docs/decisions/`; search with file-targeted reads, not repository-wide greps.** List every file read beyond those.

## G2 — Per point of R1

- the strongest case against it, with evidence (`file:line`, a quote, a measurement);
- a premise of it that is unverified;
- the observation that would settle any disagreement.

An objection without evidence is labelled `opinion`. Check especially: whether SG-286's packet, as written, would put a secret or owner value into a model's context despite its rules; whether Haiku at `high` is likely to carry SG-286's stop rules; and whether anything makes C1 or C3 safer than the pick claims.

## G3 — Report

Your final message **is** the report (read back with `SG-289 --status`; the Architect copies it unedited to `docs/worklogs/SG-289_report.md`). **Keep the whole report under 100 lines.** The most serious objection first. Shape: `SG-289` as the first token; the contract-version line (`PB-4`); the extra-files list; the points of R1; a closing line of what you read.

## Constraints

Read-only; reads confined to the repository at BASE; no host commands, Docker, credentials, browser, network or database. Hang bound: file reads 120 s each. A denial is a STOP (`PB-2`).

## Acceptance criteria

Each point of R1 answered; each objection evidenced or labelled `opinion`; extra-files list complete; report under 100 lines. `PB-3` vacuity: "no objection" needs one sentence on what was checked.

## Report

Destination: final message (engine-published). Identity line and stop path are `PB-4`/`PB-6`. State that you wrote nothing.

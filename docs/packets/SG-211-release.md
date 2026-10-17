# SG-211 — D-22: production release (verify live==tree, release record, first version tag)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: none (read-only probes: served GETs, health, DB sha/migration-head reads; zero writes). Restart: none** (no build, no recreate — the SG-210 serve stands).
**Autonomy: L3** (approved queue; checkpoints only on `G-K2`/assumption-change/stage end). Authority: owner D-22 ("lets do the release now" + standing close-release). First release on record — zero tags exist; this slice sets the precedent deliberately small.

Authoring date (metadata, never a gate): 2026-10-17.

## Why this exists

D-22 speaks the R5 word (scope approved 2026-10-13, awaited since). Live==tree through SG-208 (SG-210 verified). A release here = an attested, tagged point on the served bytes — not new product, not a deploy (nothing to deploy: unserved delta NONE).

## Handed-over facts (expected — re-verify on target, `PB-1`)

- Served state (expected, SG-210 poststate): container `5f82f760`, image `38fcae5e`, index `231224da…`, JS `47c65dea…` (320700 B), CSS `c3b58cda…`, DB `e6bef157…` 28 tables, alembic `20260924_sg114_relation`. Product content through SG-208. Re-derive live, never assume.
- Tag namespace is EMPTY (`git tag` count 0, verified 2026-10-17) — anything created is the first precedent. Name: `release-2026-10-17` (date of the served bytes; annotated, message carries the served shas).

## G1 — verify live==tree, then attest

- Re-read live: served index/JS/CSS shas via GETs, health, DB sha + migration head (read-only), container/image ids. Every value must equal the SG-210 poststate record. ANY mismatch STOPS the slice (no tag on unverified bytes — `PB-6`); a match is attested, not assumed.
- Write the release record `docs/releases/2026-10-17.md`: date, tree HEAD + product content (SG-205/207/208 + SG-206/210 serves), served shas (container/image/bundle), health + DB reads, what's NOT in it (Option C/D unapproved, AI stages transport-less per SG-209, server enforcement open per D-19, R5 scope note), and the tag name. No invented scope, no roadmap promises.
- Create the annotated tag `release-2026-10-17` on the tree HEAD the bytes were verified against, push it (`git push origin release-2026-10-17`). The tag push is the outward-facing act D-22 explicitly approves — stated, not silent.

## Constraints

- **Scope ceiling:** record + tag ONLY; evidence ONLY `docs/worklogs/SG-211_*`. Zero product/config/test/lockfile/schema/migration bytes; no restart; no secret in any artifact. `PB-3`: a tag on bytes whose verification reads are missing/failed is a FAIL, never a release.
- Reads: lane GETs + git only. Hang bounds: reads 120 s; tag ops 120 s. Expected duration ≈300 s (Architect record, `G-A9` uncalibrated; verification reads + record + tag — no build legs).
- Simplicity: verify + record + tag; no new machinery. Excluded (stated): any product change; backfill of past serves (this tag covers the live bytes as verified today, never retroactively).

## Acceptance criteria

- **A1:** every live re-read equals its SG-210 record (table of expected-vs-read, per value); on any delta: STOPPED, no tag, reason named.
- **A2:** release record committed at the path; annotated tag exists locally AND on origin (`ls-remote` read-back); tag points at the verified HEAD.
- **A3:** report `docs/worklogs/SG-211_report.md`; elapsed vs ≈300 s; constraints answered; FIRST/DURING/REMAINING; FIRST token `SG-211`.
- **A4:** notes-ref receipt, first line `Dispatch-ID: SG-211 | Report: docs/worklogs/SG-211_report.md`, Work-HEAD recorded, pushed + read back. Never the retired finalizer.

Guards invoked: PG-EV-02/03/05; PG-SC-09; PG-IC-01/07; PG-PR-03. Stop follows `PB-6`.

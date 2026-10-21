# SG-221 audit — pilot renders surfaced in the drawer (3 links + serializer field + Scene tab), rated 98

Immutable audit: base `0779966` → G1 `9bde876` (derivation + 3 live link rows + failing tests) → work `d02667d` (pass: serializer + drawer branch + pass/full/lint logs) → report `d953027` → receipt `4c7ac42` (transcript + mapped read-back; Work-HEAD d953027). Local `--ff-only` to the exact tip (`4c7ac42` == origin/automation at pull); tree clean. Trigger exit 0; status verb `result=done id=SG-221 exit=0`. Receipt note `Dispatch-ID: SG-221 | Report: docs/worklogs/SG-221_report.md` IS on the remote — own read-back finds `d953027` via `git log --notes`. Per `DISPATCH.md` §2: receipt present → NOT failed. No runner misfire — sixth clean trigger in a row.

## Verified (parsed from the committed artifacts, not the report's §(c))

- **Product diff exactly as packeted (re-read by this audit):** `assets.py` +1 line (`"source_kind": e.source_kind`); `types.ts` optional `source_kind?` + comment; drawer +11/-8 (new `sceneEvidence`/`sceneUrl` beside the `sourceUrl` pattern; honest-empty copy byte-identical when absent); two new test files (+93/+27). Nothing else in `backend/` or `frontend/` moved.
- **3 links derived live, written once:** `SG-221_links.txt` shows per-statement `changes()=1` ×3 — Miso render→Miso asset, Costiță renders→Costiță asset (matches the SG-217/218/220 photo→asset mapping). Table inventory pre/post differs ONLY in `asset_evidence` 14→17; evidence 21, provider_call 33, audit_event 94, asset 7 all identical. No UPDATE/DELETE.
- **Derivation survived its own premise correction:** the ledger stores the data-URL hash, not the raw photo hash (F-SG221-1) — the Coder rebuilt the exact reference per upload row and got a unique match per render with the expected mapping; no stop fired. The 4th `scene_render` row (2026-10-12, pre-D-27) was correctly excluded by the packet's window (F-SG221-2).
- **Fail-pre→pass-post genuine:** backend `KeyError: 'source_kind'` (1 failed) → `1 passed`; frontend `Unable to find [data-testid="scene-image"]` (1 failed, 17 skipped) → pass; full suite 29 files / 298 tests passed exit 0 on the candidate; `tsc` + targeted `eslint` + `ruff` exit 0. Existing honest-empty, cutout, and AI no-fetch tests pass unmodified.
- **Money:** $0, zero network calls beyond lane/repo/test runners; `provider_call` 33→33. **Secrets:** literal gate exit 1 EMPTY. Elapsed ≈245 s vs ≈600 s.
- **Deviations disclosed, none deducted:** read-only docker-socket denial routed to the lane socket (F-SG221-3); Source-tab ordering observation recorded, untouched (F-SG221-4); response-id null by product rule.

## Rating

**Holistic: 98/100, no flag.** Three live links with the derivation quoted per link, one additive key, one tab branch, honest states byte-preserved, full suite green, and the ledger-hash surprise handled by rebuilding the reference instead of assuming it. `deduction_attribution`: empty. `slowest_waste`: `none` — every CO-79 phase output was used. Guards: PG-EV-02/03/05/06/09; PG-SC-05/09/12; PG-IC-01/07/08/09; PG-PR-01/03/10; PG-DP-01.

## Dispositions

| Item | Destination |
|---|---|
| 3 pilot renders linked + surfaced (unserved candidate) | Serve rider SG-222 — same turn: rebuild + one recreate + verify, then the owner can open the assets live |
| Data-URL hash semantics | Recorded (SG-220 F-2 + F-SG221-1) — future scene packets state the reference-rebuild derivation |
| Source-tab ordering | Recorded, untouched — a future drawer slice may name it explicitly if it ever matters |
| Pre-window 2026-10-12 render | Unlinked by criterion — stays that way unless a decision re-opens it |
| Runner clean | Nothing filed — ISS-4 stays at 18 |

Harness context-size reading unavailable; no conclusion made.

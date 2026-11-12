# SG-311 — The screenshots SG-301 owes: the new font, the app header and three screens, proven from the DOM

`PB-1`–`PB-6` bind (`CODER.md` §14). `PB-7` is not named; **no test suite runs here** — SG-301r1's gate is green (`docs/worklogs/SG-301r1_report.md`: frontend 47 files / 423 tests, host 805, image proof with `npm ci`).

**This slice changes no product or test byte.** It writes only `docs/worklogs/SG-311*` and `docs/worklogs/SG-301_shots/`.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: temporary databases only** — throwaway SQLite files under scratch. No live database read or write.
**Restart: none.** No deploy; rider SG-310 follows once SG-301 is rated.
**Provider: none.** No key, no `.env`, no spend; every provider off.

**Contract:** recorded `0.59.0` (`AGENTS.md`, D30). **This lane denies reading the contract folder; do not try.** Echo your own contract's version line if you received one; **if you received none, say exactly that.**

**Approval:** stage C (*"d14 ok"*, L3); the owner: *"design, look and feel are very important, so hold every screen to that, and open every screenshot yourself."* SG-301 (two runs) built the change and passed its gate but ran out of time before its screenshots; its one retry is used, so the screenshots are their own slice.

## Why this exists

SG-301 (`a15b76d..db8c719`) changed what every screen looks like: **Instrument Sans** everywhere (`frontend/src/theme/tokens.css` `--font-sans`, imported in `frontend/src/main.tsx`), **the app header** on the paper look (`frontend/src/App.tsx`, `frontend/src/components/shell/AppHeader.tsx`), plain words through `frontend/src/lib/labels.ts` on **Inbox**, **Expiry** and the **asset page**, and the Pantry's **EXPIRED** label at 13 px. Its tests check the source; **nothing has yet shown the screens.** Run 1's enumeration table (`docs/worklogs/SG-301_report.md` §G2) lists every text removed or reworded — use it to choose what to read from the DOM.

## G0 — Preflight

```
mkdir -p output/SG-311-scratch/docker-config
export DOCKER_CONFIG="$PWD/output/SG-311-scratch/docker-config"
export DOCKER_HOST="unix:///run/dispatch-storagegenie-SG-311/docker.sock"
echo "$DOCKER_HOST"; ls -l /run/dispatch-storagegenie-SG-311/
docker version
```

`docker version` shows a **Server** section; otherwise **STOP as BLOCKED with the verbatim error** (`PB-2`). `PATH=$PWD/backend/venv/bin:$PATH`. `curl -s http://127.0.0.1:8003/v1/health` at start and end; both 200. **`date +%s` at the start of every step.** Scratch only in `output/SG-311-scratch/`, npm's cache there too if needed; **no `/tmp` for anything, including `tee` and `curl -o`.** `output/` itself and `output/dispatch` are never touched.

## G1 — The scratch app

As SG-302 did (`docs/worklogs/SG-302_report.md` §G4, `docs/worklogs/SG-300_shots/INDEX.md`): a fresh SQLite under `output/SG-311-scratch/` by the project's migrations (`alembic upgrade head`); test data **through the API** with generated images — food and non-food, one item with no name, one expired food item, a few due soon, one counted and one amount item, and **an Inbox import whose AI step is skipped** (providers off and AI consent off give `{"status":"skipped","reason":"consent_disabled"}` on the AI step, `docs/worklogs/SG-269_findings.md` F11; establish how from `backend/app/api/v1/` and say). Backend `127.0.0.1:18311`; frontend from a scratch build **with `VITE_API_BASE=http://127.0.0.1:18311`** on `127.0.0.1:14311` — grep the bundle for `18311` and for `8003`; a bundle pointing at 8003 is a STOP. Never port 8003, the live container or the stored files.

## G2 — The shots

Headless Chrome driven by a Node script in scratch speaking the DevTools Protocol (built-in `WebSocket`, no install). Into `docs/worklogs/SG-301_shots/`, in this order:

| Shot | Theme | Width |
|---|---|---|
| Pantry with the header (an EXPIRED tile in view) | light, dark | 1280 |
| Pantry with the header | light | 375 |
| Catalog with the header | light | 1280 |
| Inbox, the skipped-step import open | dark | 1280 |
| Expiry page | dark | 1280 |
| Asset page | light | 1280 |

**Proof per shot, read from the DOM through the same DevTools session, into `docs/worklogs/SG-301_shots/INDEX.md`:** sha256 (12) and size; the on-screen text that proves the state; the computed `font-family` of the page heading **and of one body text node**; the EXPIRED label's computed `font-size` on the Pantry shots; the header's computed background colour; and for Inbox, Expiry and the asset page, that **none** of `optimistic concurrency`, `blueprint`, `Phase 0`, `AWAITING_REVIEW`, `consent_disabled`, `If-Match` or an `Import <hex>` fragment appears in `document.body.innerText` (quote the check). On the Inbox shot, quote the skipped step's label (expected *Skipped (AI off)*, never *Done*). **No two shots share a hash** — check it and quote the check. A shot failing its proof is retaken once, then reported failed — never described as showing what it does not.

**Design notes, not fixes:** for each shot, one line on anything that looks wrong to an owner who cares about design (text clipped, crowding, mismatched surfaces, leftover developer wording) — report it; change nothing.

Stop the servers by the PIDs you started, never `pkill -f`; **remove `output/SG-311-scratch/` by that exact path before writing the report.**

## Acceptance criteria

- **A1** — Preflight proven; health 200 start and end; phase seconds from stamps.
- **A2** — Scratch app on 18311/14311 with the bundle check quoted; the skipped-step import made and how.
- **A3** — Seven shots with hash, size, proving text, both font families, the EXPIRED size, the header background, and the absence check where named; distinct-hash check quoted.
- **A4** — Design notes, one line per shot.
- **A5** — Zero product, test, backend, migration, Dockerfile, compose, lockfile, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; no `/tmp`; scratch removed before the report.
- **A6** — `PB-3` vacuity: a failure would look like the system font in the DOM, a removed string in `innerText`, a skipped step reading *Done*, EXPIRED under 13 px, two shots with one hash, a bundle pointing at 8003, scratch left behind. Say which you checked.
- **A7** — The last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

## Scope ceiling

- **Written:** `docs/worklogs/SG-311*`, `docs/worklogs/SG-301_shots/` only. **Any product or test file change is a STOP.**
- **Authorised runtimes:** the preflight; the project's migrations on a scratch file; the frontend build into scratch; the scratch servers on `127.0.0.1:18311` and `:14311`; headless Chrome; a Node DevTools script in scratch. No install, no other port, no image build.
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Preflight **120 s**; frontend build **300 s**; scratch server start **60 s** each; one screenshot **60 s**; ordinary commands **120 s**. No interactive command.

## Budget — a stop rule

`RUN_BUDGET_S` 2100 s. **At 1100 s by your stamps, stop, remove scratch, commit, write the report, publish.** **No optional goal.** Expected ≈650 s (`UNVERIFIED — my estimate`: SG-302's scratch app and 7 shots took ≈511 s; this adds a skipped-step import and more DOM reads). A stop leaves the rest `REMAINING`.

## Report

Destination: `docs/worklogs/SG-311_report.md`. The first line states the slice ID, model and effort read from the process arguments, working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. Then elapsed and phase seconds; how the skipped step was made; the shot table with every proof; the design notes; your contract line or its absence; every `UNCLEAR` / `REMAINING` line; one line per criterion. **Every claim that something "matches", "is exact" or "shows" names the comparison that proves it.**

**Publish, literally, in this order, after your report commit (trailer `Dispatch-ID: SG-311`):**

```
git push origin automation
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-311 | Report: docs/worklogs/SG-311_report.md | Work-HEAD: <report commit>" HEAD
git push origin refs/notes/storagegenie-coder-reports
git fetch origin automation
git rev-parse HEAD origin/automation
```

The two hashes must be equal; quote them. A refused push is a STOP, quoted verbatim. **Publish even after a stop or a failure.**

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.

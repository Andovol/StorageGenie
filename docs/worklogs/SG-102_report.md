# SG-102 — Persisted-snapshot wiring + live re-confirms (EU base, OFF accept) (report)

**Dispatch-ID:** SG-102
**Coder / effort:** `opencode` / `high` — effort read from the packet dispatch head (`effort: high`); **model: `unknown`** (no model id is sent per policy, and no process argument or provider metadata exposed one — reported `unknown` rather than guessed from the system-prompt identity line).
**Work dir:** `/home/andrei/StorageGenie` · **Remote:** `origin` = `git@github.com:Andovol/StorageGenie.git`
**BASE (requested ref `origin/automation` resolved):** `f1d3aeb4f63d10ed9ded2294af7b8cd0ca4deef6`
**WORK_HEAD:** `<filled after commit>` · **Report:** `docs/worklogs/SG-102_report.md`
**Contract echo (verbatim):** `0.33.0` — recorded in `STATE.md:4` (`**Version:** \`0.33.0\` …`) and `AGENTS.md:4`; published side `/home/andrei/storagegenie-contract/VERSION` → `0.33.0`, HEAD `b232b845d74e89cb346c60fa4b9a40ec401c42dd` "Contract payload 0.33.0", and the **G-L1 payload hash was executed this time**: `sha256sum RULES.md` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46` == `RULES.sha256`, `sha256sum -c` → `RULES.md: OK`. Recorded == published == `0.33.0`.
**DATABASE: none live** (no migration; all live legs ran in-process on temp DBs). **Restart: none. Deploy: none. Container actions: none** (`PG-PR-04`). No model/migration: `app/models` + `alembic` diff **empty**.
**Spend (real $):** **Jina 1 successful metered search (2 attempts)** — the Jina snapshot/response exposes **no cost or usage field**, so actual `$` is not measurable from the client and is reported in **units**, bounded by the packet's **≤2 searches ≤$0.01 worst-case** (uncalibrated `G-A9`). OFF `$0`; synthesis `$0`; all offline work `$0`.

---

## Result in one line

Snapshot recording is **wired into the endpoint** (`PG-SC-02` closed in-slice): `trigger_enrich` now appends one OFF row always and one Jina row iff the fallback fired, through the SG-100 writer, and the response flips `snapshots_recorded` to **`True`** — proven end-to-end by a new offline test file (fail-pre 3F/2P → pass-post 5P) and by **live re-confirm legs**: OFF **ACCEPTED** (200, 10 products, first code `8711000517604`), EU base **NXDOMAIN confirmed** with the raw resolver line (no code switch), and Jina **global** 200 (5 results) **recorded through the same `record_jina_snapshot` the endpoint calls**.

## G0 — consent / key-name gate: **GREEN** (gate open; live ran)

- `reader.ai_status()` → `(True, 'enabled')`; `settings.jina_api_key` resolves (`jina_key_present: True`, NAME only). `.env` key NAMES: `DATABASE_URL`, `STORAGE_ROOT`, `HOUSEHOLD_DEFAULT_NAME`, `CORS_ORIGINS`, `OPENCODE_API_KEY`, `SG_CONSENT`, `SG_PROVIDER_ID`, `JINA_API_KEY` — no value printed, logged, quoted or committed. No key value appears in any file, log or assertion.

## G1 — snapshot recording wired into the endpoint (`PG-SC-02`): **MET**

- `backend/app/api/v1/enrich.py` (+17/−5): imports `snapshots as snapshots_mod`; immediately **after** `jina_mod.fetch_with_fallback(...)` and **before** the candidate commit:
  ```python
  query_text = jina_mod.build_jina_query(brand, query_name)
  snapshots_mod.record_off_snapshot(db, record.primary, query=query_text)
  if record.fallback is not None:
      snapshots_mod.record_jina_snapshot(db, record.fallback, query=query_text)
  ```
  and `"snapshots_recorded": False` → `True` (`:220`). The module docstring was corrected (it had claimed the snapshots were UNRECORDED).
- **Query = the searched brand+name TEXT** the endpoint already holds: `build_jina_query(brand, query_name)` is the exact function the Jina client uses, so the recorded query matches the text that crossed the wire (never a photo, a coordinate or a key).
- **Degraded snapshots record with reason** (SG-100 rule, restated): the writer stores `no_result_reason` + quoted `raw_text` and `raw_body=None`; the test asserts this for both sources at HTTP 503.
- **`snapshots.py` byte-untouched** (M45 not triggered there): no failing test proved a hunk, so none was made. The writer + loader are both in acceptance — the new test triggers the endpoint and reads rows back via `get_snapshots_by_source` and `get_snapshot` (writer and reader in one leg).

## G2 — live re-confirm legs (in-process, temp DB): **MET**

All three legs ran in one process against temp SQLite `/tmp/opencode/sg102/live.db` (`DATABASE_URL` overridden before import; root `.env` loaded silently, NAMES only). Production DB opened **read-only** only for before/after counts.

- **Leg A (OFF, free) — ACCEPTED.** Real client `fetch_off_search` (no scripted transport). Request shape asserted: `GET https://world.openfoodfacts.org/api/v2/search` with `search_terms`, `brands_tags`, `countries_tags_en=romania`, `page`, `page_size`, `fields`. Outcome **200 with 10 products**, first `code` **`8711000517604`**, 0.26s. Recorded row `source=off`, `query="Jacobs Jacobs Cronat Gold instant coffee"`.
- **Leg B (EU base, diagnostic, free) — EU STANDS.** Raw resolver output: `getent hosts eu.s.jina.ai` → **exit 2, no output**; `socket.getaddrinfo` → `gaierror: [Errno -2] Name or service not known`. A retrieval attempt through the **real** client at `JINA_EU_BASE_URL` degraded loudly: `status_code=None`, `no_result_reason="transport: ConnectError: [Errno -2] Name or service not known"`. **No code switch** — the EU default stands; global remains diagnostic-only (SG-082).
- **Leg C (Jina global, metered) — 200.** Real client at `JINA_GLOBAL_BASE_URL`: `status 200`, **5 results**, 8.165s, `raw_body` **3646 bytes**, `no_result_reason=None`. Recorded to the temp DB **through the same `record_jina_snapshot` the endpoint calls** (`source=jina`, same query) — the live→persisted loop is closed, not re-implemented.
- **Loader read-back:** `off` count=1, `jina` count=1, temp total=2.
- **Production counts identical before/after:** `provider_call 17 / job 7 / candidate 6 / assertion 28 / asset 6` (read-only `mode=ro`).
- **Budget:** Jina 2 attempts (Leg B EU DNS-fail + Leg C global success = 1 successful metered search); OFF 2 searches (Leg A + the free recorder fix-check). Within the stated bounds. No synthesis calls (proven SG-101).

## G3 — tests + gates ($0 offline): **MET**

New `backend/tests/test_sg102_enrich_wiring.py` — 5 tests driving the REAL endpoint/router/clients/writer/loader (no network, no key):

1. OFF hit → 1 OFF row, 0 Jina rows, `snapshots_recorded: True`, loader reads by id/source;
2. OFF miss → **exactly 1 OFF + 1 Jina row** (no double-write), Jina raw body carries the mega-image URL;
3. degraded 503 (both sources) → named `http_status` reason, `raw_body=None`, `raw_text` quoted;
4. consent-false → 403, **0 sends, 0 snapshot rows** (the gate precedes every recording hunk);
5. over-cap → 402, 0 sends, 0 snapshot rows.

- **Fail-then-pass, BOTH raw committed (`PG-EV-09`, `PG-EV-01`):** fail-pre = clean HEAD worktree + the new test file → **3 failed, 2 passed in 1.14s** (raw R-FAILPRE); pass-post = **5 passed in 1.02s** (raw R-PASSPOST). The 2 pass-pre tests are the "records nothing" gate tests, which hold pre **and** post by design — the 3 recording tests genuinely fail pre with `assert False is True`.
- **Targeted:** `test_sg102 + test_sg098 + test_sg100` → **26 passed in 2.09s** (raw R-TARGETED).
- **Full suite:** **2 failed, 508 passed in 22.51s** (raw R-SUITE); the 2 are the known decoder env reds, **stash-proved** at a clean HEAD worktree (`test_signals.py` 2F/5P, raw R-STASHPROOF).
- **Gates:** ruff **clean**; mypy **41 → 41** errors (delta **0**, 84 source files); secret-pattern grep over changed/new files **0 real** (only a code comment naming the `Bearer` header, no value).
- **Scope:** `git status --porcelain -- app/models alembic` → **empty** (no model/migration diff).

## F-SG102-1 — SG-098 pinned the old `False` (M45, disclosed)

`backend/tests/test_sg098_enrich_endpoint.py:194` asserted `body["snapshots_recorded"] is False`, and its module docstring/comment described the snapshots as UNRECORDED. The wiring necessarily invalidates that pin. Updated **minimally** (6+/5−): the assertion flips to `is True`; the docstring and comment now say the snapshots are recorded to the `enrich_snapshot` table while the **candidate row** still carries no raw body (the non-vacuous contrast is preserved and re-asserted). This is the one existing-file touch **outside** the packet's enumerated ceiling; it was required by the "full suite green" criterion. Reported, not hidden.

## F-SG102-2 — the raw-body recorder lever captured a `ResponseNotRead` error (disclosed)

The packet's "raw-body recorder from leg 1" was implemented as an `httpx` **response event hook**. On the **real** network the hook fires before the body is read, so `resp.text` raised `ResponseNotRead` and the recorder captured the 95-byte error string, not the body. The **authoritative verbatim body was never lost** — it is the snapshot's own `raw`/`raw_text` (Jina `raw_body` = 3646 bytes, OFF 10 products). The lever was fixed with `resp.read()` before `resp.text` and verified **free** on OFF (captured **5627 bytes**, first product `8711000517604`); no metered re-run was performed (the authorized retry is transient-only and Leg C succeeded).

## Cross-product / privacy (`PG-IC-01`, `PG-SC-05`)

No criterion demanded a migration, fetcher/synthesis change, frontend, deploy, restart, container act, or metered calls beyond Jina ≤2 + the authorized retry — no cell collides; stated so the check exists on paper. Reads used TestClient + host commands only; no image pulled/run; `docker compose config` never run. Identifiers TEXT only (never photos/GPS); key never in any file, log or assertion. No fixed dates in code — the live leg read the clock; fixture timestamps are sample data. `STATE.md` / `AGENTS.md` / `docs/packets` untouched.

## Acceptance criteria — status

| Criterion | Status | Evidence |
|---|---|---|
| Endpoint records OFF row always + Jina row when fallback present, readable via the loader | **MET** | new tests 1–3; `get_snapshots_by_source`/`get_snapshot`; R-PASSPOST |
| `snapshots_recorded: True`; degraded path records reason; one fetch = one row/source; consent gate first | **MET** | tests 1–5; 503 reason; count==2 (1+1); 0 rows on 403/402 |
| OFF leg classified (ACCEPTED with count+code, or NOT MET) | **MET** | ACCEPTED, 200, 10 products, code `8711000517604`, 0.26s |
| EU leg measured with raw line quoted and no code switch | **MET** | `getent` exit 2 / `gaierror`; EU default stands |
| Jina leg recorded through the real writer with spend actuals | **MET** | 200, 5 results, `record_jina_snapshot`; 1 search (units), $ unexposed |
| Tests fail-pre/pass-post both committed raw | **MET** | R-FAILPRE 3F/2P; R-PASSPOST 5P |
| Gates green; Jina ≤2 searches; synthesis $0; production counts identical; no vacuous pass | **MET** | suite 2F/508P; ruff clean; mypy Δ0; secret 0; 2 attempts; $0 synth; 17/7/6/28/6 both |

**Vacuous-pass check (`PG-EV-01`, loudly):** no criterion passed vacuously. The 3 recording tests **genuinely failed** pre-change with `assert False is True` (raw committed), and the 2 pass-pre tests are gate tests that legitimately hold pre and post. The degraded test asserts the **named reason and the quoted raw text**, not merely a raise. The "one fetch = one row per source" test asserts `count() == 2` exactly, catching a double-write. The consent/over-cap tests assert `0 sends` **and** `0 rows`, not just a status code. The live legs quote real status codes/counts/raw resolver output. **Where this slice is weaker than it looks:** (a) the live legs are one-shot measurements — a single OFF product and a single Jina search, not a distribution; (b) Jina's `$` is not exposed by the client, so the spend criterion is met in **units** (searches) against an **uncalibrated** bound, not in measured dollars; (c) the production service is **old code** and the `enrich_snapshot` migration is **unapplied** there, so the new wiring is unreachable in production until the owner-gated rider (`PG-PR-05`).

## Interim honesty (`PG-PR-05`)

The production DB **lacks** the `enrich_snapshot` table until a later owner-gated rider applies the migration and deploys; the running service is old code, so the new wiring is unreachable there. Proof in this slice is **tests + in-process live legs on temp DBs**, never the deployed service. Production was touched **read-only** for before/after counts only.

## Report note on the notes ref (receipt)

Work pushed to `automation`; worktree clean. Note added on `WORK_HEAD`, notes ref pushed, and verified against the **fetched, mapped** ref. Executed, verbatim:

```
<paste filled after commit>
```

No push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`. The final tip (the docs-only receipt commit) is dual-annotated too (note-anchor inoculation, SG-092 precedent). `note=yes`.

---

## UNCLEAR

- **FIRST READ:** the packet's `enrich.py:209` `snapshots_recorded: False` and the `.primary`/`.fallback` record shape both held; the writer's explicit `query` kwarg held. The one wording I had to decide: G2 Leg C is labelled "Jina **global**" while the standing line says EU stays the default — I read it as *run the metered leg against the global base (the only base that resolves here) without changing the code default*, which the evidence supports (EU is NXDOMAIN on this host). The packet's line-reference `:209` was pre-hunk; after my edits the flip sits at `:220`.
- **DURING EXECUTION:** `eu.s.jina.ai` is **NXDOMAIN** on this host (raw resolver output quoted) while `s.jina.ai` resolves — so the EU "retrieval attempt" is a loud transport degradation, and the only meaningful live Jina search is at the global base. The packet's raw-body recorder lever, implemented as a response event hook, captured a `ResponseNotRead` error on the real network (F-SG102-2); the snapshot's own `raw`/`raw_text` was never affected.
- **REMAINING:** the migration is **unapplied in production** and the wiring is not deployed (owner-gated rider owed, `PG-PR-04`/`PG-PR-05`); reviewer alternatives (`web_alternates` first-class rows) ride SG-103; the Jina `$` actual remains unmeasurable from the client (uncalibrated bound only); `.rules-cache/` is still absent (published hash now verified from the contract checkout, F-SG099-3 narrowed); no live distribution of OFF results — a single product search.

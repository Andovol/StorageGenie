# SG-122 — report

**Dispatch-ID:** SG-122 · **Coder:** opencode · **Effort:** high · **Model:** opencode-go/deepseek-v4.1-flash
**Work dir:** `/home/andrei/StorageGenie` · **Remote:** `origin` = `git@github.com:Andovol/StorageGenie.git`
**BASE REF:** `origin/automation` · **BASE_RESOLVED:** `a1616dd4e28a66f7df1ff25be65019958b5acb4e` · **START_HEAD:** `a1616dd4e28a66f7df1ff25be65019958b5acb4e` · **WORK_HEAD:** `9108c44308d2cf5992a02cfb8ea5cd7375e83d4f`
**Spend (real $):** $0.000000 — zero metered calls on any path.
**Contract:** recorded `0.37.0` == published `1acd7730e5fa6de5b7403aacce71207e9946461d` (D15 adoption); source path `/home/andrei/storagegenie-contract/{VERSION,HEAD}`.

## MODEL + EFFORT provenance
- EFFORT `high` read from process arguments: `opencode run --auto --dir /home/andrei/StorageGenie --variant high <packet>`.
- MODEL `opencode-go/deepseek-v4.1-flash` read from provider metadata in the run log (`providerID=opencode-go`, model `deepseek-v4.1-flash`). No model id rode the dispatch trigger.

## G0 — capability + before-census + shape verification
- **Capability:** `docker ps` → `storagegenie-backend-1 Up 2 hours (healthy)`; health exact `{"status":"ok","db":"ok","storage":"ok"}` HTTP 200; `alembic current` → `20260924_sg114_relation (head)` — packet hypothesis **VERIFIED**.
- **Before-census 0/0/0** (queries in `SG-122_verify.log`): `location 0`, `asset_location 0`, `asset_relation 0`. Tree was still in SG-121's empty state → safe to seed (`PG-IC-08`). Not nonzero in either direction.
- **Live ids re-discovered read-only** (`PG-IC-09`, not inherited): household `01a0a029-1477-7ca0-b200-bce78a96c679` (Popescu Household); asset A `01a0a467-eb0e-7b83-a227-af122dc9268b` (Toothpaste); asset B `01a0c446-44c9-7b82-9d1c-2b51fa518191` (CEAFĂ DE PORC). Both match SG-121's expected ids.
- **Shape verification** (`PG-SC-03`) — required body fields as the CODE defines them, **all match the packet's expectation, no mismatch**:
  - `locations.py:140 @router.post("/locations", status_code=201)` · `LocationCreate` (`:31`) → `name: str` **required** (non-blank, ≤200, stripped), `parent_id: str | None = None` optional.
  - `locations.py:217 @router.post("/assets/{asset_id}/locations")` (200) · `AssignLocationRequest` (`:63`) → `location_id: str` **required**.
  - `relations.py:113 @router.post("/assets/{asset_id}/relations", status_code=201)` · `RelationCreate` (`:40`) → `to_asset_id: str` + `relation_type: str` **required**, vocabulary `RELATION_TYPES = {"related_to","contains"}` (`:29`); `"related_to"` is valid.

## G1 — the three POSTs (status + body + created id)
| # | Route | Status | Created identifier |
|---|---|---|---|
| P1 | `POST /v1/locations?household_id=01a0a029-…679` body `{"name":"Kitchen"}` | **201** | location `01a0d89a-19c3-7460-b187-ecb7d0c0733f` |
| P2 | `POST /v1/assets/01a0a467-…68b/locations?household_id=01a0a029-…679` body `{"location_id":"01a0d89a-19c3-7460-b187-ecb7d0c0733f"}` | **200** | binding asset A ↔ location (row in `asset_location`) |
| P3 | `POST /v1/assets/01a0a467-…68b/relations?household_id=01a0a029-…679` body `{"to_asset_id":"01a0c446-44c9-7b82-9d1c-2b51fa518191","relation_type":"related_to"}` | **201** | relation `01a0d89a-5aa3-78c1-8eb3-7424c1d99e72` (A→B) |

Raw bodies are pasted verbatim in `SG-122_verify.log`. All three rows are **left in place** (`PG-EV-06`); no cleanup DELETE.

## G2 — re-run SG-121 GETs (row-bearing)
| Route | Status | Row-bearing evidence |
|---|---|---|
| `GET /v1/locations?household_id=…679` | 200 | `{"items":[{"id":"01a0d89a-19c3-7460-b187-ecb7d0c0733f","name":"Kitchen",…}]}` |
| `GET /v1/assets/01a0a467-…68b/relations?household_id=…679` | 200 | `{"items":[{"id":"01a0d89a-5aa3-78c1-8eb3-7424c1d99e72",…,"relation_type":"related_to","direction":"outgoing"}]}` |
| `GET /v1/assets/01a0a467-…68b?household_id=…679` | 200 | `"locations":[{"id":"01a0d89a-19c3-7460-b187-ecb7d0c0733f","name":"Kitchen",…}]`, `"relations":[{…}]` — both present and row-bearing |

Post-census (read): `location 1`, `asset_location 1`, `asset_relation 1`.

## G3 — verdict (exactly one)
**SEEDED** — three rows created through the real write routes with ids quoted, all re-run reads row-bearing; SG-121's REMAINING closes, recommend nothing.

## Acceptance criteria check (`PG-SC-09`)
- Census question — "is the tree still in SG-121's empty state, safe to seed?" → **yes**, 0/0/0 quoted.
- Writes question — "did the real routes accept exactly three rows?" → **yes**, three status codes + created ids quoted (a 201/200 without a quoted id would evidence nothing; ids are quoted).
- Re-reads question — "do the activated surfaces now answer against data?" → **yes**, three row-bearing bodies quoted.
- No fourth mutation: exactly P1/P2/P3. No vacuous pass: every write carries its created identifier.

## Actual versus budget (units: seconds, live clock)
| Leg | Start | End | Actual | Budget |
|---|---|---|---|---|
| G0 capability/census/handlers | 12:44:30Z | 12:46:12Z | ~102s | 60s ordinary / 600s overall |
| G1 three POSTs | 12:46:12Z | 12:46:29Z | ~17s | 60s ordinary |
| G2 re-run GETs + post-census | 12:46:29Z | 12:46:44Z | ~15s | 60s ordinary |
| G4 files/commit/receipt | 12:46:44Z | — | in progress | 600s overall |

No command was killed or timed out; every command carried a 60s bound.

## Receipt — note on `refs/notes/storagegenie-coder-reports` (pasted verbatim)
$ git notes --ref=refs/notes/storagegenie-coder-reports show 9108c44308d2cf5992a02cfb8ea5cd7375e83d4f
error: no note found for object 9108c44308d2cf5992a02cfb8ea5cd7375e83d4f.
pre_show_exit=1                                   # no existing note -> refusal guard did not fire

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m \
    "Dispatch-ID: SG-122 | Report: docs/worklogs/SG-122_report.md | Work-HEAD: 9108c44308d2cf5992a02cfb8ea5cd7375e83d4f" \
    9108c44308d2cf5992a02cfb8ea5cd7375e83d4f
add_exit=0

$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   2e59d2e..10e9638  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_exit=0

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg122-verify
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg122-verify
fetch_exit=0

$ git notes --ref=refs/notes/sg122-verify show 9108c44308d2cf5992a02cfb8ea5cd7375e83d4f
Dispatch-ID: SG-122 | Report: docs/worklogs/SG-122_report.md | Work-HEAD: 9108c44308d2cf5992a02cfb8ea5cd7375e83d4f
show_exit=0

note=yes

## UNCLEAR
- **FIRST READ:** the packet's G2 says "≤4 GETs" but lists three; I ran the three listed (locations, relations, asset-detail) — the fourth slot unused. No ambiguity affected execution.
- **DURING EXECUTION:** `sqlite3` is not installed in `storagegenie-backend-1`; I used the container's `python` with the stdlib `sqlite3` module for all read-only census/SELECT probes (still a read; no other runtime launched).
- **REMAINING:** none for this slice — the three seed rows are live by design and removal is the Architect's decision, not this packet's.

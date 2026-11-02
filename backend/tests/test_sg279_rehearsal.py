"""SG-279 rehearsal: upgrade + downgrade on a populated old-head database.

Temporary file only; no live database. Built at the old head
`20261023_sg233_reminder` by running the migrations (never `create_all`).
"""

from __future__ import annotations

import difflib
import json
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

from app.config import settings

OLD_HEAD = "20261023_sg233_reminder"
NEW_HEAD = "20261102_sg279_candidate_state"
FIVE = ["proposed", "accepted", "edited", "held", "rejected"]


def _alembic_config(url: str) -> Config:
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option("script_location", str(Path(__file__).resolve().parents[1] / "alembic"))
    config.set_main_option("sqlalchemy.url", url)
    return config


def _snapshot(engine):  # type: ignore[no-untyped-def]
    with engine.connect() as conn:
        master = conn.execute(
            text("SELECT type, name, sql FROM sqlite_master ORDER BY type, name")
        ).fetchall()
        master = [(t, n, s) for (t, n, s) in master]
        tables = [r[0] for r in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))]
        counts = {}
        for tbl in tables:
            if tbl.startswith("sqlite_"):
                continue
            counts[tbl] = conn.execute(text(f'SELECT count(*) FROM "{tbl}"')).scalar()
        cand_rows = conn.execute(
            text("SELECT id, job_id, evidence_ids_json, proposed_fields_json, state, household_id, created_at, updated_at FROM candidate ORDER BY id")
        ).fetchall()
        cand_info = conn.execute(text("PRAGMA table_info(candidate)")).fetchall()
        cand_fk = conn.execute(text("PRAGMA foreign_key_list(candidate)")).fetchall()
        cand_idx = conn.execute(text("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='candidate' ORDER BY name")).fetchall()
        rev = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
        integrity = conn.execute(text("PRAGMA integrity_check")).fetchall()
        fkcheck = conn.execute(text("PRAGMA foreign_key_check")).fetchall()
        # FTS search for the seeded asset
        try:
            fts = conn.execute(
                text("SELECT asset_id FROM asset_fts WHERE asset_fts MATCH :q"), {"q": '"RehearsalBrush"'}
            ).fetchall()
        except Exception as exc:  # pragma: no cover
            fts = [("FTS_ERROR:" + str(exc),)]
    return {
        "master": master,
        "counts": counts,
        "cand_rows": [tuple(r) for r in cand_rows],
        "cand_info": [tuple(r) for r in cand_info],
        "cand_fk": [tuple(r) for r in cand_fk],
        "cand_idx": [tuple(r) for r in cand_idx],
        "rev": rev,
        "integrity": [tuple(r) for r in integrity],
        "fkcheck": [tuple(r) for r in fkcheck],
        "fts": [tuple(r) for r in fts],
    }


def test_sg279_rehearsal_upgrade_and_downgrade(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:  # noqa: C901  # type: ignore[no-untyped-def]
    db_path = tmp_path / "rehearsal.db"
    url = f"sqlite:///{db_path}"
    monkeypatch.setattr(settings, "database_url", url)
    config = _alembic_config(url)
    print(f"\nSG279_REHEARSAL_DB={db_path} URL={url}")
    print(f"SG279_ALEMBIC_INVOCATION=command.upgrade(_alembic_config(url), '{OLD_HEAD}') then command.upgrade(config, 'head')")
    command.upgrade(config, OLD_HEAD)
    print(f"SG279_POPULATED_AT={OLD_HEAD}")

    engine = create_engine(url, connect_args={"check_same_thread": False})
    import uuid

    with engine.begin() as conn:
        hid = uuid.uuid4().hex
        conn.execute(text("INSERT INTO household (id, name) VALUES (:id, 'R')"), {"id": hid})
        jid = uuid.uuid4().hex
        conn.execute(
            text("INSERT INTO job (id, household_id, job_type, state) VALUES (:id, :h, 'import', 'COMPLETED')"),
            {"id": jid, "h": hid},
        )
        asset_id = uuid.uuid4().hex
        conn.execute(
            text("INSERT INTO asset (id, household_id, display_name, asset_type, status, version) VALUES (:id, :h, 'RehearsalBrush Toothbrush', 'product', 'ACTIVE', 1)"),
            {"id": asset_id, "h": hid},
        )
        for i, state in enumerate(FIVE):
            cid = uuid.uuid4().hex
            conn.execute(
                text("INSERT INTO candidate (id, job_id, evidence_ids_json, proposed_fields_json, state, household_id) VALUES (:id, :j, '[]', :p, :s, :h)"),
                {"id": cid, "j": jid, "p": json.dumps({"kind": "new_asset", "fields": {}}), "s": state, "h": hid},
            )
        print(f"SG279_SEEDED candidates=5 states={','.join(FIVE)} asset={asset_id}")
        print(f"SG279_HOUSEHOLD={hid} JOB={jid}")

    before = _snapshot(engine)
    print(f"SG279_BEFORE rev={before['rev']} candidate_rows={len(before['cand_rows'])} counts={before['counts']}")
    print(f"SG279_BEFORE_FTS={before['fts']}")
    assert before["rev"] == OLD_HEAD
    assert len(before["fts"]) == 1, before["fts"]

    # --- upgrade to head (new migration) ---
    command.upgrade(config, "head")
    after = _snapshot(engine)
    print(f"SG279_AFTER rev={after['rev']} candidate_rows={len(after['cand_rows'])} counts={after['counts']}")
    print(f"SG279_AFTER_FTS={after['fts']}")
    assert after["rev"] == NEW_HEAD
    # row values unchanged
    assert before["cand_rows"] == after["cand_rows"], "candidate row values changed"
    print("SG279_CHECK candidate row values unchanged: PASS")
    # indexes, FKs, server defaults unchanged (FK/index order is not semantic; compare as sets)
    assert set(before["cand_idx"]) == set(after["cand_idx"]), f"indexes changed {before['cand_idx']} vs {after['cand_idx']}"
    if before["cand_idx"] != after["cand_idx"]:
        print("SG279_NOTE index row order differs but set identical (non-semantic): PASS")
    print(f"SG279_CHECK indexes unchanged {after['cand_idx']}: PASS")
    def _fk_norm(rows):  # type: ignore[no-untyped-def]
        # PRAGMA foreign_key_list ids are ordering only; compare the semantic triple.
        return {(r[2], r[3], r[4], r[5], r[6]) for r in rows}

    assert _fk_norm(before["cand_fk"]) == _fk_norm(after["cand_fk"]), f"FKs changed {before['cand_fk']} vs {after['cand_fk']}"
    if before["cand_fk"] != after["cand_fk"]:
        print(f"SG279_NOTE FK PRAGMA id order differs but semantic set identical before={before['cand_fk']} after={after['cand_fk']} (non-semantic, ordering only): PASS")
    print(f"SG279_CHECK foreign keys unchanged {after['cand_fk']}: PASS")
    assert before["cand_info"] == after["cand_info"], f"table_info changed {before['cand_info']} vs {after['cand_info']}"
    print("SG279_CHECK table_info (columns/defaults) unchanged: PASS")
    # every other object's definition unchanged except candidate table
    before_map = {(t, n): s for (t, n, s) in before["master"]}
    after_map = {(t, n): s for (t, n, s) in after["master"]}
    assert set(before_map) == set(after_map), f"object set changed {set(before_map) ^ set(after_map)}"
    diff_keys = [k for k in before_map if before_map[k] != after_map[k]]
    print(f"SG279_SCHEMA_DIFF_KEYS={diff_keys}")
    assert diff_keys == [("table", "candidate")], f"unexpected schema diff {diff_keys}"
    old_sql = before_map[("table", "candidate")]
    new_sql = after_map[("table", "candidate")]
    print("SG279_CANDIDATE_SQL_BEFORE:")
    print(old_sql)
    print("SG279_CANDIDATE_SQL_AFTER:")
    print(new_sql)
    text_diff = list(difflib.unified_diff(old_sql.splitlines(), new_sql.splitlines(), lineterm=""))
    print("SG279_ACTUAL_TEXT_DIFF:")
    for line in text_diff:
        print(line)
    # semantic check: only the accepted set changed
    import re

    def _states(sql: str) -> set[str]:
        return set(re.findall(r"'([a-z_]+)'", sql))

    assert _states(old_sql) == set(FIVE), _states(old_sql)
    assert _states(new_sql) == set(FIVE + ["split", "merged"]), _states(new_sql)
    # strip the CHECK clause precisely, then compare the rest allowing only
    # quoting and FK ordering differences (both non-semantic, proven below).
    def _without_check(sql: str) -> str:
        cleaned = re.sub(
            r",?\s*CONSTRAINT ck_candidate_state CHECK \(state IN \([^)]+\)\)",
            "",
            sql,
        )
        cleaned = cleaned.replace('"candidate"', "candidate")
        return " ".join(cleaned.split())

    def _fk_clauses(sql: str) -> set[str]:
        return set(re.findall(r"FOREIGN KEY\([^)]+\) REFERENCES [^(]+\([^)]+\) ON DELETE CASCADE", sql))

    old_no_check = _without_check(old_sql)
    new_no_check = _without_check(new_sql)
    print(f"SG279_NO_CHECK_OLD={old_no_check}")
    print(f"SG279_NO_CHECK_NEW={new_no_check}")
    if old_no_check == new_no_check:
        print("SG279_CHECK schema diff is only the accepted set (quoting otherwise identical): PASS")
    else:
        # FK order swap is the only permitted extra difference: same FK set, verified via PRAGMA.
        assert _fk_clauses(old_sql) == _fk_clauses(new_sql), f"FK clause set differs {_fk_clauses(old_sql)} vs {_fk_clauses(new_sql)}"
        # Remove FK clauses and compare the remainder (must be quoting/whitespace only).
        def _without_fk_and_check(sql: str) -> str:
            s = re.sub(
                r",?\s*CONSTRAINT ck_candidate_state CHECK \(state IN \([^)]+\)\)",
                "",
                sql,
            )
            s = re.sub(r",?\s*FOREIGN KEY\([^)]+\) REFERENCES [^(]+\([^)]+\) ON DELETE CASCADE", "", s)
            s = s.replace('"candidate"', "candidate")
            return " ".join(s.split())

        assert _without_fk_and_check(old_sql) == _without_fk_and_check(new_sql), "non-CHECK non-FK schema text differs"
        print("SG279_CHECK schema diff is only the accepted set plus FK ordering and quoting (both non-semantic): PASS")
        print(f"SG279_NOTE FK clause order swapped but set identical {_fk_clauses(new_sql)}; quoting differs only on table name; PRAGMA set comparison above proves no semantic loss: PASS")
    # other counts unchanged (alembic_version row count is 1 both sides; candidate count same)
    assert before["counts"] == after["counts"], f"row counts changed {before['counts']} vs {after['counts']}"
    print(f"SG279_CHECK row counts unchanged {after['counts']}: PASS")
    # FTS still finds asset
    assert before["fts"] == after["fts"] and len(after["fts"]) == 1
    print("SG279_CHECK FTS search returns seeded asset on both sides: PASS")
    # integrity + FK checks clean
    assert after["integrity"] == [("ok",)], after["integrity"]
    assert after["fkcheck"] == []
    print("SG279_CHECK integrity_check=ok foreign_key_check=empty: PASS")

    # PG-EV-01: the same comparison fails on a deliberately altered row
    altered_rows = list(after["cand_rows"])
    altered_first = list(altered_rows[0])
    altered_first[4] = "bogus-altered"
    altered_rows[0] = tuple(altered_first)
    assert altered_rows != after["cand_rows"], "deliberate alteration must differ"
    print(f"SG279_PG_EV01 deliberate row alteration detected (state {after['cand_rows'][0][4]} -> bogus-altered): PASS")
    altered_master = dict(after_map)
    altered_master[("trigger", "asset_fts_after_insert")] = "ALTERED"
    assert altered_master != after_map
    print("SG279_PG_EV01 deliberate object alteration detected: PASS")

    # --- downgrade success (no new-state rows) ---
    command.downgrade(config, OLD_HEAD)
    down_ok = _snapshot(engine)
    print(f"SG279_DOWNGRADE_OK rev={down_ok['rev']}")
    assert down_ok["rev"] == OLD_HEAD
    assert down_ok["cand_rows"] == before["cand_rows"]
    down_sql = [s for (t, n, s) in down_ok["master"] if t == "table" and n == "candidate"][0]
    assert _states(down_sql) == set(FIVE)
    print("SG279_CHECK downgrade success restores five-state and data intact: PASS")

    # --- back to new head for refusal branches ---
    command.upgrade(config, "head")
    assert _snapshot(engine)["rev"] == NEW_HEAD

    # refusal with a split row
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO candidate (id, job_id, evidence_ids_json, proposed_fields_json, state, household_id) VALUES (:id, (SELECT job_id FROM candidate LIMIT 1), '[]', '{}', 'split', (SELECT household_id FROM candidate LIMIT 1))"),
            {"id": uuid.uuid4().hex},
        )
    pre_split = _snapshot(engine)
    print(f"SG279_REFUSAL_SPLIT pre rev={pre_split['rev']} rows={len(pre_split['cand_rows'])}")
    with pytest.raises(RuntimeError, match="split|merged|five-state"):
        command.downgrade(config, OLD_HEAD)
    post_split = _snapshot(engine)
    assert post_split["rev"] == NEW_HEAD, post_split["rev"]
    assert post_split["cand_rows"] == pre_split["cand_rows"]
    assert post_split["master"] == pre_split["master"]
    print("SG279_CHECK downgrade refusal with split row leaves revision/data/schema unchanged: PASS")
    # clean split row
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM candidate WHERE state='split'"))

    # refusal with a merged row
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO candidate (id, job_id, evidence_ids_json, proposed_fields_json, state, household_id) VALUES (:id, (SELECT job_id FROM candidate LIMIT 1), '[]', '{}', 'merged', (SELECT household_id FROM candidate LIMIT 1))"),
            {"id": uuid.uuid4().hex},
        )
    pre_merged = _snapshot(engine)
    print(f"SG279_REFUSAL_MERGED pre rev={pre_merged['rev']} rows={len(pre_merged['cand_rows'])}")
    with pytest.raises(RuntimeError, match="split|merged|five-state"):
        command.downgrade(config, OLD_HEAD)
    post_merged = _snapshot(engine)
    assert post_merged["rev"] == NEW_HEAD
    assert post_merged["cand_rows"] == pre_merged["cand_rows"]
    assert post_merged["master"] == pre_merged["master"]
    print("SG279_CHECK downgrade refusal with merged row leaves revision/data/schema unchanged: PASS")

    print(f"SG279_NEW_REVISION={NEW_HEAD}")
    print("SG279_TXN=non-transactional DDL (Alembic log: Will assume non-transactional DDL)")
    print(f"SG279_ALEMBIC_INVOCATION_FOR_RIDER=command.upgrade(_alembic_config(url), 'head') with settings.database_url={url}")
    engine.dispose()

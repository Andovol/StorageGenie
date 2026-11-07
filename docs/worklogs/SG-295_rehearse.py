"""SG-295 G3 rehearsal on copies while the app keeps running.

Holds no owner data: prints counts, hashes, schema comparison results,
revisions, container image ids and HTTP status codes only.
All copies live under output/SG-295-scratch/ and are removed by exact path
by the operator at the end of the slice (not by this script).
The live database is read only through SQLite's backup API from a read-only
mount; the live container is never touched here.
"""
import hashlib
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time

ROOT = "/home/andrei/StorageGenie"
SCRATCH = f"{ROOT}/output/SG-295-scratch"
LIVE_DIR = f"{ROOT}/data/db"
SG279_LOG = f"{ROOT}/docs/worklogs/SG-279_rehearsal.log"
NEW_IMAGE = "storagegenie-backend:latest"
RECOVERY_IMAGE = "storagegenie-backend:recovery-sg270"
RECOVERY_ID = "sha256:2acd0c2438f34b5070b13bd04fa898b42cde126241dab43b0d124aa3a7a99ea2"
LABEL = "sg295-scratch"
RUN_NAME = "sg295-recovery-run"
OLD_REV = "20261023_sg233_reminder"
NEW_REV = "20261102_sg279_candidate_state"
OLD_STATES = sorted(["proposed", "accepted", "edited", "held", "rejected"])
NEW_STATES = sorted(["proposed", "accepted", "edited", "held", "rejected", "split", "merged"])

os.environ["DOCKER_CONFIG"] = f"{SCRATCH}/docker-config"
os.environ["DOCKER_HOST"] = "unix:///run/dispatch-storagegenie-SG-295/docker.sock"

T0 = time.time()

KILL_SCRIPT = '''"""Interrupt the real SG-279 migration right after candidate is dropped."""
import os
from sqlalchemy import event
from sqlalchemy.engine import Engine


def _after(conn, cursor, statement, parameters, context, executemany):
    s = (statement or "").upper()
    if "DROP TABLE" in s and "CANDIDATE" in s and "_ALEMBIC_TMP" not in s:
        print("KILLPOINT after drop of candidate; exiting", flush=True)
        os._exit(99)


event.listen(Engine, "after_cursor_execute", _after)
from alembic.config import Config
from alembic import command

command.upgrade(Config("/app/alembic.ini"), "head")
'''

PROBE = (
    "import urllib.request as u, urllib.error as e\n"
    "def g(p):\n"
    "    try:\n"
    "        return str(u.urlopen('http://127.0.0.1:8000' + p, timeout=10).status)\n"
    "    except e.HTTPError as x:\n"
    "        return str(x.code)\n"
    "    except Exception as x:\n"
    "        return type(x).__name__\n"
    "print('HEALTH', g('/v1/health'))\n"
    "print('HOUSEHOLDS', g('/v1/households'))\n"
)


def say(msg):
    print(f"[{time.time() - T0:7.1f}s] {msg}", flush=True)


def run(cmd, timeout=300):
    say("+ " + " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.stdout and r.stdout.strip():
        print(r.stdout.rstrip()[-3000:], flush=True)
    if r.stderr and r.stderr.strip():
        print(r.stderr.rstrip()[-3000:], flush=True)
    print(f"RC={r.returncode}", flush=True)
    return r


def docker_run(extra, image, cmd):
    return ["docker", "run", "--rm", "--network", "none", "--label", LABEL, *extra, image, *cmd]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sidecar_bytes(path, suffix):
    p = path + suffix
    return os.path.getsize(p) if os.path.exists(p) else None


def drop_sidecars(path):
    for s in ("-wal", "-shm"):
        if os.path.exists(path + s):
            os.remove(path + s)


def fresh(src, dst):
    drop_sidecars(dst)
    if os.path.exists(dst):
        os.remove(dst)
    shutil.copyfile(src, dst)


def norm(s):
    return re.sub(r"\s+", " ", (s or "").strip())


def ro(path):
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def master_map(path):
    con = ro(path)
    try:
        return {(t, n): norm(s) for t, n, s in con.execute("SELECT type, name, sql FROM sqlite_master")}
    finally:
        con.close()


def table_counts(path):
    con = ro(path)
    try:
        tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        return {t: con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in tables}
    finally:
        con.close()


def candidate_rowhash(path):
    con = ro(path)
    try:
        cols = [r[1] for r in con.execute("PRAGMA table_info(candidate)")]
        rows = con.execute(f'SELECT {", ".join(cols)} FROM candidate ORDER BY id').fetchall()
        h = hashlib.sha256()
        for row in rows:
            h.update(repr(tuple("" if v is None else str(v) for v in row)).encode())
        return h.hexdigest(), len(rows)
    finally:
        con.close()


def semantic(path):
    con = ro(path)
    try:
        sql = con.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='candidate'").fetchone()[0]
        fks = sorted((r[2], r[3], r[4], r[5], r[6]) for r in con.execute("PRAGMA foreign_key_list(candidate)"))
        cols = [tuple(r[1:]) for r in con.execute("PRAGMA table_info(candidate)")]
        m = re.search(r"CHECK \(state IN \(([^)]*)\)\)", sql)
        states = sorted(re.findall(r"'([a-z_]+)'", m.group(1))) if m else None
        return {"states": states, "fks": fks, "cols": cols}
    finally:
        con.close()


def verify(path, expect_rev):
    """Refusal is any exception or any failed check. Same function for restore and for the truncated copy."""
    try:
        con = ro(path)
        try:
            ic = con.execute("PRAGMA integrity_check").fetchone()[0]
            fk = con.execute("PRAGMA foreign_key_check").fetchall()
            rev = con.execute("SELECT version_num FROM alembic_version").fetchone()[0]
        finally:
            con.close()
    except Exception as e:
        return False, f"unreadable {type(e).__name__}"
    ok = ic == "ok" and not fk and rev == expect_rev
    return ok, f"integrity={ic} fk_violations={len(fk)} rev={rev}"


def step1_upgrade(live_copy, base_counts, base_cand):
    s1 = f"{SCRATCH}/s1-upgrade.db"
    fresh(live_copy, s1)
    pre_counts = table_counts(s1)
    pre_cand = candidate_rowhash(s1)
    pre_master = master_map(s1)
    pre_sem = semantic(s1)
    r = run(docker_run(["-v", f"{SCRATCH}:/scratch", "-e", "DATABASE_URL=sqlite:////scratch/s1-upgrade.db"],
                       NEW_IMAGE, ["alembic", "upgrade", "head"]))
    if r.returncode != 0:
        say("STEP1 upgrade command failed")
        return False
    ok_v, det = verify(s1, NEW_REV)
    post_counts = table_counts(s1)
    post_cand = candidate_rowhash(s1)
    post_master = master_map(s1)
    post_sem = semantic(s1)
    changed = sorted(k for k in set(pre_master) | set(post_master) if pre_master.get(k) != post_master.get(k))
    say(f"step1 verify {det} ok={ok_v}")
    say(f"step1 counts_equal={pre_counts == post_counts} candidate_rows={post_cand[1]} rowhash_equal={pre_cand[0] == post_cand[0]}")
    say(f"step1 objects_changed={changed}")
    say(f"step1 states_after={post_sem['states']} fks_equal={pre_sem['fks'] == post_sem['fks']} cols_equal={pre_sem['cols'] == post_sem['cols']}")
    say(f"step1 counts_equal_to_live_copy={post_counts == base_counts} rowhash_equal_to_live_copy={post_cand[0] == base_cand[0]}")
    schema_ok = (
        changed == [("table", "candidate")]
        and post_sem["states"] == NEW_STATES
        and pre_sem["fks"] == post_sem["fks"]
        and pre_sem["cols"] == post_sem["cols"]
    )
    data_ok = post_counts == pre_counts and pre_cand[0] == post_cand[0]
    if not (ok_v and schema_ok and data_ok):
        say("STEP1 upgrade verification failed")
        return False
    con = sqlite3.connect(s1, isolation_level=None)
    try:
        con.execute("PRAGMA foreign_keys=ON")
        cid = con.execute("SELECT id FROM candidate LIMIT 1").fetchone()[0]
        con.execute("BEGIN")
        con.execute("UPDATE candidate SET state='split' WHERE id=?", (cid,))
        split_ok = True
        con.execute("UPDATE candidate SET state='merged' WHERE id=?", (cid,))
        merged_ok = True
        try:
            con.execute("UPDATE candidate SET state='bogus' WHERE id=?", (cid,))
            bogus = "accepted"
        except sqlite3.IntegrityError as e:
            bogus = "refused_ck_candidate_state" if "ck_candidate_state" in str(e) else f"refused_other:{e}"
        con.execute("ROLLBACK")
    finally:
        con.close()
    rb_equal = candidate_rowhash(s1)[0] == post_cand[0]
    say(f"step1 in_transaction split_accepted={split_ok} merged_accepted={merged_ok} bogus={bogus} rolled_back_rowhash_equal={rb_equal}")
    passed = split_ok and merged_ok and bogus == "refused_ck_candidate_state" and rb_equal
    say(f"STEP1 {'PASS' if passed else 'FAIL'}")
    return passed


def step2_interrupt(live_copy):
    s2 = f"{SCRATCH}/s2-interrupted.db"
    fresh(live_copy, s2)
    with open(f"{SCRATCH}/kill_after_drop.py", "w") as f:
        f.write(KILL_SCRIPT)
    r = run(docker_run(["-v", f"{SCRATCH}:/scratch", "-e", "DATABASE_URL=sqlite:////scratch/s2-interrupted.db"],
                       NEW_IMAGE, ["python", "/scratch/kill_after_drop.py"]))
    try:
        names = master_map(s2)
        cand_present = ("table", "candidate") in names
        tmp_present = ("table", "_alembic_tmp_candidate") in names
        rev = ro(s2).execute("SELECT version_num FROM alembic_version").fetchone()[0]
    except Exception as e:
        say(f"step2 damaged file unreadable {type(e).__name__}")
        return False, s2
    damage = r.returncode != 0 and (not cand_present or tmp_present) and rev == OLD_REV
    say(f"step2 killer_rc={r.returncode} candidate_present={cand_present} tmp_candidate_present={tmp_present} rev={rev}")
    say(f"STEP2 damage_landed={damage}")
    return damage, s2


def step3_restore(live_copy, s2, base_counts, h_live):
    fresh(live_copy, s2)
    h_s2 = sha256(s2)
    ok_v, det = verify(s2, OLD_REV)
    c = table_counts(s2)
    say(f"step3 hash_equal_to_backup={h_s2 == h_live} {det} ok={ok_v} counts_equal={c == base_counts}")
    passed = h_s2 == h_live and ok_v and c == base_counts
    say(f"STEP3 {'PASS' if passed else 'FAIL'}")
    return passed


def step4_recovery_serves():
    os.makedirs(f"{SCRATCH}/storage", exist_ok=True)
    started = run(["docker", "run", "-d", "--name", RUN_NAME, "--label", LABEL, "--network", "none",
                   "-v", f"{SCRATCH}:/scratch",
                   "-e", "DATABASE_URL=sqlite:////scratch/s2-interrupted.db",
                   "-e", "STORAGE_ROOT=/scratch/storage",
                   RECOVERY_IMAGE])
    health = households = "not-run"
    try:
        if started.returncode != 0:
            say("step4 recovery container did not start")
            return False
        img = subprocess.run(["docker", "inspect", "--format", "{{.Image}}", RUN_NAME],
                             capture_output=True, text=True, timeout=60).stdout.strip()
        say(f"step4 container_image_is_recovery_tag_id={img == RECOVERY_ID}")
        deadline = time.time() + 120
        while time.time() < deadline:
            p = subprocess.run(["docker", "exec", RUN_NAME, "python", "-c", PROBE],
                               capture_output=True, text=True, timeout=120)
            vals = dict(line.split(" ", 1) for line in p.stdout.splitlines() if " " in line)
            health = vals.get("HEALTH", "no-output")
            households = vals.get("HOUSEHOLDS", "no-output")
            if health == "200":
                break
            time.sleep(2)
        say(f"step4 GET /v1/health={health} GET /v1/households={households}")
        logs = subprocess.run(["docker", "logs", RUN_NAME], capture_output=True, text=True, timeout=60)
        tb = (logs.stdout + logs.stderr).count("Traceback")
        say(f"step4 startup_log_traceback_count={tb}")
    finally:
        run(["docker", "stop", "-t", "20", RUN_NAME], timeout=300)
        run(["docker", "rm", RUN_NAME], timeout=120)
        gone = subprocess.run(["docker", "ps", "-a", "--filter", f"name=^{RUN_NAME}$", "--format", "{{.Names}}"],
                              capture_output=True, text=True, timeout=60).stdout.strip() == ""
        say(f"step4 scratch_container_removed_by_name={gone}")
    passed = health == "200" and households == "200" and gone
    say(f"STEP4 {'PASS' if passed else 'FAIL'}")
    return passed


def step5_truncated(live_copy, h_live):
    trunc = f"{SCRATCH}/s5-truncated.db"
    fresh(live_copy, trunc)
    size = os.path.getsize(trunc)
    with open(trunc, "r+b") as f:
        f.truncate(size // 2)
    ok_v, det = verify(trunc, OLD_REV)
    h_t = sha256(trunc)
    refused = (not ok_v) and h_t != h_live
    say(f"step5 truncated_bytes={size // 2} hash_equal_to_backup={h_t == h_live} verify_ok={ok_v} {det}")
    say(f"STEP5 {'PASS (refused)' if refused else 'FAIL (accepted)'}")
    return refused


def main():
    say("SG295-G3-START app stays up; copies under output/SG-295-scratch; counts/hashes only")
    live_copy = f"{SCRATCH}/live-copy.db"
    if os.path.exists(live_copy):
        os.remove(live_copy)
    drop_sidecars(live_copy)
    backup_py = (
        "import sqlite3;"
        "src=sqlite3.connect('file:/live/storagegenie.db?mode=ro',uri=True);"
        "dst=sqlite3.connect('/scratch/live-copy.db');"
        "src.backup(dst);dst.commit();dst.close();src.close();"
        "print('backup-ok');"
    )
    r = run(docker_run(["-v", f"{LIVE_DIR}:/live:ro", "-v", f"{SCRATCH}:/scratch"],
                       NEW_IMAGE, ["python", "-c", backup_py]))
    if r.returncode != 0 or not os.path.exists(live_copy):
        say("SG295-G3-STOP-S0 backup failed")
        return 2
    wal = sidecar_bytes(live_copy, "-wal")
    if wal not in (None, 0):
        say(f"SG295-G3-STOP-S0 backup copy has non-empty -wal ({wal} bytes)")
        return 2
    h_live = sha256(live_copy)
    base_counts = table_counts(live_copy)
    base_cand = candidate_rowhash(live_copy)
    ok_base, det_base = verify(live_copy, OLD_REV)
    say(f"live-copy sha256={h_live[:16]} {det_base} tables={len(base_counts)} candidate_rows={base_cand[1]} rowhash={base_cand[0][:16]} ok={ok_base}")
    if not ok_base:
        say("SG295-G3-STOP-S0 backup copy did not verify")
        return 2

    if not step1_upgrade(live_copy, base_counts, base_cand):
        say("SG295-G3-STOP-S0 step 1")
        return 2
    damage, s2 = step2_interrupt(live_copy)
    if not damage:
        say("SG295-G3-STOP-S0 step 2 no damage landed; rehearsal proves nothing")
        return 2
    if not step3_restore(live_copy, s2, base_counts, h_live):
        say("SG295-G3-STOP-S0 step 3")
        return 2
    if not step4_recovery_serves():
        say("SG295-G3-STOP-S0 step 4")
        return 2
    if not step5_truncated(live_copy, h_live):
        say("SG295-G3-STOP-S0 step 5")
        return 2
    say("SG295-G3-ALL-PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

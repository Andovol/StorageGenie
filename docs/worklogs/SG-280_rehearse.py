"""SG-280 G3 rehearsal on copies while the app keeps running.

Holds no owner data: prints counts, hashes, schema text and revision only.
All copies live under output/SG-280-scratch/, removed by exact path at the end
of the slice (not here). Live database is only read via SQLite backup API
from a read-only mount; the app keeps serving throughout.
"""
import hashlib
import os
import re
import shutil
import sqlite3
import subprocess
import sys

SCRATCH = "/home/andrei/StorageGenie/output/SG-280-scratch"
LIVE_COPY = os.path.join(SCRATCH, "live-copy.db")
NEW_IMAGE = "storagegenie-backend:latest"
OLD_IMAGE = "sha256:96a662414c234074c5323665276610d45ba58d753c72027072c96c0a2dc25f22"
OLD_REV = "20261023_sg233_reminder"
NEW_REV = "20261102_sg279_candidate_state"

os.environ["DOCKER_CONFIG"] = os.path.join(SCRATCH, "docker-config")
os.environ["DOCKER_HOST"] = "unix:///run/dispatch-storagegenie-SG-280/docker.sock"


def run(cmd, **kw):
    print("+ " + " ".join(cmd), flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, **kw)
    print(r.stdout[-2000:] if r.stdout else "", flush=True)
    print(r.stderr[-2000:] if r.stderr else "", flush=True)
    print(f"RC={r.returncode}", flush=True)
    return r


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm(s):
    return re.sub(r"\s+", " ", (s or "").strip())


def master_rows(path):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        return con.execute(
            "SELECT type, name, tbl_name, sql FROM sqlite_master ORDER BY type, name"
        ).fetchall()
    finally:
        con.close()


def table_counts(path):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        tables = [
            r[0]
            for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
        ]
        return {t: con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in tables}
    finally:
        con.close()


def candidate_rowhash(path):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        cols = [r[1] for r in con.execute("PRAGMA table_info(candidate)")]
        rows = con.execute(
            f'SELECT {", ".join(cols)} FROM candidate ORDER BY id'
        ).fetchall()
        h = hashlib.sha256()
        for row in rows:
            h.update(repr(tuple("" if v is None else str(v) for v in row)).encode())
        return h.hexdigest(), len(rows)
    finally:
        con.close()


def checks(path):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        ic = con.execute("PRAGMA integrity_check").fetchone()[0]
        con.execute("PRAGMA foreign_keys=ON")
        fk = con.execute("PRAGMA foreign_key_check").fetchall()
        rev = con.execute("SELECT version_num FROM alembic_version").fetchone()[0]
        return ic, len(fk), rev
    finally:
        con.close()


def main():
    print("SG280-G3-START app stays up; copies under scratch; counts/hashes only")
    # 0. read-only mount works with wal?
    r = run([
        "docker", "run", "--rm", "--label", "sg280-scratch",
        "-v", "/home/andrei/StorageGenie/data/db:/data/db:ro",
        NEW_IMAGE, "python", "-c",
        "import sqlite3;con=sqlite3.connect('file:/data/db/storagegenie.db?mode=ro',uri=True);"
        "print('ro-mount-ok', con.execute('SELECT COUNT(*) FROM candidate').fetchone()[0])",
    ])
    if r.returncode != 0 or "ro-mount-ok" not in (r.stdout or ""):
        print("SG280-G3-RO-MOUNT-FAIL STOP, not mounting read-write")
        return 2
    # backup via backup API from read-only mount
    backup_py = (
        "import sqlite3;"
        "src=sqlite3.connect('file:/live/storagegenie.db?mode=ro',uri=True);"
        "dst=sqlite3.connect('/scratch/live-copy.db');"
        "src.backup(dst);dst.commit();"
        "print('backup-ok');"
    )
    if os.path.exists(LIVE_COPY):
        os.remove(LIVE_COPY)
    r = run([
        "docker", "run", "--rm", "--label", "sg280-scratch",
        "-v", "/home/andrei/StorageGenie/data/db:/live:ro",
        "-v", "/home/andrei/StorageGenie/output/SG-280-scratch:/scratch",
        NEW_IMAGE, "python", "-c", backup_py,
    ])
    if r.returncode != 0 or not os.path.exists(LIVE_COPY):
        print("SG280-G3-BACKUP-FAIL STOP")
        return 2
    print(f"live-copy sha256={sha256_file(LIVE_COPY)}")
    base_counts = table_counts(LIVE_COPY)
    base_hash, base_n = candidate_rowhash(LIVE_COPY)
    print(f"live-copy counts tables={len(base_counts)} candidate={base_n} rowhash={base_hash[:16]}")
    # 1. upgrade on real data
    step1 = os.path.join(SCRATCH, "step1.db")
    shutil.copyfile(LIVE_COPY, step1)
    pre_counts = table_counts(step1)
    pre_hash, pre_n = candidate_rowhash(step1)
    pre_master = {(t, n): norm(s) for t, n, _, s in master_rows(step1)}
    r = run([
        "docker", "run", "--rm", "--label", "sg280-scratch",
        "-v", "/home/andrei/StorageGenie/output/SG-280-scratch:/scratch",
        "-e", "DATABASE_URL=sqlite:////scratch/step1.db",
        NEW_IMAGE, "alembic", "upgrade", "head",
    ])
    if r.returncode != 0:
        print("SG280-G3-STEP1-UPGRADE-FAIL STOP")
        return 2
    ic, fk_n, rev = checks(step1)
    post_counts = table_counts(step1)
    post_hash, post_n = candidate_rowhash(step1)
    post_master = {(t, n): norm(s) for t, n, _, s in master_rows(step1)}
    print(f"step1 rev={rev} integrity={ic} fk_violations={fk_n}")
    print(f"step1 counts_equal={pre_counts == post_counts} rowhash_equal={pre_hash == post_hash}")
    changed = [k for k in pre_master if k in post_master and pre_master[k] != post_master[k]]
    only = [k for k in post_master if k not in pre_master] + [k for k in pre_master if k not in post_master]
    print(f"step1 master_changed={changed} master_only={only}")
    if rev != NEW_REV or ic != "ok" or fk_n != 0 or pre_counts != post_counts or pre_hash != post_hash:
        print("SG280-G3-STEP1-VERIFY-FAIL STOP")
        return 2
    if set(changed) != {("table", "candidate")} or only:
        print("SG280-G3-STEP1-SCHEMA-FAIL STOP")
        return 2
    # split/merged accepted, invalid refused, rolled back
    con = sqlite3.connect(step1)
    try:
        con.execute("PRAGMA foreign_keys=ON")
        row = con.execute("SELECT id FROM candidate LIMIT 1").fetchone()
        cid = row[0]
        con.execute("BEGIN")
        try:
            con.execute("UPDATE candidate SET state='split' WHERE id=?", (cid,))
            print("step1 split accepted")
            con.execute("UPDATE candidate SET state='merged' WHERE id=?", (cid,))
            print("step1 merged accepted")
            try:
                con.execute("UPDATE candidate SET state='bogus' WHERE id=?", (cid,))
                print("step1 bogus unexpectedly accepted FAIL")
                con.execute("ROLLBACK")
                return 2
            except sqlite3.IntegrityError as e:
                msg = str(e)
                print(f"step1 bogus refused ok={('ck_candidate_state' in msg)}")
                if "ck_candidate_state" not in msg:
                    con.execute("ROLLBACK")
                    return 2
            con.execute("ROLLBACK")
        finally:
            try:
                con.execute("ROLLBACK")
            except Exception:
                pass
    finally:
        con.close()
    print("SG280-G3-STEP1-PASS")
    # 2. interrupted migration at worst point
    step2 = os.path.join(SCRATCH, "step2.db")
    shutil.copyfile(LIVE_COPY, step2)
    for suf in ("-wal", "-shm"):
        p = step2 + suf
        if os.path.exists(p):
            os.remove(p)
    wrapper = os.path.join(SCRATCH, "kill_after_drop.py")
    with open(wrapper, "w") as f:
        f.write(
            "import os\n"
            "from sqlalchemy import event\n"
            "from sqlalchemy.engine import Engine\n"
            "def _fn(*args):\n"
            "    try:\n"
            "        s = str(args[2]) if len(args) > 2 else ''\n"
            "    except Exception:\n"
            "        return\n"
            "    su = s.upper()\n"
            "    if 'RENAME' in su and 'CANDIDATE' in su:\n"
            "        print('KILLPOINT rename seen; exiting', flush=True)\n"
            "        os._exit(99)\n"
            "event.listen(Engine, 'before_cursor_execute', _fn)\n"
            "from alembic.config import Config\n"
            "from alembic import command\n"
            "cfg = Config('/app/alembic.ini')\n"
            "command.upgrade(cfg, 'head')\n"
        )
    r = run([
        "docker", "run", "--rm", "--label", "sg280-scratch",
        "-v", "/home/andrei/StorageGenie/output/SG-280-scratch:/scratch",
        "-e", "DATABASE_URL=sqlite:////scratch/step2.db",
        NEW_IMAGE, "python", "/scratch/kill_after_drop.py",
    ])
    print(f"step2 killer rc={r.returncode}")
    con = sqlite3.connect(f"file:{step2}?mode=ro", uri=True)
    try:
        names = {row[0] for row in con.execute("SELECT name FROM sqlite_master")}
        rev2 = None
        try:
            rev2 = con.execute("SELECT version_num FROM alembic_version").fetchone()[0]
        except Exception as e:
            print(f"step2 rev unreadable: {type(e).__name__}")
        print(f"step2 objects candidate_missing={('candidate' not in names)} tmp_present={('_alembic_tmp_candidate' in names)} rev={rev2}")
        damaged = (
            r.returncode != 0
            and ("candidate" not in names or "_alembic_tmp_candidate" in names)
            and rev2 == OLD_REV
        )
        print(f"step2 damage_landed={damaged}")
        if not damaged:
            print("SG280-G3-STEP2-NO-DAMAGE STOP rehearsal proves nothing")
            return 2
    finally:
        con.close()
    print("SG280-G3-STEP2-PASS")
    # 3. restore by exact S2 procedure
    for suf in ("", "-wal", "-shm"):
        p = step2 + suf
        if os.path.exists(p):
            os.remove(p)
    shutil.copyfile(LIVE_COPY, step2)
    for suf in ("-wal", "-shm"):
        p = step2 + suf
        if os.path.exists(p):
            os.remove(p)
    h_live = sha256_file(LIVE_COPY)
    h_step2 = sha256_file(step2)
    ic3, fk3, rev3 = checks(step2)
    c3 = table_counts(step2)
    print(f"step3 hash_equal={h_live == h_step2} integrity={ic3} fk={fk3} rev={rev3} counts_equal={c3 == base_counts}")
    if h_live != h_step2 or ic3 != "ok" or fk3 != 0 or rev3 != OLD_REV or c3 != base_counts:
        print("SG280-G3-STEP3-FAIL STOP")
        return 2
    print("SG280-G3-STEP3-PASS")
    # 4. old image reads restored file (expected to fail if image object gone)
    r = run([
        "docker", "create", "--label", "sg280-scratch",
        "--name", "sg280-old-read",
        "-v", "/home/andrei/StorageGenie/output/SG-280-scratch:/scratch",
        "-e", "DATABASE_URL=sqlite:////scratch/step2.db",
        "-e", "STORAGE_ROOT=/scratch/storage",
        OLD_IMAGE, "python", "-c", "print('old-image-present')",
    ])
    if r.returncode != 0:
        print("SG280-G3-STEP4-OLD-IMAGE-MISSING STOP in S0")
        return 3
    run(["docker", "rm", "sg280-old-read"])
    print("SG280-G3-STEP4-PASS")
    # 5. truncated copy is refused
    trunc = os.path.join(SCRATCH, "trunc.db")
    shutil.copyfile(LIVE_COPY, trunc)
    size = os.path.getsize(trunc)
    with open(trunc, "r+b") as f:
        f.truncate(size // 2)
    try:
        h_t = sha256_file(trunc)
        con = sqlite3.connect(f"file:{trunc}?mode=ro", uri=True)
        try:
            ic_t = con.execute("PRAGMA integrity_check").fetchone()[0]
        finally:
            con.close()
        refused = (h_t != h_live) or (ic_t != "ok")
        print(f"step5 hash_equal={h_t == h_live} integrity={ic_t} refused={refused}")
        if not refused:
            print("SG280-G3-STEP5-NOT-REFUSED FAIL")
            return 2
    except Exception as e:
        print(f"step5 refused by exception ok=True {type(e).__name__}")
    print("SG280-G3-STEP5-PASS")
    print("SG280-G3-ALL-PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

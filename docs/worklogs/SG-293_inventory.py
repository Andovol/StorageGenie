#!/usr/bin/env python3
# SG-293 inventory of a docker-export tar. Holds no data.
# Usage (script on stdin, only the tar path is read):  python3 - /scratch/live-1.tar
# One line per entry, sorted: path|type|mode|uid|gid|size|sha256|link|pax
#   pax = name=sha256(value) for every PAX extended header (SCHILY.xattr.*, capabilities, ...)
# Modification times are deliberately not recorded.
# Footer lines start with '#'. Exit 2 if the tar cannot be fully parsed; exit 3 if zero entries.
import hashlib
import json
import sys
import tarfile


def digest_of_stream(stream):
    h = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1 << 20), b""):
        h.update(chunk)
    return h.hexdigest()


def sha_text(value):
    return hashlib.sha256(value.encode("utf-8", "surrogateescape")).hexdigest()


def kind(m):
    if m.isreg():
        return "file"
    if m.isdir():
        return "dir"
    if m.issym():
        return "symlink"
    if m.islnk():
        return "hardlink"
    if m.ischr():
        return "chardev"
    if m.isblk():
        return "blockdev"
    if m.isfifo():
        return "fifo"
    return "other:%r" % (m.type,)


def main(path):
    lines = []
    count = 0
    with_pax = 0
    with tarfile.open(path, mode="r:") as tf:
        for m in tf:
            count += 1
            sha = digest_of_stream(tf.extractfile(m)) if m.isreg() else ""
            link = m.linkname if (m.issym() or m.islnk()) else ""
            pax = ";".join(
                "%s=%s" % (name, sha_text(m.pax_headers[name]))
                for name in sorted(m.pax_headers)
            )
            if m.pax_headers:
                with_pax += 1
            lines.append("|".join([
                json.dumps(m.name), kind(m), oct(m.mode), str(m.uid), str(m.gid),
                str(m.size), sha, json.dumps(link), pax,
            ]))
        global_pax = dict(tf.pax_headers)
    for line in sorted(lines):
        print(line)
    print("# GLOBAL_PAX=%s" % ";".join(
        "%s=%s" % (name, sha_text(global_pax[name])) for name in sorted(global_pax)))
    print("# ENTRY_COUNT=%d" % count)
    print("# ENTRIES_WITH_PAX=%d" % with_pax)
    return 3 if count == 0 else 0


if __name__ == "__main__":
    try:
        rc = main(sys.argv[1])
    except Exception as exc:  # any failure to parse fully is a hard failure
        print("# PARSE FAIL: %s: %s" % (type(exc).__name__, exc))
        sys.exit(2)
    if rc == 3:
        print("# ZERO ENTRIES")
    sys.exit(rc)

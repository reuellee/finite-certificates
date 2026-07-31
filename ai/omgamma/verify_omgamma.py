#!/usr/bin/env python3
"""Verify the shipped mutation-graph connectivity certificates.

Runs the standalone checkers (which share no code with the generators)
on the certificates in data/:
  * (8,3): pure-python checker (reference implementation)
  * (8,4), (9,3): numpy fast checker (same semantics)
  * (9,4): fast checker on the big-run certificate, if present
  * one sabotage canary (corrupted tree voltage must be rejected)
Exit 0 iff everything passes.
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(script, n, r, files):
    return subprocess.run(
        [sys.executable, os.path.join(HERE, script), str(n), str(r)]
        + files, cwd=HERE, capture_output=True, text=True)


def cert(r, n):
    return [os.path.join(HERE, "data", f"flip_{r}_{n}_{k}.txt")
            for k in ("reps", "tree", "gens", "exhibits")]


def main():
    ok = True

    p = run("checker.py", 8, 3, cert(3, 8))
    print(("PASS" if p.returncode == 0 else "FAIL") +
          "  (8,3) certificate [pure checker]")
    ok &= p.returncode == 0

    for (n, r) in [(8, 4), (9, 3)]:
        p = run("checker_fast.py", n, r, cert(r, n))
        print(("PASS" if p.returncode == 0 else "FAIL") +
              f"  ({n},{r}) certificate [fast checker]")
        ok &= p.returncode == 0

    # (9,4): the COMPACT sub-certificate (root-path closure of the classes
    # referenced by holonomy generators).  It certifies H = Gbar, not
    # class-list completeness -- see OMGAMMA.md Sec. 7.
    for (r, n) in [(4, 9), (3, 9)]:
        big = os.path.join(HERE, "data", f"big_{r}_{n}")
        bigfiles = [os.path.join(big, "subcert_" + x) for x in
                    ("reps.txt.gz", "tree.txt.gz", "gens.txt",
                     "exhibits.txt")]
        if all(os.path.exists(x) for x in bigfiles):
            p = run("checker_fast.py", n, r, bigfiles)
            print(("PASS" if p.returncode == 0 else "FAIL") +
                  f"  ({n},{r}) sub-certificate [fast checker]")
            ok &= p.returncode == 0
        else:
            print(f"SKIP  ({n},{r}) sub-certificate (not present)")

    # canary: corrupt a tree voltage -> must be rejected
    tmp = os.path.join(HERE, "data", "verify_tmp")
    os.makedirs(tmp, exist_ok=True)
    files = []
    for src in cert(3, 8):
        dst = os.path.join(tmp, os.path.basename(src))
        shutil.copy(src, dst)
        files.append(dst)
    lines = open(files[1]).read().splitlines()
    for i, ln in enumerate(lines):
        parts = ln.split()
        if parts[1] != 'root':
            parts[4] = str(int(parts[4]) ^ 9)
            lines[i] = " ".join(parts)
            break
    open(files[1], 'w').write("\n".join(lines) + "\n")
    p = run("checker.py", 8, 3, files)
    print(("PASS" if p.returncode != 0 else "FAIL") +
          "  canary: corrupted voltage rejected")
    ok &= p.returncode != 0

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

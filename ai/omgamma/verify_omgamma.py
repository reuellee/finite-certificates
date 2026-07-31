#!/usr/bin/env python3
"""Verify the shipped mutation-graph connectivity certificates.

Runs the standalone checkers (which share no code with the generators) on
the certificates in data/.  Exit 0 iff everything passes.

DESIGN NOTE (fixed 2026-07-31, was a SERIOUS defect): this script used to
treat a MISSING certificate as "SKIP" and still exit 0, so deleting the
headline artifacts left CI green.  The expected certificates are now an
explicit manifest:

  REQUIRED  every file must exist, be readable and be non-empty, and its
            checker must pass.  A missing or unreadable required artifact
            is a FAILURE, reported by name.
  OPTIONAL  artifacts that are legitimately not computed yet (a campaign
            still running).  These are skipped, but every skip is printed
            with the reason, and the manifest lists them explicitly --
            nothing is silently ignored.

Usage:
  python verify_omgamma.py                 verify data/ in this directory
  python verify_omgamma.py --root DIR      verify an alternative data root
  python verify_omgamma.py --canary        self-test: confirm that a
                                           missing / empty required
                                           artifact is REJECTED
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def cert(root, r, n):
    return [os.path.join(root, f"flip_{r}_{n}_{k}.txt")
            for k in ("reps", "tree", "gens", "exhibits")]


def subcert(root, r, n, prefix="subcert"):
    return [os.path.join(root, f"big_{r}_{n}", f"{prefix}_{k}")
            for k in ("reps.txt.gz", "tree.txt.gz", "gens.txt",
                      "exhibits.txt")]


def manifest(root):
    """(label, checker script, n, r, files) for each certificate."""
    required = [
        ("(8,3) certificate [pure checker]", "checker.py", 8, 3,
         cert(root, 3, 8)),
        ("(8,4) certificate [fast checker]", "checker_fast.py", 8, 4,
         cert(root, 4, 8)),
        ("(9,3) certificate [fast checker]", "checker_fast.py", 9, 3,
         cert(root, 3, 9)),
        ("(9,3) sub-certificate [fast checker]", "checker_fast.py", 9, 3,
         subcert(root, 3, 9)),
        ("(9,4) sub-certificate [fast checker]", "checker_fast.py", 9, 4,
         subcert(root, 4, 9)),
    ]
    optional = [
        ("(9,4) campaign sub-certificate [fast checker]",
         "checker_fast.py", 9, 4, subcert(root, 4, 9, "subcertB"),
         "emitted by finish94.sh once the (9,4) coverage sweep completes"),
    ]
    return required, optional


def run(script, n, r, files):
    return subprocess.run(
        [sys.executable, os.path.join(HERE, script), str(n), str(r)]
        + files, cwd=HERE, capture_output=True, text=True)


def readable_nonempty(path):
    try:
        if os.path.getsize(path) == 0:
            return "empty"
        with open(path, "rb") as f:
            f.read(1)
    except OSError as e:
        return f"unreadable ({e.strerror})"
    return None


def main(root, canary=False):
    ok = True
    required, optional = manifest(root)

    # ---- manifest presence gate (runs BEFORE any checker, so a missing
    #      artifact fails fast and loudly instead of being skipped)
    print(f"[verify] artifact root: {root}")
    missing = []
    for (label, _s, _n, _r, files) in required:
        for p in files:
            if not os.path.exists(p):
                missing.append((label, p, "missing"))
            else:
                why = readable_nonempty(p)
                if why:
                    missing.append((label, p, why))
    if missing:
        for (label, p, why) in missing:
            print(f"FAIL  REQUIRED artifact {why}: {p}   [{label}]")
        print(f"FAIL  {len(missing)} required artifact(s) unusable — the "
              f"certificates this repo claims are not present. This is a "
              f"verification FAILURE, not a skip.")
        return 1
    print(f"[verify] all {sum(len(f) for _l, _s, _n, _r, f in required)} "
          f"required artifacts present and readable")

    for (label, script, n, r, files) in required:
        p = run(script, n, r, files)
        good = p.returncode == 0
        print(("PASS  " if good else "FAIL  ") + label)
        if not good:
            print(p.stdout[-2000:])
            print(p.stderr[-2000:])
        ok &= good

    for (label, script, n, r, files, why) in optional:
        if all(os.path.exists(x) and not readable_nonempty(x)
               for x in files):
            p = run(script, n, r, files)
            good = p.returncode == 0
            print(("PASS  " if good else "FAIL  ") + label + " [optional]")
            ok &= good
        else:
            print(f"SKIP  {label} [OPTIONAL, declared in the manifest]: "
                  f"{why}")

    # ---- sabotage canary: a corrupted tree voltage must be rejected
    tmp = os.path.join(HERE, "data", "verify_tmp")
    os.makedirs(tmp, exist_ok=True)
    files = []
    for src in cert(root, 3, 8):
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
    print(("PASS  " if p.returncode != 0 else "FAIL  ") +
          "canary: corrupted voltage rejected")
    ok &= p.returncode != 0

    if canary:
        ok &= missing_artifact_canary(root)
    return 0 if ok else 1


def missing_artifact_canary(root):
    """The verifier itself must REJECT a data root with a required
    artifact deleted, renamed or emptied -- the defect this file used to
    have was passing such a root."""
    ok = True
    required, _ = manifest(root)
    victims = [
        ("deleted", lambda p: os.remove(p)),
        ("renamed", lambda p: os.rename(p, p + ".moved")),
        ("emptied", lambda p: open(p, "w").close()),
    ]
    for (mode, mutate) in victims:
        with tempfile.TemporaryDirectory() as td:
            dst = os.path.join(td, "data")
            shutil.copytree(root, dst,
                            ignore=shutil.ignore_patterns(
                                "*.npz", "canary_*", "verify_tmp",
                                "*.orig", "*.full", "*.bak", "pure94"))
            # victim = a file of the LAST required certificate (9,4)
            target = manifest(dst)[0][-1][4][0]
            if not os.path.exists(target):
                print(f"FAIL  canary '{mode}': could not stage {target}")
                ok = False
                continue
            mutate(target)
            p = subprocess.run(
                [sys.executable, os.path.abspath(__file__), "--root", dst],
                cwd=HERE, capture_output=True, text=True)
            good = p.returncode != 0 and "REQUIRED artifact" in p.stdout
            print(("PASS  " if good else "FAIL  ") +
                  f"canary: required artifact {mode} -> verifier "
                  f"{'rejects' if good else 'ACCEPTS'} "
                  f"(exit {p.returncode})")
            ok &= good
    return ok


if __name__ == "__main__":
    args = sys.argv[1:]
    canary = "--canary" in args
    root = os.path.join(HERE, "data")
    if "--root" in args:
        root = args[args.index("--root") + 1]
    sys.exit(main(root, canary=canary))

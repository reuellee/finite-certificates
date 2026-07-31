"""Sabotage canaries: the standalone checker MUST fail on each corrupted
variant of a valid certificate.

  python canary_checker.py <n> <r>
      canaries data/flip_<r>_<n>_{reps,tree,gens,exhibits}.txt with
      checker.py (the pure-python reference)
  python canary_checker.py <n> <r> <reps> <tree> <gens> <exhibits>
                           [--fast]
      canaries an arbitrary certificate (e.g. the compact (9,4)
      sub-certificate); --fast uses checker_fast.py, and .gz inputs are
      supported (they are decompressed into the temp dir before being
      corrupted, so the corruption is applied to real certificate text).
"""
import gzip
import os
import shutil
import subprocess
import sys

TMP = "data/canary_tmp"


def run_checker(n, r, files, script):
    p = subprocess.run(
        [sys.executable, script, str(n), str(r)] + files,
        capture_output=True, text=True)
    return p.returncode


def _copy_plain(src, dst):
    """Copy src to dst, decompressing .gz so the corruptors see text."""
    if src.endswith(".gz"):
        with gzip.open(src, "rt") as a, open(dst, "w") as b:
            shutil.copyfileobj(a, b)
    else:
        shutil.copy(src, dst)


def main(n, r, base=None, script="checker.py"):
    base = base or {k: f"data/flip_{r}_{n}_{k}.txt"
                    for k in ("reps", "tree", "gens", "exhibits")}
    os.makedirs(TMP, exist_ok=True)

    def variant(name, mutate):
        files = {}
        for k, path in base.items():
            dst = f"{TMP}/{name}_{k}.txt"
            _copy_plain(path, dst)
            files[k] = dst
        mutate(files)
        rc = run_checker(n, r, [files['reps'], files['tree'],
                                files['gens'], files['exhibits']], script)
        ok = (rc != 0)
        print(("PASS " if ok else "FAIL ") +
              f"canary '{name}': checker {'rejects' if ok else 'ACCEPTS'}")
        return ok

    def flip_rep_char(files):
        lines = open(files['reps']).read().splitlines()
        s = lines[len(lines) // 2]
        i = len(s) // 3
        s = s[:i] + ('-' if s[i] == '+' else '+') + s[i + 1:]
        lines[len(lines) // 2] = s
        open(files['reps'], 'w').write("\n".join(lines) + "\n")

    def corrupt_tree_eps(files):
        lines = open(files['tree']).read().splitlines()
        for t, ln in enumerate(lines):
            parts = ln.split()
            if parts[1] != 'root':
                parts[4] = str(int(parts[4]) ^ 5)
                lines[t] = " ".join(parts)
                break
        open(files['tree'], 'w').write("\n".join(lines) + "\n")

    def corrupt_gen_perm(files):
        lines = open(files['gens']).read().splitlines()
        parts = lines[0].split()
        sig = parts[1].split(',')
        sig[0], sig[1] = sig[1], sig[0]
        parts[1] = ",".join(sig)
        lines[0] = " ".join(parts)
        open(files['gens'], 'w').write("\n".join(lines) + "\n")

    def truncate_exhibits(files):
        lines = open(files['exhibits']).read().splitlines()
        open(files['exhibits'], 'w').write("\n".join(lines[:1]) + "\n")

    def swap_tree_parent(files):
        lines = open(files['tree']).read().splitlines()
        # point a mid mutation edge at a different parent
        for t, ln in enumerate(lines):
            parts = ln.split()
            if parts[1] != 'root' and int(parts[0]) > 3:
                parts[1] = str(max(0, int(parts[1]) - 1))
                lines[t] = " ".join(parts)
                break
        open(files['tree'], 'w').write("\n".join(lines) + "\n")

    allok = True
    allok &= variant("rep_char", flip_rep_char)
    allok &= variant("tree_eps", corrupt_tree_eps)
    allok &= variant("gen_perm", corrupt_gen_perm)
    allok &= variant("exhibit_trunc", truncate_exhibits)
    allok &= variant("tree_parent", swap_tree_parent)
    print("ALL CANARIES PASS" if allok else "CANARY FAILURE")
    sys.exit(0 if allok else 1)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--fast"]
    script = "checker_fast.py" if "--fast" in sys.argv else "checker.py"
    n, r = int(args[0]), int(args[1])
    b = None
    if len(args) >= 6:
        b = dict(zip(("reps", "tree", "gens", "exhibits"), args[2:6]))
    main(n, r, b, script)

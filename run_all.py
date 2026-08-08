#!/usr/bin/env python3
"""Run every verify_*.py in the tree; exit nonzero if any fails.

--fast skips the slow verifiers, including the three expensive diagonal-two
atlas/mutation/saturation replays.
"""
import os, subprocess, sys

SLOW = {
    "verify_diag2_escape_set_atlas178.py",
    "verify_diag2_escape_set_mutation_square.py",
    "verify_diag2_pivot_49_50_pair_saturation.py",
    "verify_druzkowski.py",
    "verify_sae_circuit.py",
}
fast = "--fast" in sys.argv
root = os.path.dirname(os.path.abspath(__file__))

fails, ran, skipped = [], 0, 0
for dirpath, _, files in os.walk(root):
    for f in sorted(files):
        if not (f.startswith("verify_") and f.endswith(".py")):
            continue
        if fast and f in SLOW:
            skipped += 1
            print(f"SKIP  {f} (--fast)")
            continue
        path = os.path.join(dirpath, f)
        r = subprocess.run([sys.executable, path], cwd=dirpath,
                           capture_output=True, text=True, timeout=1200)
        ran += 1
        status = "PASS" if r.returncode == 0 else "FAIL"
        print(f"{status}  {os.path.relpath(path, root)}")
        if r.returncode != 0:
            fails.append(path)
            print(r.stdout[-800:], r.stderr[-800:])

print(f"\n{ran} verifiers run, {skipped} skipped, {len(fails)} failed")
sys.exit(1 if fails else 0)

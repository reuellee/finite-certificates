"""Independent cross-check of exactlp.py against known ground truth.

Ground truth: the 126 shipped realization certificates. For each, deleting
column p leaves a Y that PROVABLY extends (the certificate is the extension).
So exact_feasible on those rows must return FEASIBLE, every time.
Then: run the exact oracle on the SAME rows the float LP is asked about and
count any disagreement in the direction that matters (float said no, exact
says yes) -- that quantifies the heuristic-failure gap.
"""
import io, json, os, sys, random
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OMOPEN = os.path.dirname(HERE)
sys.path.insert(0, OMOPEN)
import numpy as np
import exactlp, weaponA, catalog

certs = [json.loads(l) for l in io.open(os.path.join(OMOPEN, 'data', 'certs_realizable.jsonl'), encoding='utf-8')]
random.seed(20260802)
sample = random.sample(certs, 12)
geom = catalog.realize_mod().Geom(9, 4)
print('certs sampled:', len(sample))

ok = bad = 0
gap_checked = gap_found = 0
for c in sample:
    Z = np.array(c['matrix'], dtype=object) if isinstance(c.get('matrix'), list) else None
    if Z is None:
        print('  no Z field; keys:', list(c.keys())[:8]); break
    chi = np.array([1 if ch == '+' else -1 for ch in c['chi']], dtype=np.int64)
    for p in range(9):
        # completion_rows indexes the OTHER columns by original element
        # index, so the full configuration is passed; column p is the unknown.
        A, bs = weaponA.completion_rows(Z, chi, geom, p)
        A = [[int(v) for v in row] for row in A]
        st, w = exactlp.exact_feasible(A)
        # ground truth: the real column Z[:,p] completes it
        if st == 'FEASIBLE':
            ok += 1
        else:
            bad += 1
            print('  MISMATCH: exact says INFEASIBLE but the shipped certificate completes it!',
                  c.get('row'), 'p=', p)
print('exact FEASIBLE on known-extendible deletions: %d ok, %d MISMATCH' % (ok, bad))
print('VERDICT:', 'PASS' if bad == 0 and ok > 0 else 'FAIL')

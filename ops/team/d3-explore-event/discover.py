#!/usr/bin/env python3
"""Bounded numerical discovery only. No numerical result is an accepted claim."""
from itertools import combinations
from pathlib import Path
from fractions import Fraction
from time import perf_counter, process_time
import json
import numpy as np
from scipy.optimize import linprog

ROOT = Path(__file__).resolve().parents[3]
OWN = Path(__file__).resolve().parent


def main():
    wall, cpu = perf_counter(), process_time()
    event = json.loads((ROOT / 'ops/team/d3-satinj-falsifier/DISCOVERED_EVENT.json').read_text())
    triples = sorted(combinations(range(8), 3), key=lambda x: x[::-1])
    tstar = Fraction(event['root'])
    records = []
    for side, t in [('left', tstar-Fraction(1, 1000000)),
                    ('right', tstar+Fraction(1, 1000000))]:
        y = np.asarray(event['parent'], dtype=float)
        y[event['coord'], event['label']-1] += float(t)
        normals = np.asarray([[(-1)**(r+3)*np.linalg.det(y[np.ix_([k for k in range(4) if k!=r], tri)])
                               for r in range(4)] for tri in triples])
        normals /= np.linalg.norm(normals, axis=1)[:, None]
        for block, sig in enumerate(event['signatures']):
            a = normals * np.asarray([1 if sig >> i & 1 else -1 for i in range(56)])[:, None]
            # Primal feasibility and normalized Gordan dual are complementary.
            primal = linprog(np.zeros(4), A_ub=-a, b_ub=-np.ones(56),
                             bounds=[(None, None)]*4, method='highs')
            dual = linprog(np.zeros(56), A_eq=np.vstack((a.T, np.ones(56))),
                           b_eq=np.asarray([0.,0.,0.,0.,1.]), bounds=(0, None), method='highs')
            rec = dict(side=side, parameter=str(t), block=block, signature=sig,
                       primal_status=int(primal.status), dual_status=int(dual.status))
            if primal.success:
                rec['primal_point'] = primal.x.tolist()
                rec['primal_min_margin'] = float(np.min(a @ primal.x))
            if dual.success:
                support = np.flatnonzero(dual.x > 1e-9).tolist()
                rec['support'] = support
                rec['support_labels'] = [''.join(str(j+1) for j in triples[i]) for i in support]
                rec['weights_in_unit_row_gauge'] = dual.x[support].tolist()
                rec['equality_residual'] = float(np.max(np.abs(a.T @ dual.x)))
            records.append(rec)
    out = dict(status='HEURISTIC_DISCOVERY_ONLY', lp_calls=12, records=records,
               wall_seconds=perf_counter()-wall, cpu_seconds=process_time()-cpu)
    (OWN/'DISCOVERY.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()

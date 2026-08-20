#!/usr/bin/env python3
"""Exact structural census of the 994-factor diagonal-three residue.

This checker deliberately does not decide feasibility. It rebuilds the residue
from the exact S3 closure certificate and partitions it by cheap algebraic
invariants that determine the order of the next exact attacks: global factor
multiplicity, multidegree in the three moving columns, term count, coefficient
L1 norm, and the size of the residue intersection with its full S3 zero-set
orbit.
"""
from __future__ import annotations
from collections import Counter
from itertools import permutations
import hashlib, json
from pathlib import Path
import sys
import numpy as np
HERE=Path(__file__).resolve().parent; sys.path.insert(0,str(HERE))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled
import DIAG9_GRAPH_global_factor_census as global_factors
import verify_diag3_pair_fullsupport_block_symmetry as sym
import verify_diag3_pair_global_parent_face_gate as gate
EXPECTED_RESIDUE=994
EXPECTED_RESIDUE_SHA256='c330ba558fedd9b0502c8e96b35cecf179e2ec5b2eb5324893a374c4f09039cf'
GROUPS=((0,1,2),(3,4,5),(6,7,8))

def key(poly): return tuple(sorted(global_factors.primitive(poly).items()))
def transform(poly,perm): return sym.transform(poly,perm)
def multidegree(poly): return tuple(max(sum(m[i] for i in group) for m in poly) for group in GROUPS)
def residue_ids(polynomials,candidates,points):
 open_ids=set(sym.base_open_ids(points,polynomials,candidates)); crossed=set(candidates)-open_ids
 index={key(p):i for i,p in enumerate(polynomials)}; closure=set()
 for fid in crossed:
  for perm in permutations(range(3)):
   moved=index[key(transform(polynomials[fid],perm))]
   if moved in set(candidates): closure.add(moved)
 return tuple(sorted(set(candidates)-closure))

def main():
 # Replay the load-bearing symmetry theorem first.
 sym.main()
 candidates=gate.parse_candidates(); _occ,_map,polynomials=labeled.factor_polynomials()
 with np.load(gate.POINT_BANK,allow_pickle=False) as source:
  points=tuple(gate.normalized_values(m.tolist()) for m in np.asarray(source['chart_matrix'],dtype=np.int64))
 residue=residue_ids(polynomials,candidates,points)
 digest=hashlib.sha256(','.join(map(str,residue)).encode('ascii')).hexdigest()
 if len(residue)!=EXPECTED_RESIDUE or digest!=EXPECTED_RESIDUE_SHA256: raise AssertionError('residue changed')
 residue_set=set(residue); index={key(p):i for i,p in enumerate(polynomials)}
 with np.load(gate.FACTOR_CENSUS,allow_pickle=False) as source: multiplicity=np.asarray(source['factor_multiplicity'],dtype=np.int64)
 orbit_seen=set(); orbit_hist=Counter(); invariant_hist=Counter(); reps=[]
 for fid in residue:
  if fid in orbit_seen: continue
  full={index[key(transform(polynomials[fid],perm))] for perm in permutations(range(3))}
  hit=tuple(sorted(full & residue_set)); orbit_seen.update(hit); orbit_hist[len(hit)]+=1
  p=polynomials[min(hit)]; inv=(int(multiplicity[min(hit)]),multidegree(p),len(p),sum(abs(int(c)) for c in p.values()),len(hit))
  invariant_hist[inv]+=1; reps.append((min(hit),inv))
 if orbit_seen!=residue_set or len(reps)!=264: raise AssertionError((len(orbit_seen),len(reps)))
 print('PASS residue',len(residue),digest)
 print('WORKLOAD_CLASSES',len(reps))
 print('CLASS_SIZE_HIST',json.dumps(dict(sorted(orbit_hist.items())),sort_keys=True))
 print('MULTIPLICITY_HIST',json.dumps(dict(sorted(Counter(int(multiplicity[f]) for f in residue).items())),sort_keys=True))
 print('INVARIANT_BUCKETS',len(invariant_hist))
 print('SCOPE structural prioritization only; no feasibility claim for residue factors')
if __name__=='__main__': main()

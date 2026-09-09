#!/usr/bin/env python3
"""Independent source-audit algebra and integral incidence checks.

No producer module is imported/executed. Gauge reconstruction uses Cramer
brackets, covariance uses elementary GL generators, and Cech exactness uses
an integer augmented-simplex contraction. Global topology is in REVIEW.md.
"""
from pathlib import Path
from hashlib import sha256
from itertools import combinations
import json
import subprocess
import time
import sympy as sp
from sympy.matrices.normalforms import smith_normal_form

BASE = "9aefa1d783ffae751406c4e295e228153041772c"
PINS = {
 "ops/team/ai-d3-reset-source/FINDINGS.md": "f32f2fa3904e825a8d83cfb53d658862e53953a933d44c80dc9ae3dee28a43c5",
 "ops/team/ai-d3-reset-source/RESULT.json": "0d0ba2ecbc281ed10c4c373cde574c2a7ad1598b064da12661a01fa701ed328c",
 "ops/team/ai-d3-reset-source/verify_identities.py": "4ee8a2e89bd0a693458519c7af407bb8e0c476401ebe4027bbcd08fd3382bb39",
 "ops/team/ai-d3-reset-falsifier/FINDINGS.md": "aa451796f65dcb3b1f3a59cd75e7085f51ed98725204be90d7d5d87bdb676c29",
 "ops/team/ai-d3-reset-falsifier/COUNTERMODELS.json": "a49b40888b4e9e6d7e2299903acaa00b1467fb138fb5a864f27e8d3f9d810657",
 "ops/team/ai-d3-reset-falsifier/RESULT.json": "41438272d0ba1146f5d1034aface8aa8fda0adfca32b8c1b160c780989a93f9d",
 "ops/research-team/cycles/2026-09-04-d3-block-gordan-compact-relative-source-gate1/THEOREM_CANDIDATE.md": "fa26329cb30866a6c127f2b789a1a818f61c3d951aac57ae1ba2b558cd42c56a",
 "ai/omreal/ATLAS_HELLY.md": "9a1c2791c9b991679587d0a9ba6307191e025069b766b55855bfa0d1357071f0",
 "ai/omreal/9DVL_THEOREM_PROSPECTUS.md": "cc6d7c6fcf93e4cdd2a2980cb92f34fd934b97b5a28e80034f1f8367fa7e7879",
 "ai/omreal/data/CANONICAL_RESEARCH_STATE_V11.json": "5929b922ecf04246920d56a1adedc29382379eb5abae8b600601995d6b5dae86",
}

def require(ok, reason):
    if not ok:
        raise AssertionError(reason)

def pin_sources(root):
    result = {}
    for path, expected in PINS.items():
        frozen = subprocess.check_output(["git", "show", BASE+":"+path], cwd=root)
        require(sha256(frozen).hexdigest() == expected, "frozen source drift: "+path)
        local = (root/path).read_bytes()
        require(local.replace(b"\r\n",b"\n") == frozen.replace(b"\r\n",b"\n"),
                "worktree source drift: "+path)
        result[path] = {"git_blob_sha256": expected,
                           "worktree_sha256": sha256(local).hexdigest()}
    return result

def det_normal(y):
    return sp.Matrix([y.row_join(sp.eye(4)[:,k]).det() for k in range(4)])

def universal_generator_checks(corrupt=False):
    y = sp.Matrix(4,3,sp.symbols("v0:12"))
    a = det_normal(y)
    t = sp.Symbol("t", nonzero=True)
    generators = []
    for i in range(4):
        g = sp.eye(4); g[i,i] = t
        generators.append(g)
        for j in range(4):
            if i != j:
                g = sp.eye(4); g[i,j] = t
                generators.append(g)
    for i,j in combinations(range(4),2):
        g = sp.eye(4); g.row_swap(i,j)
        generators.append(g)
    for g in generators:
        # This form has no inverse or adjugate, and checks both GL signs.
        residual = g.T*det_normal(g*y) - (abs(g.det()) if corrupt else g.det())*a
        require(all(sp.expand(v) == 0 for v in residual), "oriented generator covariance")
    scales = sp.symbols("d0:3")
    scaled = det_normal(y*sp.diag(*scales))
    require(all(sp.expand(scaled[k]-sp.prod(scales)*a[k]) == 0 for k in range(4)),
            "triple scaling")
    return {"GL_generators": len(generators), "coordinate_identities": 4*len(generators),
            "triple_scaling_identities": 4}

def cramer_section(v, omit_orientation=False):
    b = v[:,:4]
    determinant = b.det()
    require(determinant != 0, "basis rank")
    brackets = {}
    for j in range(4,8):
        for i in range(4):
            replaced = b.copy(); replaced[:,i] = v[:,j]
            brackets[i,j] = replaced.det()
    require(all(brackets[i,4] != 0 for i in range(4)), "fifth frame point")
    orientation = 1 if omit_orientation else sp.sign(determinant)
    columns = [sp.eye(4)[:,i] for i in range(4)]
    columns.append(sp.Matrix([orientation*sp.sign(brackets[i,4]) for i in range(4)]))
    for j in range(5,8):
        c = sp.Matrix([orientation*brackets[i,j]/abs(brackets[i,4]) for i in range(4)])
        columns.append(c/sum(abs(x) for x in c))
    return sp.Matrix.hstack(*columns)

def gauge_checks(corrupt=False):
    # A different rational parent, with nontrivial column orientations.
    v = sp.Matrix([[sp.Integer(t)**p for t in (-3,-1,0,2,3,5,8,13)] for p in range(4)])
    v = v*sp.diag(1,1,1,1,-1,1,-1,1)
    require(all(v[:,list(t)].det() != 0 for t in combinations(range(8),4)), "uniform fixture")
    n = cramer_section(v,corrupt)
    d = [sp.Integer(t) for t in (3,5,7,11,13,17,19,23)]
    g = sp.Matrix([[2,1,0,0],[0,1,2,0],[0,0,1,3],[0,0,0,1]])
    transforms = [g, sp.diag(-1,1,1,1)*g]
    triples = tuple(combinations(range(8),3))
    for transform in transforms:
        new = transform*v*sp.diag(*d)
        require(cramer_section(new,corrupt) == n, "Cramer gauge orbit invariance")
        for triple in triples:
            q = sp.prod(d[j] for j in triple)
            residual = transform.T*det_normal(new[:,list(triple)]) - q*transform.det()*det_normal(v[:,list(triple)])
            require(residual == sp.zeros(4,1), "all labeled normal transport")
    require(cramer_section(n) == n, "gauge idempotence")
    require(cramer_section(v*sp.diag(1,1,1,1,1,-1,1,1)) != n, "no negative-column quotient")
    require(all(sum(abs(t) for t in n[:,j]) == 1 for j in range(5,8)), "simplex magnitudes")

    # Weight gauge is a projective positive-diagonal action on one simplex.
    # Different block supports ensure a genuine numerical-mass change.
    w = [sp.Rational(1,6),sp.Rational(1,3),0,0,sp.Rational(1,2),0]
    q = [sp.Integer(t) for t in (2,3,5,7,11,13)]
    raw = [a/b for a,b in zip(w,q)]
    image = [a/sum(raw) for a in raw]
    back_raw = [a*b for a,b in zip(image,q)]
    require([a/sum(back_raw) for a in back_raw] == w, "joined gauge inverse")
    require([a != 0 for a in image] == [a != 0 for a in w], "coordinate zero faces")
    old_masses = [sum(w[2*j:2*j+2]) for j in range(3)]
    new_masses = [sum(image[2*j:2*j+2]) for j in range(3)]
    require([x != 0 for x in old_masses] == [x != 0 for x in new_masses], "block support")
    require(old_masses != new_masses, "mass-value distinction canary")
    return {"uniform_parent_brackets":70, "transported_normals":112,
            "orientation_signs_checked":[1,-1], "zero_faces_preserved":True,
            "numerical_mass_change_canary":True}

def add(*chains):
    out = {}
    for chain in chains:
        for k,v in chain.items(): out[k] = out.get(k,0)+v
    return {k:v for k,v in out.items() if v}

def apply(chain,op):
    return add(*({k:c*v for k,v in op(cell).items()} for cell,c in chain.items()))

def simplex_contraction(corrupt=False):
    def boundary(cell):
        return {cell[:j]+cell[j+1:]: (-1)**j for j in range(len(cell))}
    count = 0
    for size in range(1,4):
        for labels in combinations(range(3),size):
            apex = min(labels)
            cells = [cell for n in range(size+1) for cell in combinations(labels,n)]
            def h(cell):
                return {} if apex in cell else {(apex,)+cell: 2 if corrupt else 1}
            for cell in cells:
                require(apply(boundary(cell),boundary) == {}, "augmented boundary squared")
                require(add(apply(h(cell),boundary),apply(boundary(cell),h)) == {cell:1},
                        "integer augmented simplex contraction")
            count += 1
    return {"nonempty_bad_index_patterns":count, "integer_chain_contraction":True}

def distinction_checks(root):
    data = json.loads((root/'ops/team/ai-d3-reset-falsifier/COUNTERMODELS.json').read_bytes())
    expected = {"both_invariants_fail":(3,1,4), "pair_only_failure":(2,0,2),
                "triple_only_failure":(0,1,1)}
    results = {}
    for model in data['models']:
        free = [set(a) for a in model['free_axes']]
        require(len(free)==3 and all(0<len(a)<9 for a in free), "proper coordinate sections")
        require(all(a-b and b-a for a,b in combinations(free,2)), "antichain")
        intersections = {t:set.intersection(*(free[i] for i in t))
                         for r in range(1,4) for t in combinations(range(3),r)}
        dims = {t:len(v) for t,v in intersections.items()}
        require(all(dims[(i,)] >= 3 for i in range(3)), "single lower vanishings")
        pairs = list(combinations(range(3),2))
        require(all(dims[t]>=1 for t in pairs), "pair Hc0 vanishing")
        source_pairs = [t for t in pairs if dims[t]==1]
        target = int(dims[(0,1,2)]==1)
        if target:
            row = [(-1)**next(j for j in range(3) if j not in t) for t in source_pairs]
            matrix = sp.Matrix([row])
            diagonal = smith_normal_form(matrix, domain=sp.ZZ)
            nonzero = [abs(diagonal[i,i]) for i in range(min(diagonal.shape)) if diagonal[i,i]]
            require(nonzero == [1], "primitive integral pair restriction")
            kernel = len(source_pairs)-len(nonzero)
        else:
            row=[]; nonzero=[]; kernel=len(source_pairs)
        triple_hc0 = int(dims[(0,1,2)]==0)
        computed=(kernel,triple_hc0,kernel+triple_hc0)
        require(computed == expected[model['id']], "independent invariant distinction")
        # For these intersection degrees there is no possible nonzero d2.
        require(not any(dims[(i,)]-1 == dims[(0,1,2)] for i in range(3)),
                "possible higher differential needs proof")
        results[model['id']] = {"pair_kernel_Z_rank":kernel,"triple_Hc0_Z_rank":triple_hc0,
                "union_Hc2_Z_rank":kernel+triple_hc0,"pair_map_row":row,
                "pair_map_nonzero_Smith_invariants":list(map(int,nonzero)),
                "intersection_dimensions": {''.join(map(str,t)):d for t,d in dims.items()}}
    return results

def main():
    started=time.perf_counter()
    root=Path(__file__).resolve().parents[3]
    result={"reviewed_base":BASE,"source_hashes":pin_sources(root),
            "producer_code_imported_or_executed":False}
    result['universal_algebra']=universal_generator_checks()
    result['gauge']=gauge_checks()
    result['integral_Cech_stalks']=simplex_contraction()
    result['generic_distinctions']=distinction_checks(root)
    rejected=0
    for damaged in (lambda:universal_generator_checks(True),lambda:gauge_checks(True),
                    lambda:simplex_contraction(True)):
        try: damaged()
        except AssertionError: rejected+=1
    require(rejected==3,"hostile mutation escaped")
    result['hostile_mutations_rejected']=rejected
    result['elapsed_seconds']=round(time.perf_counter()-started,6)
    result['status']='PASS_INDEPENDENT_FINITE_CHECKS'
    result['scope']='Global quotient, topology, effectivity, and obligation credit reviewed in prose; no global triangulation constructed.'
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()

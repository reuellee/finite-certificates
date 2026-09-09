#!/usr/bin/env python3
"""Independent rational reconstruction; imports no research acceptance code."""
import hashlib
import itertools as it
import json
import math
import pathlib
import subprocess
import time
from collections import Counter
from fractions import Fraction as F

import numpy as np  # NPZ decoding only

ROOT = pathlib.Path(__file__).resolve().parents[3]
EVENT = "dff5dc46744ca6680770b20392139f61bec69ff6"
DIAGONALS = "efbb652c543dbf05a6ebb947fde5cb4218b07e26"
COHERENT = "845791277cb0c41eb7b8d6dd7aea892cf135d79c"
TOPOLOGY = "b468869778beb404cd2c4f4b5b426115a4c9356b"
OPENING = "c27a36d6e3f47a2b4c7bb017774cbe5df30abdc2"


def blob(rev, path):
    return subprocess.check_output(["git", "-C", str(ROOT), "show", rev + ":" + path])


def read(rev, path):
    return json.loads(blob(rev, path))


def trim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return tuple(p)


def add(a, b):
    return trim([(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
                 for i in range(max(len(a), len(b)))])


def mul(a, b):
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            r[i+j] += x*y
    return trim(r)


def scale(a, c):
    return trim([c*x for x in a])


def det(a):
    n = len(a)
    out = (0,)
    for p in it.permutations(range(n)):
        s = (-1) ** sum(p[i] > p[j] for i in range(n) for j in range(i+1,n))
        v = (s,)
        for i in range(n):
            v = mul(v, a[i][p[i]])
        out = add(out, v)
    return out


def value(p, x):
    r = F(0)
    for c in reversed(p):
        r = r*x+c
    return r


def sign(x):
    return (x > 0) - (x < 0)


def strict_bound(p, center, radius, wanted=1):
    # Independent centered Taylor absolute-remainder bound, not Bernstein.
    q = [sum(F(p[j])*math.comb(j,k)*center**(j-k)
             for j in range(k,len(p))) for k in range(len(p))]
    return wanted*q[0] - sum(abs(q[k])*radius**k for k in range(1,len(q)))


def rows(Y, signature):
    triples = sorted(it.combinations(range(8), 3), key=lambda s: tuple(reversed(s)))
    out = []
    for i, T in enumerate(triples):
        out.append([scale(det([[Y[r][j] for j in T] for r in range(4) if r != k]),
                          (-1)**(k+3)*(1 if signature >> i & 1 else -1))
                    for k in range(4)])
    return out


def cofactors(selected):
    return [scale(det([row for i,row in enumerate(selected) if i != j]), (-1)**j)
            for j in range(5)]


def dot(a,b):
    out = (0,)
    for x,y in zip(a,b):
        out = add(out,mul(x,y))
    return out


def rank(a):
    a = [[F(v) for v in row] for row in a]
    r = 0
    for j in range(len(a[0])):
        pivot = next((i for i in range(r,len(a)) if a[i][j]), None)
        if pivot is None:
            continue
        a[r],a[pivot] = a[pivot],a[r]
        q = a[r][j]
        a[r] = [v/q for v in a[r]]
        for i in range(len(a)):
            if i != r:
                q = a[i][j]
                a[i] = [u-q*v for u,v in zip(a[i],a[r])]
        r += 1
    return r


def candidate_pins(rev, track):
    prefix = "ops/team/d3-explore-" + track + "/"
    files = subprocess.check_output(["git","-C",str(ROOT),"ls-tree","-r","--name-only",rev,prefix],text=True).splitlines()
    pins = {p: hashlib.sha256(blob(rev,p)).hexdigest() for p in files}
    manifest = read(rev,prefix+"SOURCE_MANIFEST.json")
    sources = manifest.get("source_sha256", manifest.get("sha256", {}))
    for p,h in sources.items():
        assert hashlib.sha256(blob(OPENING,p)).hexdigest() == h, p
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h, p
    return {"revision":rev,"files":pins,"inherited_sources_checked":len(sources)}


def event_review():
    cert = read(EVENT,"ops/team/d3-explore-event/CERTIFICATE.json")
    source = read(OPENING,"ops/team/d3-satinj-falsifier/DISCOVERED_EVENT.json")
    parent = np.load(ROOT/"ai/omreal/data/seeat_parent2599_upper178.npz")["chart_matrix"][0].tolist()
    assert parent == source["parent"]
    Y = [[(int(v),) for v in row] for row in parent]
    assert source["label"] == 2 and source["coord"] == 1
    Y[1][1] = (54,1)
    sigs = source["signatures"]
    assert sigs == cert["signatures"]
    A = [rows(Y,s) for s in sigs]
    active = [19,21,37,38]
    assert cert["active_support"] == active
    D = [A[0][i] for i in active]
    delta = det(D)
    assert list(map(str,delta)) == cert["event_factor"]
    assert len(delta) == 2 and delta[1] > 0
    root = -F(delta[0],delta[1])
    assert str(root) == source["root"] == cert["event_parameter"]
    eps = F(1,1000000)
    assert list(map(str,[root-eps,root+eps])) == cert["closed_interval"]
    # adj(D)*1 via transposed cofactor expansion.
    p = []
    for i in range(4):
        v = (0,)
        for j in range(4):
            minor = [[D[r][c] for c in range(4) if c != i] for r in range(4) if r != j]
            v = add(v,scale(det(minor),(-1)**(i+j)))
        p.append(v)
    assert [list(map(str,x)) for x in p] == cert["primal_section_coefficients"]
    margins = [dot(a,p) for a in A[0]]
    assert len(margins) == 56
    assert all(margins[i] == delta for i in active)
    nonactive = [i for i in range(56) if i not in active]
    assert {str(i):list(map(str,margins[i])) for i in nonactive} == cert["nonactive_margin_polynomials"]
    bounds = [strict_bound(margins[i],root,eps) for i in nonactive]
    assert min(bounds) > 0
    brackets = []
    for C in sorted(it.combinations(range(8),4),key=lambda s:tuple(reversed(s))):
        q = det([[Y[r][j] for j in C] for r in range(4)])
        assert strict_bound(q,root,eps,sign(q[0])) > 0
        brackets.append(q)
    assert len(brackets) == 70
    duals = []
    for b,support in enumerate(source["supports"]):
        selected = [A[b][i] for i in support]
        c = cofactors(selected)
        assert [list(v) for v in c] == source["cofactor_polynomials"][b]
        for k in range(4):
            assert dot(c,[a[k] for a in selected]) == (0,)
        for j in range(5):
            if b == j == 0:
                assert c[j] == delta
            else:
                assert strict_bound(c[j],root,eps,-1) > 0
        duals.append(c)
    assert rank([[value(x,root) for x in a] for a in D]) == 3
    assert any(value(x,root) for x in p)
    assert all(value(margins[i],root) == 0 for i in active)
    assert all(value(margins[i],root) > 0 for i in nonactive)
    # Meaningful bad inputs fail this independently reconstructed arithmetic.
    canaries = {
        "event_is_not_strict": not all(value(m,root)>0 for m in margins),
        "negated_right_primal_rejected": not all(value(scale(m,-1),root+eps)>0 for m in margins),
        "right_selected_dual_has_mixed_sign": min(value(c,root+eps) for c in duals[0]) < 0 < max(value(c,root+eps) for c in duals[0]),
        "shifted_root_rejected": value(delta,root+eps) != 0,
        "flipped_active_signature_bit_rejected": value(scale(margins[active[0]],-1),root+eps)<0,
        "corrupted_dual_identity_rejected": dot([add(duals[0][0],(1,))]+duals[0][1:], [A[0][i][0] for i in source["supports"][0]]) != (0,),
        "endpoints_positive_interior_negative_rejected": strict_bound((root*root-eps*eps/4,-2*root,1),root,eps)<=0,
        "empty_or_omitted_row_denominator_rejected": len(margins[:-1]) != 56 and len([]) != 56,
    }
    assert all(canaries.values())
    return {"pins":candidate_pins(EVENT,"event"),"verdict":"ACCEPT_FINITE_EXACT_AND_MATRIX_LOCAL_GERM",
            "independent_method":"Permutation determinants and centered Taylor absolute-remainder bounds; no Bernstein or producer imports",
            "parent_brackets":70,"primal_rows":56,"positive_nonactive_margin_intervals":52,
            "minimum_nonactive_taylor_lower_bound":str(min(bounds)),
            "dual_polynomial_identities":12,"event_active_rank":3,
            "singleton_full_normalized_dual_fiber":True,
            "local_germ":"Valid in the stated open parent-matrix neighborhood; no normalized-gauge transport asserted",
            "canaries":canaries,"original_obligations_closed":0}


def scalar_det(a):
    # Rational Gaussian elimination differs from the candidate's integer expansion.
    a = [[F(x) for x in row] for row in a]
    out = F(1)
    for j in range(len(a)):
        pivot = next((i for i in range(j,len(a)) if a[i][j]),None)
        if pivot is None:
            return F(0)
        if pivot != j:
            a[j],a[pivot] = a[pivot],a[j]
            out = -out
        q = a[j][j]
        out *= q
        for i in range(j+1,len(a)):
            ratio = a[i][j]/q
            for k in range(j+1,len(a)):
                a[i][k] -= ratio*a[j][k]
    return out


def normalized(A):
    B = [[F(v) for v in row[:4]] for row in A]
    d = scalar_det(B)
    Q = [[F(0)]*8 for _ in range(4)]
    for i in range(4):
        for j in range(8):
            C = [row[:] for row in B]
            for r in range(4):
                C[r][i] = F(A[r][j])
            Q[i][j] = scalar_det(C)/d
    f = [Q[i][4] for i in range(4)]
    Tdet = 1/(d*math.prod(f))
    C = [[Q[i][j]/f[i] for j in range(8)] for i in range(4)]
    scalings = [abs(f[j]) if j<4 else F(1) if j==4 else 1/abs(C[0][j]) for j in range(8)]
    assert min(scalings)>0 and Tdet>0
    C = [[C[i][j]*scalings[j] for j in range(8)] for i in range(4)]
    return C,Tdet


def diagonal_review():
    cert = read(DIAGONALS,"ops/team/d3-explore-diagonals/HYBRID_OUTPUT.json")
    bank = np.load(ROOT/"ai/omreal/data/seeat_parent2599_upper178.npz")["chart_matrix"]
    endpoints = [normalized(bank[i].tolist()) for i in [37,176]]
    A,B = [v[0] for v in endpoints]
    assert [[str(x) for x in row] for row in A] == cert["normalized_a"]
    assert [[str(x) for x in row] for row in B] == cert["normalized_b"]
    assert list(map(str,[v[1] for v in endpoints])) == cert["transform_determinants"]
    assert all(A[i][:5]==B[i][:5] for i in range(4))
    assert A[0] == B[0]
    bases = list(it.combinations(range(8),4))
    def brackets(C):
        return [scalar_det([[C[r][j] for j in cols] for r in range(4)]) for cols in bases]
    signs = list(map(sign,brackets(A)))
    assert signs == cert["parent_signs"] == list(map(sign,brackets(B)))
    for index in [37,176]:
        assert list(map(sign,brackets(bank[index].tolist()))) == signs
    coords = [(r,c) for c in range(5,8) for r in range(1,4)]
    assert [list(x) for x in coords] == cert["coordinate_order"]
    results = {}
    for kind,n in [("columns",3),("coordinates",9)]:
        valid = []
        first_bad = {}
        for mask in range(1<<n):
            H = [row[:] for row in A]
            for i,(r,c) in enumerate(coords):
                bit = c-5 if kind=="columns" else i
                if mask>>bit & 1:
                    H[r][c] = B[r][c]
            for k,cols in enumerate(bases):
                d = scalar_det([[H[r][j] for j in cols] for r in range(4)])
                if sign(d)!=signs[k]:
                    first_bad[mask] = ("".join(str(j+1) for j in cols),sign(d),signs[k])
                    break
            else:
                valid.append(mask)
        record = cert["results"][kind]
        assert valid == record["parent_valid_masks"] == [0,(1<<n)-1]
        assert len(first_bad) == (1<<n)-2
        for witness in record["invalid_first_witness"]:
            label,actual,wanted = first_bad[witness["mask"]]
            assert (label,actual,wanted) == (witness["basis"],sign(F(witness["determinant"])),witness["expected_sign"])
        results[kind] = {"enumerated":1<<n,"valid_masks":valid,"invalid_certificates_checked":len(first_bad)}
    wrong = [row[:] for row in A]
    for r in range(4):
        wrong[r][0] = -wrong[r][0]
    assert list(map(sign,brackets(wrong))) != signs
    return {"pins":candidate_pins(DIAGONALS,"diagonals"),"verdict":"ACCEPT_FINITE_ENDPOINT_HYBRID_OBSTRUCTION",
            "independent_method":"Cramer's rule normalization and rational Gaussian determinants",
            "results":results,"negative_column_rescaling_rejected":True,
            "scope":"One fixed oriented first-five-ray frame; endpoint-coordinate/column hybrid graphs only",
            "continuous_paths_with_intermediate_values":"NOT_EXCLUDED; inherited positive source path retained",
            "original_obligations_closed":0}


def divide(a,b):
    a = list(map(F,trim(a)))
    b = list(map(F,trim(b)))
    q = [F(0)]*max(1,len(a)-len(b)+1)
    while len(a)>=len(b) and any(a):
        k = len(a)-len(b)
        c = a[-1]/b[-1]
        q[k] = c
        for i,x in enumerate(b):
            a[i+k] -= c*x
        a = list(trim(a))
    return trim(q),trim(a)


def positive_open(p,a,b):
    """Sturm exclusion of interior roots, with explicit endpoint factors removed."""
    assert a<b and p!=(0,)
    original = p
    for endpoint in [a,b]:
        while len(p)>1 and value(p,endpoint)==0:
            p,rem = divide(p,(-endpoint,1))
            assert rem==(0,)
    seq = [p,tuple(i*p[i] for i in range(1,len(p)))] if len(p)>1 else [p]
    while len(seq)>1:
        rem = divide(seq[-2],seq[-1])[1]
        if rem==(0,):
            break
        seq.append(scale(rem,-1))
    def variations(x):
        signs = [sign(value(q,x)) for q in seq]
        signs = [s for s in signs if s]
        return sum(x!=y for x,y in zip(signs,signs[1:]))
    return variations(a)==variations(b) and value(original,(a+b)/2)>0


def transform(p,offset,slope):
    out = (0,)
    power = (1,)
    for c in p:
        out = add(out,scale(power,c))
        power = mul(power,(offset,slope))
    return out


def admission(parent,sigs):
    bases = list(it.combinations(range(8),4))
    bsign = {C:sign(scalar_det([[parent[r][j] for j in C] for r in range(4)])) for C in bases}
    triples = sorted(it.combinations(range(8),3),key=lambda x:tuple(reversed(x)))
    gps = 0
    for sig in sigs:
        signs = dict(bsign)
        signs.update({T+(8,):(1 if sig>>i&1 else -1) for i,T in enumerate(triples)})
        def chi(T):
            return (-1)**sum(T[i]>T[j] for i in range(4) for j in range(i+1,4))*signs[tuple(sorted(T))]
        for S in it.combinations(range(9),2):
            for a,b,c,d in it.combinations([i for i in range(9) if i not in S],4):
                v = [chi(S+(a,b))*chi(S+(c,d)), -chi(S+(a,c))*chi(S+(b,d)), chi(S+(a,d))*chi(S+(b,c))]
                assert min(v)<0<max(v)
                gps += 1
    bank = np.load(ROOT/"ai/omreal/data/seeat_parent2599_upper178.npz")
    anchors = read(OPENING,"ops/team/ai-d3-shared-pencil-falsifier/admissibility_flow.json")["records"]
    noninclusions = 0
    for rec in anchors:
        P = rec["parent"]
        assert P == bank["chart_matrix"][rec["upper_chart_index"]].tolist()
        assert all(sign(scalar_det([[P[r][j] for j in C] for r in range(4)]))==bsign[C] for C in bases)
        Y = [[(v,) for v in row] for row in P]
        assert rec["point"] == bank["point"][rec["upper_point_index"]].tolist()
        assert int(bank["assignment"][rec["upper_point_index"]])==rec["upper_chart_index"]
        assert all(value(dot(a,[(v,) for v in rec["point"]]),0)>0 for a in rows(Y,rec["signature"]))
        for other in rec["other_systems"]:
            if other["dual"] is None:
                continue
            d = other["dual"]
            assert min(d["weights"])>0
            A = rows(Y,other["signature"])
            # These inherited anchor weights use primitive normals, whereas
            # the new chord weights use raw determinant normals.
            raw_weights = [F(w,math.gcd(*(int(x[0]) for x in A[i])))
                           for i,w in zip(d["support"],d["weights"])]
            assert all(sum(w*A[i][k][0] for i,w in zip(d["support"],raw_weights))==0 for k in range(4))
            noninclusions += 1
    assert gps==3780 and noninclusions==6
    return {"gp_relations":gps,"strict_properness_anchors":3,"ordered_noninclusions":noninclusions}


def topology_review():
    cert = read(TOPOLOGY,"ops/team/d3-explore-topology/EXACT_RESULT.json")
    parent = np.load(ROOT/"ai/omreal/data/seeat_parent2599_upper178.npz")["chart_matrix"][0].tolist()
    sigs = cert["signatures"]
    h,v = cert["horizontal"],cert["vertical"]
    L,H = map(F,h["parent_interval"])
    V = F(v["v_interval"][1])
    bounds = {}
    systems = {}
    bracket_sets = {}
    for direction,row in [("horizontal",0),("vertical",1)]:
        Y = [[(x,) for x in line] for line in parent]
        Y[row][7] = (parent[row][7],1)
        A = [rows(Y,s) for s in sigs]
        systems[direction] = A
        brackets = {C:det([[Y[r][j] for j in C] for r in range(4)]) for C in it.combinations(range(8),4)}
        bracket_sets[direction] = brackets
        lower,upper = [],[]
        for p in brackets.values():
            assert p[0]!=0 and len(p)<=2
            if len(p)==2 and p[1]:
                root = -F(p[0],p[1])
                (lower if p[0]*p[1]>0 else upper).append(root)
        bounds[direction] = [max(lower),min(upper)]
        if direction=="horizontal":
            assert bounds[direction]==[L,H]
        else:
            assert bounds[direction][0]<0 and bounds[direction][1]==V
        record = h if direction=="horizontal" else v
        for b,support in enumerate(record["dual_supports_zero_based"]):
            selected = [A[b][i] for i in support]
            c = cofactors(selected)
            if value(c[0],0)<0:
                c = [scale(p,-1) for p in c]
            assert [list(map(str,p)) for p in c] == record["dual_polynomials"][b]
            assert all(dot(c,[a[k] for a in selected])==(0,) for k in range(4))
            if direction=="vertical":
                for p in c:
                    assert positive_open(p,F(0),V) and value(p,0)>0 and value(p,V)>0
    A = systems["horizontal"]
    alpha_poly = tuple(h["alpha_polynomial_ascending"])
    alo,ahi = map(F,h["alpha_isolator"])
    beta = F(h["beta"])
    assert L<alo<ahi<0<beta<H
    assert value(alpha_poly,alo)<0<value(alpha_poly,ahi)
    assert positive_open(tuple(i*alpha_poly[i] for i in range(1,len(alpha_poly))),L,H)
    ds = [[tuple(map(F,p)) for p in c] for c in h["dual_polynomials"]]
    ratio = ds[0][0][0]/alpha_poly[0]
    assert ratio>0 and ds[0][0]==scale(alpha_poly,ratio)
    assert value(ds[1][1],beta)==0 and len(ds[1][1])==2 and ds[1][1][1]<0
    for b,c in enumerate(ds):
        a,z = (alo,H) if b==0 else (L,beta) if b==1 else (L,H)
        for j,p in enumerate(c):
            if (b,j) in [(0,0),(1,1)]:
                continue
            assert positive_open(p,a,z)
            if b==1:
                assert value(p,beta)>0
    left = [tuple(map(F,p)) for p in h["left_primal_polynomials"]]
    delta = det([A[0][i] for i in [19,21,37,38]])
    assert delta==scale(alpha_poly,-ratio)
    for i,a in enumerate(A[0]):
        margin = dot(a,left)
        if i in [19,21,37,38]:
            assert margin==delta
        else:
            assert positive_open(margin,L,ahi) and value(margin,L)>0 and value(margin,ahi)>0
    right = [tuple(map(F,p)) for p in h["right_primal_in_z"]]
    for a in A[1]:
        margin = dot([transform(p,beta,H-beta) for p in a],right)
        assert positive_open(margin,F(0),F(1))
        assert value(margin,0)>=0 and value(margin,1)>=0
    bv = bracket_sets["vertical"]
    zeros = [C for C,p in bv.items() if value(p,V)==0]
    assert zeros==[(2,4,6,7)]
    r3578 = bv[(2,4,6,7)]
    r1234 = bv[(0,1,2,3)]
    r1238 = bv[(0,1,2,7)]
    r3457 = bv[(2,3,4,6)]
    assert Counter((2,4,6,7)+(0,1,2,3)) == Counter((0,1,2,7)+(2,3,4,6))
    assert value(r1238,V)==F(43095889251278677,10548542)
    assert value(r1234,V)==2443943962 and value(r3457,V)==4595799854
    assert value(r3578,0)!=0 and value(r3578,V)==0
    assert positive_open((1,-4,4),F(0),F(1)) is False  # interior double zero
    assert positive_open((F(3,4),-4,4),F(0),F(1)) is False  # positive endpoints, negative middle
    assert value(ds[1][1],beta+F(1,1000000))!=0
    assert len([C for C,p in bv.items() if value(p,0)==0])==0
    return {"pins":candidate_pins(TOPOLOGY,"topology"),"verdict":"ACCEPT_TWO_CHORDS_AND_SPECIFIC_NORMALIZED_COMPONENT_ESCAPE",
            "independent_method":"Reconstructed normals/cofactors; rational Sturm root exclusion with endpoint-factor removal",
            "admission":admission(parent,sigs),"parent_chords":{k:list(map(str,v)) for k,v in bounds.items()},
            "horizontal_full_blocks":"GBB / BBB / BGB with exact alpha and beta boundaries",
            "vertical_dual_identities":12,"vertical_positive_weights":15,
            "parent_boundary":"3578 only","balanced_ratio":True,"ratio_denominator_nonzero_at_limit":True,
            "scope":"Only the ambient triple-bad component containing the certified horizontal interval is proved noncompact",
            "hostile_interior_double_root_rejected":True,"shifted_beta_rejected":True,"interior_origin_as_infinity_rejected":True,
            "source_orbits_removed":0,"original_obligations_closed":0}


def coherent_review():
    cert = read(COHERENT,"ops/team/d3-explore-coherent/RESULT.json")
    src = read(OPENING,"ops/team/d3-satinj-falsifier/DISCOVERED_EVENT.json")
    parent = src["parent"]
    for record in cert["initial_test"]:
        t = F(record["parameter"])
        Y = [[(F(x),) for x in row] for row in parent]
        Y[1][1] = (F(54)+t,)
        A = [rows(Y,s) for s in src["signatures"]]
        signs = []
        for b in range(3):
            for first in [0,2]:
                S = [first]+src["supports"][b][1:]
                c = [p[0] for p in cofactors([A[b][i] for i in S])]
                c = [x/sum(c) for x in c]
                if b==0:
                    signs.append(list(map(sign,c)))
                else:
                    assert min(c)>0
        assert signs==record["block_0_endpoint_signs"]
        S = [0,2]+src["supports"][0][1:]
        M = [[A[0][i][k][0] for i in S] for k in range(4)]+[[1]*6]
        assert rank(M)==5
        if record["point"]=="event":
            for v in cert["follow_through"]["vertices"]:
                weights = list(map(F,v["normalized_weights"]))
                assert sum(weights)==1 and min(weights)>=0
                assert all(sum(w*A[v["block"]][i][k][0] for i,w in zip(v["support"],weights))==0 for k in range(4))
    f = cert["follow_through"]
    d1,d2 = f["boundary_1"],[v[0] for v in f["boundary_2"]]
    assert d1==[[-1,-1,0],[1,0,-1],[0,1,1]] and d2==[1,-1,1]
    assert rank(d1)==2 and all(sum(x*y for x,y in zip(row,d2))==0 for row in d1)
    assert math.gcd(*d2)==1
    assert any(sum(x*y for x,y in zip(row,[1,1,1]))!=0 for row in d1)
    return {"pins":candidate_pins(COHERENT,"coherent"),"verdict":"ACCEPT_FINITE_INSTANCE_AND_INHERITED_MASS_MAP_ARGUMENT",
            "three_point_six_coordinate_fiber":"edge / singleton / empty",
            "primitive_integral_triangle_boundary":True,"wrong_orientation_rejected":True,
            "scope":"Fixed-parent joined witness fiber; section to boundary simplex prevents pair-layer filling only",
            "novel_general_mechanism":False,"original_target":"NULL","original_obligations_closed":0}


def main():
    start = time.process_time()
    out = {"event":event_review(),"topology":topology_review(),"coherent":coherent_review(),
           "diagonals":diagonal_review(),"producer_acceptance_imports":[]}
    out["overall_verdict"] = "ACCEPT_SCOPED_AUXILIARY_RESULTS_ONLY"
    out["original_obligations_closed"] = 0
    out["ledger"] = "2/9"
    out["global_pair_residual"] = "UNKNOWN"
    out["global_component_coverage"] = "UNKNOWN"
    out["review_cpu_seconds"] = time.process_time()-start
    print(json.dumps(out,indent=2))


if __name__ == "__main__":
    main()

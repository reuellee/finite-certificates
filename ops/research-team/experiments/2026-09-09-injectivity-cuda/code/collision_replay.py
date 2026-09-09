#!/usr/bin/env python3
"""Independent cellular compact-support replay; imports no producer code."""
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import hashlib
import json

RAYS = [(1,0),(1,1),(0,1),(-1,2),(-1,1),(-2,1),
        (-1,0),(-1,-1),(0,-1),(1,-2),(1,-1),(2,-1)]

def rank(a):
    if not a: return 0
    a = [[Fraction(x) for x in row] for row in a]
    r = 0
    for j in range(len(a[0])):
        p = next((i for i in range(r, len(a)) if a[i][j]), None)
        if p is None: continue
        a[r],a[p] = a[p],a[r]
        v = a[r][j]
        a[r] = [x/v for x in a[r]]
        for i in range(len(a)):
            if i != r and a[i][j]:
                f = a[i][j]
                a[i] = [x-f*y for x,y in zip(a[i],a[r])]
        r += 1
        if r == len(a): break
    return r

def bad(point, signature):
    u,v = point
    p = (u,v,-u-v)
    return not all(p[signature] > p[j] for j in range(3) if j != signature)

def link(indices):
    vertices = [r for r,p in enumerate(RAYS) if all(bad(p,i) for i in indices)]
    edges = []
    for r in range(12):
        s = (r+1)%12
        mid = tuple(x+y for x,y in zip(RAYS[r], RAYS[s]))
        if all(bad(mid,i) for i in indices):
            assert r in vertices and s in vertices
            edges.append((r,s))
    return vertices,edges

def complex_for(indices, deletion="full"):
    vertices,edges = link(indices)
    cells = [(0,)] + [(0,r+1) for r in vertices]
    cells += [tuple(sorted((0,r+1,s+1))) for r,s in edges]
    basis = {d:[] for d in range(10)}
    for c in cells:
        for ball_dim in (0,6,7):
            if deletion == "none": removed = False
            elif deletion == "open_ball": removed = ball_dim != 7
            else:
                removed_ray = len(c)==2 and (
                    deletion == "full" or (c[1]-1)%2==1)
                removed = ball_dim != 7 and (len(c)==1 or removed_ray)
            if not removed:
                basis[len(c)-1+ball_dim].append((c,ball_dim))
    differentials = {}
    for d in range(1,10):
        out = {x:i for i,x in enumerate(basis[d-1])}
        m = [[0]*len(basis[d]) for _ in basis[d-1]]
        for col,(c,b) in enumerate(basis[d]):
            for k in range(len(c)):
                face = c[:k]+c[k+1:]
                key = (face,b)
                if key in out: m[out[key]][col] += (-1)**k
            if b==7:
                key = (c,6)
                if key in out: m[out[key]][col] += (-1)**(len(c)-1)
        differentials[d] = m
    # Check the exact cellular chain identity before using any ranks.
    for d in range(2,10):
        a,b = differentials[d-1],differentials[d]
        for i in range(len(basis[d-2])):
            for j in range(len(basis[d])):
                assert sum(a[i][k]*b[k][j] for k in range(len(basis[d-1]))) == 0
    ranks = {d:rank(m) for d,m in differentials.items()}
    betti = [len(basis[d])-ranks.get(d,0)-ranks.get(d+1,0) for d in range(10)]
    assert all(x>=0 for x in betti)
    return {"vertices":vertices,"edges":edges,
            "chain_dimensions":[len(basis[d]) for d in range(10)],
            "betti":betti}

def parallel(a,b):
    return all(a[i]*b[j]==a[j]*b[i] for i,j in combinations(range(4),2))

def collision_checks():
    # Coordinate deductions in OPENING_AUDIT.md prove exhaustiveness.
    # These exact controls test every listed line and reject h!=0 collisions.
    witnessed = set()
    for u,v in RAYS + [(0,0),(2,3)]:
        for h in (-1,0,1):
            rows = [(1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1),
                    (u,-1,h,h),(v,-1,-h,h),(-u-v,-1,h,-h)]
            pairs = [(i,j) for i,j in combinations(range(7),2) if parallel(rows[i],rows[j])]
            predicted = h==0 and any(x==0 for x in (u,v,u+v,u-v,2*u+v,u+2*v))
            assert bool(pairs)==predicted
            witnessed.update(pairs)
    assert witnessed == {(1,4),(1,5),(1,6),(4,5),(4,6),(5,6)}
    return sorted(witnessed)

def main():
    model_path = Path(__file__).resolve().parents[2]/"injectivity/falsifier/MODEL.json"
    model_bytes = model_path.read_bytes()
    model = json.loads(model_bytes)
    assert model["matrix_rows"] == ["e1","e2","e3","e4", "(u,-1,h,h)",
                                      "(v,-1,-h,h)","(-u-v,-1,h,-h)"]
    assert model["h"] == "1 - sum(y_k^2, k=1..7)"
    result = {"classification":"INDEPENDENT_ABSTRACT_DELETION_ONLY",
              "base":"59fec66666518257c585194b81061f60d91f439d",
              "source_model_sha256":hashlib.sha256(model_bytes).hexdigest(),
              "collision_pairs":collision_checks(), "sets":{},"controls":{}}
    for size in (1,2,3):
        for inds in combinations(range(3),size):
            key = "".join(map(str,inds))
            new = complex_for(inds)
            old = complex_for(inds,"none")
            expected_old = [0]*10
            expected_old[1] = size-1
            assert old["betti"] == expected_old
            expected = [0]*10
            expected[2] = {1:8,2:4,3:0}[size]
            expected[8] = {1:8,2:5,3:2}[size]
            assert new["betti"] == expected
            assert len(new["vertices"]) == {1:9,2:6,3:3}[size]
            assert len(new["edges"]) == {1:8,2:4,3:0}[size]
            result["sets"][key] = new
    # Actual restriction cochains in degree1 have both source and target zero.
    # Thus every induced restriction and their alternating sum are uniquely zero.
    result["new_D"] = {"source_dimension":0,"target_dimension":0,
                         "matrix":[],"rank":0,"kernel_dimension":0}
    # Reconstruct the old nonzero map in bases at ray indices1,5,9.
    target_vertices = result["sets"]["012"]["vertices"]
    assert target_vertices == [1,5,9]
    columns = []
    for inds,sign in [((0,1),1),((0,2),-1),((1,2),1)]:
        vertices,edges = link(inds)
        isolated = [r for r in vertices if not any(r in edge for edge in edges)]
        assert len(isolated)==1
        r = target_vertices.index(isolated[0])
        col = [(1 if r==i else 0)-(1 if r==2 else 0) for i in (0,1)]
        columns.append([sign*x for x in col])
    old_D = [list(x) for x in zip(*columns)]
    assert rank(old_D)==2
    assert all(sum(row[j]*[1,-1,1][j] for j in range(3))==0 for row in old_D)
    result["controls"]["old_D_reconstructed"] = old_D
    result["controls"]["old_kernel_dimension"] = 1
    partial = complex_for((0,),"omit_basis_collisions")
    assert partial["betti"][2]==4 and partial["betti"][2]!=8
    result["controls"]["omit_basis_collision_wrong_Hc2"] = partial["betti"][2]
    opened = complex_for((0,),"open_ball")
    assert opened["betti"] == [0]*10
    result["controls"]["open_ball_wrong_singleton_all_zero"] = True
    result["controls"]["reuse_old_compactification_wrong_pair_Hc1"] = 1
    result["status"] = "PASS_INDEPENDENT_ABSTRACT_ONLY"
    path = Path(__file__).with_name("INDEPENDENT_RESULT.json")
    encoded = json.dumps(result,indent=2)+"\n"
    path.write_text(encoded)
    print(encoded,end="")

if __name__ == "__main__": main()

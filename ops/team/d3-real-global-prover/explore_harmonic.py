"""Bounded exact constant-metric maximum-principle screen on the full source.

Discovery only: imports existing chart arithmetic; does not change accounting.
"""
from fractions import Fraction as Q
from pathlib import Path
import hashlib, importlib.util, json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec=importlib.util.spec_from_file_location('old',ROOT/'ops/team/d3-bracket-chart/verify_genus_one_fiber.py')
old=importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
raw=old.SOURCE.read_bytes()
assert hashlib.sha256(raw).hexdigest()==old.PIN
source=json.loads(raw)
q=[{tuple(m):int(v) for v,m in rec['terms']} for rec in source['equations'][:3]]
a,b,c,d,e,f,g,h,i=[old.variable(j) for j in range(9)]
dn=old.plus(old.times(b,old.plus(i,old.scale(f,-1))),old.times(f,g))
red=[old.plus(old.times(i,old.coefficient(p,3,0)),old.times(dn,old.coefficient(p,3,1))) for p in q[1:]]
B,A=old.coefficient(red[0],0,0),old.coefficient(red[0],0,1)
D,C=old.coefficient(red[1],0,0),old.coefficient(red[1],0,1)
N=old.plus(old.times(A,D),old.scale(old.times(C,B),-1))
assert len(N)==389
indices=[1,2,4,5,6,7,8]
pairs=[(j,k) for j in indices for k in indices if j<=k]
def diff(p,j):
    out={}
    for m,v in p.items():
        if m[j]:
            t=list(m);t[j]-=1
            out[tuple(t)]=v*m[j]
    return out
H=[old.scale(diff(diff(N,j),k),1 if j==k else 2) for j,k in pairs]
support=sorted(set().union(*(p.keys() for p in H)))
rows=[[Q(p.get(m,0)) for p in H] for m in support]
original_rows=[row[:] for row in rows]
origins=list(range(len(rows)))
rank=0;pivots=[];selected=[]
for col in range(len(pairs)):
    where=next((r for r in range(rank,len(rows)) if rows[r][col]),None)
    if where is None:continue
    rows[where],rows[rank]=rows[rank],rows[where]
    origins[where],origins[rank]=origins[rank],origins[where]
    selected.append(origins[rank])
    scale=rows[rank][col]
    rows[rank]=[x/scale for x in rows[rank]]
    for r in range(len(rows)):
        if r!=rank and rows[r][col]:
            scale=rows[r][col]
            rows[r]=[x-scale*y for x,y in zip(rows[r],rows[rank])]
    pivots.append(col);rank+=1
free=[j for j in range(len(pairs)) if j not in pivots]
basis=[]
for k in free:
    vector=[Q(0) for _ in pairs];vector[k]=Q(1)
    for row,pivot in zip(rows,pivots):vector[pivot]=-row[k]
    basis.append(vector)
certificate_rows=[original_rows[j] for j in selected]
tmp=[row[:] for row in certificate_rows]
det=Q(1)
for j in range(len(tmp)):
    row=next(k for k in range(j,len(tmp)) if tmp[k][j])
    if row!=j:tmp[row],tmp[j]=tmp[j],tmp[row];det=-det
    pivot=tmp[j][j];det*=pivot
    for k in range(j+1,len(tmp)):
        factor=tmp[k][j]/pivot
        for l in range(j,len(tmp)):tmp[k][l]-=factor*tmp[j][l]
out={'source_sha256':old.PIN,'operator':'sum_j G_jj N_jj + 2 sum_j<k G_jk N_jk',
     'variables':[source['variables'][j] for j in indices],'unknowns':len(pairs),'support_equations':len(support),'rank':rank,
     'nullity':len(basis),'pair_order':[[source['variables'][j],source['variables'][k]] for j,k in pairs],
     'nullspace_basis':[[str(x) for x in v] for v in basis],
     'forced_zero_diagonals':[source['variables'][j] for j in indices if all(v[pairs.index((j,j))]==0 for v in basis)],
     'selected_monomials':[list(support[j]) for j in selected],
     'selected_coefficient_rows':[[int(x) for x in row] for row in certificate_rows],
     'selected_matrix_determinant':str(det),
     'result':'No nonzero constant symmetric metric makes N harmonic. This does not determine topology.'}
(HERE/'HARMONIC_SCREEN.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))

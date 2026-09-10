"""Bounded exact incidence families for a distinct-collinear rank11 canary."""
from pathlib import Path
from itertools import combinations
import random,json,time
import sympy as s
ROOT=Path(__file__).resolve().parent
lam=s.Symbol('lam');rng=random.Random(230910)
PROTO=[[(0,1,2),(0,3,4),(1,3,5),(2,6,7)],
       [(0,1,2),(0,3,4),(1,5,6),(3,5,7)]]

def block(edges,t):
    rows=[]
    for i,j,k in edges:
        row=[0]*8;row[i]=t[k]-t[j];row[j]=t[i]-t[k];row[k]=t[j]-t[i]
        rows.append(row)
    return s.Matrix(rows)

def norm(Y,J):
    return s.Matrix([(-1)**(r+3)*Y[[k for k in range(4) if k!=r],J].det()
                     for r in range(4)])

def inspect(edges,t,rank_hint):
    B=[block(e,t) for e in edges];zero=s.zeros(4,8)
    M=(zero.row_join(B[0])).col_join(B[1].row_join(zero)).col_join(B[2].row_join(-B[2]))
    F=M[:,list(range(2,8))+list(range(10,16))]
    ns=F.nullspace()
    if len(ns)!=1:return {'status':'wrong nullity','nullity':len(ns)}
    v=ns[0];a=[0,0]+list(v[:6]);b=[0,0]+list(v[6:])
    Y=s.Matrix([[1]*8,list(t),a,b]);br={''.join(str(j+1) for j in J):s.factor(Y[:,J].det()) for J in combinations(range(8),4)}
    zeros=[k for k,c in br.items() if c==0]
    if zeros:return {'status':'nonuniform','zero_parent_brackets':zeros}
    points=[s.Matrix([0,0,1,0]),s.Matrix([0,0,0,1]),s.Matrix([0,0,1,1])]
    rec=[];gam=[]
    for h,(sup,q) in enumerate(zip(edges,points)):
        N=s.Matrix.hstack(*(norm(Y,list(J)) for J in sup)).T
        assert N.rank()==3 and N*q==s.zeros(4,1)
        assert all(N[list(I),:].rank()==3 for I in combinations(range(4),3))
        lc=N.T.nullspace()[0];assert all(lc)
        if h:
            g=s.zeros(1,8)
            for coef,J in zip(lc,sup):
                for pos,j in enumerate(J):
                    cols=[Y[:,k] for k in J];cols[pos]=points[0]
                    g[j]+=coef*s.Matrix.hstack(*cols,q).det()
            gam.append(g)
        rec.append({'support':sup,'normal_rows':N.tolist(),'circuit':list(lc)})
    rank=s.Matrix.vstack(*gam).rank()
    return {'status':'actual uniform rank11 canary','transverse_parameters':list(t),
            'parent_matrix':Y.tolist(),'parent_brackets':br,'supports':edges,
            'stacked_rank':M.rank(),'normalized_nullity':len(ns),'concurrences':[list(q) for q in points],
            'vertical_gradients':[list(g) for g in gam],'vertical_gradient_rank':rank,'ordinary_rows':rec}

def main():
    rows=[];hits=[];start=time.time()
    for trial in range(24):
        edges=[PROTO[0]]
        for _ in range(2):
            p=list(range(8));rng.shuffle(p)
            edges.append(sorted(tuple(sorted(p[j] for j in J)) for J in rng.choice(PROTO)))
        if len({tuple(map(tuple,e)) for e in edges})<3:continue
        # Seven pairwise-distinct rational transverse directions; the eighth varies.
        t=list(range(7))+[lam]
        B=[block(e,t) for e in edges];z=s.zeros(4,8)
        M=z.row_join(B[0]).col_join(B[1].row_join(z)).col_join(B[2].row_join(-B[2]))
        F=M[:,list(range(2,8))+list(range(10,16))]
        d=s.Poly(F.det(method='domain-ge'),lam)
        params=list(s.ground_roots(d.as_expr(),lam)) if not d.is_zero else [s.Integer(8)]
        rec={'family':trial,'supports':edges,'determinant':str(s.factor(d.as_expr())),'candidates':[]}
        for x in params:
            r=inspect(edges,list(range(7))+[x],11);rec['candidates'].append({'parameter':str(x),**r})
            if r['status']=='actual uniform rank11 canary':hits.append(r)
        rows.append(rec)
        print('family',trial,'hits',len(hits),'seconds',round(time.time()-start,1),flush=True)
        if hits:break
    out={'scope':'At most24 selected one-parameter transverse-line incidence families; rational exceptional parameters only.','families':rows,'hits':hits}
    (ROOT/'COLLINEAR_RANK_PROBE.json').write_text(json.dumps(out,indent=2,default=str)+'\n')

if __name__=='__main__':main()

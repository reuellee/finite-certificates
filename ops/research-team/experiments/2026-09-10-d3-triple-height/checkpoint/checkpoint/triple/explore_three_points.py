import sympy as s,itertools,random,json
b,c,e,f,h,i=s.symbols('b c e f h i'); d=f+b-b*f;a=s.cancel((b*d-b-c*d+c+e-f)/(e-f));g=s.cancel(-(a*b*f-a*c*e+a*c*h-a*f*h-b*b*f+b*c*e+b*f*h-c*e*h)/(c*(e-b)))
print('a=',s.factor(a),'g=',s.factor(g),flush=True)
Y=s.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],[0,0,1,0,1,b,e,h],[0,0,0,1,1,c,f,i]])
supports=['123/124/345/567','123/145/246/357','123/145/267/468']
def normal(Y,t):
 q=Y[:,[int(k)-1 for k in t]]
 return s.Matrix([(-1)**(r+3)*q.extract([j for j in range(4) if j!=r],range(3)).det() for r in range(4)]).T
rng=random.Random(102)
for trial in range(500):
 vals={v:s.Rational(rng.choice([j for j in range(-6,8) if j not in[0,1]])) for v in [b,c,e,f,h,i]}
 if vals[e] in[vals[f],vals[b]]:continue
 YY=Y.subs(vals)
 bs=[YY[:,B].det() for B in itertools.combinations(range(8),4)]
 if not all(x.is_Rational and x!=0 for x in bs):continue
 As=[s.Matrix.vstack(*(normal(YY,t) for t in S.split('/'))) for S in supports]
 ns=[A.nullspace() for A in As]
 if not all(len(N)==1 for N in ns):continue
 P=s.Matrix.hstack(*(N[0] for N in ns))
 print('FOUND',trial,'Y=',YY.tolist(),'p=',P.tolist(),'prank=',P.rank(),flush=True)
 out={'schema':'three_distinct_boundary_points_v1','Y':[[str(t) for t in r] for r in YY.tolist()],'supports':supports,'points':[[str(t) for t in N[0]] for N in ns],'point_rank':P.rank(),'parent_brackets':[str(t) for t in bs]}
 open('d3_direct_proof_20260910/triple/THREE_BOUNDARY_POINTS.json','w').write(json.dumps(out,indent=2)+'\n')
 break
else:print('NO POINT')

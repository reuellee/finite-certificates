import sympy as s
x,y=s.symbols('x y')
V=((x*x-1)**2+(y*y-1)**2)/4
assert s.simplify(s.diff(V,x)-x*(x*x-1))==0
assert s.simplify(s.diff(V,y)-y*(y*y-1))==0
counts={0:0,1:0,2:0}
for a in (-1,0,1):
 for b in (-1,0,1):
  h=[s.diff(V,z,2).subs({x:a,y:b}) for z in (x,y)]
  counts[sum(1 for z in h if z.is_negative)]+=1
assert counts=={0:4,1:4,2:1}
D=s.Matrix([[-1,0,0,-1],[1,-1,0,0],[0,1,-1,0],[0,0,1,1]])
assert D.rank()==3 and D.T*s.ones(4,1)==s.zeros(4,1)
print('PASS',counts,'rank',D.rank(),'H0',4-D.rank())

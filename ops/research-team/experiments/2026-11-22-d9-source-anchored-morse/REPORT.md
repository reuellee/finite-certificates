# D9 source-anchored Morse incidence, 2026-11-22

**Ledger 2/9 unchanged. D9 open. Local exact demonstration only.**

On the previously certified parent-2599 local disk, the complete residual zero locus is the line q(s,u)=As+Bu, with A=1401176374297, B=849195472073. Consider U+={-1<s,u<1, q>0}. Put c=B/A, t=(s+cu)/(1+cu), X=t/(1-t)-(1-t)/t, Y=u/(1-u^2). Because 0<c<1, this is a global rational diffeomorphism U+ -> R^2.

Define W(X)=X^6/6-13X^4/64+9X^2/128 and Phi=W(X)+Y^2. This is proper on U+; its critical set consists exactly of (X,Y)=(0,0),(+/-1/2,0),(+/-3/4,0). Since W'(X)=X(X^2-1/4)(X^2-9/16), there are three index-zero points at X=0,+/-3/4 and two index-one points at X=+/-1/2. The Hessian X entries are respectively 9/64,45/128 and -5/32; the Y entry is 2.

For the negative gradient flow in (X,Y), Y=0 is invariant, and each saddle descends to the two neighboring minima. Pullback by the rational diffeomorphism supplies the corresponding gradient flow under the pulled-back metric. The complete low-index incidence matrix is D=[[-1,0],[1,-1],[0,1]], of exact rational rank 2. Thus 3-rank(D)=1, agreeing with the known connectivity of U+.

**Novelty/scope:** This is a source-anchored two-dimensional instance of the previously established incidence approach, not a new theorem for the full nine-dimensional D9 sector. The Morse function is engineered using an already available global chart; no all-family coverage, global active-factor elimination, or new diagonal follows. Do not promote the theorem ledger.

**Next gate:** certify a second independent wall on a local 2D/3D source-reconstructible patch and test whether the complete critical incidence can be obtained without a priori global trivialization. A local success is still not a universal proof.

Replay algebra (SymPy):
```python
import sympy as s
x=s.symbols('x')
W=x**6/s.Integer(6)-s.Rational(13,64)*x**4+s.Rational(9,128)*x**2
assert s.factor(s.diff(W,x)-x*(x*x-s.Rational(1,4))*(x*x-s.Rational(9,16)))==0
assert [s.diff(W,x,2).subs(x,v) for v in (0,s.Rational(1,2),s.Rational(3,4))]==[s.Rational(9,64),-s.Rational(5,32),s.Rational(45,128)]
D=s.Matrix([[-1,0],[1,-1],[0,1]])
assert D.rank()==2 and (D*D.T).rank()==2
```

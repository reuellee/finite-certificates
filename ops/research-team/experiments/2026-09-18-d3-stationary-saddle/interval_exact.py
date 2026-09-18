"""Closed rational interval arithmetic. No floating-point acceptance."""
from fractions import Fraction as Rat
class IV:
    __slots__=('lo','hi')
    def __init__(self,lo,hi=None):
        if isinstance(lo,IV): self.lo,self.hi=lo.lo,lo.hi;return
        self.lo=Rat(lo);self.hi=self.lo if hi is None else Rat(hi)
        if self.lo>self.hi:raise ValueError('reversed interval')
    def __add__(self,o):
        o=IV(o);return IV(self.lo+o.lo,self.hi+o.hi)
    __radd__=__add__
    def __neg__(self):return IV(-self.hi,-self.lo)
    def __sub__(self,o):return self+-IV(o)
    def __rsub__(self,o):return IV(o)+-self
    def __mul__(self,o):
        o=IV(o);a=[self.lo*o.lo,self.lo*o.hi,self.hi*o.lo,self.hi*o.hi];return IV(min(a),max(a))
    __rmul__=__mul__
    def __truediv__(self,o):
        o=IV(o)
        if o.lo<=0<=o.hi:raise ZeroDivisionError('interval denominator contains zero')
        return self*IV(1/o.hi,1/o.lo)
    def __rtruediv__(self,o):return IV(o)/self
    def __pow__(self,n):
        if not isinstance(n,int) or n<0:raise ValueError('nonnegative integral powers only')
        if n==0:return IV(1)
        if n%2:return IV(self.lo**n,self.hi**n)
        if self.lo>=0:return IV(self.lo**n,self.hi**n)
        if self.hi<=0:return IV(self.hi**n,self.lo**n)
        return IV(0,max(self.lo**n,self.hi**n))
    def absmax(self):return max(abs(self.lo),abs(self.hi))
    def nonzero(self):return self.lo>0 or self.hi<0
    def as_pair(self):return [str(self.lo),str(self.hi)]

def terms(expr,variables):
    import sympy as s
    return [(tuple(m),Rat(str(c))) for m,c in s.Poly(expr,*variables).terms()]

def poly_eval(ts,box):
    powers=[[x**n for n in range(1+max((m[i] for m,c in ts),default=0))] for i,x in enumerate(box)]
    out=IV(0)
    for m,c in ts:
        z=IV(c)
        for i,n in enumerate(m):
            if n:z=z*powers[i][n]
        out=out+z
    return out

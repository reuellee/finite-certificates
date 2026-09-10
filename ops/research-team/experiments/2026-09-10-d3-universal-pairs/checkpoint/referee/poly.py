"""Independent referee polynomial arithmetic; extracted from earlier referee helpers only."""
import ast
from itertools import permutations
from exact import Q,q,colex

def trim(p):
    p=list(p)
    while len(p)>1 and not p[-1]:p.pop()
    return p or [Q(0)]

def add(p,r):
    n=max(len(p),len(r))
    return trim([(p[i] if i<len(p) else Q(0))+(r[i] if i<len(r) else Q(0)) for i in range(n)])

def mul(p,r):
    out=[Q(0)]*(len(p)+len(r)-1)
    for i,a in enumerate(p):
        for j,b in enumerate(r):out[i+j]+=a*b
    return trim(out)

def scale(p,c):return trim([c*a for a in p])

def value(p,t):return sum(a*t**i for i,a in enumerate(p))

def pdet(a):
    n=len(a);out=[Q(0)]
    for p in permutations(range(n)):
        term=[Q((-1)**sum(p[i]>p[j] for i in range(n) for j in range(i+1,n)))]
        for i,j in enumerate(p):term=mul(term,a[i][j])
        out=add(out,term)
    return out

def poly_expression(s):
    def parse(x):
        if isinstance(x,ast.Constant):
            assert type(x.value) is int
            return [Q(x.value)]
        if isinstance(x,ast.Name):
            assert x.id=='t'
            return [Q(0),Q(1)]
        if isinstance(x,ast.UnaryOp):
            assert isinstance(x.op,(ast.USub,ast.UAdd))
            return scale(parse(x.operand),-1 if isinstance(x.op,ast.USub) else 1)
        assert isinstance(x,ast.BinOp)
        a,b=parse(x.left),parse(x.right)
        if isinstance(x.op,ast.Add):return add(a,b)
        if isinstance(x.op,ast.Sub):return add(a,scale(b,-1))
        if isinstance(x.op,ast.Mult):return mul(a,b)
        if isinstance(x.op,ast.Div):
            assert len(b)==1 and b[0]
            return scale(a,1/b[0])
        assert isinstance(x.op,ast.Pow) and len(b)==1 and b[0].denominator==1 and 0<=b[0]<=10
        out=[Q(1)]
        for _ in range(int(b[0])):out=mul(out,a)
        return out
    return trim(parse(ast.parse(s,mode='eval').body))

def geometry(parent,direction,signature):
    y=[[trim([q(x),q(d)]) for x,d in zip(row,dr)] for row,dr in zip(parent,direction)]
    assert len(y)==4 and all(len(r)==8 for r in y)
    bs=[pdet([[y[r][i] for i in s] for r in range(4)]) for s in colex(8,4)]
    ns=[]
    for i,s in enumerate(colex(8,3)):
        ns.append([scale(pdet([[y[r][k] for k in s]+[[Q(r==j)]] for r in range(4)]),
                        1 if signature>>i&1 else -1) for j in range(4)])
    return bs,ns

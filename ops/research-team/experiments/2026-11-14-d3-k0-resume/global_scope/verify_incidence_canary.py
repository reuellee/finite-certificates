from fractions import Fraction
# Row is d^2 on all four triple faces of the ordered quadruple.
row = [-1,1,-1,1]
nullvectors = [(1,1,0,0),(-1,0,1,0),(1,0,0,1)]
assert all(sum(Fraction(a)*b for a,b in zip(row,v)) == 0 for v in nullvectors)
# Last three coordinates give the identity matrix, proving independence.
assert [v[1:] for v in nullvectors] == [(1,0,0),(0,1,0),(0,0,1)]
assert all(row)
assert sum(a*b for a,b in zip(row,(1,0,0,0))) != 0
print('PASS: all four columns nonzero; rank 1; kernel dimension 3. Abstract incidence canary only.')

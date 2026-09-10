# Exact distinct-collinear rank-eleven canary

The following actual uniform parent realizes ordinary concurrences
p=e3, q=e4, r=e3+e4. Their common line contains no parent. The incidence
matrix of the transverse-line height model has rank11, so its normalized
fixed-transverse height fiber has dimension zero. Its two vertical wall
gradients are independent. Thus this is a regular example, not a critical
counterexample and not a compactness counterexample.

Use rows Y=(1,t,a,b), with

    t=(0,1,2,3,4,5,6,485/173),
    a=(0,0,-19203/1946,7785/973,13840/973,12975/973,1730/139,624/139),
    b=(0,0,0,-12975/973,-17300/973,-25950/973,692/139,1).

The ordered ordinary supports are

    P: 123 / 145 / 246 / 378,
    Q: 146 / 278 / 348 / 567,
    R: 156 / 178 / 245 / 368.

For a support triple i,j,k, let its three-sparse row have coefficients
(t_k-t_j,t_i-t_k,t_j-t_i) in those columns. Write B_P,B_Q,B_R for the
four-row matrices. The full collinear equations are

    B_P b=0, B_Q a=0, B_R(a-b)=0.

After the four shear gauges a1=a2=b1=b2=0, the square12-by12 matrix in
the family t8=lambda has determinant

    -4 (lambda-6) (lambda-2) (173 lambda-485).

At lambda=485/173 its nullspace is one-dimensional, giving the displayed
height vector. Direct determinants check all70 parent brackets nonzero,
rank three for each ordinary normal matrix, independence of every three
of its rows, and the three stated distinct concurrences. The circuit
formula gives gamma rank two. All exact values are in
COLLINEAR_RANK_PROBE.json.

The bounded producer collinear_rank_probe.py considered only three selected
one-parameter support families and four rational exceptional parameters,
then stopped at this canary. No all-family or no-critical-point claim is
made. It refutes a blanket collinearity-implies-rank-at-most10 assertion;
it does not refute the narrower unproved assertion that criticality plus
collinearity forces that rank drop. Independent reconstruction by another
track is requested before using this referee-produced example as accepted
evidence.

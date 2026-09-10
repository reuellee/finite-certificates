# Exact obstruction to continuous Gordan witness selection

**Result: the proposed canonical-selection ingredient is false on an actual uniform rank-4 parent family. More strongly, no continuous normalized nonnegative Gordan witness section exists near the constructed parent in its full bad locus.** This is a new literal parent chamber and a new fixed signature; it is not a counterexample to the three source signatures, an antichain construction, or the 9DVL cohomological injectivity claim. Ledger 2/9; original obligations closed: zero.

## Literal construction

Column indices are 0 through 7. Triple indices use the source's colex convention: `sorted(combinations(range(8),3), key=lambda t:t[::-1])`. Normals use the source's raw rational cofactors, so `n_ijk(Y) dot x = det(Y_i,Y_j,Y_k,x)`. A signature bit 1 multiplies the corresponding normal by +1; bit 0 multiplies it by -1.

The center parent is

\[
Y=\begin{pmatrix}
1&1&1&1&1&1&1&1\\
0&1&2&0&1&2&0&1\\
0&0&0&1&1&1&2&2\\
-2&2&4&15&-10&-10&-8&-3
\end{pmatrix}.
\]

Every one of its 70 rank-4 brackets is nonzero. The fixed signature is **1110781293763710**. Let `a_i(Y)` be the corresponding signed normal and let

\[
P(Y)=\{w\in\mathbb R^{56}_{\ge0}:\sum_i w_i=1,\;\sum_i w_i a_i(Y)=0\}.
\]

At `x=e4=(0,0,0,1)`, all signed normal evaluations are positive except the five indices `Z=[0,19,23,28,42]`, where they vanish. Thus every normalized nonnegative witness is supported on Z. The exact witness fiber is the segment between

\[
r_0=\frac{(200,32,10,25,0)}{267},\qquad
r_1=\frac{(1900,152,95,0,200)}{2347}.
\]

The nullspace certificate proves the segment description: its two generating nonnegative kernel rays have free coordinates at the last two positions, so nonnegativity forces both ray coefficients to be nonnegative.

Furthermore,

\[
r_0\cdot(r_1-r_0)=\frac{5027435}{167315283}>0.
\]

Consequently the unique minimum-Euclidean-norm normalized witness at the center is `r0`, with squared norm `41749/71289`.

## Two bad approaches with incompatible limits

The first perturbation `Y+tH` uses

\[
H=\begin{pmatrix}
0&2&-1&-2&0&0&0&0\\
2&0&0&0&0&0&0&0\\
0&0&0&0&0&0&0&0\\
0&0&0&0&0&0&0&0
\end{pmatrix}.
\]

The derivative of the five signed last coordinates is `d=(0,-2,2,2,-2)`. A second auxiliary perturbation is

\[
G=\begin{pmatrix}
0&-1&-1/2&1&0&0&0&0\\
1&0&0&0&0&0&0&0\\
-1&0&0&0&0&0&0&0\\
0&0&0&0&0&0&0&0
\end{pmatrix}.
\]

Its derivative on those five signed last coordinates is `(1,1,1,1,1)`. Set `H2=-H+G/89`. The second approach `Y+tH2` therefore has derivative `-d+(1/89)1`.

For each of these two approaches, `certificate.json` contains five exact rational polynomials `k_i(t)` with

- `sum k_i(t) a_i(Y+tH)=0` (respectively with H2), as a polynomial identity;
- every `k_i(t)>0` for `0<=t<=10^-6`;
- all 70 original bracket signs unchanged throughout that interval;
- all 51 signed last coordinates outside Z strictly positive throughout that interval.

The positive kernel polynomials come from the alternating four-row cofactors of the five-row signed normal matrix, divided by their common factor `t`. Their positivity is proved by rational coefficient domination, not sampled numerics. Normalizing by their sum proves that both entire punctured intervals lie in the bad locus.

Suppose feasible normalized witnesses on the first approach converge to `w` at the center. The center's positive outside-Z evaluations force `w` to be supported on Z. For t>0, the last-coordinate witness equation and nonnegative outside-Z terms give

\[
\sum_{i\in Z} w_i(t)\frac{a_{i,4}(Y+tH)}{t}\le 0.
\]

Taking limits gives `d dot w <= 0`. The same reasoning on the second approach gives `(-d+(1/89)1) dot w <= 0`, or `d dot w >= 1/89`. No normalized center witness can meet both inequalities. Therefore **no section continuous at Y exists on a relative neighborhood in the full bad locus**.

The minimum-norm selector already fails on the first approach because `d dot r0=2/89>0`. Its discontinuity is not merely a numerical support-change artifact.

## Properness and normalization scope

For every `0<t<=10^-6`, the parent `Y+tG` remains in the same strict parent chamber, and e4 has all 56 signed margins positive. Thus the fixed signature is realizable in this chamber, its good locus is nonempty, and its bad locus is proper and nonempty. At `t=10^-6`, the minimum signed margin is exactly `1999997/2000000000000`. No claim about a three-signature antichain is required or made for this single-block selection counterexample.

The displayed parent is a literal realization. It transfers directly to the chart in which the first four columns are the identity: their determinant is exactly 2 at the center and remains positive throughout all certified intervals, so `T(Y)=Y[:,0:4]^-1` is continuous. All triple cofactors transform by the common invertible map `det(T)T^-T`. Therefore their weight fibers are unchanged, including the minimum-norm obstruction.

If further parent normalization uses continuous positive column factors `d_j`, each triple normal acquires the additional positive factor `c_i=product(d_j for j in triple_i)`. The normalized fibers are related by the continuous invertible map `w'_i=(w_i/c_i)/sum_j(w_j/c_j)`. Hence the stronger **nonexistence of any continuous normalized section** survives such a regular positive gauge change. Euclidean minimization itself need not be preserved by that diagonal rescaling. We have not supplied coordinates in the repository's full canonical nine-dimensional gauge.

## Replay, search extent, and limits

Run `python falsifier/certify.py` from the cycle root. It uses exact SymPy rational/polynomial arithmetic and reads `candidate.json`; it does not import the searcher's acceptance logic or any input geometry module. `search.py` is the reproducer for candidate discovery and uses source determinant conventions, rational linear algebra, and SciPy LP only for candidate ranking. Exact final acceptance is separate.

The bounded discovery used one grid-lift parent candidate, 31 nonempty active supports of its five-row fiber, 24 derivative coordinate directions, and 1,371 lexicographic derivative targets before the first successful target. The two extra bad/good all-parameter families were a certificate completion of that found construction. The initial three-signature LP screen at the pinned THREE_ROW_WITNESS was diagnostic only and is not part of this proof. No long-running process or exhaustive atlas search was launched. SymPy 1.14.0 was installed as a temporary dependency; no paid compute or API service was used.

This retires the conjecture that generic minimum-norm witness selection is globally continuous, and the stronger idea that a continuous normalized witness can always be chosen locally on the bad locus. It does **not** eliminate stratified witness correspondences, multivalued methods, homological attachment arguments, or prove/refute the original injectivity map. Any further route must accommodate incompatible witness limits across incident bad strata.

# Saturation-assisted original pair attachment: constructive gate

**NULL / STALLED / STOP.** No original attachment obligation closed. The
ledger remains 2/9. Main F4SAT computation is ineligible and was not started.
This is not a counterexample to the proposed combination or to 9DVL.

Base: `3a7ce7b5d57543d54eace7707659418cea6d69c9`, tree
`7e2e958bcc7fef306bfc309c1502a279925b4ab6`.
Scope: one bounded constructive gate on the original map

    D = (r01, -r02, r12): direct_sum Hc1(Aij) -> Hc1(T).

All original proper incomparable extension labels remain fixed. No arbitrary
signing or local circuit is substituted for a whole extension. In particular,
the balanced-end N/M description is not used unconditionally: that source
assumes Hc0(T)=0. The original D and its cochain mapping problem do not require
that unproved vanishing.

## 1. Strongest surviving geometric lemma: a local sign collar

Let x be coordinates on a normalized open nine-dimensional parent chart X,
with all 70 prescribed parent brackets strictly signed. Write N(x) for the
4-by-56 matrix of the actual derived normals, as columns. For each original
extension rho_i, N_i is obtained by multiplying column I by rho_i(I).
All charts and any denominators are retained; this is a chart statement.

Take every nonidentically-zero minor of N of orders 1 through 4. After clearing
only known nonzero chart denominators, factor their numerators over Q. Fix one
irreducible factor q. Let u be the product of the other distinct factors,
parent brackets, and chart units. This definition does not assert that the
existing six-kind residual-factor table already contains every minor factor.
No such enlarged factor list was constructed or counted in this gate.

**Conditional collar lemma.** At any real x0 satisfying

    q(x0)=0,  u(x0)!=0,  grad q(x0)!=0,

there is a neighborhood, with coordinates (z,s) and q=s, in which every actual
B_i, A_ij and T is simultaneously a product of the z-neighborhood with a union
of the three transverse cells s<0, s=0, s>0. These are the actual inclusions,
with the original labels; zero Gordan weights are included.

Proof. The implicit-function theorem supplies the coordinates and permits
shrinking to a connected product neighborhood. Every minor equals q^e times
a continuous nonzero unit there. Hence its sign and zero status are constant
on each of the three transverse cells. A support-minimal nonnegative kernel
vector is a positive circuit of at most five normals. On a circuit of size k,
choose k-1 independent coordinate rows; the circuit coefficients are the
alternating (k-1)-minors, up to a common factor. Its rank, support, and coefficient
signs are therefore constant on each cell. There are finitely many supports,
so existence of a positive circuit is constant on each cell, for every fixed
original signing simultaneously. By Gordan, this is exactly membership in
B_i. Intersections preserve the same product description. The zero transverse
cell uses all minimal supports, including smaller ones, rather than discarding
weights which have become zero. This proves the statement.

Each B_i is closed relative to the chart, so its transverse set is one of
empty, {0}, {s<=0}, {s>=0}, or the whole interval. This observation does not
claim all five occur for an admissible extension.
The conclusion describes the actual bad-set membership diagram only. It does
not give a continuous witness selection, a trivialization of all witness
polytopes, or a face-natural contraction of their coordinates.

The polynomial failure ideal for smoothness on this chart branch is exactly

    I_col = <q, partial_1 q, ..., partial_9 q> : u^infinity.

An identity u^n = a q + sum_j b_j partial_j q over Q would exclude that
singularity failure, even over C. This is an actual local geometry implication,
not a cohomological rank restatement. It has not been instantiated or solved.

**Why this does not pass the gate.** The collar supplies a transverse germ,
not the connected oriented factor-end strata, their compact-support cochains,
or their global oriented incidences. It omits the real locus u=0 and true
parent infinity only by explicitly restricting its domain; both remain
unresolved parts of the original problem. No proper global collapse or face
map from this germ to the factor-stratified model has been constructed.
Consequently it adds no certified entry to the original global b_ij matrices
and removes no exhaustively attached source class. Smooth collars cannot be
silently extended across intersections, zero-support rank strata, chart seams,
or infinity. A smooth factor also need not have trivial global topology.

## 2. Explicit original-space real equations available before saturation

For any fixed proper admissible triple rho_0,rho_1,rho_2, let h_l(x)>0 encode
the prescribed chart and parent-chirotope inequalities. Normal denominators
are first cleared using their known signs.

The strict parent domain has an exact real polynomial encoding

    h_l(x) e_l^2 - 1 = 0       for every l.

Bad block i is encoded with all 56 coordinates retained:

    lambda_iI = v_iI^2,
    sum_I v_iI^2 = 1,
    sum_I rho_i(I) n_Ia(x) v_iI^2 = 0   for a=1,...,4.

This includes every zero weight and all witness-rank strata. A good block k
is encoded by an actual separating vector p_k and strict-slack variables:

    (rho_k(I) n_I(x) dot p_k) d_kI^2 - 1 = 0  for every I.

Over R these equations are equivalent to strict Gordan goodness. Thus an
actual E_ij=A_ij minus B_k system combines the parent equations, two bad-block
systems and one good-block system. T instead uses three bad-block systems.
These are point-membership equations only. They do not encode a nonzero
cohomology class, its compact support, or its vanishing under D or kappa_i.

Saturating by parent units does not retain their real signs by itself. The
slack equations above retain signs over R, but not over C; a complex emptiness
certificate is sufficient and may be far stronger than the real statement.
No feasibility or emptiness assertion for these original E_ij or T systems is
made. In particular, they must not be saturated to emptiness merely because
their cohomological kernel is the intended exclusion target.

## 3. Finite inventory of candidate missing lemmas actually examined

### C1. Extend the generic-factor collar to the original global end map

The local statement and ideal I_col are given above. Existing common-root
connectivity and arbitrary-block occurrence H1 elimination apply only to
generic factor choices. The residual-elimination source supplies opposite-side
interval cospans only when the named same-block partner exists.

First unproved implication: the local collar and those carriers do not give a
proper globally defined comparison, with true-infinity relative subcomplex,
whose oriented incidence is the original b_ij. No component-faithful source
index or full face-specialization map was obtained. The complement u=0 is not
an allowable discard. Result: conditional local lemma; original target NULL.

### C2. Saturate failure of a mixed comparison prism

The row-2599 sources provide polynomial pair prisms and an H2 prism with literal
seams and genuine parent-wall faces. A prospective polynomial map P(t) from a
compact cube would have concrete failure systems such as

    h_l(P(t))=0,  0<t_a<1,

on a face required to remain in the strict parent cell, together with exact
Gordan witness equations and nonnegative weights on the whole cube. Parameter
strictness has the real encoding t_a e_a^2-1=0 and
(1-t_a) f_a^2-1=0. Only the appropriate strict faces may be tested this way:
parent-boundary faces deliberately have h_l=0 and zero witness faces remain.

First unproved implication: there is no proposed full original-domain mixed
prism map, with the prescribed boundary faces, to put into these equations.
The old source has four of six local incidences, not the universal H0/H1
comparison family or an original-space global chain. Saturation can validate
a supplied polynomial map but cannot manufacture the absent carrier from
rank equations. No interpolation search or old-prism refinement was run.
Result: candidate not defined far enough to be saturation-eligible.

### C3. Exclude critical points and deduce detector nondegeneracy

For a specified smooth stratum F_1=...=F_m=0 of an actual compactified witness
family and a specified proper function ell, rank-maximal critical points have
the polynomial system

    F=0,  d ell = sum_j mu_j d F_j.

Saturation by a specified full-rank Jacobian minor retains the branch where
that minor is nonzero. Its zero locus is outside that localized calculation
and still requires separate equations and attachments. Abnormal Fritz-John
solutions cannot all be discarded. Actual
membership may be encoded by section 2, but it is not automatically smooth.

First unproved implication: no function, simultaneous stratification, and
relative boundary conditions were identified for which absence of the named
critical points implies a nonzero original signed trace for every nonzero
opposite-pair class. The canonical detector equivalence does not give this
geometric premise. Local regularity and critical exclusion do not determine
the signed split/merge map. Result: no justified injectivity failure ideal.

These are three examined candidate lemmas, not three proofs of impossibility.
No original-scope counterexample has been found. Nothing here rules out a
different saturation-assisted global theorem.

## 4. Freeze and resource record

At the first gate, the remaining blocker was already the absent global
attachment/comparison. The coordinator was notified and discovery was stopped.
Work after that notification only documented the candidate formulas and scope.
No saturation engine, modular screen, CAD, source census, signing enumeration,
or new local atlas was run. No computed certificate is claimed. Consequently
there is no arithmetic replay of a new certificate; source digests are supplied
separately for independent proof audit.

Closing delta: zero original obligations closed; pair coverage and residual
UNKNOWN; Hc0(T) remains open independently. No derivative, rank, slack, or
collar formula is credited as 3/9 or as an original pair-kernel reduction.
The selected experiment ends at its stated design gate. Same-route continuation
is not justified by these conditional formulas.

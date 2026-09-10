# Independent review of the additional escape theorems

Verdict: ACCEPT_DEDUCTIVELY, with the scopes below. This is a conventional proof review; no generic-point argument or finite sample is used as a substitute for the global statements.

## Whole-height flat block

Reviewed `proof/FLAT_HEIGHT_BLOCK_EXCISION.md`, SHA256 `ff82dd4adaa5e288ab483027707fdbe589338da01823ec4e6cf381e0a53a5f57`.

The coefficient-vector definition of E_Q is closed and invariant under changing accepted height charts. Each derived normal has three height-linear coordinates and one height-independent coordinate, so the ordinary determinant has height degree at most three. The parent residence is nonempty open, making polynomial identity equivalent to vanishing on its full residence. On E_Q the remaining R concurrence contributes four affine equations in five variables; every nonempty fiber is a full open convex positive-dimensional cell at every coefficient rank. The closed r=p piece retains a full four-height cell. Degree-zero shriek base change and localization therefore prove the asserted Hc0 vanishing. Finite sign sectors and the original parent component remain included.

The global36 axis condition is projected-only and fiber-saturated: its three core planes contain both p and their common central parent, forcing the primitive core dependence for every height lift. The global38 condition is also fiber-saturated: its two core planes and their intersection line are fixed under shifts along p, and the root-line incidence determinant is unchanged. These are valid closed subcases, not arbitrary closed subsets of the larger vanishing locus. Neither stationary kind48 directions nor two vertically coincident non-flat sections are included.

## Full collinear branch with a kind48 factor

Reviewed `proof/TYPE48_COLLINEAR_ESCAPE.md`, SHA256 `3501784505fa92aa7b5219f9b858c1895ac214e763c8ee9a12e435b9e9b193c8`.

The six high parents are the fixed complete-quadrilateral intersections. The proposed base is an RP1-squared bundle over RP2 minus those six points, with dimension four and no compact component. The sparse K4 argument proves the P block has rank exactly three both off the selected lines and on one selected line; centers at their intersections were correctly removed as parent-on-L cases. The high-parent kernel has precisely two shears and one non-shear direction. Uniformity forces the latter coefficient to be nonzero, so its scale normalization reconstructs the complete quadrilateral and the projection center. No unproved extra compatibility equation remains at rank eleven: the normalized kernel is a single lift, varying continuously, and strict feasibility is open in the stated full base. Finite sign lifts preserve this local argument. A compact component would have compact nonempty open image in a connected noncompact manifold, which is impossible. The separately accepted lower-rank, parent-on-L and collision removals restore the full collinear locus.

## Deficient blocks for kinds49,50,51

Reviewed `proof/RANK_DEFICIENT_BLOCK_ESCAPE.md`, SHA256 `ba777a0452dcca453a1baef12748312cbed48663ab877e3bbb20e6fa659befd1`.

If a selected plane does not contain L, equal transverse parent directions within that plane force their joining line through its concurrence. A different nonempty incidence pattern would force that concurrence to be an original parent, excluded by uniformity. The only allowed repeated nonempty pattern is leaves7,8 of kind50; even then both leaf coefficients stay nonzero. The stated leaf eliminations therefore prove that every deficient block has a zero selected row. Such a row is exactly a three-label projected cluster on the parent-free locus.

The projected cluster quotient has dimension THREE: one point of weight three and five singles, modulo PGL2. All singleton coincidences of multiplicity at most three remain allowed. The four-single collision path proves every component noncompact, including the argument excluding divergent projective renormalizations. The selected zero row forces stacked rank at most eleven on the entire base. At rank eleven the normalized height lift is again an open graph; lower ranks are already removed by their full closed-piece theorem. The finite union of selected-plane pieces equals the deficient-block locus. This accepts its Hc0 vanishing and leaves the all-(4,4,4), stacked-rank-eleven, one-common-stress case.

## Dependencies and remaining scope

These proofs use the authenticated all-six ordinary concurrence charts, genuine parent-unit three-row independence, the accepted collision excision, and the accepted common-line normalization/closed-fiber proof. The parent-on-L and rank-at-most-ten statements were reviewed separately. Full closed pieces must be removed before forming the remaining critical locus; no inference from Hc0 of a whole piece to an arbitrary closed critical subset is made.

No source-orbit count is added. Noncollinear dependent-gradient loci and the residual high-kind common-stress collinear locus remain. Universal pair vanishing stays complete; the full triple endpoint and original score3/9 have not been proved.

## Linear-gradient-pencil discriminator

Reviewed `proof/LINEAR_GRADIENT_PENCIL_GATE.md`, SHA256 `74bfe5ff1de09803101ab13d6613c97450521db552b21684da240cda9bc9bc17`. ACCEPT as the stated algebraic equivalence, conditional on the independently accepted point-kernel classification. Writing p=a q+b r gives gamma_Q=b C_Q(r) and gamma_R=a C_R(q). With C_R(q)=c C_Q(r), expansion of (C_Q-t C_R)(q+c t r) has zero constant and quadratic terms from the two known kernels and zero linear term from this equality. Conversely its linear coefficient recovers the equality. Point kernels ensure the two cross-images and c are nonzero. This is a necessary-and-sufficient pair-only test at a third distinct collinear point, not a proof that actual parent pairs exclude this degree-one kernel. Identically vanishing pencil minors alone are explicitly not claimed sufficient.

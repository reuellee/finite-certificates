# Independent mathematical review of multiplier elimination

Candidate: falsifier/audit_multiplier.py. Input is authenticated LIFTED_SYSTEM.json.
Classification: exact guarded equivalence, not emptiness or new source closure.

Write d=E_x, n=psi_x. The inherited conic identity and genuine parent/slope guards prove d!=0. The x-stationary equation uniquely forces lambda=n/d. For each remaining affine-in-lambda equation p=a+b*lambda, its replacement d*a+b*n=0 is equivalent on d!=0. Retain psi=E=psi_C=psi_L=0 and replacements for A, beta and transverse chi. This gives seven equations in six variables, not a dimension or inconsistency theorem.

The full domain must still retain all original reconstruction pivots, E_beta and psi_beta, all 70 parent brackets and applicable signs. A polynomial cancellation is valid only after its removed factor is proved a unit or its zero stratum is separately covered. The inherited lambda!=0 translates to n!=0 (also forced by the strict maximum filter).

For real d!=0, the strict maximum filter a2*lambda>0 is equivalent to a2*n*d>0, since multiplication by d^2 preserves sign. The orientation inequality is equivalent to n*(d*psi_B-n*E_B)>=0. Equality remains admitted. No assumption that d is positive is justified.

The Hessian must be formed holding lambda constant BEFORE substitution. The candidate does this. With lambda=n/d the new Hessian is d^2 times the old Hessian. The Gamma-derived tangent frame is unchanged. Hence M5_new=d^2*M5_old and the polynomial second Schur numerator satisfies S4_new=d^4*S4_old. Every principal minor of order k is multiplied by d^(4k)>0, by determinant multilinearity. Therefore all 15 principal-minor inequalities are exactly equivalent, including singular PSD and zero-minor strata. Recomputing a Hessian after substituting a variable-dependent multiplier and differentiating it would be invalid; this candidate does not do that.

No actionable flaw found in this reduction. It neither rules out any new real solutions by itself nor proves K0 empty. It supplies equivalent inputs for a future exact real resolution. It does not imply 3/9.

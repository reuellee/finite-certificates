# Producer-independent homogenizer boundary certificate

Verdict: **accepted frozen constructor partial frontier with a fail-closed null endpoint**.

The pinned 108-term affine factor was dehomogenized from, then independently re-homogenized to, the exact degree-`(2,2,2)` source in `Q[a,b,c,u,d,e,f,v,g,h,i,w]`.  No producer code, numerical probe, modular evidence, sample, network service, or connector was used.

The seven deepest-first restrictions are `u_v_w`: 11 terms, `u_v`: 37 terms, `u_w`: 23 terms, `v_w`: 23 terms, `u`: 64 terms, `v`: 69 terms, `w`: 47 terms.  All 72 tangent restrict/differentiate identities hold exactly.  The 12 normal derivatives are retained separately, so stratum singularity is never promoted to ambient singularity.

For `u=v=w=0`, the 11 surviving terms equal exactly `-h*(a*f-c*d)*(a*e*i-a*f*h-b*d*i+b*f*g+c*d*h-c*e*g)`.  The displayed factors have multidegrees `(0,0,1)`, `(1,1,0)`, and `(1,1,1)`, occur once in that displayed product, and define divisors of dimension 5 in `P2 x P2 x P2`. The constructor's five product-rule seeds—three pairwise factor intersections, `Sing(L)`, and the determinant rank-at-most-one locus—were checked exactly. `Sing(L)` is retained as an explicit seed although it lies in `V(L,C)`.

The same pinned 70-record parent stream gives three and only three certified deepest-factor correspondences: `H_08_1248=h`, `H_22_1367=-(a*f-c*d)`, and `H_34_1678=det`.  Each was checked by exact and sign-normalized sparse equality.  No parent-factor correspondence is inferred for any of the remaining six types.

On the processed `V(h,L)` seed, independent lexicographic sparse division proves that the `u` and `v` normal derivatives lie in `(h,L)` and reconstructs `dF/dw=quotient*L+e*Q`.  Thus the two exact ambient children are `V(h,L,e)` and `V(h,L,Q)`; both are projective-infinity only and already excluded by `H_08_1248` and `H_22_1367`.

For `u=v=0`, direct substitution into the independently reconstructed source and all 12 full derivatives proves that `u=v=b=c=e=f=0` is a linear `P3` family. It has exact dimension 3 and degree 1 and is excluded because `H_22_1367=c*d-a*f` vanishes identically.  It is not accepted as affine and is not claimed to exhaust the ambient singular ideal.

The inherited atlas replay certifies 64 charts, 4,032 directed principal-open overlap records, and 279 type/chart incidences (`27+36+36+36+48+48+48`).  No branch duplicates were quotiented: a later quotient must provide an explicit invertible overlap witness.

Every reviewed predecessor and constructor input is loaded with `git show` from frozen candidate `25757510dd88e8b7bbe5668c89f93b2a46b264de` and checked against its pinned SHA-256.  Later protocol-only working-tree changes therefore cannot alter or invalidate the reviewed source snapshot.

All 60 hostile mutations were rejected.  The independently reconstructed residual is `B-UV-01-unclassified-ambient-components`, SHA-256 `2747fcc6923b44996bfe79c0d06d2f88169f9fedea465cdecaa3c104bcf6b8b5`. No complete seven-type component census, nondeepest factor certification, overlap quotient, accepted affine pullback, 70-parent affine census, strict-real residence, or connected-parent tag is certified.  The ledger remains `2/9`.

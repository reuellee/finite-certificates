# Independent audit: omitted-label type49 versus type50/51

**Verdict: the proposed proof of `Hc^0(H_f intersect H_g;Q)=Hc^1(H_f intersect H_g;Q)=0` for factor kinds49+50 and49+51 survives the examined geometric and compact-support obstructions.** This is an auxiliary universal factor-pair statement, contingent on the pinned classification identifying the actual factor walls with the displayed determinant supports. It does not prove original pair injectivity or diagonal3.

The type49 support uses seven parent labels. Let e be its omitted label. Normalize five of the other seven labels as a projective frame and forget e. The equation f=0 depends only on this fixed seven-column configuration. Therefore every fiber of this forgetful map on `H_f intersect H_g` is the locus g=0 in the residence cell of e, with the other seven columns fixed. The actual parent inequalities are retained.

For kinds50 and51, e has degree one or two in their unique support. The canonical representatives are

```
50: 123/145/246/378
51: 123/145/267/468.
```

## Degree-one cases

The derived determinant contains one normal which depends linearly on e. Thus its vanishing cuts out a projective plane, the entire projective3-space, or the empty set. In a chart defined by a genuine parent-bracket unit, its intersection with the residence cell is open convex of dimension2 or3, or empty. This includes identically-zero determinant fibers; excluding those without argument would leave a gap. All these fibers have zero compact-support cohomology in degrees0 and1.

## Degree-two cases: exact incidence hypotheses

Write the two incident triples as eab and ecd and the two fixed support planes as C and D; put `L=C intersect D`. The lines ab and cd are skew, because their four labels are distinct and their parent four-bracket is nonzero.

For every degree-two case, one may choose the line named ab so that it meets C at a fixed parent label x which does not belong to D. The second endpoint of ab does not belong to C. Thus the two parent brackets `[C,y]` and `[D,x]` are nonzero; ab meets C only at x, and x is not in D. This proves ab is skew to L throughout the uniform parent domain.

`verify_ruled_quadric_cases.py` exhaustively checks all16 canonical moving-label cases, including the eight degree-two cases, and emits the exact choices and genuine bracket units in `RULED_QUADRIC_CASES.json`. Simultaneous relabeling transports this finite proof to arbitrary relative labelings of f and g; no parent sample is used for the incidence conclusion.

## The ruling parameter and its genuine missing point

Every admissible e is outside ab. Since ab is skew to L, the plane `(e,ab)` meets L in a unique point q. This defines a continuous semialgebraic map q on the whole admissible e-space.

Choose any fixed label z different from a and b. The point

`q0=(abz) intersect L`

is uniquely defined, because L cannot lie in the plane(abz) while being skew to ab. If q=q0, the planes(e,ab) and(abz) coincide, which would force the actual parent bracket `[eabz]=0`. Hence q0 is absent from every admissible fiber. The parameter lies in `L minus {q0}`, an affine line. The same genuine unit `[eabz]` supplies a global affine chart for e on the residence cell. No auxiliary boundary is inserted.

## Regular fibers

If q does not lie on cd, the equation g=0 is equivalent to

`e in r(q)=(q,ab) intersect (q,cd)`.

The two planes here are distinct: equality would contain both skew lines ab and cd. Thus r(q) is a projective line. It is not contained in the parent boundary `[eabz]=0` when q!=q0. Indeed, its intersection with ab is the point at infinity in that genuine affine chart; the whole line could lie in(abz) only if r(q)=ab, which would again put both skew lines in one plane. Consequently each nonempty residence fiber in r(q) is one open affine interval, obtained by intersecting all strict affine parent-bracket inequalities.

The family r(q) is a locally trivial line family away from the exceptional parameter below. Strict feasibility persists locally, so the image of the residence set is open in the affine q-line with that parameter removed. Each connected image component is an interval. A continuous section exists because the nonempty fibers are open convex intervals; local sections can be patched by a partition of unity. The regular residence component contracts to this section. It is an open2-manifold and therefore an open two-cell. In particular its compact-support cohomology is zero in degrees0 and1.

## Exceptional fiber and gluing

The fixed line cd either misses L or meets it at exactly one point q*. It cannot equal L: the explicit incidence patterns supply an endpoint of cd outside one of the fixed support planes C,D. Its corresponding parent four-bracket is nonzero, so cd is not contained in that plane and cannot be L. This witness is checked explicitly in the extended incidence certificate.

If q* exists, then the second plane `(e,cd)` automatically contains q*. The fiber over q* is precisely

`plane(q*,ab) intersect the parent residence cell`.

It is empty or an open convex2-cell in the same genuine affine chart. This includes a reducible quadric which is the union of two planes. If q*=q0, this entire exceptional fiber is excluded by the parent bracket and is empty.

Because q is continuous, the exceptional fiber is closed in the full residence fiber. Its complement is the regular open part already treated. The compact-support open/closed long exact sequence gives degree0 and degree1 vanishing for their union. No gluing map is discarded or assumed injective.

## Global compact-support conclusion

For the forgetful semialgebraic map p, every fiber of `H_f intersect H_g` has `Hc^0=Hc^1=0`. Hence the low-degree stalks of `Rp_! Q` vanish. Compact-support composition then proves the same low-degree vanishing on the full pair-wall locus, irrespective of the topology of the seven-column base. The argument uses `p_!`; the residence fibers are open and the map is not asserted to be proper.

This rules out the proposed boundary and exceptional-ruling counterexamples to the omitted-label route. The source-to-factor identification and the separate wall-union-to-original-D3 implication remain external proof dependencies. The hard type pairs50+50,50+51,51+51 have no omitted parent label supplied by this argument.

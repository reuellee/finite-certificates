# D9 fixed-domain CEGAR constructor findings

The complete bounded seed frontier contains the two exact committed row-2599
stress families, `12/37` and `37/176`.  Each family independently satisfies
the theorem-domain input clauses: all nine feasibility regions are nonempty
and proper, and all 72 ordered containment claims are refuted by exact integer
feasibility or Gordan witnesses.

Neither seed is a counterexample.  Exact rational one-column paths place its
two proposed separator endpoints in one component of the common feasibility
locus.  The paths contain 22,711 and 22,811 segments.  Therefore both sampled
separators are repaired exactly.

This is an exact null result, not an absence theorem.  The committed seed
frontier is complete, but the repository has no complete generator for all
fixed-domain counterexample candidates, no complete parent chamber atlas, and
no all-parent coverage.  The ledger remains `2/9`.

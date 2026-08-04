# Diagonal 9: antichain-aware graph certificates

## Result and proof boundary

The ninth diagonal is still open.  The repository contains a proof that it is
equivalent to a finite labeled master-chamber graph test, but it does not
contain the chamber roadmap needed to run that test for any of the 2,604
realizable parents.

This note contributes four exact results.

1. It proves a corrected antichain-aware spanning-tree certificate.
2. It proves that the earlier union-of-sides certificate is strictly too
   strong, even when the ninth-diagonal conclusion is true.
3. It gives a complete cut-SAT encoding and an exact finite-graph solver.
4. It specifies the finite geometric data still required for a proof rather
   than treating the 2,604 catalog representatives as a chamber atlas.

The exact combinatorial verifiers are
`DIAG9_GRAPH_verify_tree_certificate.py` and `DIAG9_GRAPH_cut_sat.py`.  They
use integer bitsets, exact graph search, exact Dilworth matching, and a
dependency-free exact DPLL solver only.

`DIAG9_GRAPH_inventory.py` independently rechecks the 2,604 exact parent
matrices and pins the current data boundary.

## 1. Labeled master graph and region poset

Fix a realizable parent $M$.  Let $G=G_M$ be the complete master-chamber
graph from `NINTH_DIAGONAL_SAFE_GRAPH.md`.  Its vertex label is

\[
                 T(v)=\{\sigma:F_\sigma\text{ contains }v\}.
\]

Every nonempty feasibility region meets a generic chamber.  Consequently the
full labeled graph determines the global region order:

\[
 F_\sigma\subseteq F_\tau
 \quad\Longleftrightarrow\quad
 \{v:\sigma\in T(v)\}\subseteq\{v:\tau\in T(v)\}.       \tag{1}
\]

Equal support rows represent the same region and must be quotient-identified.
A row is proper exactly when its support is neither empty nor all of $V(G)$.
Thus properness and pairwise incomparability need no separate oracle after the
complete graph has been certified.

For a finite subposet $P$, write $\operatorname{width}(P)$ for its largest
antichain.  For a region $d$, write

\[
                    I(d)=\{a:a\parallel d\}
\]

for the regions incomparable with $d$.

## 2. The sharp pairwise spanning-tree certificate

Let $R$ be a spanning tree of $G$.  For two chamber vertices $u,v$, put

\[
                         E_{uv}=T(u)\cap T(v).          \tag{2}
\]

> **Pairwise tree certificate theorem.**  Suppose that for every pair
> $u,v$, every vertex $w$ on the unique $R$-path from $u$ to $v$,
> and every $d\in E_{uv}\setminus T(w)$,
>
> \[
>       \operatorname{width}\bigl(E_{uv}\cap I(d)\bigr)\le7.    \tag{3}
> \]
>
> Then the induced graph $G[S]$ is connected or empty for every
> nine-element antichain $S$ of proper feasibility regions.  Hence the
> ninth diagonal holds for $M$.

**Proof.**  Let $u,v\in G[S]$.  Then $S\subseteq E_{uv}$.  If a vertex
$w$ on the tree path missed $d\in S$, the other eight members of
$S\setminus\{d\}$ would be an eight-element antichain contained in
$E_{uv}\cap I(d)$, contradicting (3).  Every path vertex therefore supports
all of $S$, so the tree path lies in $G[S]$.  This joins every pair of
vertices of $G[S]$.  QED.

The bound seven is exact for this proof mechanism.  A region $d$ belongs to
some nine-antichain in $E_{uv}$ if and only if

\[
                  \operatorname{width}(E_{uv}\cap I(d))\ge8.    \tag{4}
\]

Thus (3) says precisely that a tree waypoint may omit only regions which
cannot participate in a relevant nine-antichain common to its endpoints.

For a fixed tree edge, it is enough to apply (3) to pairs $u,v$ on opposite
sides of the cut and to its two endpoints.  The path formulation above is
cleaner and is what the verifier checks.

## 3. Why the union-cut set is too coarse

The earlier proposal associated to a tree edge $e$, with sides $A_e,B_e$,
the set

\[
 C_e=\left(\bigcup_{v\in A_e}T(v)\right)
       \cap
       \left(\bigcup_{v\in B_e}T(v)\right).            \tag{5}
\]

Replacing $E_{uv}$ by $C_e$ in (3) is sufficient: every common endpoint
family is contained in $C_e$.  It is not necessary, because the occurrence
of nine regions individually on both sides does not imply that either side
has a chamber supporting them jointly.

There is a finite exact countermodel to completeness of (5).  Let vertices
$0,\ldots,8$ form a 9-cycle and attach a leaf 9 to vertex 0.  There are
nine regions; region $i$ is supported at every vertex except cycle vertex
$i$.  Then:

* the nine rows are nonempty, proper, and pairwise incomparable;
* their common support is the singleton vertex 9, so the ninth conclusion is
  true;
* every spanning tree deletes one cycle edge;
* an internal edge of the resulting cycle path has at least two cycle
  vertices on each side, so every region occurs on both sides and $C_e$
  contains all nine regions;
* each endpoint misses one region $d$, and the other eight regions form an
  eight-antichain in $C_e\cap I(d)$.

Therefore **all nine spanning trees fail the union-cut certificate**, while
all nine pass the sharp $E_{uv}$ certificate.  The verifier exhausts the
nine trees and checks the widths exactly.  This is a no-go for the proposed
coarse certificate, not for 9DVL.

Run:

```console
python ai/omreal/DIAG9_GRAPH_verify_tree_certificate.py
```

Expected final lines include:

```text
PASS: all 9 spanning trees fail the coarse union-cut C_e condition
PASS: all 9 spanning trees pass the sharp pairwise E_uv condition
THEOREM: the pairwise tree certificate is proof-safe for s=9
NO-GO: the union-cut C_e certificate is sufficient but not complete
```

## 4. What exact finite data already exist

The repository currently has:

* all 2,628 abstract `UOM(4,8)` catalog classes and exact realizability
  verdicts, of which 2,604 are realizable;
* one exact parent matrix for each realizable class in `certs_4_8.jsonl`;
* the exhaustive classification of 367,290 four-normal determinants into 52
  incidence orbits, including 84,840 labeled residual occurrences in 13
  residual orbits;
* the generic two-sided wall-gluing theorem and its exact incidence checker;
* for parent 2599, 178 exact parent charts covering all 97,224 realizable
  single-element extension signatures;
* for one proper incomparable nine-family on parent 2599, a 22,711-segment
  exact coordinate path joining the two sampled endpoint charts.

None of these is a master-chamber coverage certificate.  In particular, the
178-chart artifact proves that every individual extension occurs somewhere;
it neither lists every residual sign chamber nor proves adjacency or coverage
of the parent realization cell.  The 2,604 catalog matrices give one point
per parent class, not one point per residual chamber.

Run the exact inventory with:

```console
python ai/omreal/DIAG9_GRAPH_inventory.py
```

## 5. Data required for a conclusive run

For each parent $M$, a proof-producing pipeline still needs:

1. **Chamber representatives.**  One exact rational parent matrix per
   connected generic residual chamber, with all parent and residual signs
   recomputed exactly.
2. **Coverage.**  An exact CAD/roadmap, certified interval decomposition, or
   equivalent proof that no further generic chamber meets the parent cell.
3. **Adjacency.**  Exact generic-wall incidences and proof that the listed
   graph contains every adjacency.  The existing gluing theorem then supplies
   all signature labels needed on an edge.
4. **Region labels.**  The complete tope set of the derived arrangement at
   every chamber representative, derived exactly from the 56 normals.
5. **Finite verdict.**  Either a disconnected nine-antichain with exact cut
   certificate, a complete SAT-unsatisfiability proof, or a passing sharp
   tree certificate.

### Complete cut-SAT encoding

The new cut-SAT verifier implements a complete test on any supplied labeled
graph.  For a chamber pair $u,v$, selection variables $z_d$ choose exactly
nine regions in $E_{uv}$, with binary clauses excluding comparable pairs.
Cut variables $y_x$ satisfy $y_u=0,y_v=1$.  For every graph edge $ab$,
put

\[
 L_{ab}=\{d\in E_{uv}:d\notin T(a)\text{ or }d\notin T(b)\}.
\]

The two clauses

\[
 (y_a\vee\neg y_b\vee\bigvee_{d\in L_{ab}}z_d),\qquad
 (\neg y_a\vee y_b\vee\bigvee_{d\in L_{ab}}z_d)       \tag{6}
\]

say that an edge crossing the cut has an endpoint removed by a selected
region.  The CNF is satisfiable exactly when a proper nine-antichain common to
$u,v$ disconnects them.  The internal solver returns `UNKNOWN`, never
`UNSAT`, if a requested node limit is reached, and every SAT result is checked
again by direct induced-graph connectivity.

Indeed, if the clauses hold and an edge with both endpoints retained crossed
the cut, none of its missing-label literals would be selected, contradicting
(6).  Hence retained vertices on the two sides cannot be adjacent, while
$u,v$ are retained and lie on opposite sides.  Conversely, from a disconnected
induced support graph, put the component of $u$ on one side and the component
of $v$ on the other.  Every crossing original edge has a removed endpoint, so
some selected region supplies a true missing-label literal in (6).  The
exact-nine counter and comparability clauses provide the remaining conditions.

Run its exact positive and negative controls with:

```console
python ai/omreal/DIAG9_GRAPH_cut_sat.py
```

The optional tree-verifier file interface is
`diag9-labeled-master-tree-v1`, with arrays `edge`, `support`, and `tree_edge`.
The complete cut-SAT verifier also accepts `diag9-labeled-master-graph-v1`,
which needs only `edge` and `support`.  Passing either finite test proves its
labeled-graph statement conditional on items 1--4.  Both intentionally print
that geometric coverage remains a trust boundary; a sampled graph must not be
relabeled a ninth-diagonal proof.

## 6. Strongest safe next computation

The right order is now:

1. build and certify one complete master roadmap for the smallest parent
   cell, not parent 2599;
2. quotient equal support rows and derive the inclusion poset by (1);
3. search for a sharp tree certificate using $E_{uv}$, never $C_e$;
4. if no tree passes, run the complete cut-SAT test from
   `NINTH_DIAGONAL_SAFE_GRAPH.md` and require an independently checkable
   UNSAT proof;
5. use reorientation/isomorphism transport only after one labeled parent
   calculation is exact.

Without the roadmap/coverage layer, no graph or SAT result over the current
sample files can prove or disprove the ninth diagonal for all 2,604 parents.

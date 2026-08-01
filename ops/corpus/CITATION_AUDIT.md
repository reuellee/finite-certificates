# Citation and attribution audit

Every claim of the form *"X proved P"*, *"P is due to Y"*, *"we could not
find P in print"* or *"this is new"* in

* `ai/maxout/paper/maxout35note.tex`
* `ai/omgamma/paper/omgamma-note.tex`
* `ai/maxout/capstone/CAPSTONE.md`
* `ai/omgamma/OMGAMMA.md`

checked against the indexed literature corpus (`ops/corpus/CORPUS.md`).
Run 2026-08-01.

**Method, and why it is not just `--answer`.** For each claim the corpus was
searched with `research_search.py --query` to find the source, and then the
**document itself was opened** in `ops/corpus/out/docs/<doc_id>.txt` and the
sentence quoted. No verdict below rests on a generated answer, and no number
below came from one. This discipline is not optional: §6.4 of `CORPUS.md`
records the corpus fabricating a table value with full confidence, and the
re-test in §6.7 shows one half of that failure mode still alive.

**Standing caveat on novelty — read before the table.** A 1,900-document
index can *contradict* "this is new"; it can never *verify* it. Absence from
this corpus is not absence from the literature: the index has no 2026 arXiv
listings, no citation graph, and no paywalled journals. Every novelty claim
below is therefore **NOT-IN-CORPUS**, never VERIFIED, and that verdict means
only "nothing here contradicts it".

**Verdict key**

| verdict | meaning |
|---|---|
| VERIFIED | the cited source, opened and quoted, says what we say it says |
| CONTRADICTED | the source, opened and quoted, says otherwise. **Act on these.** |
| PARTIAL | substance right, wording or locator imprecise enough to draw a referee |
| NOT-IN-CORPUS | the source is not indexed (usually a book), or the claim is about absence |

**Totals over 73 checked claims: 2 CONTRADICTED, 52 VERIFIED, 7 PARTIAL,
12 NOT-IN-CORPUS.**

---

## 1. CONTRADICTED — the two that matter

### C1. `ai/omgamma/OMGAMMA.md` §4, lines 262–266 — "'induced' is verbatim in all three"

> **Our claim.** "The zbMATH review of that paper states verbatim that *'if
> G^{n,r}_real is a subgraph of G^{n,r} **induced** by the set of representable
> oriented matroids, then it is shown that G^{n,r}_real is connected'*; DS4 v4
> (2024) §3.7.1 and Curto et al. (arXiv:2008.01032) say the same, and
> **'induced' is verbatim in all three** — which is exactly the
> every-intermediate-OM-is-realizable reading the corollary needs."

**Verdict: CONTRADICTED on the "all three".** Curto, Langdon and Morrison do
*not* use the word. Their sentence (`arxiv_2008_01032`, §4, opened and read in
full) is:

> "This definition is motivated by [7] and the mutation graph
> $\mathcal{G}^{k,n}_{real}$ of all chirotopes arising from arrangements of $k$
> hyperplanes in $\mathbb{R}^{n}$. **The following lemma is an analogue of a
> result from [7] stating that $\mathcal{G}^{k,r}_{real}$ is connected.**"

with `[7] = J.-P. Roudneff and B. Sturmfels, Simplicial cells in arrangements
and mutations of oriented matroids, Geometriae Dedicata 27(2):153–170, 1988`.
Mechanically: the string `induced subgraph` occurs **0 times** in that paper,
and the string `representable` occurs **0 times**; all ten occurrences of
`induced` are "the cell decomposition **induced by** $\chi$", an unrelated use.

**What survives.** Two of the three legs stand, and the *substance* of the
correction is untouched:

* DS4 v4 (`ejc_ds4_oriented_matroids_today_2024`), §3.7.1, verbatim:
  > "Cordovil and Las Vergnas [RS88] conjectured further that for all $r,n$ the
  > mutation graph **on the set of uniform oriented matroids on elements $E$**
  > and rank $r$ is connected. … Also, in all ranks the **induced subgraph
  > defined by realizable uniform oriented matroids is connected [RS88]**."
* Curto et al. attribute realizable connectivity to RS88 and state it for
  $\mathcal{G}^{k,r}_{real}$, "all chirotopes arising from arrangements of $k$
  hyperplanes" — a **labelled** object, so it supports the labelled reading in
  substance while not supplying the word.

**Fix.** Replace "'induced' is verbatim in all three" with "'induced subgraph'
is verbatim in the zbMATH review and in DS4 v4 §3.7.1; Curto et al. state the
same result for $\mathcal{G}^{k,r}_{real}$ without that word." Nothing else in
§4 changes. Note the corpus now makes this correction **first-hand for DS4**
rather than second-hand — which is a strict improvement on the §4 caveat that
"what we actually have is a review's verbatim sentence plus two secondary
restatements".

---

### C2. `ai/maxout/paper/maxout35note.tex` lines 59–60 — `\cite[\S 6]{BCLS}` for the term *zonoboxtope*

> **Our claim.** "The first interesting class beyond zonotopes is the class of
> polytopes of type $(d,n,1)$, called *$(d,n)$-zonoboxtopes* in
> \cite[\S 6]{BCLS}"

**Verdict: CONTRADICTED — the term is defined in §2, not §6.** In
`arxiv_2509_21286` (arXiv HTML, so section boundaries are explicit) §2 "From
Networks to Polytopes" runs to character offset 18621, where §3 "Boxtopes"
begins. The definition sits at offset **17300**, inside §2:

> "More generally, maxout polytopes of type $(d,n,1)$ are called
> $(d,n)$-**zonoboxtopes**."

as does the *candidate* definition, at offset 18155, still inside §2:

> "A $(d,n)$-**zonoboxtope candidate** is a convex hull of two zonotopes in
> $\mathbb{R}^{d}$, each with $n$ generators, where corresponding generators
> are parallel."

**The charitable reading, stated so the row defends itself.** §6 does open
with "Recall that a $(d,n)$-zonoboxtope $Q$ is a maxout polytope of type
$(d,n,1)$", so a reader who follows `\S 6` finds the same equivalence
asserted there and is not misled about the mathematics. What is wrong is the
locator as a *provenance* claim: the sentence reads "called
$(d,n)$-zonoboxtopes **in** \cite[\S 6]{BCLS}", which points at where the
name is given, and that is §2. The candidate family — which the note leans on
for its Remark 6.7 extension (V5) and which CAPSTONE.md restates (V15) — is
likewise defined in §2 and nowhere in §6.

**Fix.** `\cite[\S 2]{BCLS}`, or "called $(d,n)$-zonoboxtopes in \cite{BCLS}"
with no locator. (Every other BCLS locator in the note and in CAPSTONE.md is
correct; see §3 below — Proposition 6.5, Conjecture 6.6, Remark 6.7,
Proposition 6.3, Theorem 5.5 and §§5–6 all check out.)

---

## 2. PARTIAL — substance right, wording or locator loose

| # | location | claim | why it is only PARTIAL |
|---|---|---|---|
| P1 | `omgamma-note.tex` L116–117 | "it is the case Knauer and Marc identify as **beyond reach**" (of $(9,4)$) | KM computed $\underline{\mathcal G}^{9,4}$. Their words are "The computationally most demanding task was the graph $\underline{\mathcal{G}}^{9,4}$ where efficient graph representation was needed" — demanding, and done. What they put beyond reach is the *labelled* graph in general: "Checking connectivity of $\overline{\mathcal{G}}^{n,r}$ is far more demanding. We do not know anything about the connectivity of this graph beyond rank 3." The abstract's own phrasing, "the case they single out as hardest" (L43), is **VERIFIED** and is the wording L116 should match. |
| P2 | `omgamma-note.tex` L130 | `\cite[Table]{FMM13}` prints 9,276,601 | No table number. It is **Table 1** (LaTeX label `existing1`), row $r=4$, column $n=9$, and the same value is printed again at $r=5,n=9$. Cite `[Table 1]`. |
| P3 | `OMGAMMA.md` L57–59 | "plus an **unpublished** computation that $\underline{\mathcal{G}}^{n,r}$ is connected" | The computation *is* reported in the published paper: "We verified computationally that for all the parameters from Table 1 where the isomorphism classes of OMs are known, their mutation graph $\underline{\mathcal{G}}^{n,r}$ is connected. … We calculated the isomorphism class of the mutated graphs using the software Bliss [28]". What is unpublished is the code and data — no availability statement, repository URL or DOI appears anywhere in the paper (checked: `github`, `zenodo`, `available`, `supplementary`, `source code` all absent). `omgamma-note.tex` L660–664 gets this exactly right; `OMGAMMA.md` should adopt its wording. |
| P4 | `OMGAMMA.md` L38–43; `omgamma-note.tex` L78–84 | Γ̂ = $\underline{\mathcal{G}}$ = orbits under $\{\pm1\}^n\rtimes S_n$ | KM define $\underline{\mathcal{G}}$ by **graph** isomorphism — "vertices are graph isomorphism classes of UOMs of rank $r$ and isometric dimension $n$" — and explicitly contrast it with OM-isomorphism: "Testing graph isomorphism instead of OM-isomorphism was an essential ingredient in order to obtain Corollary 3.4." The identification with the hyperoctahedral quotient is true (an isometric embedding of a partial cube into $Q_n$ is unique up to $\mathrm{Aut}(Q_n)$) but is asserted in our files, not argued. It is load-bearing for "Our $\Gm$ results for $n\le 9$ reprove theirs". Worth one sentence. |
| P5 | `CAPSTONE.md` L6–8 | "Conjecture **6.6.1** of arXiv:2509.21286" | The paper has "Conjecture 6.6." with parts numbered 1., 2., 3. There is no label "6.6.1". `maxout35note.tex` L75 says "Part 1 of \cite[Conjecture 6.6]{BCLS}", which is right; CAPSTONE should match. |
| P6 | `OMGAMMA.md` L399 | "K–M cite Ex. 7.9 for the CLV statement" | KM cite it for the *duality-closedness* of the conjecture: "the fact that Conjecture 3 is closed under duality, see [7, Exercise 7.9]". The sentence it sits in is about duality, so the sense is right, but "for the CLV statement" reads as if Ex. 7.9 were the source of the conjecture. |
| P7 | `omgamma-note.tex` L124–131 (Thm ~2) | "isomorphism classes … 9,276,595 … [FMM13] print 9,276,601, which is six too many" | FMM13's Table 1 caption describes its entries as "**reorientation class**, the numbers enclosed by brackets are those of uniform oriented matroids", while Finschi's page says "**isomorphism classes**". Read literally the two count different objects and "six too many" would compare unlike things. The comparison is in fact sound — DS4 calls Finschi's 312,356 "**unlabeled** reorientation classes of uniform oriented matroids of rank 3 on 10 points", i.e. isomorphism classes, and all other cells agree exactly — but the note does not address the nomenclature and a referee will. One footnote closes it. |

---

## 3. VERIFIED

### 3.1 `ai/maxout/paper/maxout35note.tex` — all against `arxiv_2509_21286`

| # | line | claim | evidence (quoted from the opened document) |
|---|---|---|---|
| V1 | 31–33, 70–72 | `[BCLS, Proposition 6.5]` states $(3,n)$-zonoboxtopes have at most $16,26,44,60$ vertices for $n=3,4,5,6$ **and that these bounds are tight** | "**Proposition 6.5.** A $(3,n)$-zonoboxtope has at most $16,26,44,60$ vertices for $n=3,4,5,6$. These bounds are tight." |
| V2 | 73–75 | the upper bounds proven by "a depth-first search over valid bicolorings, performed for each combinatorial type of three-dimensional zonotope; the tightness by extremal examples found by sampling" | "For each type $Z$, we perform a **depth-first search** that finds a valid bicoloring of $G(Z^{\ast})$ … Taking the maximum over all combinatorial types … We prove that this bound is tight by exhibiting extremal zonoboxtopes. These were found by **sampling** …" (and later "$1000$ samples for each $n=3,4,5,6$") |
| V3 | 75–82 | Part 1 of `[BCLS, Conjecture 6.6]` proposes $4\sum_{k=0}^{2}\binom{n-1}{k}$ for odd $n$, $-(n-2)$ for even | "**Conjecture 6.6.** 1. The maximal number of vertices of a $(3,n,1)$-maxout polytope equals $4\sum_{k=0}^{2}\binom{n-1}{k}$ if $n$ is odd, and $4\sum_{k=0}^{2}\binom{n-1}{k}-(n-2)$ if $n$ is even." |
| V4 | 82 | "which equals 44 at $n=5$" | $4(\binom40+\binom41+\binom42)=4\cdot 11=44$, arithmetic on the verbatim formula |
| V5 | 100–104 | "Following `[BCLS, Remark 6.7]`, our upper bound is proven for the wider family of *zonoboxtope candidates*" | "**Remark 6.7.** All results and conjectures in this section are valid not just for zonoboxtopes, but for all zonoboxtope candidates. The distinction from Section 4 does not matter here." |
| V6 | 55–57 | "Maxout polytopes were introduced by Balakin, Cox, Loho, and Sturmfels as the polytopes computed by feedforward neural networks with maxout activation and nonnegative weights after the first layer" | abstract: "Maxout polytopes are defined by feedforward neural networks with maxout activation function and non-negative weights after the first layer." Authors confirmed: Andrei Balakin; Shelby Cox; Georg Loho; Bernd Sturmfels, 2025. |
| V7 | 184–186 | "the even-$n$ value 110 of `[BCLS, Conjecture 6.6]` is attained at $n=8$" | $n=8$ even: $4(1+7+21)-6=110$, from the verbatim formula of V3 |
| V8 | 186–188 | "the case $(4,6)$ … the maximum there is exactly 104, since 104 equals twice the maximal vertex number of a 4-dimensional zonotope with 6 generic generators" | Conjecture 6.6 part 2, verbatim: "For $4\leq d\leq n$, the maximal number of vertices of a $(d,n,1)$-maxout polytope equals $4\sum_{k=0}^{d-1}\binom{n-1}{k}$"; at $d=4,n=6$ that is $4\cdot 26=104=2\cdot(2\cdot 26/2)$, i.e. twice the standard zonotope maximum $2\sum_{k=0}^{3}\binom5k=52$ |
| V9 | 190–191 | "conjectured maxima: 60 and 88" for $(4,5)$ and $(3,7)$ | part 2 at $d=4,n=5$: $4\cdot 15=60$; part 1 at odd $n=7$: $4\cdot 22=88$ |
| V10 | 220–221 | "specializing the framework of `[BCLS, §§5–6]` to two normally equivalent zonotopes" | §5 is "Separating hypersurfaces" (Theorem 5.5), §6 is "Constructing extremal maxout polytopes" (Proposition 6.3, Corollary 6.4, Proposition 6.5) — the chamber/bicoloring machinery is exactly there |
| V11 | 88–91 | "the upper bound 44 … is correct but not attained: its tightness assertion fails at $n=5$" — i.e. that BCLS *assert* tightness | same quote as V1: "These bounds are tight." The assertion is in the statement of Prop 6.5, not only in its proof. |
| V12 | 480–484 | bibliography: Balakin, Cox, Loho, Sturmfels, *Maxout polytopes*, preprint 2025, arXiv:2509.21286 | title, authors, year and identifier all match the indexed record |

### 3.2 `ai/maxout/capstone/CAPSTONE.md`

| # | line | claim | evidence |
|---|---|---|---|
| V13 | 33–35 | "the chamber model gives $f_0(Q)$ = #chambers + #bicolored … (the paper's **Prop 6.3/Thm 5.5** specialized)" | "**Proposition 6.3.** … (1) The number of vertices of $\operatorname{conv}(P_1\cup P_2)$ is equal to the number of vertices of $P$ plus the number of bicolored facets of $G(P^{\ast})$ …"; its proof opens "By **Theorem 5.5**, each cone of $\mathcal{N}$ is refined into at most two cones in $\mathcal{M}$." Both locators correct. |
| V14 | 6–8 | "the tightness assertion of its Proposition 6.5 fails at $n=5$" | as V1 |
| V15 | 239–241 | "the paper's wider family of *zonoboxtope candidates* (two zonotopes with correspondingly parallel generators and independent translations, cf. its Remark 6.7)" | definition verbatim (see C2) and Remark 6.7 verbatim (see V5); "cf." is the right connective here |

### 3.3 `ai/omgamma/paper/omgamma-note.tex` — against `arxiv_2002_11403`, `local_fmm13_om_classification`, `local_finschi_om_49`

| # | line | claim | evidence |
|---|---|---|---|
| V16 | 74 | "the conjecture is recorded in \cite{RS88}" | KM: "A much stronger affirmation appears in [50]: **Conjecture 3 (Cordovil-Las Vergnas).** For all $r,n$ the graph $\mathcal{G}^{n,r}$ is connected." with `[50] J.-P. Roudneff and B. Sturmfels, Simplicial cells in arrangements and mutations of oriented matroids., Geom. Dedicata, 27 (1988), pp. 153–170.` DS4 independently: "Cordovil and Las Vergnas [RS88] conjectured further that …" |
| V17 | 74–84 | "Knauer and Marc observe that the statement depends on which objects one takes as vertices, and separate three graphs" $\overline{\mathcal G},\mathcal G,\underline{\mathcal G}$ | KM: "one can consider a mutation graph whose vertices are UOMs embedded into $Q_n$ … In fact, one can consider **three mutation graphs** corresponding to the different …" and the three verbatim definitions quoted in `OMGAMMA.md` §1 |
| V18 | 86 | "Knauer and Marc state the Cordovil–Las Vergnas conjecture at the middle level" | Conjecture 3 is stated for $\mathcal{G}^{n,r}$, whose vertices KM define as "reorientation classes of UOMs" |
| V19 | 86–89, 108, 350, 369 | "$\overline{\mathcal{G}}^{n,3}$ is connected for every $n$ \cite[Prop.~3.2]{KM23}" | **"Proposition 3.2. For every $n$ the graph $\overline{\mathcal{G}}^{n,3}$ is connected."** The published number is confirmed; this closes the caveat in `OMGAMMA.md` §1 that "the published numbering was not checked against the paywalled version" (the arXiv v3 HTML resolves all cross-references). |
| V20 | 88 | "via Ringel's homotopy theorem together with an explicit reorientation gadget" | proof of Prop 3.2: "We now use the proof of **Ringel's Homotopy Theorem** [48, 49] as shown in [7, Section 6.4] … So to prove that $\overline{\mathcal{G}}^{n,3}$ is connected we only need to consider the case where $\mathcal{M}$ and $\mathcal{M}'$ differ in the **reorientation of one element** $e$" |
| V21 | 89–90 | "they deduce $\mathcal{G}^{n,r}$ connected for $n\le 9$ from a computation that $\underline{\mathcal{G}}^{n,r}$ is connected in that range" | "**Proposition 3.3.** If $\underline{\mathcal{G}}^{n,r}$ is connected, then $\mathcal{G}^{n,r}$ is connected." → "We verified computationally that for all the parameters from Table 1 … their mutation graph $\underline{\mathcal{G}}^{n,r}$ is connected." → "**Corollary 3.4.** The graph $\mathcal{G}^{n,r}$ is connected for $n\leq 9$." |
| V22 | 91–95 | the three quotations ("is far more demanding"; "do not know anything about the connectivity of this graph beyond rank 3"; "suspect the existence of a counter example at least in the setting of $\overline{\mathcal{G}}^{n,r}$") | verbatim: "Checking connectivity of $\overline{\mathcal{G}}^{n,r}$ is far more demanding. We do not know anything about the connectivity of this graph beyond rank $3$, see Proposition 3.2." and, in Conclusions: "We have verified it by computer for small examples and it holds for low rank in general. However, here we suspect the existence of a counter example at least in the setting of $\overline{\mathcal{G}}^{n,r}$." |
| V23 | 43 | "among them the case they single out as hardest" | "The computationally most demanding task was the graph $\underline{\mathcal{G}}^{9,4}$ where efficient graph representation was needed." |
| V24 | 128–130 | "This value [9,276,595] appears in Finschi's database and in \cite[Table 1]{KM23}" | Finschi (`local_finschi_om_49`, re-extracted with the table fix): `[TABLE 3 ROW 4] rank = 4 (dim = 3) || … || card = 9 [col 9]: 9 276 595 || card = 10 [col 10]: unknown`, under the heading "the number of **non-degenerate (uniform) isomorphism classes** of oriented matroids". KM Table 1 ("Known orders of $\underline{\mathcal{G}}^{n,r}$, retrieved from http://www.om.math.ethz.ch/"): row 4, column 9 → `9276595`. |
| V25 | 130–131 | "Fukuda, Miyata and Moriyama print 9,276,601" | FMM13 Table 1: `r = 4 || … || n = 9 [col 8]: unknown / (9,276,601)`, and again at `r = 5 … n = 9`. Caption: "the numbers enclosed by brackets are those of uniform oriented matroids". |
| V26 | 155–158 | erratum: "\cite[Table 1]{KM23} lists 482 classes at $(n,r)=(9,3)$. The correct value is 4382, as its own dual entry at $(9,6)$, Finschi's database, \cite{FMM13} and our independent generation all agree." | KM Table 1 verbatim rows: row 3 → `col 9: 482`, `col 10: 312356`; row 6 → `col 9: 4382`. Finschi: `rank = 3 … card = 9 [col 9]: 4 382`. FMM13 Table 1: `r = 3 … n = 9 [col 8]: 461,053 / (4,382)`. **All four cross-checks confirmed, in the sources, cell by cell.** |
| V27 | 658–659 | "Their rank-3 theorem $\overline{\mathcal{G}}^{n,3}$ is theirs and is used here" | as V19 |
| V28 | 660–664 | "their connectivity computation — published in \cite{KM23}, with its method described there — is reported without publicly archived code, data or certificates" | method described (V21, Bliss); and the paper carries no data-availability statement, repository URL or DOI for artifacts — `github`, `zenodo`, `available`, `supplementary`, `source code`, `implementation` all absent from the full text |
| V29 | 665–666 | "Their suspicion of a labelled counterexample … is refuted in the range $n\le 9$, which is where they had verified the other two levels" | Corollary 3.4 covers $n\le9$ at the $\mathcal{G}$ level, via $\underline{\mathcal{G}}$; the suspicion is at the $\overline{\mathcal{G}}$ level (V22). The three levels and their ranges line up exactly as stated. |
| V30 | 691–693 | bibliography: Knauer, Marc, *Corners and simpliciality…*, European J. Combin. **112** (2023), 103714 | independently confirmed by a third party in the corpus: `arxiv_2501_12951` (Wilhelmi 2025) cites "Kolja Knauer and Tilen Marc. Corners and simpliciality in oriented matroids and partial cubes. European Journal of Combinatorics, 112:103714, 2023." |
| V31 | 687–690 | bibliography: Fukuda, Miyata, Moriyama, Discrete Comput. Geom. **49** (2013), 359–381, arXiv:1204.0645 | matches the indexed record `arxiv_1204_0645` / `local_fmm13_om_classification` |
| V32 | 694–696 | bibliography: Roudneff, Sturmfels, *Simplicial cells in arrangements and mutations of oriented matroids*, Geom. Dedicata **27** (1988), 153–170 | KM reference [50] and Curto et al. reference [7], independently, give exactly this (volume, year, page range) |
| V33 | 684–686 | bibliography: Finschi's catalog, "(uniform rank-4 classes on 9 elements computed by S. Moriyama, December 2010)" | Finschi's changelog verbatim (`local_finschi_om_catalog_index`): "**2010 December 21**: Added the classes of uniform oriented matroids of 9 elements and rank 4 computed by **Sonoko Moriyama** (University of Tokyo) using Lukas Finschi's code." |

### 3.4 `ai/omgamma/OMGAMMA.md`

| # | line | claim | evidence |
|---|---|---|---|
| V34 | 26–36 | the three graph definitions, quoted verbatim from the KM source | reproduced in `arxiv_2002_11403` word for word, including "isometric dimension $n$, embedded into $Q_n$" and "graph isomorphism classes" |
| V35 | 45–52 | "The Cordovil–Las Vergnas conjecture, as Knauer–Marc state it … citing Roudneff–Sturmfels 1988" | as V16 |
| V36 | 53–57 | "Knauer–Marc *settled it* for $n\le9$ (their corollary labeled cor:94)" and "their proposition labeled prop:mut … using Roudneff–Sturmfels' realizable connectivity" | `cor:94` = **Corollary 3.4**; `prop:mut` = **Proposition 3.3**, whose proof reads: "Since by [50] the induced subgraph of all realizable classes in $\mathcal{G}^{n,r}$ is connected, this proves that $\mathcal{G}^{n,r}$ is connected." The published numbers can now replace the source labels. |
| V37 | 59 | "(using tope graphs + the Bliss graph-iso package)" | "This was possible by considering UOMs as (tope)graphs in which finding possible mutations is easy … We calculated the isomorphism class of the mutated graphs using the software **Bliss** [28]" |
| V38 | 62–72 | the two block quotations | verbatim, as V22 |
| V39 | 83–84 | "their proposition labeled prop:pseudoline proves $\overline{\mathcal{G}}^{n,3}$ connected for every $n$ via Ringel's homotopy theorem plus an explicit reorientation gadget" | `prop:pseudoline` = **Proposition 3.2**, as V19/V20 |
| V40 | 85–87 | "Observation ('obs:connectivities'): $\overline{\mathcal{G}}$ connected ⟹ $\mathcal{G}$ connected ⟹ $\underline{\mathcal{G}}$ connected" | "the connectivity of $\overline{\mathcal{G}}^{n,r}$ implies the connectivity of $\mathcal{G}^{n,r}$ and the connectivity of $\mathcal{G}^{n,r}$ implies that $\underline{\mathcal{G}}^{n,r}$ is connected. (**Observation 3.1**)" |
| V41 | 74–80 | the corrected mission: the suspected counterexample lives at the **labelled** level | as V22. This is attribution error (c) and the corrected version is right. |
| V42 | 89–95 | erratum "482 → 4382" and its four cross-checks | as V26 |
| V43 | 115–118 | "Equivalence with Knauer–Marc's tope-graph definition (fill/remove a vertex of a $Q_r^-$ at a simplicial tope)" | "If $v$ is a simplicial vertex in a UOM $G$ of rank $r$, then $v$ is contained in a unique convex **hypercube minus a vertex**, let us denote it by $Q^{-}_{r}$. If one **fills in the missing vertex** of $Q^{-}_{r}$ and instead **removes** $v$ and does the same to the antipodes … This operation is called a **mutation**." |
| V44 | 258–273 | "the labeled-level statement IS in print, in Roudneff–Sturmfels 1988 itself … credit belongs to Roudneff and Sturmfels" — attribution error (b), corrected | DS4 v4 §3.7.1 verbatim (quoted in full under C1). **This is now first-hand corpus evidence for the correction, not a review sentence.** DS4 states both the CLV conjecture and the RS88 realizable-connectivity result on "the mutation graph on the set of uniform oriented matroids on elements $E$" — the labelled object. |
| V45 | 265 | "DS4 v4 (2024) **§3.7.1**" | the passage sits in §3.7.1 ("Topes"); DS4 also cross-references it as "connected under performing mutations, see **Subsection 3.7.1**". Locator correct. |
| V46 | 269–273 | "Knauer–Marc quote a reorientation-class weakening because they redefined the symbol, which is why the labeled statement looked absent" | exactly borne out: KM's Prop 3.3 proof says "the induced subgraph of all realizable classes in $\mathcal{G}^{n,r}$", with $\mathcal{G}$ = reorientation classes, while DS4 states the same RS88 result on the labelled set. Two published sources, two levels, same citation. |
| V47 | 322–326 | catalog table: $(3,5..9)$ = 1, 4, 11, 135, **4382**; $(4,5..8)$ = 1, 1, 11, **2628**, "same" as published | Finschi rank 3: `card = 5:1, 6:4, 7:11, 8:135, 9:4 382`; rank 4: `card = 5:1, 6:1, 7:11, 8:2 628`. FMM13 Table 1 brackets: $r=3$: (1),(4),(11),(135),(4,382); $r=4$: (1),(1),(11),(2,628). KM Table 1 row 3: 1,1,1,4,11,135,482(sic),312356; row 4: …,11,2628,9276595. All three agree except the single KM typo. |
| V48 | 468–472, 1332–1339 | "FMM13's 9,276,601 (DCG 49 (2013), Table '**existing1**', at both (4,9) and (5,9))" | the LaTeX label is carried into the extracted text: `[TABLE 1 CAPTION] The numbers of simple oriented matroids … [label: existing1]`, and 9,276,601 appears at $r=4,n=9$ and $r=5,n=9$ of that table. Locator, label and both cells confirmed. |
| V49 | 1324–1329 | Finschi changelog quotation | verbatim (V33) |
| V50 | 1332–1339 and `CORPUS.md` §6.1 | FMM13 prints the $(4,9)$ **realizable**-uniform cell as "unknown (unknown)" | FMM13 **Table 2** (label `existing1_realizable`, caption "The numbers of simple **realizable** oriented matroids … brackets are those of uniform realizable"): `r = 4 || … n = 9 [col 8]: unknown / (unknown)`. Confirmed — and note this is a *different table* from V25's, which the pre-fix corpus could not distinguish. |
| V51 | 99–102 | "bases = $r$-subsets in **colex order** (Finschi's 'RevLex-Index' order …); his glossary defines the representative as the '**lexicographically maximal chirotope**' over the class" | Finschi's glossary entry *RevLex-Index* (`finschi_glossary_revlex`), verbatim: "The index is based on the representation of oriented matroids by chirotopes, where the **signs of the bases are ordered in reverse lexicographic order**, and the representative is the oriented matroid in the corresponding equivalence class with **lexicographically maximal chirotope**." Reverse lexicographic order on $r$-subsets *is* colex, and the second phrase is verbatim. Both halves confirmed. |
| V52 | 322–333 (and `omgamma-note.tex` Thm ~2) | that Finschi's catalog counts the same objects this project calls Ḡ-orbits (relabelling + reorientation) | Finschi's glossary entry *Isomorphism Class* (`finschi_glossary_isom`): "the equivalence class defined by an **arbitrary combination of relabeling and reorientation** of the elements of the ground set." One caveat, and it resolves in our favour: his *Relabeling Class* entry adds "**and introducing or deleting loops or parallel elements**" — but the catalog tabulates *non-degenerate (uniform)* classes with "card the cardinality of a **simple** representative", and a simple oriented matroid "has no loops and no (distinct) parallel elements", so on the uniform catalog relabelling reduces to permutation and his isomorphism classes are exactly the $\{\pm1\}^n\rtimes S_n$-orbits. |

---

## 4. NOT-IN-CORPUS

These could not be checked here. Listed rather than guessed at.

| # | location | claim | why |
|---|---|---|---|
| N1 | `maxout35note.tex` L296–299 | "That all of them are in fact realizable \cite[Ch.~8]{OMbook}" (the 384 uniform rank-3 chirotopes on 5 elements) | Björner–Las Vergnas–Sturmfels–White–Ziegler, *Oriented Matroids*, CUP 1999 — a book, not indexed. The note already marks it "reassurance, not a step of the proof". |
| N2 | `OMGAMMA.md` L397–399 | duality "standard, [BLSWZ §3.4]" | same book |
| N3 | `OMGAMMA.md` L104–107 | "the 3-term Grassmann–Plücker conditions (CHI2) of Richter-Gebert & Ziegler, *Handbook of Discrete and Computational Geometry* 3rd ed., ch. 6, §6.2.3 — sufficient by their Theorem 6.2.3" | Handbook chapter, not indexed. Corpus has three-term GP relations stated in several papers, none with that numbering. |
| N4 | `OMGAMMA.md` L399 | "K–M cite Ex. 7.9" — i.e. what Exercise 7.9 of BLSWZ says | book |
| N5 | `maxout35note.tex` L253–255 | "Gordan's theorem" | classical; no attributed statement of it in the corpus |
| N6 | `CAPSTONE.md` L347–348 | "independently by Fukuda's cddlib in exact GMP arithmetic" | software attribution, no paper indexed |
| N8 | `OMGAMMA.md` L262–264 | the zbMATH review sentence | zbMATH is paywalled and not indexed; the review itself was never obtainable here |
| N9 | `OMGAMMA.md` L278–289; §4 generally | the primary text of Roudneff–Sturmfels 1988 | paywalled, pre-arXiv. §4 already says so explicitly and forbids citing it by proposition number. That restriction should stand: neither DS4 nor KM nor Curto cites it by number. |
| N10 | `maxout35note.tex` L35–38, 84–86 | **novelty**: "We prove that the maximum at $(3,5)$ is exactly 42" | a corpus cannot verify novelty. Probe: `--query "the maximal number of vertices of a (3,5)-zonoboxtope is 42 not 44 counterexample to the conjecture"` returned BCLS itself, Montúfar et al. (2104.08135), Miyata–Padrol, DS4 — **nothing contradicting**. |
| N11 | `omgamma-note.tex` L39–43, 97 | **novelty**: "the cases genuinely settled here are $(8,4)$, $(9,4)$, $(9,5)$"; "no such counterexample exists below $n=10$" | probe: `--query "connectivity of the mutation graph of labelled uniform oriented matroids of rank 4 on 9 elements"` returned KM23, Wilhelmi 2025 (2501.12951), DS4, Finschi, a cocircuit-diameter survey — **nothing contradicting**. Wilhelmi 2025 is the only post-KM mutation-graph paper indexed and it does not address CLV connectivity at any level (`Cordovil` occurs 0 times in it). |
| N12 | `omgamma-note.tex` L124–127 | **novelty of the count**: "The number of isomorphism classes … is exactly 9,276,595" as a *correction* | the corpus holds both published figures and no third recomputation. `9,276,595` does not appear anywhere in DS4. |
| N13 | `OMGAMMA.md` L1336–1338 | the exact FMM13 sentence "A database of oriented matroids by Finschi and Fukuda [FF] consists of the representatives of the reorientation classes" | not located verbatim in either extraction of FMM13; the adjacent database passage (V49) is present and consistent. Re-check against the published DCG version before quoting it with quotation marks. |

---

## 5. What the audit changed about the corpus itself

Two things this audit could not have done before 2026-08-01, both consequences
of the table-extraction fix (`CORPUS.md` §8):

* **V26 / V47 / V51 / C1** all turn on reading a specific *cell* of a specific
  *table* in a specific *source*. Before the fix the extracted text of
  Finschi's page, KM's Table 1 and FMM13's Tables 1/2/3 was a bare run of
  numbers with the leading blanks dropped, and the corpus had already been
  measured mis-assigning exactly these cells. Every table quotation above is
  reproducible with `grep` against `ops/corpus/out/docs/`.
* **V44** upgrades the highest-stakes correction in the repository — that the
  labelled realizable-connectivity lemma is Roudneff–Sturmfels', not ours —
  from "a zbMATH review sentence plus two secondary restatements" to a
  verbatim quotation from the standard survey, with a document id. And **C1**
  shows the same paragraph overstated what one of those restatements says.

Both are the intended use of the index: it does not decide mathematics, it
puts the primary text in front of you so you stop paraphrasing from memory.

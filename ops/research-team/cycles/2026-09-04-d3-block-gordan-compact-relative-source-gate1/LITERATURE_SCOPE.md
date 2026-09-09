# Primary-source scope check

Status: supporting evidence only; no cited paper is treated as the missing
9DVL theorem.

## Basu--Karisani: efficient simplicial replacement

The locally stored `arxiv-2009.13365v3.pdf` states algorithms for a
`P`-closed semialgebraic formula and for a finite tuple of such formulas,
producing simplicial replacements and compatible subcomplex diagrams through
a chosen homological degree.  This supports the claim that a closed bounded
finite semialgebraic family has an exact algorithmic route to finite homology
data.

It does not by itself identify the 9DVL compactification, distinguish true
parent infinity from seams, preserve the project's full integral labeling, or
prove the desired degree-two boundary is surjective.

## Basu--Karisani: homology functor on maps and diagrams

The locally stored `arxiv-2207.10497v1.pdf` states algorithms computing
homology maps and zigzag diagrams for semialgebraic maps presented by closed
bounded formulas.  This is relevant after the compact relative pairs and
literal subdiagram maps have been proved.

It is not a substitute for the source theorem.  In particular, applying it
before proving exact closure and boundary provenance would repeat the stopped
SREP route's central error.

## Triangulation choice

The candidate proof uses the classical compatible semialgebraic
triangulation theorem for one compact semialgebraic ambient and a finite
family of semialgebraic subsets.  It does not require triangulating the
non-proper projection to the parent as a map.  This avoids assuming that an
arbitrary semialgebraic map is a Thom map.

The exact existence statement needed here is recorded in Masahiro Shiota,
*Whitney triangulations of semialgebraic sets*, Annales Polonici Mathematici
87 (2005), 237--246, DOI `10.4064/ap87-0-20`: a compact semialgebraic set has
a semialgebraic triangulation compatible with any finite prescribed family of
semialgebraic subsets.  Primary-source landing page:
`https://impan.pl/en/publishing-house/journals-and-series/annales-polonici-mathematici/all/87/0/84789/whitney-triangulations-of-semialgebraic-sets`.

Shiota's non-proper semialgebraic Thom-map triangulation theorem is therefore
context rather than a required premise: it has additional closedness and Thom
hypotheses which must not be silently inferred here.  Primary preprint:
`https://arxiv.org/abs/1006.4719`.

## Literature verdict

The literature makes the finite conversion credible once the compact
relative source is correct.  The new research content is the 9DVL-specific
assembly: one component-complete normalized parent compactification, the
extended block-Gordan pair, the simultaneous finite family, and proof that
the resulting filtered relative complex retains labels, strict closure, and
genuine infinity.

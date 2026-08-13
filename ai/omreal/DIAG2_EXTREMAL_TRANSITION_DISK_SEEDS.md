# Diagonal two: exact seed nodes in the parent-187 transition disk

## Result

The complete parent-187 `e`-line transition census has ten residual factors
which change one of the six endpoint records belonging to the three fixed
extremal pairs.  The transition-disk probe selected ten candidate
intersections in the standard `d/e` plane involving six of those ten
factors.  Each candidate is now a certified unique transverse node in a
pinned rational rectangle.

At every node, an exact Sturm count isolates one common root, exact interval
arithmetic excludes a zero of the Jacobian and every other residual factor
throughout the rectangle, and one exact rational point is pinned in each of
the four sign sectors.  The four paired straight segments each cross exactly
one named wall once.  The complete `26,112`-tope table is then reconstructed
in all `40` rational chambers.

Every partner wall is transparent: crossing it changes none of the six
tracked endpoint records.  The tracked transition is identical on both sides
of the partner, and every tracked pair which is simultaneously bad on both
sides retains at least six common directions.  The minimum tracked overlap
remains six.  Thus none of these ten nodes creates zero overlap among the
three tracked pairs.

This is an exact finite seed audit, not coverage of a two-dimensional disk,
not proof that the displayed nodes are the nearest intersections, and not a
proof of diagonal two.  The honest 9DVL score remains `1/9`.

## 1. Pinned node set

Write `x` and `y` for the shifts in the standard `d` and `e` coordinates.
The tracked factor is listed first.

| node | `x` (approx.) | `y` (approx.) | factor types |
|---:|---:|---:|---:|
| 1 | `+1.055352659e-5` | `+0.02164554014` | `10115(51) / 21582(49)` |
| 2 | `-1.362728980e-5` | `-0.0306133442` | `22118(49) / 5849(38)` |
| 3 | `+1.749063675e-5` | `-0.0305671243` | `22118(49) / 7562(51)` |
| 4 | `-2.014729315e-5` | `+0.0128998099` | `23559(50) / 25433(49)` |
| 5 | `+2.348030579e-5` | `-0.0430619524` | `8421(51) / 5326(50)` |
| 6 | `+2.840210356e-5` | `-0.0305509174` | `22118(49) / 12307(49)` |
| 7 | `-3.203636702e-5` | `-0.0672466779` | `13869(50) / 22792(50)` |
| 8 | `-3.955106466e-5` | `+0.0128934540` | `23559(50) / 26286(50)` |
| 9 | `-4.218696268e-5` | `-0.0430202130` | `8421(51) / 16080(51)` |
| 10 | `-4.686387491e-5` | `-0.0200683814` | `23979(50) / 2598(49)` |

These ten nodes cover only factors `10115`, `22118`, `23559`, `8421`,
`13869`, and `23979`; they do not sample the `11045`, `16242`, `19971`, or
`23604` branches.  Matching a factor ID also does not assert continuation to
the same real conic component as its central-line crossing.

The type-`38` partner at node 2 is compound and exchanges ten topes per
side.  All other partner edges exchange two.  Despite that difference, all
ten partner crossings preserve the full separator profiles and masks of the
six tracked signatures.

## 2. Four-sector theorem

For every row, orient the first factor from negative to positive and hold the
partner sign fixed.  Both choices of partner sign give the same exact
transition:

- factor `10115`: pair 3 changes from overlap `9` to a tope endpoint;
- factor `22118`: pair 2 changes `9 -> 15`;
- factor `23559`: pair 3 changes `6 -> 9`;
- factors `8421` and `13869`: one endpoint record changes, but all pair
  observations stay fixed at overlaps `15`, `15`, and a tope endpoint;
- factor `23979`: pair 2 changes `6 -> 9`.

For every tracked pair bad on both sides, the intersection of the incoming
and outgoing common-direction masks is nonempty.  The exact survivor counts
per tracked pair are respectively

```text
(6,6,-), (9,9,-), (9,9,-), (6,6,6), (15,15,-),
(9,9,-), (15,15,-), (6,6,6), (15,15,-), (9,6,12),
```

where `-` denotes a pair with a tope endpoint on at least one side.

## 3. Exact reproduction

Run

```console
python ai/omreal/verify_diag2_extremal_transition_disk_seeds.py --workers 4
```

All rational coordinates are pinned constants; runtime verification uses no
floating-point geometry.  The verifier uses exact resultants and Sturm
sequences to isolate one common root in each rectangle, exact Jacobian
intervals for transversality, interval exclusion for all other `26,738`
residual equations and every parent boundary, and exact univariate root
counts on all forty comparison segments.  It then verifies all factor signs,
reconstructs every complete tope table, rebuilds the six tracked separator
profiles, and pins the semantic result.

The pinned semantic digest is

```text
105f9aae5248889363155ec518c7a54110f06760b724d6ac8188c199f5189aba
```

## 4. Proof boundary and next target

The ten rational rectangles do not cover the region between them and are not
claimed to be the nearest intersections.  In particular, intersections of
two walls which are both transparent on the central line could still create
a relevant outgoing branch elsewhere.  The next proof-producing target is a
complete exact resultant/Sturm census in a declared strip, followed by
closure of the relevant wall branches at every node in that strip.  Only then
can this seed audit be promoted to a bounded transition-disk theorem.

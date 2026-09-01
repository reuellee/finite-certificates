# S12,37 exact recursive-facet normal-link obstruction

## Endpoint

`NORMAL_LINK_REDUCTION_NO_GO` at level **(b)**: an active oriented residual
factor has an exact two-sided wall inside one certified recursive parent-link
stratum. This retires the tangential four-support reduction as stated.

The claim is deliberately local. It is not a strict open-parent crossing, a
collar or mincut, a global diagonal-nine separator, or a theorem-ledger
advance. The honest ledger remains `2/9`.

## Exact obstruction

On support `(3,1,15)`, use the exact face point

```text
(a,b,c,d,e,f,g,h,i) = (3/4,0,0,0,0,0,1/4,2/3,1/4).
```

Factor `8552` has the primitive polynomial

```text
q = d*i - e.
```

Its only labeled occurrence is `(4,9,23,37)`, with no stripped parent unit.
Independent circuit orientation gives the `S12,37` family-allowed side
`q<0`. Since `d=e=0` on the support, `q` vanishes tangentially, but in normal
coordinates `(b,c,d,e,f,delta_i)` its lowest form is

```text
q1 = d/4 - e.
```

Three projectively normalized directions have `q1` values `-29/220`, `0`,
and `1/35`. For all three, the only parent bracket that stays identically
zero is `1237`, equivalently the recursive facet `f=0`; every other
face-vanishing parent bracket has a positive first nonzero coefficient.

At `t=1/100`, exact lifts preserve that same parent stratum: all seventy
signed parent brackets are nonnegative, exactly `1237` is zero, and the
factor values are respectively

```text
-40141/30250000, 0, 8/30625.
```

The zero lift uses `e=d*i` exactly, so higher-order terms do not erase the
displayed wall. The machine-readable rays, lifts, parent-evaluation digests,
attack matrix, source pins, and nonconsequences are in `RESULT.json`.

## Replay

```console
PYTHONDONTWRITEBYTECODE=1 python ops/team/diag9-s1237-normal-link-falsifier/verify_normal_link_falsifier.py
```

The verifier rebuilds the `3,539` family-active orientations independently
from the transported base certificates, replays all seventy parent brackets
with exact rational arithmetic, validates the same-stratum wall, and rejects
hostile mutations. It does not import or reuse constructive-producer
acceptance logic.

# Diagonal eight mask-6 loop: exact nonvacuity gate

## Result

The parent-860 loop `4-11-12-14-13-23-4` is common to eight extension regions
which are globally nonempty, proper, and pairwise incomparable. This removes
the vacuity defect in the earlier 24-chamber local support quotient.

Seven exact rational realizations of catalog parent 860 have the feasibility
words

```text
00110011
11101111
10101110
01011101
11010111
10101001
11110010
```

For every one of the `7*8=56` chart/signature entries, the certificate stores
one exact alternative: a nonzero integer four-vector on which all signed
derived rows are strictly positive, or a positive integer Gordan relation
supported on at most five signed rows. Every column contains both bits, so
each region is nonempty and proper. Every ordered pair of distinct columns
has a word with first bit `1` and second bit `0`; these `56` witnesses disprove
both containments for every unordered pair.

The source repair certificate is byte-pinned and proves all eight signatures
contain every vertex of the loop.

## Nonconsequences

This establishes only the quantifier-valid family for one bounded filling
discriminator. It gives no homology, parent coverage, or diagonal-eight
conclusion by itself.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag8-mask6-nonvacuity/verify_diag8_mask6_nonvacuity.py
```

The verifier reconstructs all parent signs and signed derived rows, checks the
56 exact alternatives and 56 directed noncontainments, and rejects seven
hostile mutations. SciPy and producer decisions are outside its trust boundary.

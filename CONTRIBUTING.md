# Contributing

Contributions are welcome from anyone. You do not need permission to start:
fork the repository, push to your fork, and open a pull request. Merging stays
with the maintainer; the pull request *is* the request.

If you would rather discuss something before writing code — an idea, a target,
a suspected error — open an issue.

## Credit

**Contributors whose work appears in a paper are credited by name in that
paper.** If a contribution materially shapes a result, that means named
acknowledgement (or co-authorship where the contribution is substantial enough
to warrant it — proposing or proving a key step, not fixing a typo). Tell us
in the pull request how you want to be named, or say if you would prefer not
to be credited.

## Licence

Everything here — code, certificates, and the mathematical prose alike — is
under the [MIT Licence](LICENSE), and contributions are accepted on those
terms. (MIT is written for software; it is used here for the whole repository
deliberately, so that there is one permissive licence rather than a split
regime to reason about. Attribution is covered socially by the credit policy
above, not only legally.)

## What this repository is

Every claim here ships with a standalone verifier in exact arithmetic. Floating
point may be used to *search*; it is never used to *justify*. A result is not
"done" because a program printed it — it is done when an independent program,
sharing no code with the one that produced it, re-derives it exactly.

## The bar for a contribution

Whatever you send, the same standard applies to it as to everything already
here:

1. **Exact arithmetic for any claim.** Integers, `fractions.Fraction`, or exact
   symbolic computation. If a search used floating point, the result it found
   must be re-proven exactly before it is serialized.
2. **A verifier, not just an assertion.** New results come with a program that
   checks them from scratch. Prefer the Python standard library; `numpy`,
   `scipy`, and `sympy` are acceptable where they genuinely help. Name it
   `verify_*.py` so `run_all.py` picks it up automatically, and make it exit
   nonzero on failure. (Scripts that are *not* part of the suite — one-off
   searches, helpers that exit nonzero by design — must **not** be named
   `verify_*`; call them `check_*.py` instead.)
3. **Independence where it counts.** A verifier should not import the generator
   whose output it checks.
4. **Controls ("canaries").** Any search or checker should include cases that
   must *fail* — a deliberately impossible instance, a corrupted certificate —
   and it should demonstrably reject them. This convention exists because a
   canary here once caught a sign error in a verifier that had already
   "confirmed" five false results.
5. **Honest scope.** State what is proven, what is searched-but-unproven, and
   what is assumed. A documented limitation is a contribution; an overstated
   claim is a defect.

## Especially welcome

- **Refutations.** If a certificate here is wrong, that is the most valuable
  thing you can send. Include the counterexample and, if you can, the exact
  witness. (Concretely: an explicit 44-vertex (3,5)-zonoboxtope would refute
  `ai/maxout`'s main theorem. It would be checked in seconds and reported.)
- **Independent re-verification** — especially re-implementations that share no
  code with ours, or formalizations (Lean/Coq) of any result here.
- **Extensions**: further cases, tighter bounds, larger sweeps, better
  symmetry reductions.
- **Corrections to the literature record** — with sources.

## Checks

Every pull request runs the verifier suite in CI. You can run the same thing
locally before sending:

```
python run_all.py --fast     # the quick suite (local iteration)
python run_all.py            # everything — this is what CI runs
```

Note that `run_all.py` is not read-only: a few verifiers regenerate the
artifacts they check, so your working tree may show diffs afterwards.

A green run is necessary, not sufficient: results are read by a human too.

## Structured research cycles

The theorem-oriented research program uses the fail-closed control plane in
[`ops/research-team/PROTOCOL.md`](ops/research-team/PROTOCOL.md).  Every new
cycle must compare its target against credible alternatives before work starts,
use bounded independent work orders, and end with an explicit
`CONTINUE`/`PIVOT`/`RETIRE`/`STOP` strategy verdict.  The repository verifier
rejects governed cycles that omit these strategy or publication gates.

## Style

Match the surrounding code. No preference beyond that, and no house formatter.

## Provenance and AI assistance

Much of this repository was produced by AI systems directing exact computation,
under human direction, with adversarial cross-review between models. That is
disclosed in the papers and is not a reason to trust any result less *or more*
— the certificates are the trust boundary, and they are checkable by anyone.

You are welcome to use AI assistance in your contributions. The same rule
applies to you as to us: **no claim rests on unverified model output.** Check
what you send.

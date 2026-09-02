# Exact CAS laptop toolchain

This directory records a reproducible, rootless WSL toolchain acquired for
exact semialgebraic and algebraic research.  The installed prefix on this
machine is:

```text
/home/lee/.local/share/9dvl-exact-cas/v1
```

It contains Singular 4.4.1, Normaliz 3.11.0, 4ti2 1.6.15,
python-flint 0.8.0, and a source build of msolve 0.10.1.  The msolve upstream
test suite passes `64/64`; `smoke_test.sh` separately exercises all five
installed components.

To reproduce in WSL, choose two new absolute paths and run:

```bash
ops/toolchains/exact-cas-laptop/bootstrap_core.sh \
  /absolute/install/prefix /absolute/download/cache
```

The bootstrap verifies pinned downloads, creates the environment from
`conda-linux-64.lock`, builds msolve from source, runs its test suite, and
runs the cross-tool smoke test.  It refuses `/`, relative paths, an existing
non-conda install prefix, and overlapping install/cache targets.

## Acquired CAD material

The ignored `vendor-cache/` holds Matthew Baker's 2025 thesis, the associated
arXiv paper, and the exact Zenodo software archive listed in
`SOURCE_MANIFEST.json`.  That archive contains the QEPCAD git history and the
`origin/working` frontier/monotone development head `c31179d`.

This is useful source material and may support low-dimensional
frontier-compatible CAD experiments.  It is **not** an implementation of the
Basu--Karisani low-degree simplicial-replacement algorithm, does not emit the
cycle's labelled formula-diagram comparison certificate, and does not justify
the old direct-master-CAD route.  A local attempt to build the development
branch stopped at a missing `/bin/csh` prerequisite; no build result from
that branch is accepted or required by this toolchain.

## Scope

These tools are algebraic primitives, not theorem or topology certificates.
Every research result must pin its input, command, exact output, semantic
checks, and an independent verifier.  The ignored vendor cache and installed
WSL prefix are reproducible scratch, never canonical evidence by themselves.


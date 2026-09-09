# Collision-removal diagnostic and CUDA assessment

9 September 2026. Base: frozen PR49 revision
`59fec66666518257c585194b81061f60d91f439d`.

**The deletion removes the abstract kernel, but also destroys a required
lower vanishing assumption. Original injectivity remains open; the theorem
ledger stays 2/9.** Independent review accepted this bounded conclusion;
both separately implemented checkers passed a clean replay.

## What was tested

The previous abstract example has the coordinate rows e1,e2,e3,e4 and
three moving rows

\[
(u,-1,h,h),\quad(v,-1,-h,h),\quad(-u-v,-1,h,-h),
\qquad h=1-\|y\|^2,\ y\in\mathbb R^7.
\]

The experiment removes every point where any two distinct rows are
proportional. Checking only collisions between the three moving rows would
miss collisions with e2. The complete deleted locus is

\[
Z=\{h=0,\;uv(u+v)(u-v)(2u+v)(u+2v)=0\}.
\]

This is six plane lines times the transverse sphere S6. All original bad
loci lie over the closed ball D7. Only the specified portions of its boundary
are removed; replacing the whole ball by an open ball is a different problem.
The remaining matrix has no zero or proportional distinct rows and still has
rank four. It is still an abstract matrix, with no realization as the original
56 derived normals certified.

## Low-degree result

The following entries are dimensions over Q; all stated Hc0 groups vanish.

| Space | Hc1 before | Hc1 after | Hc2 before | Hc2 after |
|---|---:|---:|---:|---:|
| Each singleton bad locus | 0 | 0 | 0 | 8 |
| Each pair intersection | 1 | 0 | 0 | 4 |
| Triple intersection | 2 | 0 | 0 | 0 |

The old alternating map had a one-dimensional kernel. The new degree-one
map is the zero-dimensional map 0 to 0 and is injective. This removes the
old kernel by also eliminating its source and target groups.

The compact-support calculation includes the new ends introduced by
deletion. The deleted portion of a singleton, pair, or triple is a star
with respectively 9, 6, or 3 rays, times S6. Its Hc1 has dimension 8, 5,
or 2. The closed/open exact sequence contains

\[
0\to H_c^1(A\setminus Z)\to H_c^1(A)
\to H_c^1(A\cap Z)\to H_c^2(A\setminus Z)
\to H_c^2(A)=0.
\]

The middle restriction is injective, with rank 0, 1, or 2 respectively.
This yields the displayed dimensions. A separate finite product-cell
calculation checks the deletion boundary directly.

The required singleton Hc2 vanishing has therefore failed. This experiment
does not establish that normal separation suffices for injectivity under
the original assumptions. It also supplies no counterexample to that
claim. A future construction must satisfy the original shared-column
geometry and all lower assumptions together, with a proved comparison
of its global compact-support maps.

## CUDA relevance

This calculation has no demonstrated GPU bottleneck. Each current checker
replayed here in approximately 0.03 seconds including Python startup; the
producer's internal calculation took about 0.009 seconds in the clean replay.
The largest relative complex has 34 cells. These are local observations,
not a laptop comparison or a GPU speedup measurement. This session has no exposed
NVIDIA device, and no CUDA program was run.

Useful candidates for a future larger search are batched parent determinants,
derived-normal generation, feasibility-margin evaluation, and independent
candidate circuit searches. Exact modular linear algebra could also be
useful if large integer cochain matrices arise. GPU integer arithmetic can
be exact with correct overflow handling; existing Python rational code
does not automatically run on CUDA.

The proposed workflow is batched GPU discovery followed by exact certificate
verification. Floating-point tolerances cannot certify exact collisions,
signs near zero, or exhaustive coverage. No speedup is claimed before a
realistic end-to-end benchmark on the laptop. See `CUDA_ASSESSMENT.md` for
the workload and memory estimates and
[NVIDIA's performance guidance](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html)
and [floating-point guidance](https://docs.nvidia.com/cuda/floating-point/index.html).

## Evidence and scope

The diagnostic and referee use separately implemented exact checks. The
verdict is `ACCEPT_ABSTRACT_FULL_COLLISION_DELETION_ONLY`. Clean replay
matched every result field, excluding only the producer's observational
elapsed-time field. Three hostile boundary controls distinguish omitted
coordinate-row collisions, reuse of the old boundary, and an incorrectly
opened whole ball. The checkpoint contains the proofs, replay programs,
results, source hashes, and previous frozen source subset. Original source records removed: 0.
Original obligations closed: 0. No global original parent-space computation,
GPU execution, or public repository update is claimed.

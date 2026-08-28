# Exact row-2599 order-two triangle pilot

This producer studies the closed parameter triangle

`conv(chart0, chart89, chart113)`

at the pinned mathematical base `ec362dba`. Its two chart-0 sides are the
compiled edge-27 and edge-39 roadmaps. The third side is not compiled.

The producer independently reconstructs the 70 signed parent brackets and
proves every triangular Bernstein control strictly positive. It then pulls
all 17,824 candidate residual factors back to exact two-variable polynomials.
Each factor is classified as:

- exact interior zero, by a rational zero or an opposite-sign segment whose
  open part lies in the original triangle interior;
- empty on the whole closed triangle, by an exact Bernstein subdivision
  cover; or
- unresolved at the declared deterministic subdivision depth.

The exact factor IDs with an interior zero but no event on either compiled
edge are emitted separately. Such IDs demonstrate that the two-edge tree is
not even complete on this bounded order-two pilot; they are not a global
component theorem.

Replay after the checked-in artifact is present:

```bash
PYTHONDONTWRITEBYTECODE=1 python ops/team/triangle-certificate/build_order2_triangle_pilot.py --max-depth 3 > /tmp/triangle.json
cmp /tmp/triangle.json ops/team/triangle-certificate/ROW2599_ORDER2_TRIANGLE_PILOT.json
sha256sum -c ops/team/triangle-certificate/MANIFEST.sha256
```

The producer includes hostile semantic canaries. Independent referee replay
is intentionally left to a separate track.

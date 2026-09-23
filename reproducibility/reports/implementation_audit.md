# Implementation Audit Summary

Commit `c88b02b4`. Full point-by-point table in `docs/implementation_traceability.md`; executable checks in
`tests/` (16 tests, all passing).

## Result: implementation matches the paper's design, with two items that require wording

**Confirmed as described (21/21 checks):** 12-D observation with no obstacle features; H0 hybrid blend,
H1 A2C-only bypass, H2 model-free APF; per-axis 12 N clip/scale; gravity sign; relative-air-velocity drag;
semi-implicit Euler; altitude clamp + velocity reset; swept segment–AABB collision with priority over
success; nearest-surface signed clearance; center-distance APF; recorded epsilons; normalize-then-clip APF;
blend schedule {0.15,0.15,0.55,0.55} at {335.4,255,135,0} m; reward event ordering; map/start/goal/reset.

## Two mandatory clarifications (not bugs, but must be stated)

1. **Distance-basis asymmetry.** APF repulsion uses distance to the **AABB center**; reported clearance uses
   **nearest-surface** distance. Both are intentional and separately correct, but the paper must not conflate
   them. Center-basis repulsion under-repels large/wide obstacles and partly explains H2's high collision rate.

2. **Altitude penalty is dead code under the protocol.** Altitude is hard-clamped to [5,6] m before the reward
   reads it, so both altitude-penalty branches are unreachable. The paper should mark the altitude penalty as
   **inactive under the evaluation protocol** rather than an operative reward term.

## Horizon correction

`H = floor((D_xy/(v_ref·Δt))·1.8) + 300 = 1507` for `D_xy = 335.4 m`. Any "H = 500" text is stale.

## Controller/algorithm scope

Only A2C-based H0/H1 and non-learned H2 are in the evidence set. PPO/SAC are implemented in
`train_model` but are **not** part of the canonical results and are not claimed. H3/H5 exist in the manifest
but are excluded from the evidence set.

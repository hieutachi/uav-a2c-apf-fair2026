# Implementation-to-Manuscript Traceability

Line-by-line audit of the executable code (commit `c88b02b4`) against the paper's stated design.
Physics/APF/collision/reward live in `scripts/a2c_new.py`; the evaluation env `VNICTDroneEnv`
(`scripts/vnict_hybrid_experiments.py`) subclasses `DroneEnv3D` and changes nothing physical.
Automated checks: `tests/test_controller_semantics.py`, `tests/test_dynamics_and_collision.py`,
`tests/test_reward_and_horizon.py`.

| # | Claim | Code evidence | Verdict |
|---|---|---|---|
| 1 | Observation is exactly 12-D | `DroneEnv3D._obs` = `hstack(state[6], goal-disp[3], wind[3])`; `observation_space=Box((12,))` | CONFIRMED |
| 2 | A2C sees no obstacle geometry/distance | `_obs` contains only pos, vel, goal-displacement, wind; no obstacle term | CONFIRMED |
| 3 | H0 APF receives obstacle geometry | `apf_action(pos, target, self.obstacles, ...)` iterates obstacles | CONFIRMED |
| 4 | H1 bypasses APF blending | `policy_mode=="a2c"` → `blended = action` (APF term never added); manifest H1 also sets `apf_weight=0.0` | CONFIRMED |
| 5 | H2 is APF-only, no learned terms | `policy_mode=="apf"` → `blended = apf_f`; `model=None`, action=`zeros(3)` | CONFIRMED |
| 6 | Componentwise clip, per-axis 12 N | `np.clip(action,-1,1) * self.max_f` with `max_f=12.0` | CONFIRMED |
| 7 | Gravity sign / convention | `force[2] -= self.mass * self.g` (downward on +z-up frame) | CONFIRMED |
| 8 | Drag on relative air velocity | `acceleration = (force - kd*(velocity - wind))/mass` | CONFIRMED |
| 9 | Semi-implicit Euler | `velocity += a*dt` then `x += vx*dt` using the updated velocity | CONFIRMED |
| 10 | Altitude clamp then velocity reset | `z_cl = clamp(z_new, alt_min, alt_max); if z_cl != z_new: vz = 0` | CONFIRMED |
| 11 | Segment–AABB (swept) collision | `swept_aabb_collision(previous_pos, pos, o, radius)` slab test over 3 axes | CONFIRMED |
| 12 | Collision priority over success | `success = dist<ARRIVE_DIST and not collision`; `done = collision or success` | CONFIRMED |
| 13 | Signed clearance uses nearest surface | `aabb_signed_clearance` uses `max(lo-p, p-hi, 0)` (surface), not center | CONFIRMED |
| 14 | APF repulsion uses AABB **center** distance | `center=(...)/2; d=norm(pos-center)` | CONFIRMED (documented asymmetry with #13) |
| 15 | Epsilons recorded | goal `+1e-6` (`apf_action`, `_obs` dist), repulsion `d+1e-6`, degenerate-axis `1e-12` (slab test) | CONFIRMED |
| 16 | APF normalize then clip order | `if norm>1: f/=norm` then `np.clip(f_total,-1,1)` | CONFIRMED |
| 17 | Blend schedule at 335.4/255/135/0 m | `λ=clip(1-d/300, 0.15, 0.55)` → 0.15, 0.15, 0.55, 0.55 | CONFIRMED |
| 18 | Reward at declared state/order | reward computed after `drone.update`, distance shaping, then collision/success events, then altitude, clearance, step cost | CONFIRMED |
| 19 | Altitude penalty inactive after clamp | altitude is clamped to [5,6] before reward reads `st[2]`, so `st[2]∈[5,6]` and both penalty branches are unreachable under the protocol | CONFIRMED INACTIVE |
| 20 | Horizon formula & nominal output | `max_steps = int((D_xy/(5.0·dt))·1.8) + 300`, `dt=0.1`, `D_xy=‖(300,150)‖=335.41` → **H = 1507** | CONFIRMED (see note) |
| 21 | Map geometry / start / goal / reset | start `(0,0,5)`+U(−0.5,0.5); goal `(300,150,5)`; obstacles from seeded `build_map`/`generate_obstacles`; `map_sha256` recorded per unit | CONFIRMED |

## Horizon (Equation 6)

```
H = floor( (D_xy / (v_ref · Δt)) · 1.8 ) + 300
  v_ref = 5 m/s,  Δt = 0.1 s,  D_xy = sqrt(300² + 150²) = 335.41 m
  H = floor( (335.41 / 0.5) · 1.8 ) + 300 = floor(1207.48) + 300 = 1507
```

This supersedes any earlier "H = 500" statement. Observed H1 timeouts (steps up to the ~1507 cap, mean
237.8, sd 451.3) are consistent with this horizon.

## The two distance conventions (must be stated in the paper)

- **APF repulsion** uses distance to the **AABB center** (`apf_action`).
- **Reported clearance** uses **nearest-surface** signed distance (`aabb_signed_clearance`).

These are intentionally different quantities. The paper must not describe APF repulsion as surface-based; it
is center-based, which weakens repulsion for large obstacles and is part of why H2 (APF-only) collides often.

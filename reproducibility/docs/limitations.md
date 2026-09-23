# Known Limitations

## Information asymmetry (primary)
The H0–H1 comparison confounds the APF computation with the privileged obstacle geometry supplied to APF.
The A2C observation (12-D: position, velocity, goal displacement, wind) contains no obstacle information.
Any claim about "the APF contribution" must be read as "an APF-informed guidance channel plus its obstacle
input." Isolating potential-field computation would require an experiment where H1 receives matched obstacle
information (e.g., an obstacle-distance feature) without the APF blend.

## Simulation-only
- Point-mass dynamics (mass 0.5 kg, linear drag, per-axis 12 N force), not full 6-DOF rigid-body/rotor dynamics.
- Altitude hard-clamped to [5,6] m; the environment is effectively a thin 2.5-D slab.
- Wind is a Dryden-lite AR(1) process, not measured atmospheric turbulence.
- No sensor/state-estimation noise; the policy observes clean state.

## Metric interpretation
- Jitter and acceleration indices are finite-difference kinematics of sampled positions (m/s³, m/s²). They do
  **not** measure actuator effort, attitude smoothness, comfort, or flight readiness.
- APF repulsion uses AABB-center distance; reported clearance uses nearest-surface distance. These are
  different quantities and must not be conflated.
- The reward's altitude penalty is inactive under the protocol (dead code after the altitude clamp).

## Statistical
- Inferential n = 20 (map × training-run) for most metrics; 18 for successful-path efficiency (two units have
  no successful rollouts in one controller: `map-barrier-01/seed401`, `map-random-01/seed307`).
- Six paired tests, not multiplicity-corrected; treat p-values as exploratory.
- Each unit's 50 evaluation slots collapse to 32 distinct numerical seeds (18 exact repeats), so per-unit
  rates rest on fewer independent draws than the slot count suggests (pseudoreplication).
- H2 (APF-only) has no independent training-run replication; its five per-map units are repeated evaluations
  of one fixed controller.

## Reproducibility
- Archival reproduction from the ledger is exact. Evaluation from stored checkpoints is expected exact.
- Retraining is **not** bitwise reproducible: the learning stack (PyTorch) is not explicitly seeded and no
  CUDA/torch determinism flags are set.

## Scope
- Only A2C-based H0/H1 and non-learned H2 are evidence. No PPO/SAC/RRT results are claimed. H3 (no-wind) and
  H5 (strong-wind) are defined but excluded from the evidence set. `map-random-02` is defined but unused.

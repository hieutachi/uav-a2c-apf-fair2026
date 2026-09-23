# Seed Provenance

Every source of randomness traced to its exact code path (commit `c88b02b4`).

| Component | Seeded? | Code path | Seed value |
|---|---|---|---|
| Python `random` (train) | yes | `vnict_hybrid_experiments.py::train_model` | training seed (101…503) |
| NumPy `np.random` (train) | yes | `train_model` | training seed |
| SB3 `VecEnv` | yes | `make_vec_env(make_env, n_envs, seed=seed)` | training seed |
| Map / obstacle generator | yes | `generate_obstacles(..., rng=random.Random(seed))`; canonical maps via `run_rigorous_manifest.build_map` with `random.Random(spec["seed"])` | map spec seed (7001/7013/7019/7027) or training seed |
| PyTorch CPU | **no explicit seed** | A2C uses SB3 defaults; no `torch.manual_seed` in the pipeline | — |
| PyTorch CUDA | **not applicable** | training forced `device="cpu"` | — |
| Gymnasium env RNG (eval) | yes | `VNICTDroneEnv.reset(seed=numerical_seed)` → `super().reset(seed=seed)` sets `self.np_random` | `base_seed + episode_index` |
| Reset start perturbation | yes | `Drone3D.reset(rng=self.np_random)` (±0.5 m) | shares env RNG (= numerical seed) |
| Wind base direction + AR(1) innovations | yes | `WindModel(rng=self.np_random)` | shares env RNG (= numerical seed) |
| Policy stochasticity (train) | inherited | SB3 A2C rollout sampling driven by torch global RNG (unseeded) | — |
| Eval action selection | deterministic | `model.predict(obs, deterministic=True)`; H2 uses fixed APF | none |
| Vectorized/multiprocessing | n_envs=4 (train only) | SB3 `DummyVecEnv`/`SubprocVecEnv` via `make_vec_env` | training seed |

## Evaluation seed arithmetic

`numerical_seed = base_seed + episode_index`, `base ∈ {1009,1013,1019,1021,1031}`, `episode ∈ 0..9`.
Full 50-slot enumeration and duplicate flags: `data/derived/evaluation_seed_slots.csv`.

- 50 declared slots per unit.
- **32** distinct numerical seeds (range 1009–1040).
- **18** slots per unit reuse a numerical seed (overlap of the five 10-wide windows).

## Do duplicate numerical seeds produce duplicate conditions?

**Yes, within a unit.** The reset and wind streams are fully determined by the single env RNG seeded with the
numerical seed, and the evaluation policy is deterministic. `scripts/validate_ledger.py` confirms **1080**
duplicate-seed rollout instances (18 × 60 units) with byte-identical status/steps/clearance/jitter. Across
different units (different map or model) the same numerical seed yields a different full condition because the
obstacle geometry and/or policy differ; `full_condition_hash` (map_hash|controller|numerical_seed) captures this.

## Reproducibility consequence

Archival reproduction from the ledger is exact. Re-running the simulator from checkpoints is expected to be
exactly reproducible for evaluation (deterministic policy + seeded env). **Retraining from scratch is not
bitwise reproducible** because the learning stack (PyTorch) is not explicitly seeded and no CUDA/torch
determinism flags are set. Expected tolerance for retrained outcomes is stochastic, not bitwise — treat
retrained numbers as *comparable*, not identical.

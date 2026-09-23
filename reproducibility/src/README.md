# src/ — mapping to the audited implementation

To avoid forking the exact code that produced the canonical results, the release keeps the audited
implementation in the research repo's `scripts/` package and maps the conventional `src/` layout onto it.
The tests import these modules directly (see `tests/conftest.py`).

| src/ subpackage | Audited source (research repo) | Contents |
|---|---|---|
| `src/environments/` | `scripts/a2c_new.py` (`DroneEnv3D`, `WindModel`, `generate_obstacles`); `scripts/vnict_hybrid_experiments.py` (`VNICTDroneEnv`, `HybridConfig`) | 12-D observation env, Dryden-lite wind, maps |
| `src/controllers/` | `scripts/a2c_new.py::apf_action`; `DroneEnv3D.step` blend logic | APF, hybrid blend, H1/H2 policy modes |
| `src/training/` | `scripts/vnict_hybrid_experiments.py::train_model`; `scripts/run_rigorous_manifest.py::train_model` | A2C/PPO/SAC training entry points |
| `src/evaluation/` | `scripts/run_rigorous_manifest.py::evaluate_episodes`; `scripts/vnict_hybrid_experiments.py::evaluate` | deterministic rollout + per-episode audit |
| `src/metrics/` | `scripts/vnict_hybrid_experiments.py` (`path_length`, `acceleration_index`, `jitter_index`, `min_obstacle_distance`); `scripts/a2c_new.py::aabb_signed_clearance` | metric definitions |
| `src/utils/` | `scripts/a2c_new.py` (`clamp`, `swept_aabb_collision`, `smooth_trajectory`); `scripts/run_rigorous_manifest.py` (provenance/checksum helpers) | geometry, smoothing, provenance |

Checksums of these sources are recorded in `manifests/raw_artifacts.sha256` and validated by
`scripts/validate_artifacts.py`.

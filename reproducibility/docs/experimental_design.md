# Experimental Design and the Inferential Unit

## Resolved terminology

The manuscript uses the word **"checkpoint"** for the five per-map objects. The code shows these are
**independently trained models**, not periodic checkpoints of one run:

- `scripts/vnict_hybrid_experiments.py::train_model` seeds `random`, `numpy`, and the vectorized
  environment with the training seed, then trains a fresh A2C model from scratch.
- Each `(map, training_seed)` pair produces one saved model (`checkpoint_sha256` recorded per unit in
  `results/rigorous/runs/<run_id>.json`).
- Training seed labels: `101, 211, 307, 401, 503` → five independent runs/models per map.

**Action:** replace "checkpoint" with **"independent training run / model"** throughout the manuscript
(see `docs/manuscript_revision_plan.md`).

## Hierarchy

```
configuration (H0 / H1 / H2)
  └── map (random-01, corridor-01, barrier-01, mixed-01)
        └── training run / model (seed 101, 211, 307, 401, 503)   # H2: nominal label only, non-learned
              └── evaluation seed slot (base ∈ {1009,1013,1019,1021,1031} × episode 0..9 = 50 slots)
                    └── rollout (one deterministic episode)
```

- 4 maps × 5 runs = **20 units per learned configuration**; 20 × 50 = **1000 rollouts** per configuration.
- H0 and H1 both instantiate all 20 `(map, seed)` units → **20 genuine paired units**.

## Inferential unit

The unit of statistical inference is the **`(map_id, training_run)` pair**. Each unit's success rate is the
proportion over its 50 evaluation rollouts. Paired H0–H1 inference is computed over the 20 matched units
(`analysis/02_compute_statistics.py`), verified by asserting identical `(map, seed)` key sets for H0 and H1.

## Pairing is genuine, with a caveat on realization matching

- H0 and H1 share the **same maps** (identical `map_sha256`) and the **same training seed labels**, so the
  pairing is by real shared factors, not merely matching numeric labels.
- Within a unit, evaluation uses `numerical_seed = base_seed + episode_index` passed to `env.reset(seed=...)`,
  which seeds the reset perturbation and the AR(1) wind stream identically across controllers for the same
  numerical seed. Thus H0 and H1 rollouts at the same slot share the wind/reset realization.
- **Caveat:** H0 and H1 do **not** share the trained policy weights (they are different models by design), so
  "matched" refers to map, budget, protocol, and evaluation realization — not to the learned policy.

## H2 has no independent training replication

H2 is APF-only and non-learned (`model=None`, `policy_mode="apf"`, `timesteps=0`). Its five per-map "units"
are labeled with training seeds for bookkeeping but are **repeated deterministic evaluations of one fixed
controller**, not independent training runs. H2 therefore provides repeated evaluation rows but **no
training-run replication**, and must not be treated as five independent samples in any inferential claim.

## Information asymmetry (governing limitation)

The A2C observation is 12-dimensional `[position(3), velocity(3), goal-displacement(3), wind(3)]` and contains
**no obstacle geometry**. H0 receives obstacle geometry only through the APF channel; H1 receives no obstacle
geometry at all. The H0–H1 contrast therefore evaluates **an APF-informed guidance channel together with its
privileged obstacle-geometry input** — it does not isolate potential-field computation from the value of the
additional obstacle information.

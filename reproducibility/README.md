# Component Evaluation of Hybrid A2C–APF Guidance in Wind-Perturbed UAV Simulation — Reproducibility Package

## 1. Paper, authors, venue, citation
- **Paper:** *Component Evaluation of Hybrid A2C–APF Guidance in Wind-Perturbed UAV Simulation*
- **Authors:** Hieu Ta Chi; Huy Nguyen Anh; Hoa Vu Minh
- **Venue:** FAIR 2026 (submission).
- **Cite:** see [`CITATION.cff`](CITATION.cff). Also cite this repository (release tag `<TAG>`).

## 2. Scope statement
> This repository evaluates an APF-informed guidance channel in a fixed A2C UAV-navigation simulation. The
> H0–H1 comparison includes an obstacle-information asymmetry: H0 receives obstacle geometry through APF
> whereas H1 does not. It therefore does not isolate potential-field computation from the value of additional
> obstacle geometry.

## 3. Repository map
```
reproducibility/
├── README.md  LICENSE  CITATION.cff  .gitignore
├── environment.yml  requirements.txt  Dockerfile  Makefile
├── configs/     base, h0_hybrid, h1_a2c_only, h2_apf_only, evaluation, seed_registry (YAML)
├── src/         package placeholders; audited implementation lives in ../scripts (a2c_new, vnict_hybrid_experiments)
├── scripts/     build_ledger, build_manifests, validate_ledger, validate_artifacts,
│                run_smoke_test, reproduce_analysis, reproduce_figures, build_release_manifest, verify_environment.sh
├── analysis/    01_build_unit_summaries → 02_compute_statistics → 03_reconcile_manuscript_claims → 04_generate_tables_and_figures
├── tests/       controller_semantics, dynamics_and_collision, reward_and_horizon, seed_registry, result_ledger
├── data/        raw/ (rollout_ledger.csv + schema + manuscript_claims.csv), derived/ (regenerated summaries/stats)
├── models/      README (checkpoints not redistributed; checksummed in research repo)
├── figures/     source/, generated/
├── tables/      generated/, README
├── docs/        experimental_design, seed_provenance, implementation_traceability,
│                manuscript_revision_plan, limitations, computational_requirements
├── manifests/   raw_artifacts.sha256/.csv, release_artifacts.sha256, source_commit.txt, audit_scope.md
└── reports/     implementation_audit, data_validation, determinism_check,
                 result_reconciliation, reconciliation.csv, result_lock_certificate
```

## 4. Hardware & software requirements
- **Analysis reproduction:** any CPU, ~1 GB RAM, ~20 MB disk, no GPU. Python 3.13 + `numpy==2.1.1`,
  `scipy==1.15.2` (+ matplotlib/pandas for figures).
- **Simulation/retraining:** adds `gymnasium==1.2.0`, `stable-baselines3==2.7.0`, `torch==2.6.0` (CPU is
  sufficient; A2C training forced `device="cpu"`). See [`docs/computational_requirements.md`](docs/computational_requirements.md).

## 5. Installation
```bash
# conda
conda env create -f environment.yml && conda activate uav-a2c-apf-repro
# or pip
python -m pip install -r requirements.txt
bash scripts/verify_environment.sh
```

## 6. One-command smoke test
```bash
make smoke        # or: python scripts/run_smoke_test.py
```

## 7. One-command analysis reproduction (from the archived ledger)
```bash
make analysis     # or: python scripts/reproduce_analysis.py
# regenerates data/derived/*, reports/result_reconciliation.md; fails on any MISMATCH/UNREPRODUCIBLE
```

## 8. One-command figures/tables
```bash
make figures      # or: python scripts/reproduce_figures.py  -> tables/generated/, figures/generated/
```

## 9. Optional: rebuild the ledger, re-evaluate, or retrain
```bash
python scripts/build_ledger.py                       # rebuild ledger from immutable episode_audit.csv
# Re-evaluate stored checkpoints (expected exact match), from the research repo root:
python scripts/run_rigorous_manifest.py --mode full --evaluation-only \
  --hypotheses H0 H1 H2 --maps map-random-01 map-corridor-01 map-barrier-01 map-mixed-01 \
  --train-seeds 101 211 307 401 503 --eval-seeds 5 --episodes 10 --force
# Retraining is NOT bitwise reproducible (see docs/seed_provenance.md).
```
Archival result reproduction (steps 6–8) is fully separated from retraining (step 9).

## 10. Runtime, resources, determinism caveats
- Analysis: **< 30 s**, deterministic, machine-independent.
- Checkpoint re-evaluation: minutes, deterministic (≤1e-6 tolerance on continuous metrics).
- Retraining: long (see manifest projection), **not** bitwise reproducible.

## 11. Data/model availability & licensing
- Code + docs: MIT ([`LICENSE`](LICENSE)).
- Ledger and derived data: included, regenerable.
- Checkpoints (40) and per-episode trajectories (4000 `.npz`): **not redistributed here**; fetch from the
  research repo / data host and verify against recorded `checkpoint_sha256` / per-unit `SHA256SUMS`
  (use Git LFS for large binaries). No secrets, API keys, credentials, or personal data are included.

## 12. Result-reproduction table (expected key values, tolerances)
| Quantity | Expected | Tolerance | Source |
|---|---:|---:|---|
| H0 success / collision / timeout | 1000 / 0 / 0 | exact | `table_outcomes.csv` |
| H1 success / collision / timeout | 830 / 58 / 112 | exact | `table_outcomes.csv` |
| H2 success / collision / timeout | 55 / 905 / 40 | exact | `table_outcomes.csv` |
| H0 jitter mean ± sd (m/s³) | 28.53 ± 9.03 | ±0.01 | `table_continuous.csv` |
| H1 jitter mean ± sd (m/s³) | 55.33 ± 14.68 | ±0.01 | `table_continuous.csv` |
| Paired H1−H0 success `dz` / Wilcoxon p (n=20) | −0.509 / 0.0273 | ±0.005 / ±0.001 | `table_paired.csv` |
| Paired H1−H0 jitter `dz` / p (n=20) | 1.78 / <1e-5 | ±0.01 | `table_paired.csv` |
| Paired efficiency n | 18 | exact | `table_paired.csv` |
| Unique effective numerical seeds / unit | 32 | exact | `evaluation_seed_slots.csv` |

Full claim-by-claim: [`reports/result_reconciliation.md`](reports/result_reconciliation.md) (69/69 reconcile).

## 13. Known limitations
Information asymmetry (H0 sees obstacle geometry via APF, H1 does not); simulation-only point-mass dynamics;
kinematic (not actuator) smoothness metrics; APF center-distance vs surface-distance clearance; inactive
altitude penalty; n=20 paired units, exploratory (uncorrected) p-values; 32-of-50 effective seeds
(pseudoreplication); no PPO/SAC/RRT claims. Full list: [`docs/limitations.md`](docs/limitations.md).

## 14. How to cite
Cite the paper (§1) and this repository via [`CITATION.cff`](CITATION.cff) with the release tag. Release
integrity is certified in [`reports/result_lock_certificate.md`](reports/result_lock_certificate.md)
(decision: **CONDITIONAL PASS**).

# Models

Trained A2C checkpoints for H0 and H1 (one per `map × training_seed` = 40 learned models) are **not
redistributed in this package** because they are large binaries. They exist in the research repo at:

```
results/rigorous/artifacts/<run_id>/checkpoints/
```

Each unit's `run` JSON (`results/rigorous/runs/<run_id>.json`) records `checkpoint_sha256`, and each unit's
`SHA256SUMS` records file-level checksums. `manifests/raw_artifacts.csv` inventories these authority files.

H2 (APF-only) is non-learned and has no model.

## Obtaining / verifying checkpoints
- If distributing separately, use Git LFS or a data host and verify against the recorded `checkpoint_sha256`.
- Archival result reproduction (tables/figures/statistics) does **not** require the checkpoints — it runs
  entirely from `data/raw/rollout_ledger.csv`.
- Re-evaluating checkpoints (expected exact match) uses the command in `docs/computational_requirements.md`.

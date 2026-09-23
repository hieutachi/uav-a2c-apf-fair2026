# Computational Requirements

## Archival analysis reproduction (recommended, fast)
- **CPU:** any x86-64; **RAM:** ~1 GB; **Disk:** ~20 MB (ledger + derived).
- **GPU:** not required.
- **Software:** Python 3.13, `numpy==2.1.1`, `scipy==1.15.2` (matplotlib/pandas for figures).
- **Runtime:** `scripts/reproduce_analysis.py` completes in **< 30 s**.
- **Determinism:** exact; machine-independent.

## Re-evaluation from stored checkpoints (optional)
- **CPU-bound** (training/eval forced `device="cpu"`); GPU optional and unused by A2C here.
- **RAM:** ~2 GB. **Disk:** checkpoints ~tens of MB each (40 models).
- **Runtime:** minutes for the 4000 evaluation rollouts on a modern desktop.
- Command:
```bash
python scripts/run_rigorous_manifest.py --mode full --evaluation-only \
  --hypotheses H0 H1 H2 --maps map-random-01 map-corridor-01 map-barrier-01 map-mixed-01 \
  --train-seeds 101 211 307 401 503 --eval-seeds 5 --episodes 10 --force
```
- **Determinism:** expected exact for status/length; ≤1e-6 tolerance for continuous metrics.

## Retraining from scratch (optional, NOT bitwise reproducible)
- Reference hardware for the original work: Ryzen 9 9950X (16C/32T), 64 GB RAM, RTX 3090 (unused for A2C).
- **Budget:** 5,000,000 environment steps per learned unit × 40 learned units.
- **Serial projection:** the manifest's conservative estimate is ~44.8 days serial for the full trainable
  matrix; the four-map A2C H0/H1 subset is a fraction of that and is parallelizable across cores.
- **Determinism:** not bitwise reproducible (PyTorch not explicitly seeded; no CUDA determinism flags). Treat
  retrained results as comparable in distribution, not identical. See `docs/seed_provenance.md`.

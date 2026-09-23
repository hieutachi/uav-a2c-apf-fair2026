# Determinism Check

## Method

Two levels of replay determinism are relevant:

1. **Archival ledger replay** — recomputing every reported number from the frozen ledger.
2. **Simulator replay** — re-running rollouts and comparing to the ledger.

## 1. Archival ledger replay — PASS (exact)

`analysis/01`–`analysis/03` reproduce all 69 audited manuscript numbers from
`data/raw/rollout_ledger.csv` with 29 EXACT and 40 ROUNDING matches, 0 mismatches
(`reports/result_reconciliation.md`). This is deterministic and machine-independent.

## 2. Duplicate-seed internal determinism — PASS (exact, and diagnostic)

Within each unit, 18 of 50 slots reuse a numerical seed. Because the env RNG is fully determined by that
seed and the policy is deterministic, these are exact repeats. `scripts/validate_ledger.py` verifies **1080**
byte-identical duplicate rollout instances across the 60 units (status, transitions, final distance,
clearance, jitter all identical). This demonstrates the evaluation path is deterministic given a seed, and
simultaneously flags that effective distinct rollouts per unit = 32.

## 3. Full simulator replay from checkpoints — NOT EXECUTED in this audit

Re-evaluating the stored H0/H1 checkpoints (`deterministic=True`) is expected to reproduce the ledger
exactly on the same NumPy/SciPy/SB3 stack, because evaluation contains no unseeded randomness. This was not
re-executed here to preserve the immutable artifacts and because it requires loading the large checkpoint
binaries. The command to perform it independently:

```bash
python scripts/run_rigorous_manifest.py --mode full --evaluation-only \
  --hypotheses H0 H1 H2 --maps map-random-01 map-corridor-01 map-barrier-01 map-mixed-01 \
  --train-seeds 101 211 307 401 503 --eval-seeds 5 --episodes 10 --force
```

Expected agreement: **exact** for status/length; **tolerance ≤ 1e-6** for continuous metrics (float
accumulation order is fixed).

## 4. Retraining determinism — NOT REPRODUCIBLE (bitwise)

The learning stack is not explicitly seeded (no `torch.manual_seed`, no CUDA determinism flags; see
`docs/seed_provenance.md`). Retrained models will differ from the archived checkpoints. Reported aggregate
outcomes should be treated as reproducible in distribution (comparable), not bitwise identical, after
retraining. This is the principal reason the release decision is **CONDITIONAL PASS** rather than PASS.
